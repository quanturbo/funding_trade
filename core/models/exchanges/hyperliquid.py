from typing import Dict

from .base import BaseExchangeMonitor


class HyperliquidMonitor(BaseExchangeMonitor):
    id = 'hyperliquid'

    async def fetch_raw_tickers(self):
        return await self.exchange.fetch_funding_rates()

    def get_exchange_options(self) -> Dict:
        return {'options': {'defaultType': 'swap'}}

    def extract_prices(self, ticker: Dict) -> tuple:
        info = ticker.get('info', {})

        funding_rate = float(ticker.get('fundingRate', 0))
        funding_time = int(ticker.get('fundingTimestamp', 0))  # 1762675200000
        volume = int(float(info.get('dayNtlVlm', 0)))

        return funding_rate, funding_time, volume