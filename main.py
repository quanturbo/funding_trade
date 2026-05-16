# file: funding_rate_monitor.py
import asyncio
import time
import html
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from tabulate import tabulate

from config import min_funding_rate, left_show_time, telegram_config
from core.models.exchanges import (
    BybitMonitor, KucoinMonitor, BinanceMonitor, MexcMonitor, HtxMonitor,
    GateMonitor, OkxMonitor, BingxMonitor, BitgetMonitor, HyperliquidMonitor,
    LbankMonitor, BitmartMonitor, WhitebitMonitor, CoinexMonitor
)
from core.notify.telegram import TelegramNotifier
from loguru import logger


class FundingRateMonitor:
    MONITORS = [
        BybitMonitor,
        KucoinMonitor,
        BinanceMonitor,
        MexcMonitor,
        GateMonitor,
        OkxMonitor,
        BingxMonitor,
        BitgetMonitor,
        HyperliquidMonitor,
        HtxMonitor,
        LbankMonitor,
        BitmartMonitor,
        WhitebitMonitor,
        CoinexMonitor
    ]

    def __init__(self, telegram_config: Dict, min_funding_rate: float, left_show_time: int):
        self.notifier = TelegramNotifier(
            telegram_config["bot_token"], telegram_config["chat_id"]
        )
        self.min_funding_rate = min_funding_rate
        self.left_show_time = left_show_time
        self.notified = set()
        self.monitors = [m() for m in self.MONITORS]

    async def _fetch_rates(self) -> List:
        """Fetch normalized, prefiltered tickers from all exchanges."""
        tasks = [m.get_tickers(self.min_funding_rate) for m in self.monitors]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        all_rates = []
        for result in results:
            if isinstance(result, BaseException):
                logger.error(f"Monitor error: {result}")
                continue
            all_rates.extend(result)
        return all_rates

    def _get_next_rates(self, rates: List) -> List:
        filtered = []
        for r in rates:
            h, m, _ = get_time_until_funding(r.funding_time)
            minutes_left = h * 60 + m
            if not (0 <= minutes_left <= self.left_show_time):
                continue
            filtered.append(r)
        filtered.sort(key=lambda x: abs(x.funding_rate), reverse=True)
        return filtered

    def _deduplicate(self, rates: List) -> List:
        seen, unique = set(), []
        for r in rates:
            key = f"{r.exchange}:{r.symbol}"
            if key not in seen:
                seen.add(key)
                unique.append(r)
        return unique

    def _build_table_messages(self, rates: List) -> Tuple[str, str]:
        table_data = [
            [(r.exchange or "").upper()[:6], r.symbol, f"{r.funding_rate:+.3f}%"]
            for r in rates
        ]

        table_str = tabulate(
            table_data, headers=["EXCH", "SYMBOL", "RATE%"],
            tablefmt="plain", numalign="right",
        )

        plain_table = f"📊 Funding Rates (<{self.left_show_time}m)\n\n{table_str}"
        html_msg = f"<b>📊 Funding Rates (&lt;{self.left_show_time}m)</b>\n<pre>{html.escape(table_str)}</pre>"
        return plain_table, html_msg

    async def _send_alerts(self, rates: List, html_msg: str) -> int:
        alerts_sent = 0
        for r in rates:
            key = f"{r.exchange}:{r.symbol}:{r.funding_time}"
            h, m, _ = get_time_until_funding(r.funding_time)
            minutes_left = h * 60 + m
            if self._should_alert(key, minutes_left):
                self.notified.add(key)
                alerts_sent += 1
        if alerts_sent > 0:
            await self.notifier.send_alert(html_msg)
        return alerts_sent

    def _should_alert(self, key: str, minutes_left: int) -> bool:
        return 0 <= minutes_left <= self.left_show_time and key not in self.notified

    def _cleanup_old_notifications(self):
        now = int(time.time() * 1000)
        cutoff = now - (8 * 3600 * 1000)
        self.notified = {k for k in self.notified if int(k.split(':')[-1]) > cutoff}

    async def run_check_cycle(self):
        rates = await self._fetch_rates()
        next_rates = self._get_next_rates(rates)
        unique = self._deduplicate(next_rates)
        if not unique:
            logger.info("No relevant funding rates to alert")
            return
        plain_table, html_msg = self._build_table_messages(unique)
        alerts_sent = await self._send_alerts(unique, html_msg)
        logger.info("\n" + plain_table)
        if alerts_sent:
            logger.info(f"✅ Sent {alerts_sent} new alerts")
        self._cleanup_old_notifications()

    async def start(self):
        logger.info(f"🤖 Funding monitor started ({len(self.monitors)} exchanges)")
        logger.info(f"🚨 Min rate: {self.min_funding_rate}% | Show time: {self.left_show_time}m")

        try:
            while True:
                sleep_sec = self._seconds_until_check()
                logger.info(f"⏳ Sleeping {sleep_sec/60:.1f} min until next check...")
                await asyncio.sleep(sleep_sec)

                await self.run_check_cycle()

                # Sleep until next full hour (skip duplicate triggers)
                next_hour = (datetime.utcnow().replace(minute=0, second=0, microsecond=0)
                             + timedelta(hours=1))
                sleep_till_next_hour = (next_hour - datetime.utcnow()).total_seconds()
                logger.info(f"🕒 Waiting {sleep_till_next_hour/60:.1f} min for next funding window...")
                await asyncio.sleep(sleep_till_next_hour)
        except KeyboardInterrupt:
            logger.info("🛑 Stopped manually")
        finally:
            await self.cleanup()

    def _seconds_until_check(self) -> float:
        """
        Compute how long to wait until (next hour - left_show_time).
        If we are already within the left_show_time window, return 0 (run immediately).
        """
        now = datetime.utcnow()
        next_hour = (now.replace(minute=0, second=0, microsecond=0)
                     + timedelta(hours=1))
        check_time = next_hour - timedelta(minutes=self.left_show_time)

        # If we're already inside the window, start immediately
        if now >= check_time:
            return 0.0

        return (check_time - now).total_seconds()


    async def cleanup(self):
        for m in self.monitors:
            await m.close()
        logger.info("✅ Cleanup complete")


def get_time_until_funding(funding_timestamp) -> Tuple[int, int, int]:
    diff = funding_timestamp - (time.time() * 1000)
    if diff <= 0:
        return 0, 0, 0
    total_sec = diff / 1000
    return int(total_sec // 3600), int((total_sec % 3600) // 60), int(total_sec % 60)


async def main():
    bot = FundingRateMonitor(
        telegram_config,
        min_funding_rate=min_funding_rate,
        left_show_time=left_show_time,
    )
    await bot.start()


if __name__ == "__main__":
    asyncio.run(main())
