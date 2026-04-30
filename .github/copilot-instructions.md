# NEPSE Trading Bot - Development Guidelines

## Project Overview
Python-based trading bot for NEPSE TMS using Selenium for browser automation.

## Key Technologies
- **Python 3.8+**: Main language
- **Selenium 4.15+**: Browser automation
- **python-dotenv**: Environment configuration
- **Pandas**: Data analysis (for future enhancements)
- **Schedule**: Job scheduling

## Project Structure
- `src/bot/`: Core bot modules
- `tests/`: Unit tests
- `logs/`: Application logs
- `screenshots/`: Browser screenshots
- `.env`: Environment configuration (not committed)

## Development Workflow

### Environment Setup
1. Ensure Python 3.8+ is installed
2. Create virtual environment: `python3 -m venv venv`
3. Activate environment: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and update settings

### Code Organization
- All bot logic in `src/bot/` directory
- Each module handles specific responsibility
- Use consistent logging across modules
- Add error handling to all user inputs

### Important Notes
- Never commit `.env` with real credentials
- Test in DEMO_MODE before enabling trading
- Always update selectors if NEPSE TMS interface changes
- Review logs regularly for errors
- Use screenshots for UI debugging

## Next Actions
1. Update selectors in `login.py` based on actual NEPSE TMS HTML
2. Implement trader methods for order placement
3. Develop and test trading strategies
4. Add error recovery mechanisms
5. Implement portfolio tracking
