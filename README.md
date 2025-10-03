# 🚀 Octopus - Delta-Neutral Trading Bot for Aster DEX

Octopus is an algorithmic trading bot designed for Aster DEX perpetual futures, implementing a delta-neutral "Hold-and-Rotate" strategy to generate volume for Aster Genesis Stage 3.

## 🎯 Features

- **Delta-Neutral Trading**: Opens equal long + short positions simultaneously
- **Hold-and-Rotate Strategy**: Holds positions for 90+ minutes (10x holding multiplier)
- **Risk Management**: Built-in position sizing, stop-loss, and drift controls
- **Volume Generation**: Targets $15K+ daily volume with <1% risk
- **SQLite Database**: Complete trade and position history
- **Structured Logging**: Comprehensive logging with rotation
- **Aster DEX Integration**: Native support for Aster's futures API

## 📋 Requirements

- Python 3.12+
- Aster DEX API credentials
- USDT balance for trading capital

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone and navigate to project
cd octopus

# Install dependencies
uv sync

# Copy environment template
cp env.example .env
```

### 2. Configure API Credentials

Edit `.env` file with your Aster DEX credentials:

```bash
# Aster API Credentials
ASTER_API_KEY=your_api_key_here
ASTER_API_SECRET=your_api_secret_here

# Wallet
WALLET_ADDRESS=0x742d35Cc6634C0532925a3b8...

# Trading Config (optional overrides)
CAPITAL_USDT=1000.0
LEVERAGE=15
```

### 3. Test Connection

```bash
# Run validation tests
uv run python test_mvp.py
```

### 4. Launch Bot

```bash
# Start the trading bot
uv run python main.py
```

## 📊 Strategy Overview

### Hold-and-Rotate Strategy

1. **Open Delta-Neutral Positions**: Simultaneously opens equal long and short positions
2. **Hold for 90+ Minutes**: Maintains positions to qualify for 10x holding time multiplier
3. **Rotate Positions**: Closes and reopens with slight variations to generate volume
4. **Risk Controls**: Monitors position drift and implements stop-losses

### Key Parameters

- **Capital**: $1,000 USDT (configurable)
- **Leverage**: 15x (configurable)
- **Position Size**: 1.5% of capital per position
- **Hold Time**: 90+ minutes minimum
- **Target Volume**: $15,000+ daily

## 📁 Project Structure

```
octopus/
├── octopus/
│   ├── config/
│   │   └── settings.py          # Configuration management
│   ├── exchange/
│   │   ├── aster_client.py      # High-level Aster API wrapper
│   │   └── aster/               # Aster SDK integration
│   ├── strategy/
│   │   ├── delta_neutral.py    # Core trading strategy
│   │   └── risk_manager.py      # Risk management
│   ├── database/
│   │   ├── models.py            # SQLAlchemy models
│   │   └── db.py                # Database connection
│   └── utils/
├── main.py                       # Bot entry point
├── test_mvp.py                   # Validation tests
├── env.example                   # Environment template
└── logs/                         # Log files
```

## 🔧 Configuration

### Trading Parameters

| Parameter                | Default | Description                      |
| ------------------------ | ------- | -------------------------------- |
| `CAPITAL_USDT`           | 1000.0  | Trading capital in USDT          |
| `LEVERAGE`               | 15      | Position leverage                |
| `POSITION_HOLD_TIME_MIN` | 90      | Minimum hold time (minutes)      |
| `MAX_POSITION_SIZE_PCT`  | 1.5     | Max position size (% of capital) |
| `STOP_LOSS_PCT`          | 1.0     | Stop-loss threshold (%)          |
| `MAX_PNL_DRIFT_PCT`      | 0.8     | Max position drift (%)           |

### Risk Management

- **Position Sizing**: Automatically calculates based on capital and leverage
- **Stop-Loss**: Closes positions if PnL exceeds 1%
- **Drift Control**: Monitors delta-neutrality and closes if drift > 0.8%
- **Exposure Limits**: Prevents over-leveraging across all positions

## 📈 Monitoring

### Logs

Bot logs are stored in `logs/octopus_YYYY-MM-DD.log` with daily rotation.

### Database

SQLite database (`octopus.db`) contains:

- **Trades**: All executed orders with timestamps
- **Positions**: Position lifecycle tracking
- **Daily Stats**: Volume, PnL, and fee summaries

### Key Metrics

```bash
# Check today's volume
sqlite3 octopus.db "SELECT SUM(notional) FROM trades WHERE date(timestamp) = date('now')"

# Check position hold times
sqlite3 octopus.db "SELECT AVG(hold_time_minutes) FROM positions WHERE closed_at IS NOT NULL"

# Check PnL
sqlite3 octopus.db "SELECT SUM(realized_pnl) FROM trades"
```

## 🚨 Risk Warnings

- **Start Small**: Begin with $100-500 capital for testing
- **Monitor Closely**: Check logs every 2-3 hours initially
- **Stop if Issues**: Use Ctrl+C to stop the bot if anything seems wrong
- **No Wash Trading**: Bot uses market orders against external liquidity
- **Referral Code**: Ensure "KoPPFo" is applied in your Aster account

## 🛠️ Troubleshooting

| Issue                | Solution                                  |
| -------------------- | ----------------------------------------- |
| API key error        | Verify `.env` has correct `ASTER_API_KEY` |
| Order rejected       | Check leverage is set correctly           |
| Insufficient margin  | Reduce `CAPITAL_USDT` or `LEVERAGE`       |
| Position not opening | Verify hedge mode enabled on Aster UI     |
| Database locked      | Close any other DB connections            |

## 📞 Support

- **Aster API Docs**: [GitHub](https://github.com/asterdex/api-docs)
- **Issues**: Create GitHub issues for bugs
- **Discord**: Join Aster community for support

## 📄 License

MIT License - see LICENSE file for details.

---

**⚠️ Disclaimer**: This software is for educational purposes. Trading cryptocurrencies involves substantial risk. Use at your own risk.

