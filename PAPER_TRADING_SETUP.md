# Paper Trading System - Complete Setup & Usage Guide

## What You Now Have

A **complete automated paper trading system** that:

✅ **Simulates trading** without real money  
✅ **Runs automatically** - checks price every 5 seconds  
✅ **Executes orders** - no manual confirmation needed  
✅ **Logs everything** - detailed logs to `logs/nabil.log`  
✅ **Tracks portfolio** - positions, cash, P&L  
✅ **Integrates with strategy** - runs trailing stop strategy automatically  

---

## Files Created

### Code Files
```
src/bot/
  ├─ paper_trader.py ..................... Simulates trading (buy/sell orders)
  └─ nabil_scheduler.py .................. Runs strategy on 5-second intervals

Demo & Test Files
  ├─ demo_paper_trading.py ............... Full demo (10 minutes)
  └─ test_paper_trading.py ............... Quick test (30 seconds)

Documentation
  └─ PAPER_TRADING_GUIDE.md .............. Complete usage guide
```

---

## How It All Works Together

```
                    PAPER TRADING ARCHITECTURE
                    ═════════════════════════════

         USER STARTS BOT
              │
              ↓
    ┌─────────────────────────────┐
    │ NABILPaperTrader Scheduler  │
    │  (Runs every 5 seconds)     │
    └──────────┬──────────────────┘
               │
         ┌─────┴─────┐
         ↓           ↓
    
    Fetch Price    Run Strategy
    (simulated)    Analysis
         │              │
         └──────┬───────┘
                ↓
        Check For Triggers
        (stop loss, trailing, ladder)
                │
         ┌──────┴──────┐
         │ Any orders? │
         └──────┬──────┘
                │
         ┌──────Y──────┐
         │             │
         ↓             ↓
    EXECUTE        Log to
    with Paper     nabil.log
    Trader         │
         │         │
         └────┬────┘
              ↓
         Update Portfolio
         (positions, P&L)
              │
              ↓
       Wait 5 seconds
              │
         Loop continues...
```

---

## Quick Start

### 1. Run Demo (Full 10 minutes)
```bash
cd /Users/anil/Coding/lets\ code/nepse-trading
python demo_paper_trading.py
```

**What happens:**
- Initializes paper account (Rs. 1,000,000)
- Buys 10 NABIL @ Rs. 1,000
- Runs automatically for 10 minutes
- Checks price every 5 seconds
- Executes orders automatically
- Shows status updates every 30 seconds
- Logs everything to `logs/nabil.log`

### 2. Quick Test (30 seconds)
```bash
python test_paper_trading.py
```

**For testing without waiting:**
- Same as demo but only 30 seconds
- Quick verification it works

### 3. Watch Logs in Real-Time
```bash
# In another terminal window
tail -f logs/nabil.log
```

**See as it happens:**
- Every price check
- Every order execution
- Portfolio updates
- All P&L calculations

---

## What Gets Logged

### On Startup
```
NABIL PAPER TRADING STARTED
Log File: logs/nabil.log
Start Time: 2026-04-28 16:34:45
Check Interval: 5 seconds

PAPER TRADING INITIALIZED
Starting Cash: Rs. 1,000,000.00
```

### Initial Setup
```
>>> SETTING UP STRATEGY
    Entry Price: Rs. 1000.00
    Initial Quantity: 10 shares

>>> EXECUTING INITIAL BUY ORDER
✓ PAPER BUY EXECUTED
   Order ID: PAPER-BUY-1
   Symbol: NABIL
   Quantity: 10 shares
   Price: Rs. 1000.00 per share
   Total Cost: Rs. 10,000.00
   Position: 10 shares (Avg: Rs. 1000.00)
   Cash Remaining: Rs. 990,000.00
   Timestamp: 2026-04-28 16:34:45
```

### Every 5 Seconds (Price Check)
```
[CHECK #0001] 16:34:50 | Price: Rs. 1002.21
[CHECK #0002] 16:34:55 | Price: Rs. 1003.06
[CHECK #0003] 16:35:00 | Price: Rs. 999.41
[CHECK #0004] 16:35:05 | Price: Rs. 996.44
[CHECK #0005] 16:35:10 | Price: Rs. 994.36
```

### When Orders Trigger
```
>>> 1 ORDER(S) TRIGGERED - EXECUTING AUTOMATICALLY

✓ PROFIT PAPER SELL EXECUTED
   Order ID: PAPER-SELL-1
   Symbol: NABIL
   Quantity: 10 shares
   Sell Price: Rs. 1,090.00 per share
   Avg Cost: Rs. 1,000.00
   Total Proceeds: Rs. 10,900.00
   P&L: Rs. +900.00 (+9.00%)
   Remaining Shares: 0
   Cash After: Rs. 1,000,900.00
   [Position CLOSED for NABIL]
```

### Portfolio Updates (Every 10 Checks)
```
PORTFOLIO SUMMARY
==========================
Cash: Rs. 990,000.00
Holdings Value: Rs. 9,943.61
Total Value: Rs. 999,943.61
Unrealized P&L: Rs. -56.39 (-0.01%)

Holdings:
  NABIL: 10 @ Rs. 1000.00 → Rs. 994.36 = -0.56%
```

### On Completion
```
PAPER TRADING STOPPED

FINAL STATISTICS:
  Total Checks: 120
  Total Trades: 3
  Final Price: Rs. 1,050.32
  Price Change: +5.03%

Total Portfolio Value: Rs. 1,005,300.00
===========================
```

---

## Understanding the System

### PaperTrader (`src/bot/paper_trader.py`)

**What it does:**
- Simulates buy orders (deducts cash, adds to position)
- Simulates sell orders (adds cash, removes from position)
- Tracks average cost
- Calculates P&L
- Maintains trade history
- Logs all activity

**Key metrics tracked:**
```python
portfolio = {
    'shares': 10,           # Quantity owned
    'avg_cost': 1000.00,    # Average entry price
    'total_invested': 10000.00  # Total capital invested
}

cash = 990000.00            # Remaining cash
```

### NABILPaperTrader Scheduler (`src/bot/nabil_scheduler.py`)

**What it does:**
- Sets up strategy
- Runs every 5 seconds (configurable)
- Fetches/simulates price
- Calls strategy.analyze()
- Automatically executes orders
- Updates portfolio
- Logs everything

**Configuration:**
```python
# Check every 5 seconds (default)
trader = NABILPaperTrader(check_interval=5)

# Or every 10 seconds
trader = NABILPaperTrader(check_interval=10)

# Or every 2 seconds (very frequent)
trader = NABILPaperTrader(check_interval=2)
```

### Demo Scripts

**demo_paper_trading.py:**
- Full 10-minute demo
- Shows status updates every 30 seconds
- Prints final report

**test_paper_trading.py:**
- Quick 30-second test
- Good for verification
- Same functionality, less time

---

## Example Run Output

Here's what you'd see when running the demo:

```
══════════════════════════════════════════════════════════════════════════════════════
                   NABIL PAPER TRADING - AUTOMATED DEMO
══════════════════════════════════════════════════════════════════════════════════════

This demo will:
  ✓ Simulate NABIL trading with 10 shares purchase at Rs. 1,000
  ✓ Check price every 5 seconds
  ✓ Automatically execute trading strategy (no user confirmation)
  ✓ Log all activity to: logs/nabil.log
  ✓ Track P&L, fills, and portfolio value

📊 Initializing Paper Trader...
📈 Setting up NABIL strategy...
   Entry: 10 shares @ Rs. 1,000.00

══════════════════════════════════════════════════════════════════════════════════════
⏱️  STARTING AUTOMATED TRADING - CHECK EVERY 5 SECONDS
══════════════════════════════════════════════════════════════════════════════════════

[STATUS UPDATE] Checks: 60 | Trades: 2 | Price: Rs. 1,045.30 | PV: Rs. 1,004,530 | P&L: +4,530
[STATUS UPDATE] Checks: 120 | Trades: 3 | Price: Rs. 1,002.15 | PV: Rs. 1,003,215 | P&L: +3,215

══════════════════════════════════════════════════════════════════════════════════════
FINAL STATUS
══════════════════════════════════════════════════════════════════════════════════════
Total Price Checks: 120
Total Trades Executed: 3
Final Price: Rs. 1,002.15
Final Portfolio Value: Rs. 1,003,215.00
Total Unrealized P&L: Rs. +3,215.00

✓ All logs saved to: logs/nabil.log
══════════════════════════════════════════════════════════════════════════════════════
```

---

## Log File Location

**Path:** `logs/nabil.log`

**View it anytime:**
```bash
# See everything
cat logs/nabil.log

# See last 50 lines
tail -50 logs/nabil.log

# Watch live updates
tail -f logs/nabil.log

# Search for specific events
grep "SELL EXECUTED" logs/nabil.log    # Find all sells
grep "P&L:" logs/nabil.log              # Find P&L lines
grep "✓" logs/nabil.log                 # Find successful executions
```

---

## Strategy Behavior During Paper Trading

### 1. Initial Entry
- Automatically buys 10 NABIL @ Rs. 1,000
- Logs to paper_trader
- Updates to logs/nabil.log

### 2. Price Monitoring
- Every 5 seconds: fetches/simulates price
- Analyzes against strategy triggers
- Logs each check to nabil.log

### 3. Trigger Detection
When price moves:
- **If +10%:** Trailing stop activates (automatic, no order)
- **If -10%:** Hard stop triggers → **SELL ORDER EXECUTED**
- **If -20%:** Ladder 1 triggers → **BUY 20 MORE**
- **If -30%:** Ladder 2 triggers → **BUY 10 MORE**

### 4. Automatic Execution
All orders are executed automatically:
- Creates order summary
- Executes with paper_trader
- Updates positions
- Calculates P&L
- Logs everything

---

## Real-Time vs Simulated Prices

### Current: Simulated Prices
```python
# Random walk simulation (±0.5% per 5 seconds)
def simulate_price_movement(self):
    change_pct = random.uniform(-0.5, 0.5) / 100
    new_price = self.current_price * (1 + change_pct)
    return new_price
```

### To Use Real Prices: Override Method
```python
class RealNABILTrader(NABILPaperTrader):
    def simulate_price_movement(self):
        # Replace with real TMS call
        current_price = self.trader.get_current_price("NABIL")
        self.current_price = current_price
        return current_price

# Use it
trader = RealNABILTrader()
trader.setup_strategy(entry_price=1000.0)
trader.start(duration_minutes=60)
```

---

## Key Features Explained

### ✅ Automatic Execution
- No user confirmation needed
- Orders execute immediately when triggers fire
- All logged automatically

### ✅ 5-Second Interval
```python
schedule.every(5).seconds.do(check_price_and_execute)
```
- Checks price every 5 seconds
- Can be adjusted (2, 10, 60 seconds, etc.)
- Configurable per use case

### ✅ Complete Logging
Every action logged to `logs/nabil.log`:
- Timestamps (to the second)
- Order details (symbol, quantity, price)
- Execution confirmations
- P&L calculations
- Portfolio snapshots

### ✅ Portfolio Tracking
```python
{
    'cash': 990000.00,
    'holdings': {
        'NABIL': {
            'shares': 10,
            'avg_cost': 1000.00,
            'current_price': 1000.00,
            'position_value': 10000.00,
            'unrealized_pnl': 0.00,
            'unrealized_pnl_pct': 0.00
        }
    },
    'total_unrealized_pnl': 0.00,
    'total_value': 1000000.00
}
```

---

## Customization Examples

### Change Check Interval
```python
# Check every 2 seconds (more responsive)
trader = NABILPaperTrader(check_interval=2)

# Check every 30 seconds (less responsive)
trader = NABILPaperTrader(check_interval=30)

# Check every minute
trader = NABILPaperTrader(check_interval=60)
```

### Change Log File Location
```python
# Custom log file
trader = NABILPaperTrader(log_file="logs/custom_log.log")
```

### Change Strategy Parameters
In `nabil_scheduler.py`, modify setup_strategy():
```python
trader.setup_strategy(
    entry_price=1200.0,        # Different entry price
    initial_quantity=20        # Buy 20 instead of 10
)
```

Or modify the strategy itself:
```python
self.strategy = TrailingStopStrategy(
    ...
    stop_loss_pct=5,           # Tighter stop
    trailing_activation_pct=5, # Activate at 5% gain
    ladder_triggers={15: 25}   # Different ladders
)
```

### Change Starting Capital
In `paper_trader.py`:
```python
self.cash = 500000  # Start with 500k instead of 1M
```

---

## Workflow Diagram

```
User starts bot
    ↓
Initialize Paper Account
- Cash: Rs. 1,000,000
- Positions: Empty
    ↓
Setup Strategy
- Symbol: NABIL
- Entry: 10 @ Rs. 1,000
- Stops: -10%, +10%
- Ladders: 20%, 30%
    ↓
Execute Initial Buy
- Paper BUY: 10 @ Rs. 1,000
- Cash: Rs. 990,000
- Position: 10 shares
- Log: ✓ EXECUTED
    ↓
Start Scheduler Loop
    │
    ├─ Every 5 seconds:
    │  ├─ Get price (simulate)
    │  ├─ Run strategy.analyze()
    │  ├─ Check for triggers
    │  ├─ If triggered: Execute order
    │  ├─ Update portfolio
    │  └─ Log activity
    │
    ├─ Every 10 checks:
    │  └─ Log portfolio summary
    │
    └─ Repeat until duration complete
    ↓
Generate Final Report
- Total checks: 120
- Total trades: 3
- Final P&L: +Rs. 3,215
- All logged to nabil.log
    ↓
Bot Complete
```

---

## Troubleshooting

### Log file not being created?
```bash
# Create logs directory manually
mkdir -p logs

# Check permissions
ls -la logs/
```

### Bot runs but no logs?
```bash
# Check if file is being written
tail logs/nabil.log

# Or check file size
ls -lh logs/nabil.log
```

### Want to see logs while running?
```bash
# Terminal 1: Run bot
python demo_paper_trading.py

# Terminal 2: Watch logs
tail -f logs/nabil.log
```

### Want to stop before duration completes?
```bash
# While bot is running in terminal, press:
Ctrl+C
```

### Want to review all past logs?
```bash
# See entire history
cat logs/nabil.log

# Count total trades executed
grep -c "EXECUTED" logs/nabil.log

# See all profits
grep "✓ PROFIT" logs/nabil.log
```

---

## What Happens Next?

### Option 1: Keep Testing
- Run demo multiple times
- Review different price scenarios
- Adjust strategy parameters
- Perfect your parameters

### Option 2: Connect to Real TMS
- Replace simulated prices with TMS prices
- Keep paper trading mode
- Verify strategy works with real data
- Move to live when confident

### Option 3: Go to Production
- Switch from paper trader to real trader
- Test with small position (5 shares)
- Scale up gradually
- Monitor real P&L

---

## Summary

What you now have:

✅ **PaperTrader** - Simulates trades (paper_trader.py)  
✅ **Scheduler** - Runs every 5 seconds (nabil_scheduler.py)  
✅ **Demo Scripts** - Easy startup (demo_paper_trading.py)  
✅ **Logging** - Everything to nabil.log  
✅ **Tracking** - Full portfolio management  
✅ **Automation** - No manual intervention needed  

**Get started now:**
```bash
python demo_paper_trading.py
```

Then check the logs:
```bash
tail -f logs/nabil.log
```

**You're ready!** 🚀

