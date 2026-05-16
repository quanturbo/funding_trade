# path: monitors/binance_monitor.py
from datetime import datetime
from typing import Dict, Any
import asyncio
from .base import BaseExchangeMonitor


class BinanceMonitor(BaseExchangeMonitor):
    id = 'binance'

    async def fetch_raw_tickers(self):
        return await self.exchange.fetch_funding_rates()

    def get_exchange_options(self) -> Dict:
        return {"options": {"defaultType": "swap"}}

    async def get_only_perpetual(self, tickers: Dict[str, Dict]):
        return tickers

    def extract_prices(self, ticker: Dict) -> tuple:
        info = ticker.get('info', {})

        funding_rate = float(info.get('lastFundingRate', 0))
        funding_time = int(info.get('nextFundingTime', 0))  # 1762527600000

        volume = 0  # no volume

        return funding_rate, funding_time, volume

    # async def fetch_raw_tickers(self) -> Dict[str, Any]:
    #     mark_prices_task = asyncio.create_task(self.exchange.fetch_mark_prices())
    #     tickers_task = asyncio.create_task(self.exchange.fetch_tickers())
    #     mark_prices, tickers = await asyncio.gather(mark_prices_task, tickers_task)
    #
    #     merged_data = {}
    #     for symbol, mark_data in mark_prices.items():
    #         ticker = tickers.get(symbol, {})
    #
    #         ticker_last_upd = int(datetime.now().timestamp()) - ticker.get("timestamp", 0) / 1000
    #         if ticker_last_upd > 3600:
    #             continue  # skip old if data is longer than hour
    #
    #         merged_data[symbol] = {
    #             "last": float(ticker.get("last", 0)),
    #             "markPrice": float(mark_data.get("markPrice", 0)),
    #             "indexPrice": float(mark_data.get("indexPrice", 0)),
    #             "volume": int(ticker.get("quoteVolume", 0)),
    #         }
    #     return merged_data
    #
    # def get_exchange_options(self) -> Dict:
    #     return {"options": {"defaultType": "swap"}}
    #
    # def extract_prices(self, ticker: Dict) -> tuple:
    #     return tuple(ticker.values())
