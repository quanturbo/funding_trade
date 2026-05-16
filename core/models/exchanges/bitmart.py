from typing import Dict

from .base import BaseExchangeMonitor


class BitmartMonitor(BaseExchangeMonitor):
    id = 'bitmart'

    async def fetch_raw_tickers(self):
        return await self.exchange.fetch_tickers()

    def get_exchange_options(self) -> Dict:
        return {"options": {"defaultType": "swap"}}

    # async def get_only_perpetual(self, tickers: Dict[str, Dict]):
    #     return {symbol: data for symbol, data in tickers.items()
    #                      if '-' not in data.get('symbol', '')}

    def extract_prices(self, ticker: Dict) -> tuple:
        info = ticker.get('info', {})

        funding_rate = float(info.get('funding_rate', 0))
        funding_time = int(float(info.get('funding_time', 0)))  # 1762527600000

        volume = int(ticker.get('quoteVolume', 0))  # 1762527600000


        return funding_rate, funding_time, volume
