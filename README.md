# NEPSE Trading Bot

An automated trading bot for Nepal Stock Exchange (NEPSE) TMS using Python and Selenium.

## Features

- 🤖 Automated login to NEPSE TMS
- 📊 Real-time stock price monitoring
- 💹 Trading strategy framework
- 🛡️ Risk management capabilities
- 📈 Portfolio tracking
- 🔍 Order history monitoring
- 🎯 Demo mode for testing

## Project Structure

```
nepse-trading/
├── src/
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── main.py          # Main bot orchestrator
│   │   ├── config.py        # Configuration management
│   │   ├── logger.py        # Logging setup
│   │   ├── browser.py       # Selenium browser management
│   │   ├── login.py         # Login automation
│   │   ├── trader.py        # Trading operations
│   │   └── strategy.py      # Trading strategies
│   └── __init__.py
├── tests/                    # Unit tests
├── config/                   # Configuration files
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## Prerequisites

- Python 3.8+
- Chrome/Chromium browser
- Chrome WebDriver (matching your Chrome version)

## Installation

1. **Clone the repository**
   ```bash
   cd nepse-trading
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your NEPSE credentials and email settings
   ```

5. **Download ChromeDriver**
   - Download from: https://chromedriver.chromium.org/
   - Place in project root or add to PATH

## Configuration

Edit `.env` file with your settings:

```env
NEPSE_USERNAME=your_username
NEPSE_PASSWORD=your_password
NEPSE_LOGIN_URL=https://tms17.nepsetms.com.np/login

HEADLESS_MODE=False          # False to see browser, True to hide
IMPLICIT_WAIT=10             # Wait time in seconds
TRADING_ENABLED=False        # Enable actual trading
DEMO_MODE=True               # Run in demo mode
LOG_LEVEL=INFO               # Logging level

EMAIL_SMTP=smtp.gmail.com     # SMTP server for sell alerts
EMAIL_PORT=465                # SSL port (465 for Gmail)
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password  # Use an app password, not your login password
EMAIL_TO=recipient_email@gmail.com
```

### Email alerts

The bot can send a sell notification email when price is at or below the current stop loss.

To enable it:
- fill in the email variables in `.env`
- use an SMTP provider that supports app passwords or SMTP auth
- keep `EMAIL_TO` as the address that should receive the alert

If these variables are empty, email alerts are skipped safely.

## Usage

### Run the bot

```bash
python -m src.bot.main
```

### Run in demo mode (recommended for testing)

```env
DEMO_MODE=True
TRADING_ENABLED=False
```

This will:
- Simulate login
- Skip actual trading
- Log all actions for verification

## Architecture

### Core Components

**BrowserManager**
- Handles Selenium WebDriver lifecycle
- Provides methods for navigation, waiting, and element interaction

**LoginManager**
- Automates login to NEPSE TMS
- Verifies successful authentication

**Trader**
- Executes trading operations
- Fetches market data and portfolio information

**TradingStrategy**
- Base class for trading strategies
- Includes sample Simple Moving Average strategy

**TradingBot**
- Main orchestrator
- Manages bot lifecycle and scheduling

## Adding Your Own Strategy

1. Create a new strategy class in `src/bot/strategy.py`:

```python
class MyStrategy(TradingStrategy):
    def analyze(self, market_data):
        # Your analysis logic
        return signals
    
    def execute_signals(self, signals):
        # Your execution logic
        pass
```

2. Update `src/bot/main.py` to use your strategy:

```python
self.strategy = MyStrategy(self.trader)
```

## Logging

Logs are saved in `logs/` directory with daily rotation. Check logs for troubleshooting.

## Security Notes

- ⚠️ Never commit `.env` files with real credentials
- Use environment variables for sensitive data
- Regularly rotate your NEPSE password
- Monitor bot logs for unauthorized access attempts
- Test strategies in DEMO mode before enabling trading

## Troubleshooting

### Chrome Driver Issues
```bash
# Download correct version matching your Chrome
# Check Chrome version: chrome://settings/help
```

### Timeout Errors
- Increase `IMPLICIT_WAIT` in `.env`
- Check your internet connection
- Verify NEPSE TMS is accessible

### Login Failures
- Verify credentials in `.env`
- Check if NEPSE TMS interface has changed
- Review login.py selectors (may need updates)

## Disclaimer

This bot is for educational purposes. Always:
- Test in DEMO mode first
- Use small amounts for initial live trading
- Monitor the bot regularly
- Understand the markets and risks
- Comply with NEPSE regulations

## Next Steps

1. ✅ Review and understand the code structure
2. ✅ Set up environment and dependencies
3. ✅ Test login in DEMO mode
4. ✅ Inspect NEPSE TMS interface and update selectors
5. ✅ Develop your trading strategy
6. ✅ Backtest your strategy
7. ✅ Enable trading cautiously

## License

MIT License

## Support

For issues and improvements, refer to the inline documentation and comments in the code.
