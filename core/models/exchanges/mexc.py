import time
from datetime import datetime, timedelta
from operator import index
from typing import Dict

from .base import BaseExchangeMonitor


class MexcMonitor(BaseExchangeMonitor):
    id = 'mexc'

    async def fetch_raw_tickers(self):
        return await self.exchange.fetch_tickers()

    def get_exchange_options(self) -> Dict:
        return {'options': {'defaultType': 'swap'}}

    def extract_prices(self, ticker: Dict) -> tuple:
        info = ticker.get('info', {})

        funding_rate = float(info.get('fundingRate', 0))
        funding_time = 0  # ((int(time.time() * 1000) // 3600000) + 1) * 3600000
        volume = 0

        return funding_rate, funding_time, volume

    # async def get_funding_time(self, symbol: str):
    #     return (await self.exchange.fetch_funding_rate(symbol))['fundingTimestamp']
