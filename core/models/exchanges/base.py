# core/models/exchanges/base.py
import traceback
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List

import ccxt.async_support as ccxt

from core.models import FundingTicker
from core.utils import logger


class BaseExchangeMonitor(ABC):
    """Base class for all exchange monitors."""
    id = "base"

    def __init__(self, threshold_percent: float = 1.0):
        self.threshold_percent = threshold_percent
        self.exchange = getattr(ccxt, self.id)(
            {**self.get_exchange_options(), "enableRateLimit": True}
        )

    @abstractmethod
    def get_exchange_options(self) -> Dict:
        """Exchange-specific CCXT config."""
        return {"options": {"defaultType": "future"}}

    @abstractmethod
    def extract_prices(self, ticker: Dict) -> tuple:
        """
        Extract funding_rate, funding_time, volume from ticker.
        Returns:
            (funding_rate: float, funding_time: int (ms), volume: float)
        """
        pass

    @abstractmethod
    async def fetch_raw_tickers(self):
        """Fetch tickers from the exchange."""
        pass

    async def get_only_perpetual(self, tickers: Dict[str, Dict]):
        """Optionally override to limit tickers to perpetual contracts."""
        return tickers

    async def get_funding_time(self, symbol: str):
        """Fetch missing funding time for a symbol if the API doesn’t include it."""
        try:
            return (await self.exchange.fetch_funding_rate(symbol))['fundingTimestamp']
        except Exception as e:
            raise NotImplementedError(f"{self.id} {symbol} get_funding_time not implemented")

    async def get_tickers(self, min_funding_rate: float) -> List[FundingTicker]:
        """
        Fetch all tickers → normalize → filter by min funding rate.
        Returns a list of FundingTicker instances ready for the monitor.
        """
        all_prices = []

        try:
            tickers = await self.fetch_raw_tickers()
            tickers = await self.get_only_perpetual(tickers)

            for symbol, ticker in tickers.items():
                try:
                    funding_rate, funding_time, volume = self.extract_prices(ticker)

                    # Skip invalid funding_rate
                    if (funding_rate := funding_rate * 100) is None:
                        continue

                    # Skip if below min rate (abs)
                    if abs(funding_rate) < min_funding_rate:
                        continue

                    # If funding time missing, fetch it
                    if not funding_time:
                        try:
                            funding_time = await self.get_funding_time(symbol)
                        except NotImplementedError:
                            continue
                        except Exception as e:
                            logger.warning(f"{self.id} {symbol} funding time fetch error: {e}")
                            continue

                    if not funding_time or funding_time <= 0:
                        continue

                    all_prices.append(
                        FundingTicker(
                            exchange=self.id,
                            symbol=symbol.split(":")[0],
                            funding_rate=funding_rate,
                            funding_time=funding_time,
                            volume=volume,
                        )
                    )

                except Exception as e:
                    logger.error(f"{self.id} {symbol} extract error: {e}")
                    traceback.print_exc()
                    continue

        except Exception as e:
            logger.error(f"Error fetching {self.id}: {e}")
            traceback.print_exc()

        return all_prices

    async def close(self):
        """Close the CCXT connection."""
        if self.exchange:
            await self.exchange.close()
