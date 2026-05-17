# funding_trade

Funding rate monitor and arbitrage bot across major CEX perpetual futures markets. Scans for high funding rates in real time and sends Telegram alerts for actionable opportunities.

## Supported Exchanges

Binance, Bybit, OKX, Gate.io, MEXC, KuCoin, BingX, Bitget, HTX, Hyperliquid, LBank, BitMart, WhiteBit, CoinEx

## Requirements

- Python 3.11+
- `pip install -r requirements.txt`

## Setup

```bash
cp .env.example .env
# Edit .env — add your Telegram bot token and chat ID
python main.py
```

## Configuration

Edit `config.py` to tune strategy parameters:

| Setting | Default | Description |
|---|---|---|
| `min_funding_rate` | 0.5 | Minimum funding rate % to show |
| `left_show_time` | 7 | Hours left until funding to trigger alert |
| `min_volume` | 500,000 | Minimum 24h volume filter |

## Structure

```
main.py      # Entry point — funding rate monitor loop
config.py    # Strategy settings and Telegram config
core/
  models/    # Per-exchange API adapters
  notify/    # Telegram notifier
  utils/     # Helpers
```

## License

Private — all rights reserved.
