# funding_trade

Funding rate monitoring service across major CEX perpetual futures markets. Scans for elevated funding rates in real time and sends Telegram alerts for actionable opportunities.

## Business Value

This tool cuts down the manual work of checking many exchange interfaces before each funding window. By consolidating opportunities from multiple venues into one ranked alert stream, it helps teams react faster and miss fewer high-rate events. It can also serve as a low-risk signal layer before allocating engineering effort to full execution automation.

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

No open-source license is declared yet.
