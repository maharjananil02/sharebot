# Paper Trading - Quick Reference Card

## ⚡ Quick Commands

### Start Paper Trading

**Full Demo (10 minutes):**
```bash
python demo_paper_trading.py
```

**Quick Test (30 seconds):**
```bash
python test_paper_trading.py
```

### Monitor Logs

**Watch in real-time:**
```bash
tail -f logs/nabil.log
```

**View all logs:**
```bash
cat logs/nabil.log
```

**See last 50 lines:**
```bash
tail -50 logs/nabil.log
```

### Search Logs

**Find all sells:**
```bash
grep "SELL EXECUTED" logs/nabil.log
```

**Find profitable trades:**
```bash
grep "✓ PROFIT" logs/nabil.log
```

**Count total trades:**
```bash
grep -c "EXECUTED" logs/nabil.log
```

**See P&L values:**
```bash
grep "P&L:" logs/nabil.log
```

**Find order summaries:**
```bash
grep "ORDER SUMMARY" logs/nabil.log
```

---

## 📊 What Gets Logged

| Event | Log Line | Frequency |
|-------|----------|-----------|
| Price check | `[CHECK #0001]` | Every 5 seconds |
| Buy order | `✓ PAPER BUY EXECUTED` | When triggered |
| Sell order | `✓ PROFIT PAPER SELL` | When triggered |
| Portfolio | `PORTFOLIO SUMMARY` | Every 10 checks |
| Final report | `PAPER TRADING STOPPED` | At end |

---

## 🎯 Key Triggers

| Condition | Action | Log Entry |
|-----------|--------|-----------|
| Price ↑ 10% | Activate trailing stop | Trailing stop info |
| Trailing hit | Sell automatically | `SELL_TRAILING` |
| Price ↓ 10% | Hard stop triggers | `SELL_STOP` |
| Price ↓ 20% | Ladder 1 buys | `BUY_LADDER` x20 |
| Price ↓ 30% | Ladder 2 buys | `BUY_LADDER` x10 |

---

## 📈 Portfolio Metrics

**Always logged:**
- Cash balance
- Holdings value
- Total portfolio value
- Unrealized P&L
- Position details
- Individual P&L %

**Track in logs:**
```bash
grep "Total Portfolio Value" logs/nabil.log
grep "Unrealized P&L" logs/nabil.log
```

---

## ⚙️ Configuration

### Change Check Interval
In code:
```python
trader = NABILPaperTrader(check_interval=5)  # 5 seconds (default)
trader = NABILPaperTrader(check_interval=10) # 10 seconds
trader = NABILPaperTrader(check_interval=2)  # 2 seconds
```

### Change Starting Capital
Edit `paper_trader.py`:
```python
self.cash = 1000000  # Change to any amount
```

### Change Log File
In code:
```python
trader = NABILPaperTrader(log_file="logs/custom.log")
```

---

## 🔄 Trading Flow

```
START
  ↓
Initialize (1M cash, 0 positions)
  ↓
Setup strategy
  ↓
Buy 10 @ Rs. 1,000 (initial)
  ↓
Every 5 seconds:
  ├─ Check price
  ├─ Analyze triggers
  └─ Execute orders (automatic)
  ↓
Every 10 checks:
  └─ Log portfolio summary
  ↓
When duration complete:
  └─ Final report + stats
```

---

## 📝 Log File Format

```
TIMESTAMP - LOGGER - LEVEL - MESSAGE

Examples:
2026-04-28 16:34:45 - src.bot.nabil_scheduler - INFO - ✓ PAPER BUY EXECUTED
2026-04-28 16:34:50 - src.bot.nabil_scheduler - INFO - [CHECK #0001] | Price: Rs. 1002.21
2026-04-28 16:34:55 - src.bot.nabil_scheduler - INFO - Order ID: PAPER-BUY-1
```

---

## 🎯 What to Monitor

**During trading:**
- Price updates (every 5 seconds)
- Order executions (when triggered)
- P&L changes (after each trade)
- Portfolio value (real-time)

**After trading:**
- Total trades executed
- Win rate (profitable trades)
- Final portfolio value
- Total P&L

---

## 📊 Example Output Lines

### Order Execution
```
✓ PAPER BUY EXECUTED
   Symbol: NABIL
   Quantity: 20 shares
   Price: Rs. 800.00
   Total Cost: Rs. 16,000.00
   P&L: (for sells) Rs. +500.00 (+2.5%)
```

### Price Check
```
[CHECK #0042] 16:45:30 | Price: Rs. 1,050.00
```

### Portfolio Status
```
PORTFOLIO SUMMARY
Cash: Rs. 950,000.00
Holdings Value: Rs. 42,000.00
Total Value: Rs. 992,000.00
Unrealized P&L: Rs. -8,000.00 (-0.80%)
```

---

## ✅ Verification Checklist

After running demo, verify:

- [ ] `logs/nabil.log` file exists
- [ ] Initial buy order logged
- [ ] Price checks every 5 seconds
- [ ] Portfolio summary logged
- [ ] Final report shows statistics
- [ ] P&L calculated correctly

---

## 🚀 Next Steps

1. **Run demo:**
   ```bash
   python demo_paper_trading.py
   ```

2. **Watch logs:**
   ```bash
   tail -f logs/nabil.log
   ```

3. **After completion, review:**
   ```bash
   cat logs/nabil.log | grep "PROFIT"
   ```

4. **Analyze results:**
   - Total profit/loss?
   - Number of trades?
   - Strategy working?

5. **Customize:**
   - Change parameters
   - Run again
   - Compare results

---

## 📞 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| No logs appearing | Check `logs/` directory exists |
| Bot stops immediately | Check strategy setup |
| Can't find log file | Use `find logs -name "*.log"` |
| Want to stop early | Press Ctrl+C |
| Want to see live updates | Use `tail -f logs/nabil.log` |
| Need to search logs | Use `grep` command |

---

## 🎓 Understanding the Strategy

```
Hard Floor (Protection)
├─ Trigger: Price ↓ 10%
├─ Action: SELL ALL
└─ Purpose: Limit loss to -10%

Trailing Stop (Profit)
├─ Trigger: Price ↑ 10%
├─ Action: Move stop up 5%
└─ Purpose: Let profits run

Ladder-In (Accumulation)
├─ Level 1: Price ↓ 20% → Buy 20 more
├─ Level 2: Price ↓ 30% → Buy 10 more
└─ Purpose: Better average cost
```

---

## 📊 Interpreting Results

After demo completes, you'll see:

```
[FINAL STATUS]
Total Checks: 120
Total Trades: 3
Final Price: Rs. 1,050.32
Portfolio Value: Rs. 1,005,300.00
Unrealized P&L: Rs. +5,300.00
```

**What this means:**
- Checked price 120 times (120 × 5 sec = 10 min)
- Executed 3 trades total
- Price rose from Rs. 1,000 to Rs. 1,050 (+5%)
- Portfolio gained Rs. 5,300 (+0.53%)

---

## 💡 Pro Tips

1. **Run multiple times** to see different scenarios
2. **Watch logs live** to understand strategy behavior
3. **Adjust parameters** and re-run to compare
4. **Search logs** for specific events
5. **Track P&L** by symbol and time
6. **Note which triggers** fire most often
7. **Analyze winning trades** - what triggered them?

---

## 📁 Important Paths

```
Project Root:
/Users/anil/Coding/lets\ code/nepse-trading/

Code:
src/bot/
  ├─ paper_trader.py
  └─ nabil_scheduler.py

Scripts:
  ├─ demo_paper_trading.py
  └─ test_paper_trading.py

Logs:
logs/
  └─ nabil.log

Docs:
  ├─ PAPER_TRADING_GUIDE.md
  ├─ PAPER_TRADING_SETUP.md
  └─ (this file)
```

---

## 🎯 Success Metrics

Track these:
- **Win Rate:** % of profitable trades
- **Profit Factor:** Avg win / Avg loss
- **Max Drawdown:** Worst loss in sequence
- **Total P&L:** Final profit/loss
- **Trades Count:** How many executed

---

## Ready? Start here:

```bash
# 1. Start the demo
python demo_paper_trading.py

# 2. In another terminal, watch logs
tail -f logs/nabil.log

# 3. When done, review results
cat logs/nabil.log | tail -30
```

**You're all set!** 📈

