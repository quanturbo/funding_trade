import aiosqlite
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class PriceHistoryDB:
    def __init__(self, db_path: str = "data/price_history.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db: Optional[aiosqlite.Connection] = None

    async def connect(self):
        """Initialize database connection and create tables"""
        self.db = await aiosqlite.connect(self.db_path)
        self.db.row_factory = aiosqlite.Row
        await self._create_tables()

    async def _create_tables(self):
        """Create tables with proper indexes for efficient querying"""
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS price_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                exchange TEXT NOT NULL,
                symbol TEXT NOT NULL,
                last_price REAL NOT NULL,
                mark_price REAL NOT NULL,
                index_price REAL NOT NULL,
                deviation_percent REAL NOT NULL
            )
        """)

        # Indexes for efficient time-series queries
        await self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_symbol_time 
            ON price_snapshots(symbol, timestamp DESC)
        """)

        await self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_exchange_symbol 
            ON price_snapshots(exchange, symbol, timestamp DESC)
        """)

        await self.db.commit()

    async def insert_batch(self, deviations: List) -> int:
        """Batch insert price snapshots for performance"""
        if not deviations:
            return 0

        timestamp = int(datetime.now().timestamp())

        data = [
            (
                timestamp,
                dev.exchange,
                dev.symbol,
                float(dev.last_price),
                float(dev.mark_price),
                float(dev.index_price),
                float(dev.deviation_percent)
            )
            for dev in deviations
        ]

        await self.db.executemany("""
            INSERT INTO price_snapshots 
            (timestamp, exchange, symbol, last_price, mark_price, index_price, deviation_percent)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, data)

        await self.db.commit()
        return len(data)

    async def get_history(
            self,
            symbol: str,
            exchange: Optional[str] = None,
            hours: int = 24,
            limit: int = 1000
    ) -> List[Dict]:
        """Get price history for charting"""
        since_timestamp = int(datetime.now().timestamp()) - (hours * 3600)

        if exchange:
            query = """
                SELECT timestamp, exchange, symbol, last_price, mark_price, 
                       index_price, deviation_percent
                FROM price_snapshots
                WHERE symbol = ? AND exchange = ? AND timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT ?
            """
            params = (symbol, exchange, since_timestamp, limit)
        else:
            query = """
                SELECT timestamp, exchange, symbol, last_price, mark_price, 
                       index_price, deviation_percent
                FROM price_snapshots
                WHERE symbol = ? AND timestamp >= ?
                ORDER BY timestamp DESC
                LIMIT ?
            """
            params = (symbol, since_timestamp, limit)

        async with self.db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_symbols(self) -> List[str]:
        """Get all unique symbols in database"""
        async with self.db.execute(
                "SELECT DISTINCT symbol FROM price_snapshots ORDER BY symbol"
        ) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

    async def cleanup_old_data(self, days: int = 30):
        """Remove data older than specified days"""
        cutoff = int(datetime.now().timestamp()) - (days * 86400)
        await self.db.execute(
            "DELETE FROM price_snapshots WHERE timestamp < ?", (cutoff,)
        )
        await self.db.commit()
        await self.db.execute("VACUUM")

    async def close(self):
        """Close database connection"""
        if self.db:
            await self.db.close()