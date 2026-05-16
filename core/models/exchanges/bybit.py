from typing import Dict

from .base import BaseExchangeMonitor


class BybitMonitor(BaseExchangeMonitor):
    id = 'bybit'

    async def fetch_raw_tickers(self):
        return await self.exchange.fetch_funding_rates()

    def get_exchange_options(self) -> Dict:
        return {}

    async def get_only_perpetual(self, tickers: Dict[str, Dict]):
        return {symbol: data for symbol, data in tickers.items()
                         if data.get('info', {}).get('deliveryTime') == '0'}

    def extract_prices(self, ticker: Dict) -> tuple:
        info = ticker.get('info', {})

        funding_rate = float(info.get('fundingRate', 0))
        funding_time = int(info.get('nextFundingTime', 0))  # 1762527600000

        volume = 0  # no volume

        return funding_rate, funding_time, volume
