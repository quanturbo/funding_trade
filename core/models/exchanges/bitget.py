import time
from typing import Dict

from .base import BaseExchangeMonitor


class BitgetMonitor(BaseExchangeMonitor):
    id = 'bitget'

    async def fetch_raw_tickers(self):
        return await self.exchange.fetch_funding_rates()

    async def get_funding_time(self, symbol: str):
        return (await self.exchange.fetch_funding_rate(symbol))['fundingTimestamp']

    def get_exchange_options(self) -> Dict:
        return {"options": {"defaultType": "future"}}

    async def get_only_perpetual(self, tickers: Dict[str, Dict]):
        return {symbol: data for symbol, data in tickers.items()
                         if data.get('symbol', '').endswith(':USDT')}

    def extract_prices(self, ticker: Dict) -> tuple:
        info = ticker.get('info', {})

        funding_rate = float(info.get('fundingRate', 0))
        funding_time = 0  # ((int(time.time() * 1000) // 3600000) + 1) * 3600000

        volume = int(float(info.get('usdtVolume', 0)))

        return funding_rate, funding_time, volume