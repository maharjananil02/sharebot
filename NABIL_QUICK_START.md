# NABIL Trailing Stop Strategy - Quick Start Guide

## What You Now Have

A complete **three-layer trading strategy** for NABIL that:
1. **Protects downside** with a 10% hard stop loss
2. **Locks in profits** with a trailing stop
3. **Averages down** with ladder-in purchases

---

## Files Overview

### 📖 Documentation Files (Read in This Order)

1. **[NABIL_TRAILING_STOP_SUMMARY.md](NABIL_TRAILING_STOP_SUMMARY.md)** ⭐ START HERE
   - Complete strategy overview
   - All three components explained
   - Real trading scenarios
   - Decision flow diagram

2. **[NABIL_ORDER_SUMMARIES.md](NABIL_ORDER_SUMMARIES.md)** 
   - Example order summaries you'll see
   - What to expect before each trade
   - Order confirmation workflow

3. **[NABIL_STRATEGY_INTEGRATION.md](NABIL_STRATEGY_INTEGRATION.md)**
   - How to integrate with your trading bot
   - Code examples
   - Implementation steps

### 💻 Code Files

1. **`src/bot/trailing_stop_strategy.py`** - Core strategy engine
   - `TrailingStopStrategy` class
   - `Order` class for tracking orders
   - All logic for stops, trailing, ladder-in

2. **`test_trailing_stop.py`** - Live demo
   - Run this to see strategy in action
   - Simulates price movements
   - Shows order summaries

---

## Quick Start (5 Minutes)

### 1. Open the main summary document
```bash
cat NABIL_TRAILING_STOP_SUMMARY.md
```
This gives you the big picture.

### 2. Run the demo to see it in action
```bash
# Make sure you're in the project directory
cd /Users/anil/Coding/lets\ code/nepse-trading

# Run the demo
python test_trailing_stop.py

# When prompted, select:
# 1 = See how trailing stop ratchets as price rises
# 2 = See how ladder-in works when price drops
# 3 = See both scenarios
```

### 3. Review example order summaries
```bash
cat NABIL_ORDER_SUMMARIES.md
```
You'll see these exact summaries before real orders.

### 4. Understand integration
```bash
cat NABIL_STRATEGY_INTEGRATION.md
```
Learn how to connect to your actual trading bot.

---

## Strategy at a Glance

```
Symbol: NABIL
Entry: 10 shares at current market price

┌─ HARD FLOOR (10% loss limit)
│  └─ If price drops 10%: SELL ALL NOW
│
├─ TRAILING STOP (profit protection)
│  └─ Activates when you gain 10%
│  └─ Ratchets up 5% per price climb
│  └─ Sells if price drops below trailing level
│
└─ LADDER IN (accumulation on weakness)
   └─ 20% drop: Buy 20 more shares
   └─ 30% drop: Buy 10 more shares
```

---

## Your Key Numbers

| When | Price | Action |
|------|-------|--------|
| Entry | Rs. 1,000 | Buy 10 shares |
| Price ↓ 10% | Rs. 900 | 🛑 **HARD STOP - SELL ALL** |
| Price ↑ 10% | Rs. 1,100 | 📈 Trailing stop activates |
| Price ↓ 20% | Rs. 800 | 🪜 Ladder #1: Buy 20 more |
| Price ↓ 30% | Rs. 700 | 🪜 Ladder #2: Buy 10 more |

---

## Before You Start

### ✓ Checklist

- [ ] Read NABIL_TRAILING_STOP_SUMMARY.md
- [ ] Run `python test_trailing_stop.py` and try scenarios 1 & 2
- [ ] Review NABIL_ORDER_SUMMARIES.md
- [ ] Understand NABIL_STRATEGY_INTEGRATION.md
- [ ] Adjust parameters if needed
- [ ] Have capital ready for ladder-in (up to Rs. 35,000 total)
- [ ] Ensure you can monitor during market hours

### ⚠️ Important Warnings

1. **This requires user confirmation** - Every order shows a summary, you must confirm before execution
2. **You need capital** - Ladder-in can need Rs. 35,000 total if both levels trigger
3. **Requires monitoring** - You should watch prices and confirm orders
4. **Demo mode first** - Test in demo mode before using real money
5. **Paper trade** - Try with simulated prices first to get comfortable

---

## Running the Strategy IRL

### Step 1: Setup Your Bot
```python
from src.bot.trailing_stop_strategy import TrailingStopStrategy
from src.bot.trader import Trader

# Your trader instance
trader = Trader(browser_manager)

# Create strategy
strategy = TrailingStopStrategy(
    trader=trader,
    symbol="NABIL",
    initial_quantity=10,
    entry_price=current_price,  # Get from market
    stop_loss_pct=10,
    trailing_activation_pct=10,
    trailing_step_pct=5,
    ladder_triggers={20: 20, 30: 10}
)
```

### Step 2: Monitor Prices
```python
while trading_active:
    price = get_current_price("NABIL")
    orders = strategy.analyze(price)
    
    if orders:
        print(strategy.get_order_summary(orders))
        if confirm_execution():
            execute_orders(orders)
```

### Step 3: Track Your Position
```python
# Status anytime
print(strategy.get_position_report())
```

---

## Example Outcomes

### 🌟 Best Case
```
Entry:    Rs. 1,000 (10 shares)
Peak:     Rs. 1,150 (+15%)
Exit:     Rs. 1,100 (trailing stop ratcheted up)
Result:   +Rs. 1,000 profit (10%) ✓
```

### 😐 Neutral Case
```
Entry:    Rs. 1,000 (10 shares)
Movement: Rs. 950 to Rs. 1,050 (wandering)
Hold:     10 shares (no triggers)
Result:   Unresolved - can choose to exit
```

### 🪜 Accumulation Case
```
Entry:     Rs. 1,000 (10 shares) = Rs. 10,000
Drop 20%:  Rs. 800 + Buy 20 = Rs. 26,000 total
Drop 30%:  Rs. 700 + Buy 10 = Rs. 33,000 total
Recovery:  Rs. 1,000 exit price
Result:    +Rs. 7,000 profit (21%) ✓
```

### 🛑 Protected Loss Case
```
Entry:    Rs. 1,000 (10 shares) = Rs. 10,000
Crash:    Rs. 900 (hard stop triggers)
Exit:     Sell 10 @ Rs. 900 = Rs. 9,000
Result:   -Rs. 1,000 loss (-10%) PROTECTED ✓
```

---

## Adjusting the Strategy

### More Conservative (Lower Risk)
```python
strategy = TrailingStopStrategy(
    ...
    stop_loss_pct=5,              # Sell at -5%
    trailing_activation_pct=5,    # Trailing at +5%
    trailing_step_pct=3,          # Move 3% at a time
    ladder_triggers={10: 10}      # Only one ladder level
)
```

### More Aggressive (Higher Risk)
```python
strategy = TrailingStopStrategy(
    ...
    stop_loss_pct=20,             # Sell at -20%
    trailing_activation_pct=15,   # Trailing at +15%
    trailing_step_pct=7,          # Move 7% at a time
    ladder_triggers={15: 25, 25: 15, 40: 10}  # More ladders
)
```

---

## Support & Troubleshooting

### Common Issues

**Q: Where do I see if an order was executed?**
A: Check `strategy.orders` list or call `strategy.get_position_report()`

**Q: Can I modify ladder triggers?**
A: Yes, pass different dict when creating strategy: `ladder_triggers={20: 25, 35: 15}`

**Q: What if price jumps over a ladder level?**
A: The strategy tracks using `<=` comparison, so it will still trigger

**Q: How do I close the position manually?**
A: Use `strategy.get_position_report()` to check status, then create a manual SELL order

**Q: What if I'm not sure?**
A: Run `python test_trailing_stop.py` to see scenarios in action

---

## Next Actions

### Immediately
1. Read NABIL_TRAILING_STOP_SUMMARY.md
2. Run python test_trailing_stop.py

### This Week
1. Integrate strategy into your trading bot
2. Test in demo mode with simulated prices
3. Verify order confirmations work

### When Ready
1. Start with 5 shares instead of 10 (lower risk)
2. Monitor first trade manually
3. Scale up once comfortable
4. Adjust parameters based on experience

---

## Files Reference

```
/Users/anil/Coding/lets code/nepse-trading/

📄 NABIL_TRAILING_STOP_SUMMARY.md ← Read this first!
📄 NABIL_ORDER_SUMMARIES.md
📄 NABIL_STRATEGY_INTEGRATION.md
📄 NABIL_QUICK_START.md ← You are here

💻 src/bot/
   └─ trailing_stop_strategy.py ← Core implementation

🧪 test_trailing_stop.py ← Demo script
```

---

## Questions?

### For strategy logic questions:
- See NABIL_TRAILING_STOP_SUMMARY.md

### For what orders look like:
- See NABIL_ORDER_SUMMARIES.md

### For integration with your bot:
- See NABIL_STRATEGY_INTEGRATION.md

### To see it in action:
- Run: `python test_trailing_stop.py`

---

## Summary

You now have:

✅ A complete trailing stop strategy for NABIL  
✅ Hard stop loss protection (-10% max)  
✅ Trailing stop for profit protection  
✅ Ladder-in for accumulation on weakness  
✅ Order confirmation workflow (you approve each trade)  
✅ Demo script to see it in action  
✅ Integration guide for your trading bot  

**Next step:** Read NABIL_TRAILING_STOP_SUMMARY.md to understand everything, then run the demo!

