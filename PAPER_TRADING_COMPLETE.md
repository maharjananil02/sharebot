# Paper Trading System - COMPLETE SUMMARY

## What You Now Have

A **production-ready paper trading system** that:

✅ **Simulates trading** without real money  
✅ **Runs automatically** every 5 seconds  
✅ **Executes orders** without user intervention  
✅ **Logs everything** to `logs/nabil.log`  
✅ **Tracks portfolio** with real-time P&L  
✅ **Integrates strategy** with trailing stop system  

---

## Files Created (4 total)

### Code Files (2)

1. **`src/bot/paper_trader.py`** (~200 lines)
   - Simulates buy/sell orders
   - Tracks cash and positions
   - Calculates P&L
   - Maintains trade history
   - Logs all trades

2. **`src/bot/nabil_scheduler.py`** (~250 lines)
   - Scheduler running every 5 seconds
   - Runs trailing stop strategy
   - Automatically executes orders
   - Simulates price movements
   - Logs to nabil.log

### Demo & Test Files (2)

3. **`demo_paper_trading.py`** (~50 lines)
   - Full 10-minute demo
   - Status updates every 30 seconds
   - Final report generation
   - Ready to run immediately

4. **`test_paper_trading.py`** (~30 lines)
   - Quick 30-second test
   - Same functionality as demo
   - Good for verification

### Documentation Files (3)

5. **`PAPER_TRADING_GUIDE.md`**
   - Complete usage guide
   - How it all works together
   - Configuration options
   - Examples and troubleshooting

6. **`PAPER_TRADING_SETUP.md`**
   - Detailed setup instructions
   - Architecture explanation
   - Real-world usage
   - Customization guide

7. **`PAPER_TRADING_QUICK_REFERENCE.md`** ← You are here
   - Quick commands
   - Key information at a glance
   - Common issues & solutions

---

## How It Works

### Architecture
```
Every 5 Seconds:
├─ Simulate/fetch price
├─ Run strategy analysis
├─ Check for triggers (stop, trailing, ladder)
├─ Execute ALL orders automatically (no manual confirmation!)
├─ Update positions and P&L
└─ Log everything to nabil.log

Every 10 checks (50 seconds):
└─ Log portfolio summary

When complete:
└─ Final report + statistics
```

### Key Difference From Manual System

**Manual (Before):**
- Check price manually
- See order summary
- **Wait for user confirmation**
- Execute if user approves

**Automated Paper Trading (Now):**
- Check price automatically every 5 seconds
- Analyze triggers continuously
- **Execute orders automatically**
- No user intervention needed
- Everything logged to file

---

## Quick Start (3 Steps)

### Step 1: Run Demo
```bash
cd /Users/anil/Coding/lets\ code/nepse-trading
python demo_paper_trading.py
```

### Step 2: Watch Logs (Optional, in another terminal)
```bash
tail -f logs/nabil.log
```

### Step 3: Let It Run
- Runs for 10 minutes
- Automatically checks price every 5 seconds
- Executes trades when triggered
- Logs everything
- Shows final report

---

## What Gets Logged

### Every 5 Seconds
```
[CHECK #0001] 16:34:50 | Price: Rs. 1002.21
[CHECK #0002] 16:34:55 | Price: Rs. 1003.06
```

### When Orders Execute
```
✓ PAPER BUY EXECUTED
   Quantity: 20 shares
   Price: Rs. 800.00
   Total Cost: Rs. 16,000.00
   P&L: Rs. +500.00 (if sell)
```

### Every 10 Checks
```
PORTFOLIO SUMMARY
Cash: Rs. 950,000.00
Holdings Value: Rs. 42,000.00
Total Value: Rs. 992,000.00
Unrealized P&L: Rs. -8,000.00
```

### Final Report
```
FINAL STATISTICS:
  Total Checks: 120
  Total Trades: 3
  Final Price: Rs. 1,050.32
  Price Change: +5.03%
```

---

## Configuration

### Check Interval (How often to check price)

```python
# Every 5 seconds (default)
trader = NABILPaperTrader(check_interval=5)

# Every 10 seconds
trader = NABILPaperTrader(check_interval=10)

# Every 2 seconds (very frequent)
trader = NABILPaperTrader(check_interval=2)

# Every 60 seconds
trader = NABILPaperTrader(check_interval=60)
```

### Starting Capital
Edit `src/bot/paper_trader.py`:
```python
self.cash = 1000000  # Change to any amount
```

### Strategy Parameters
Edit `src/bot/nabil_scheduler.py`:
```python
self.strategy = TrailingStopStrategy(
    stop_loss_pct=10,           # Hard stop at 10% loss
    trailing_activation_pct=10, # Trailing at 10% gain
    trailing_step_pct=5,        # Move stop 5% per climb
    ladder_triggers={20: 20, 30: 10}  # Ladder-in points
)
```

---

## Understanding Trading Flow

### Initial Setup
1. Initialize paper account (Rs. 1,000,000 cash)
2. Setup strategy (trailing stop with ladder-in)
3. Execute initial buy (10 NABIL @ Rs. 1,000)

### Continuous Loop (Every 5 Seconds)
1. Fetch/simulate price for NABIL
2. Run strategy analysis
3. Check triggers:
   - Hard stop (↓ 10%)?
   - Trailing stop (if active)?
   - Ladder 1 (↓ 20%)?
   - Ladder 2 (↓ 30%)?
4. If triggered → **EXECUTE AUTOMATICALLY**
5. Update portfolio
6. Log to nabil.log

### Completion
1. After duration expires
2. Generate final report
3. Show statistics
4. All logged to file

---

## Log File Viewing

### Path
```
logs/nabil.log
```

### Commands
```bash
# View everything
cat logs/nabil.log

# Watch live updates
tail -f logs/nabil.log

# See last 50 lines
tail -50 logs/nabil.log

# Count total trades
grep -c "EXECUTED" logs/nabil.log

# Find profitable trades
grep "✓ PROFIT" logs/nabil.log

# Find losses
grep "✗ LOSS" logs/nabil.log

# See all P&L
grep "P&L:" logs/nabil.log

# Find specific order type
grep "SELL_TRAILING" logs/nabil.log
```

---

## Strategy Triggers

| Condition | Action | Automatic? | Log Entry |
|-----------|--------|-----------|-----------|
| Price ↑ 10% | Activate trailing | Yes | Trailing activated |
| Trailing hit | Sell | **Yes** | SELL_TRAILING |
| Price ↓ 10% | Hard stop | **Yes** | SELL_STOP |
| Price ↓ 20% | Buy 20 more | **Yes** | BUY_LADDER |
| Price ↓ 30% | Buy 10 more | **Yes** | BUY_LADDER |

**Key Point:** All orders execute automatically. No manual intervention needed.

---

## Example Run Sequence

### Minute 0
```
NABIL PAPER TRADING STARTED
Starting Cash: Rs. 1,000,000.00

>>> SETTING UP STRATEGY
    Entry Price: Rs. 1,000.00
    Initial Quantity: 10 shares

>>> EXECUTING INITIAL BUY ORDER
✓ PAPER BUY EXECUTED
   Price: Rs. 1,000.00
   Position: 10 shares
   Cash: Rs. 990,000.00
```

### Minute 1-2 (Price wanders, no triggers)
```
[CHECK #0001] Price: Rs. 1,002.21
[CHECK #0002] Price: Rs. 1,003.06
[CHECK #0003] Price: Rs. 999.41
```

### Minute 4 (Ladder trigger!)
```
[CHECK #0008] 16:34:39 | Price: Rs. 800.00

>>> 1 ORDER(S) TRIGGERED - EXECUTING AUTOMATICALLY

✓ PAPER BUY EXECUTED
   Quantity: 20 shares
   Price: Rs. 800.00
   Total Cost: Rs. 16,000.00
   Position: 30 shares (Avg: Rs. 933.33)
```

### Minute 6
```
PORTFOLIO SUMMARY
Cash: Rs. 974,000.00
Holdings Value: Rs. 28,000.00
Total Value: Rs. 1,002,000.00
Position: NABIL 30 @ Rs. 933.33 = -0.67%
```

### Minute 10 (Price recovers, sell!)
```
[CHECK #0120] 16:44:50 | Price: Rs. 1,050.00

>>> 1 ORDER(S) TRIGGERED - EXECUTING AUTOMATICALLY

✓ PROFIT PAPER SELL EXECUTED
   Quantity: 30 shares
   Price: Rs. 1,050.00
   Proceeds: Rs. 31,500.00
   P&L: Rs. +4,500.00 (+14.29%)
```

### End
```
PAPER TRADING STOPPED

FINAL STATISTICS:
  Total Checks: 120
  Total Trades: 3
  Final Price: Rs. 1,050.00
  Final Portfolio: Rs. 1,005,500.00
  Total P&L: +Rs. 5,500.00 (+0.55%)
```

---

## Key Metrics Tracked

### For Every Trade:
- Order ID (PAPER-BUY-1, PAPER-SELL-2, etc.)
- Timestamp (to the second)
- Symbol name
- Buy/Sell quantity
- Price executed
- Total cost/proceeds
- P&L (for sells)
- Current position
- Cash after

### Portfolio (Every 10 rounds):
- Available cash
- Holdings value
- Total portfolio value
- Unrealized P&L
- Unrealized P&L %
- Position details per symbol

---

## Real vs. Paper Trading Comparison

| Aspect | Paper Trading | Real Trading |
|--------|---------------|-------------|
| Money Risk | ❌ No real money | ✅ Real capital at risk |
| Execution | Simulated | Real TMS orders |
| Speed | Instant (paper) | Subject to TMS |
| Price Source | Simulated (random walk) | Real market price |
| Logging | ✅ Complete | ✅ Same system |
| Strategy | ✅ Full trailing stop | ✅ Same strategy |
| Confirmation | No manual confirmation | No manual confirmation |
| Automation | ✅ Full automation | ✅ Full automation |

---

## Customization Examples

### Only Check Every 10 Seconds
```python
trader = NABILPaperTrader(check_interval=10)
```

### Start With Different Capital
Edit `paper_trader.py`:
```python
self.cash = 500000  # Instead of 1M
```

### Different Entry Price
```python
trader.setup_strategy(entry_price=1200.0, initial_quantity=10)
```

### Different Strategy Parameters
Edit `nabil_scheduler.py`:
```python
self.strategy = TrailingStopStrategy(
    ...
    stop_loss_pct=5,              # Tighter stop
    trailing_activation_pct=15,   # Higher activation
    ladder_triggers={15: 25, 40: 10}  # More ladders
)
```

### Longer Duration
```python
trader.start(duration_minutes=60)  # Run for 1 hour
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Script doesn't start | Check Python environment: `python --version` |
| ImportError | Reinstall deps: `pip install -r requirements.txt` |
| Log file not created | Create directory: `mkdir -p logs` |
| No orders executing | Check log for trigger reasons |
| Can't see logs | Use: `tail -f logs/nabil.log` |
| Script hangs | Press Ctrl+C to stop gracefully |
| Want to restart | Just run script again, logs append |

---

## Next Phase: Real TMS Integration

When ready to use real prices, modify this method in `nabil_scheduler.py`:

```python
def simulate_price_movement(self):
    """Currently simulated - add real TMS price here"""
    
    # Replace with:
    current_price = self.trader.get_current_price("NABIL")
    self.current_price = current_price
    return current_price
```

Then it will use real market prices while keeping the same logging and order execution.

---

## Summary

### You Now Have:
✅ Fully automated paper trading  
✅ Every 5-second price checking  
✅ Automatic order execution  
✅ Complete logging to nabil.log  
✅ Trailing stop strategy integrated  
✅ Ladder-in accumulation  
✅ Portfolio tracking  
✅ Real-time P&L calculation  

### To Start:
```bash
python demo_paper_trading.py
```

### To Monitor:
```bash
tail -f logs/nabil.log
```

### To Understand Trade Results:
```bash
grep "P&L:" logs/nabil.log
```

---

## Files Reference

| File | Purpose | Status |
|------|---------|--------|
| `src/bot/paper_trader.py` | Core trading simulation | ✅ Ready |
| `src/bot/nabil_scheduler.py` | Scheduler & automation | ✅ Ready |
| `demo_paper_trading.py` | Full demo (10 min) | ✅ Ready |
| `test_paper_trading.py` | Quick test (30 sec) | ✅ Ready |
| `PAPER_TRADING_GUIDE.md` | Complete guide | ✅ Ready |
| `PAPER_TRADING_SETUP.md` | Setup & customization | ✅ Ready |
| `PAPER_TRADING_QUICK_REFERENCE.md` | This file | ✅ Ready |

---

## Ready? 🚀

**Start now:**
```bash
python demo_paper_trading.py
```

**Watch logs:**
```bash
tail -f logs/nabil.log
```

**You're all set!**

---

**Questions? Review:**
- `PAPER_TRADING_GUIDE.md` - Complete explanation
- `PAPER_TRADING_SETUP.md` - Detailed setup
- `logs/nabil.log` - What actually happened

Happy trading! 📈

