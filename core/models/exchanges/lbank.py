from typing import Dict

from .base import BaseExchangeMonitor


class LbankMonitor(BaseExchangeMonitor):
    id = 'lbank'

    async def fetch_raw_tickers(self):
        return await self.exchange.fetch_funding_rates()

    def get_exchange_options(self) -> Dict:
        return {"options": {"defaultType": "swap"}}
    #
    # async def get_only_perpetual(self, tickers: Dict[str, Dict]):
    #     return {symbol: data for symbol, data in tickers.items()
    #                      if '-' not in data.get('symbol', '')}

    def extract_prices(self, ticker: Dict) -> tuple:
        funding_rate = float(ticker.get('fundingRate', 0) or 0)  #  or 0 need because some is not trading
        funding_time = int(ticker.get('fundingTimestamp', 0))  # 1762527600000

        volume = 0  # no volume

        return funding_rate, funding_time, volume
