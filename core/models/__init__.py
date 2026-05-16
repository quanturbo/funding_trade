from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class FundingTicker:
    exchange: str
    symbol: str
    funding_rate: float
    funding_time: int
    volume: Optional[float] = None
