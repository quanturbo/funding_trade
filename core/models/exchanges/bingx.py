from typing import Dict, Any
import asyncio
from .base import BaseExchangeMonitor


class BingxMonitor(BaseExchangeMonitor):
    id = 'bingx'

    async def fetch_raw_tickers(self):
        return await self.exchange.fetch_funding_rates()

    def get_exchange_options(self) -> Dict:
        return {"options": {"defaultType": "swap"}}

    async def get_only_perpetual(self, tickers: Dict[str, Dict]):
        return tickers

    def extract_prices(self, ticker: Dict) -> tuple:
        info = ticker.get('info', {})

        funding_rate = float(info.get('lastFundingRate', 0))
        funding_time = int(info.get('nextFundingTime', 0))  # 1762675200000

        volume = 0  # no volume

        return funding_rate, funding_time, volume
