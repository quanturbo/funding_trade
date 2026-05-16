from typing import Dict

from .base import BaseExchangeMonitor


class GateMonitor(BaseExchangeMonitor):
    id = 'gate'

    async def fetch_raw_tickers(self):
        return await self.exchange.fetch_funding_rates()

    def get_exchange_options(self) -> Dict:
        return {'options': {'defaultType': 'swap'}}

    def extract_prices(self, ticker: Dict) -> tuple:
        info = ticker.get('info', {})

        funding_rate = float(info.get('funding_rate', 0))
        funding_time = int(info.get('funding_next_apply', 0)) * 1000
        volume = 0

        return funding_rate, funding_time, volume