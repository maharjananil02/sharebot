# Multi-Stock Paper Trading - Quick Start

## ✅ What's New

Your trading bot is now **fully generic** and works with **any NEPSE stock symbol**!

### Before (Symbol-Specific)
```python
trader = NABILPaperTrader()  # Only for NABIL
```

### After (Generic)
```python
trader = StockPaperTrader(symbol="NABIL")   # NABIL
trader = StockPaperTrader(symbol="GUFL")    # GUFL now!
trader = StockPaperTrader(symbol="NEPAL")   # Any stock!
```

## 🚀 Quick Run

### Trade NABIL (Same as before)
```bash
python3 demo_paper_trading.py
```

### Trade GUFL (NEW!)
```bash
python3 demo_gufl_trading.py
```

### Quick Test GUFL
```bash
python3 test_gufl_trading.py
```

## 📋 What Works

✅ **Real NEPSE prices** - Auto-fetches from https://www.nepalstock.com/today-price  
✅ **Any stock symbol** - NABIL, GUFL, NEPAL, JBLB, etc.  
✅ **Three-layer strategy** - Hard stop, trailing stop, ladder-in  
✅ **15-minute checks** - Automatic trading every 15 minutes  
✅ **Separate logs** - `logs/nabil.log`, `logs/gufl.log`, etc.  
✅ **Backward compatible** - NABIL code still works  
✅ **Fully automated** - No manual confirmations  

## 📂 Files Created/Updated

**New:**
- `src/bot/stock_trader.py` - Generic trader for any stock
- `demo_gufl_trading.py` - GUFL demo (15-min checks)
- `test_gufl_trading.py` - GUFL quick test (30 sec)
- `MULTI_STOCK_GUIDE.md` - Complete documentation

**Updated:**
- `demo_paper_trading.py` - Now uses generic module
- `test_paper_trading.py` - Now uses generic module

**Original (Still Available):**
- `src/bot/nabil_scheduler.py` - NABIL-specific version

## 🎯 Common Tasks

### Run GUFL Trading
```bash
python3 demo_gufl_trading.py
# Enter GUFL price (or press Enter to auto-fetch)
# Runs continuously checking every 15 minutes
```

### Run NABIL Trading (Backward Compatible)
```bash
python3 demo_paper_trading.py
# Works exactly as before
```

### Add NewStock (Programmatically)
```python
from src.bot.stock_trader import StockPaperTrader

trader = StockPaperTrader(symbol="NEWSTOCK")
trader.setup_strategy(entry_price=100.0)
trader.start()
```

### Create NewStock Demo Script
```python
#!/usr/bin/env python3
from src.bot.stock_trader import StockPaperTrader

trader = StockPaperTrader(symbol="NEWSTOCK", check_interval=900)
trader.setup_strategy(entry_price=100.0, initial_quantity=50)
trader.start()
```

## 🔧 Configuration

**Check Interval** (default 900 seconds = 15 minutes):
```python
trader = StockPaperTrader(symbol="GUFL", check_interval=900)   # 15 min
trader = StockPaperTrader(symbol="GUFL", check_interval=5)     # 5 sec (testing)
trader = StockPaperTrader(symbol="GUFL", check_interval=3600)  # 1 hour
```

**Initial Quantity** (default 10 shares):
```python
trader.setup_strategy(entry_price=50.0, initial_quantity=50)
```

**Custom Log File**:
```python
trader = StockPaperTrader(symbol="GUFL", log_file="my_logs/gufl.log")
```

## 📊 Strategy for Any Stock

All stocks get the same three-layer strategy:

1. **Hard Stop Loss**: -10% from entry
2. **Trailing Stop**: Activates at +10% gain, moves up 5% per climb
3. **Ladder-In**:
   - Buy 20 more shares if price drops 20%
   - Buy 10 more shares if price drops 30%

## 📈 Example Output (GUFL)

```
GUFL PAPER TRADING - FULL DEMO
This will run continuously, checking prices every 15 minutes
Press Ctrl+C to stop

1. Enter GUFL price from https://www.nepalstock.com/today-price
   GUFL Price (press Enter to auto-fetch): 50.25
   ✓ Using manual price: Rs. 50.25

2. Initializing GUFL Paper Trader...
   Check interval: 15 minutes
   Log file: logs/gufl.log

3. Setting up trading strategy...
   Entry quantity: 50 shares
   Protective layers:
     • Hard stop: -10% from entry
     • Trailing: Activate at +10%, move up 5% per climb
     • Ladder-in: +20 @ -20%, +10 @ -30%

4. Starting automated paper trading...
   Data logging to: logs/gufl.log
```

## 📝 Logging

Each stock gets its own log file in `logs/`:

- `logs/nabil.log` - NABIL trading activity
- `logs/gufl.log` - GUFL trading activity
- `logs/nepal.log` - NEPAL trading activity (if added)

**Log content:**
- Strategy initialization
- Price checks every 15 minutes
- Order executions
- Portfolio P&L
- Trade summaries

## 🛑 Stop Trading

Press **Ctrl+C** to stop gracefully:
- Completes current check
- Logs final portfolio report
- Exits cleanly

## ✨ Status Check

```python
status = trader.get_status()
print(f"Stock: {status['symbol']}")
print(f"Current Price: Rs. {status['current_price']:.2f}")
print(f"Position: {status['position']} shares")
print(f"Portfolio P&L: Rs. {status['unrealized_pnl']:+,.0f}")
```

## 📚 Full Documentation

For complete documentation, see [MULTI_STOCK_GUIDE.md](MULTI_STOCK_GUIDE.md)

## 🎓 Next Steps

1. **Test GUFL**: Run `python3 test_gufl_trading.py`
2. **Full GUFL Demo**: Run `python3 demo_gufl_trading.py`
3. **Add More Stocks**: Create new demo scripts for other stocks (NEPAL, JBLB, etc.)
4. **Monitor Logs**: Check `logs/*.log` for detailed trading activity

## 💡 Features

- ✅ Real NEPSE price fetching
- ✅ Automatic 15-minute scheduling
- ✅ Three-layer protective strategy
- ✅ Complete activity logging
- ✅ Portfolio P&L tracking
- ✅ Works for ANY stock symbol
- ✅ Backward compatible with NABIL code
- ✅ No manual confirmations needed

---

**Ready to trade multiple stocks? Start with:**
```bash
python3 demo_gufl_trading.py
```
