from typing import Dict

from .base import BaseExchangeMonitor


class KucoinMonitor(BaseExchangeMonitor):
    id = 'kucoinfutures'

    async def fetch_raw_tickers(self):
        return await self.exchange.fetch_tickers()

    def get_exchange_options(self) -> Dict:
        return {}

    async def get_only_perpetual(self, tickers: Dict[str, Dict]):
        return {symbol: data for symbol, data in tickers.items()
                         if data.get('info', {}).get('type') == "FFWCSX"}

    def extract_prices(self, ticker: Dict) -> tuple:
        info = ticker.get('info', {})

        funding_rate = float(info.get('fundingFeeRate', 0))
        funding_time = int(info.get('nextFundingRateDateTime', 0))
        volume = int(ticker.get('volumeOf24h', 0))

        return funding_rate, funding_time, volume
