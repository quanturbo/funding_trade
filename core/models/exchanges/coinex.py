from typing import Dict

from .base import BaseExchangeMonitor


class CoinexMonitor(BaseExchangeMonitor):
    id = 'coinex'

    async def fetch_raw_tickers(self):
        return await self.exchange.fetch_funding_rates()

    def get_exchange_options(self) -> Dict:
        return {"options": {"defaultType": "swap"}}

    # async def get_only_perpetual(self, tickers: Dict[str, Dict]):
    #     return {symbol: data for symbol, data in tickers.items()
    #                      if '-' not in data.get('symbol', '')}

    def extract_prices(self, ticker: Dict) -> tuple:
        funding_rate = float(ticker.get('fundingRate', 0))
        funding_time = int(float(ticker.get('fundingTimestamp', 0)))

        volume = 0

        return funding_rate, funding_time, volume
