# Paper Trading System - Complete Guide

## Overview

You now have a **complete paper trading system** that simulates trading without real money. The system:

✅ **Simulates** buy/sell orders like real trading  
✅ **Runs Automatically** - checks price every 5 seconds  
✅ **Executes Automatically** - no user confirmation needed  
✅ **Logs Everything** - detailed logs to `logs/nabil.log`  
✅ **Tracks Portfolio** - cash, positions, P&L  
✅ **Simulates Prices** - random walk to test strategy  

---

## How It Works

```
START BOT
    ↓
INITIALIZE PAPER ACCOUNT (1 million Rs cash)
    ↓
SETUP STRATEGY (Buy 10 shares @ Rs. 1,000)
    ↓
EVERY 5 SECONDS:
    ├─ Simulate new price
    ├─ Run strategy analysis
    ├─ Check for triggers
    ├─ AUTOMATICALLY execute ALL orders
    ├─ Update positions & P&L
    └─ Log everything
    ↓
CONTINUE for duration (e.g., 10 minutes)
    ↓
STOP & GENERATE FINAL REPORT
    ↓
ALL LOGGED TO: logs/nabil.log
```

---

## Key Components

### 1. PaperTrader (src/bot/paper_trader.py)
- Simulates buy/sell orders
- Tracks portfolio & positions
- Calculates P&L
- Maintains trade history
- Logs all trades

### 2. NABILPaperTrader Scheduler (src/bot/nabil_scheduler.py)
- Runs strategy every 5 seconds
- Automatically executes orders
- Simulates price movements
- Logs to nabil.log
- Generates reports

### 3. Demo Script (demo_paper_trading.py)
- Quick start - run immediately
- Shows full workflow
- Prints status updates

---

## Getting Started

### Step 1: Run the Demo

```bash
cd /Users/anil/Coding/lets\ code/nepse-trading
python demo_paper_trading.py
```

**What you'll see:**
- Initial buy order execution (10 @ Rs. 1,000)
- Price updates every 5 seconds
- Order summaries when trades trigger
- Portfolio updates every 10 checks
- Final report after completion

**Expected output:**
```
✓ PAPER BUY EXECUTED
  Symbol: NABIL
  Quantity: 10 shares
  Price: Rs. 1,000.00 per share
  Total Cost: Rs. 10,000.00
  Cash Remaining: Rs. 990,000.00

[CHECK #0001] 14:23:15 | Price: Rs. 1,002.50
[CHECK #0002] 14:23:20 | Price: Rs. 998.75
...
```

### Step 2: Monitor the Logs

```bash
# In another terminal, watch the log file
tail -f logs/nabil.log
```

**See everything that happens:**
- Every price check
- Every order execution
- P&L calculations
- Portfolio summaries
- System events

### Step 3: Stop and Review

Press `Ctrl+C` to stop the demo, then review the full log:

```bash
cat logs/nabil.log
```

---

## Configuration

### Adjust Check Interval

```python
from src.bot.nabil_scheduler import NABILPaperTrader

# Check every 5 seconds (default)
trader = NABILPaperTrader(check_interval=5)

# Check every 10 seconds (slower)
trader = NABILPaperTrader(check_interval=10)

# Check every 2 seconds (faster)
trader = NABILPaperTrader(check_interval=2)
```

### Adjust Starting Capital

Currently 1 million Rs. To change (edit paper_trader.py):

```python
# In PaperTrader.__init__()
self.cash = 500000  # or any amount
```

### Adjust Strategy Parameters

In `demo_paper_trading.py`, modify:

```python
trader.setup_strategy(
    entry_price=1200.0,        # Different entry price
    initial_quantity=20        # Buy 20 shares instead of 10
)
```

Or modify the strategy itself in `nabil_scheduler.py`:

```python
self.strategy = TrailingStopStrategy(
    ...
    stop_loss_pct=5,           # Tighter stop (-5% instead of -10%)
    trailing_step_pct=3,       # Smaller ratchet
    ladder_triggers={15: 25, 30: 10}  # Different ladders
)
```

---

## Real Usage (Connect to TMS)

To use real prices instead of simulated:

```python
from src.bot.nabil_scheduler import NABILPaperTrader

class RealNABILTrader(NABILPaperTrader):
    def simulate_price_movement(self):
        """Override to fetch real price"""
        # Get price from TMS
        current_price = self.trader.get_current_price("NABIL")
        self.current_price = current_price
        return current_price

# Use it
trader = RealNABILTrader()
trader.setup_strategy(entry_price=1000.0)
trader.start(duration_minutes=60)  # Run for 1 hour
```

---

## Log File Structure

All output goes to `logs/nabil.log`:

```
2026-04-28 14:23:10 - nabil_scheduler - INFO - NABIL PAPER TRADING STARTED
2026-04-28 14:23:10 - nabil_scheduler - INFO - >>> SETTING UP STRATEGY

2026-04-28 14:23:11 - nabil_scheduler - INFO - ✓ PAPER BUY EXECUTED
   Symbol: NABIL
   Quantity: 10 shares
   Price: Rs. 1,000.00 per share
   Total Cost: Rs. 10,000.00
   ...

2026-04-28 14:23:16 - nabil_scheduler - INFO - [CHECK #0001] 14:23:16 | Price: Rs. 1,002.50

2026-04-28 14:23:21 - nabil_scheduler - INFO - [CHECK #0002] 14:23:21 | Price: Rs. 998.75

2026-04-28 14:23:31 - nabil_scheduler - INFO - >>> 1 ORDER(S) TRIGGERED - EXECUTING AUTOMATICALLY

2026-04-28 14:23:31 - nabil_scheduler - INFO - ✓ PROFIT PAPER SELL EXECUTED
   Symbol: NABIL
   P&L: Rs. +500 (+5.0%)
   ...

2026-04-28 14:23:31 - nabil_scheduler - INFO - ==============================
PORTFOLIO SUMMARY
==============================
```

---

## Understanding the Output

### Paper Buy Order
```
✓ PAPER BUY EXECUTED
   Order ID: PAPER-BUY-1
   Symbol: NABIL
   Quantity: 20 shares
   Price: Rs. 800.00 per share
   Total Cost: Rs. 16,000.00
   Position: 30 shares (Avg: Rs. 933.33)  ← New average cost
   Cash Remaining: Rs. 974,000.00
   Timestamp: 2026-04-28 14:23:31
```

**What this means:**
- Successfully bought 20 shares
- Total spent: Rs. 16,000
- Now holding 30 shares total
- Average cost reduced to Rs. 933.33

### Paper Sell Order
```
✓ PROFIT PAPER SELL EXECUTED
   Order ID: PAPER-SELL-2
   Symbol: NABIL
   Quantity: 10 shares
   Sell Price: Rs. 1,090.00 per share
   Avg Cost: Rs. 1,000.00
   Total Proceeds: Rs. 10,900.00
   P&L: Rs. +900.00 (+9.00%)  ← Profit!
   Remaining Shares: 20
   Cash After: Rs. 984,900.00
   Timestamp: 2026-04-28 14:23:35
```

**What this means:**
- Sold 10 shares at profit
- Made Rs. 900 profit on this trade
- Still holding 20 shares
- Cash increased by proceeds

### Portfolio Summary (Every 10 Checks)
```
PORTFOLIO SUMMARY
==========================
Cash: Rs. 950,000.00
Holdings Value: Rs. 28,000.00
Total Value: Rs. 978,000.00
Unrealized P&L: Rs. -22,000.00 (-2.20%)

Holdings:
  NABIL: 30 @ Rs. 933.33 → Rs. 920.00 = -1.43%
```

**All metrics:**
- Your remaining cash
- Value of stocks you're holding
- Total portfolio value
- Unrealized gains/losses

---

## Viewing Results

### Live Monitoring (Best for watching it run)
```bash
tail -f logs/nabil.log
```

### See Everything After Completion
```bash
cat logs/nabil.log
```

### Search for Specific Orders
```bash
# Find all sell orders
grep "SELL EXECUTED" logs/nabil.log

# Find all buys with profit
grep "✓ PROFIT" logs/nabil.log

# Count total trades
grep -c "EXECUTED" logs/nabil.log
```

### Extract P&L
```bash
# Show all P&L values
grep "P&L:" logs/nabil.log
```

---

## What Information Is Logged

For **Every Buy Order:**
- Order ID
- Symbol & quantity
- Price & total cost
- New position size
- Average cost
- Cash remaining
- Timestamp

For **Every Sell Order:**
- Order ID
- Symbol & quantity
- Sell price & avg cost
- Total proceeds
- **P&L in Rs. and percentage**
- Remaining shares
- Cash after
- Timestamp

For **Every Price Check:**
- Check number
- Time
- Current price
- Any orders triggered

For **Portfolio Updates (every 10 checks):**
- Cash balance
- Holdings value
- Total value
- Unrealized P&L
- Position details

---

## Example Log File

Here's what a 2-minute paper trading session looks like:

```
2026-04-28 14:23:10 - NABIL PAPER TRADING STARTED
2026-04-28 14:23:10 - Log File: logs/nabil.log
2026-04-28 14:23:10 - Check Interval: 5 seconds

2026-04-28 14:23:11 - >>> SETTING UP STRATEGY
2026-04-28 14:23:11 - Entry Price: Rs. 1,000.00
2026-04-28 14:23:11 - Initial Quantity: 10 shares

2026-04-28 14:23:11 - >>> EXECUTING INITIAL BUY ORDER
2026-04-28 14:23:11 - ✓ PAPER BUY EXECUTED
   Order ID: PAPER-BUY-1
   Symbol: NABIL
   Quantity: 10 shares
   Price: Rs. 1,000.00 per share
   Total Cost: Rs. 10,000.00
   Position: 10 shares (Avg: Rs. 1,000.00)
   Cash Remaining: Rs. 990,000.00

2026-04-28 14:23:16 - [CHECK #0001] 14:23:16 | Price: Rs. 1,002.50

2026-04-28 14:23:21 - [CHECK #0002] 14:23:21 | Price: Rs. 998.75

2026-04-28 14:23:26 - [CHECK #0003] 14:23:26 | Price: Rs. 1,005.00

2026-04-28 14:23:31 - [CHECK #0004] 14:23:31 | Price: Rs. 1,100.00
2026-04-28 14:23:31 - >>> TRAILING STOP ACTIVATED at 1100.00
2026-04-28 14:23:31 - New trailing stop level: Rs. 1,045.00

2026-04-28 14:23:36 - [CHECK #0005] 14:23:36 | Price: Rs. 1,120.00
2026-04-28 14:23:36 - TRAILING STOP MOVED UP: Rs. 1,045.00 → Rs. 1,064.00

[... more checks ...]

2026-04-28 14:24:51 - [CHECK #0018] 14:24:51 | Price: Rs. 1,050.00
2026-04-28 14:24:51 - >>> 1 ORDER(S) TRIGGERED - EXECUTING AUTOMATICALLY

2026-04-28 14:24:51 - ✓ PROFIT PAPER SELL EXECUTED
   Order ID: PAPER-SELL-1
   Symbol: NABIL
   Quantity: 10 shares
   Sell Price: Rs. 1,050.00 per share
   Avg Cost: Rs. 1,000.00
   Total Proceeds: Rs. 10,500.00
   P&L: Rs. +500.00 (+5.00%)
   Remaining Shares: 0
   Cash After: Rs. 1,000,500.00
   [Position CLOSED for NABIL]

2026-04-28 14:25:10 - PAPER TRADING STOPPED

2026-04-28 14:25:10 - ==============================
PORTFOLIO SUMMARY
==============================
Cash: Rs. 1,000,500.00
Holdings Value: Rs. 0.00
Total Value: Rs. 1,000,500.00
Unrealized P&L: Rs. +500.00 (+0.05%)

Total Trades Executed: 2
Report Generated: 2026-04-28 14:25:10
```

---

## System Benefits

✅ **Risk-Free Testing**
- Test strategy without real money
- See if logic works before going live

✅ **Complete Logging**
- Every action recorded
- Review exactly what happened
- Track P&L over time

✅ **Automated Execution**
- No manual confirmations needed
- Runs continuously
- Scalable to multiple stocks

✅ **Realistic Simulation**
- Price movements simulated
- Orders execute at current price
- Position tracking works like real trading

✅ **Easy Integration**
- Replace simulated prices with real TMS data
- Same code works for paper and real trading
- Just change price data source

---

## Next Steps

1. **Run the demo:**
   ```bash
   python demo_paper_trading.py
   ```

2. **Watch the logs:**
   ```bash
   tail -f logs/nabil.log
   ```

3. **Stop and review:**
   - Press Ctrl+C
   - Review full log file

4. **Customize:**
   - Adjust check interval
   - Change strategy parameters
   - Add real price fetching

5. **Go Live:**
   - Connect to your TMS price feed
   - Run in production mode
   - Monitor real portfolio

---

## Troubleshooting

**Log file not created?**
- Ensure `logs/` directory exists
- Check file permissions

**Prices not moving?**
- That's OK - using simulated random walk
- For real prices, implement price fetcher

**Orders not executing?**
- Check logs for error messages
- Verify strategy triggers are correct

**Can't stop the bot?**
- Press Ctrl+C
- Wait for graceful shutdown
- Or force kill with Ctrl+Z (then kill in another terminal)

---

## Summary

You now have:

✅ **Paper Trading System** - Simulates trades without real money  
✅ **Automatic Scheduling** - Runs every 5 seconds  
✅ **Complete Logging** - All activity to nabil.log  
✅ **Strategy Integration** - Trailing stop strategy automated  
✅ **Portfolio Tracking** - Cash, positions, P&L  
✅ **Demo Ready** - Run immediately with no setup  

**Start now:** `python demo_paper_trading.py`

