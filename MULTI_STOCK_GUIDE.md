# Generic Multi-Stock Paper Trading System

## Overview

The trading system is now **generic and works with any NEPSE stock symbol** (NABIL, GUFL, NEPAL, etc.). All stock-specific code has been unified into the `StockPaperTrader` class.

## Key Components

### Generic Class: `StockPaperTrader`
Located in: `src/bot/stock_trader.py`

```python
from src.bot.stock_trader import StockPaperTrader

# Works for ANY stock
trader = StockPaperTrader(symbol="GUFL")    # or "NABIL", "NEPAL", etc.
```

### Backward Compatibility: `NABILPaperTrader`
The original `NABILPaperTrader` class still works - it's now just a wrapper:

```python
from src.bot.stock_trader import NABILPaperTrader

trader = NABILPaperTrader()  # Still works exactly as before
```

## Features

### Automatic Price Fetching
Fetches **REAL live prices** from `https://www.nepalstock.com/today-price`:

```python
trader = StockPaperTrader(symbol="GUFL")
price = trader.fetch_real_price()  # Fetches GUFL price from NEPSE
```

### Automatic 15-Minute Checks
Scheduled to check price and execute trades every 15 minutes:

```python
trader.setup_strategy(entry_price=50.0)  # Rs. 50 for GUFL
trader.start()  # Runs continuously, checks every 15 minutes
```

### Three-Layer Strategy
Applied to ANY stock:
- **Hard Stop Loss**: -10% from entry price
- **Trailing Stop**: Activates at +10% gain, ratchets up 5% per climb
- **Ladder-In Purchases**:
  - Buy 20 more shares if price drops 20%
  - Buy 10 more shares if price drops 30%

### Complete Logging
All activity logged to stock-specific files:

```
logs/nabil.log    # NABIL trading log
logs/gufl.log     # GUFL trading log
logs/nepal.log    # NEPAL trading log (if added)
```

## Usage Examples

### Example 1: NABIL Trading (NABIL)

```bash
python3 demo_paper_trading.py
# Input: 525 (current NABIL price)
# Runs continuously, checks every 15 minutes
# Logs to: logs/nabil.log
```

### Example 2: GUFL Trading (NEW)

```bash
python3 demo_gufl_trading.py
# Input: 50 (current GUFL price)
# Runs continuously, checks every 15 minutes
# Logs to: logs/gufl.log
```

### Example 3: Quick Test - GUFL

```bash
python3 test_gufl_trading.py
# Quick 30-second test
# Rapid iterations (5-second checks)
# Verifies system working
```

### Example 4: Custom Stock (Programmatic)

```python
from src.bot.stock_trader import StockPaperTrader

# For NEPAL stock
trader = StockPaperTrader(symbol="NEPAL", check_interval=900)
trader.setup_strategy(entry_price=100.0)
trader.start()

# For any other NEPSE stock
trader = StockPaperTrader(symbol="JBLB", check_interval=900)
trader.setup_strategy(entry_price=25.0)
trader.start()
```

## Configuration

### Check Interval
Default: **900 seconds = 15 minutes**

```python
# For quick testing (5 seconds)
trader = StockPaperTrader(symbol="GUFL", check_interval=5)

# For standard operation (15 minutes)
trader = StockPaperTrader(symbol="GUFL", check_interval=900)

# For hourly checks
trader = StockPaperTrader(symbol="GUFL", check_interval=3600)
```

### Initial Quantity
Default: **10 shares**

```python
# Buy 50 GUFL shares at entry
trader.setup_strategy(entry_price=50.0, initial_quantity=50)

# Buy 100 NABIL shares at entry
trader.setup_strategy(entry_price=525.0, initial_quantity=100)
```

### Log File
Auto-generated or custom:

```python
# Auto-generated (default)
trader = StockPaperTrader(symbol="GUFL")
# Log file: logs/gufl.log

# Custom location
trader = StockPaperTrader(symbol="GUFL", log_file="my_logs/gufl_trades.log")
```

## Price Fetching

### Automatic (Default)
Fetches from `https://www.nepalstock.com/today-price`:

```python
trader.setup_strategy()  # No price provided
# System auto-fetches GUFL price from NEPSE
```

### Manual (Fallback)
Provide price explicitly:

```python
trader.setup_strategy(entry_price=50.0)
# Uses your provided price instead of fetching
```

## Status Monitoring

Check current trading status:

```python
status = trader.get_status()
print(f"Price: Rs. {status['current_price']:.2f}")
print(f"Position: {status['position']} shares")
print(f"Portfolio Value: Rs. {status['portfolio_value']:,.0f}")
print(f"Unrealized P&L: Rs. {status['unrealized_pnl']:+,.0f}")
print(f"Total Checks: {status['checks']}")
print(f"Total Trades: {status['trades']}")
```

## Output Example

### Logs (logs/gufl.log)
```
2024-01-15 10:30:45 - __main__ - INFO - 
========================================================================================
GUFL PAPER TRADING STARTED
Log File: logs/gufl.log
Start Time: 2024-01-15 10:30:45
Check Interval: 900 seconds
========================================================================================

>>> FETCHING REAL GUFL PRICE FROM NEPSE LIVE...
    Entry Price (NEPSE Live): Rs. 50.25

>>> SETTING UP STRATEGY FOR GUFL
    Entry Price (Live): Rs. 50.25
    Initial Quantity: 50 shares

>>> EXECUTING INITIAL BUY ORDER
    ✓ BUY 50 GUFL @ Rs. 50.25 = Rs. 2,512.50

[CHECK #0001] 10:30:47 | Price: Rs. 50.32
[CHECK #0002] 10:45:47 | Price: Rs. 50.18
[CHECK #0003] 11:00:47 | Price: Rs. 51.00
>>> 1 ORDER(S) TRIGGERED - EXECUTING AUTOMATICALLY

    ═══════════════════════════════════════════════════════════════════════
    📊 GUFL TRADING ORDERS
    ═══════════════════════════════════════════════════════════════════════
    
    ✓ SELL 50 GUFL (Trailing Stop Hit at +1.5% above entry)
        Entry: Rs. 50.25 | Price: Rs. 51.00 | Quantity: 50 | Total: Rs. 2,550.00
        Status: EXECUTED | Profit: Rs. 37.50 | Return: +0.75%
    
    ═══════════════════════════════════════════════════════════════════════

[SUMMARY] Portfolio Value: Rs. 1,000,037.50 | Realized P&L: +Rs. 37.50
```

## File Structure

**New Files:**
- `src/bot/stock_trader.py` - Core generic trader + NABILPaperTrader wrapper
- `demo_gufl_trading.py` - Full GUFL trading demo (15-min intervals)
- `test_gufl_trading.py` - Quick GUFL test (30 seconds)

**Updated Files:**
- `demo_paper_trading.py` - Now uses `stock_trader.py` (backward compatible)
- `test_paper_trading.py` - Now uses `stock_trader.py` (backward compatible)

**Existing (Unchanged):**
- `src/bot/nabil_scheduler.py` - Still available if needed
- `src/bot/trailing_stop_strategy.py` - Core strategy logic
- `src/bot/paper_trader.py` - Trading simulator

## For Different Stocks

### Adding NEPAL Stock Trading

```python
from src.bot.stock_trader import StockPaperTrader

trader = StockPaperTrader(symbol="NEPAL", check_interval=900)
trader.setup_strategy(entry_price=50.0)
trader.start()
```

### Adding JBLB Stock Trading

```python
from src.bot.stock_trader import StockPaperTrader

trader = StockPaperTrader(symbol="JBLB", check_interval=900)
trader.setup_strategy(entry_price=25.0)
trader.start()
```

### Adding AIL Stock Trading

```python
from src.bot.stock_trader import StockPaperTrader

trader = StockPaperTrader(symbol="AIL", check_interval=900)
trader.setup_strategy(entry_price=200.0)
trader.start()
```

## Troubleshooting

### Problem: "Cannot connect to nepalstock.com"
**Solution:** Check internet connection and ensure nepalstock.com is accessible

### Problem: "Stock symbol not found"
**Solution:** Verify symbol is correct and listed on https://www.nepalstock.com/today-price

### Problem: "No log file generated"
**Solution:** Ensure `logs/` directory exists: `mkdir -p logs`

### Problem: "Module not found" error
**Solution:** Run from project root: `cd nepse-trading && python3 demo_gufl_trading.py`

## Stop Trading

Press **Ctrl+C** to stop trading gracefully:
- Completes current check
- Logs final portfolio report
- Exits cleanly

```
>>> STOPPED BY USER
════════════════════════════════════════════════════════════════════════════════
GUFL PAPER TRADING STOPPED
════════════════════════════════════════════════════════════════════════════════
```

## API Reference

### StockPaperTrader Class

| Method | Returns | Description |
|--------|---------|-------------|
| `__init__(symbol, check_interval, log_file)` | None | Initialize trader |
| `setup_strategy(entry_price, quantity)` | None | Setup and execute initial buy |
| `fetch_real_price()` | float | Fetch live price from NEPSE |
| `simulate_price_movement()` | float | Get next price (real or simulated) |
| `check_price_and_execute()` | None | Check price and execute strategy |
| `start(duration_minutes)` | None | Start trading (None = continuous) |
| `stop()` | None | Stop trading and report |
| `get_status()` | dict | Get current status |

## Complete Runnable Examples

### Example: Trade NABIL
```bash
python3 demo_paper_trading.py
# Enter: 525 (or press Enter to auto-fetch)
# Runs continuously
```

### Example: Trade GUFL
```bash
python3 demo_gufl_trading.py
# Enter: 50 (or press Enter to auto-fetch)
# Runs continuously
```

### Example: Test GUFL
```bash
python3 test_gufl_trading.py
# Enter: 50 (or press Enter to auto-fetch)
# Runs for 30 seconds
```

## Summary

✓ **Generic System**: Works with ANY NEPSE stock symbol  
✓ **Real NEPSE Prices**: Auto-fetches from nepalstock.com  
✓ **Backward Compatible**: NABIL code still works  
✓ **Easy to Extend**: Add any new stock with 2 lines of code  
✓ **Fully Automated**: No manual confirmations needed  
✓ **Complete Logging**: Stock-specific log files  
✓ **Three-Layer Strategy**: Applied to any stock  

