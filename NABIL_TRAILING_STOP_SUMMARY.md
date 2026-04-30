# NABIL Trailing Stop Strategy - Complete Overview

## Strategy Summary

You're implementing a sophisticated three-layer trading strategy for NABIL with:

**Initial Setup:**
- **Stock:** NABIL  
- **Initial Position:** 10 shares
- **Entry Price:** Current market price (Rs. 1,000 assumed)
- **Total Risk:** Limited to maximum 10% loss

---

## Strategy Components

### 1. HARD FLOOR (Stop Loss) - Your Risk Limit
**What it does:** Prevents catastrophic losses by selling all shares if price drops 10%

| Metric | Value |
|--------|-------|
| **Trigger** | Stock drops 10% from entry price |
| **Floor Level** | Rs. 900 (if entry @ Rs. 1,000) |
| **Action** | **SELL ALL 10 SHARES IMMEDIATELY** |
| **Purpose** | Limit maximum loss to -10% |
| **Worst Case** | Lose Rs. 1,000 (if entered @ Rs. 1,000) |

**Example Timeline:**
```
Entry:               Rs. 1,000.00  (10 shares) ← Your position
↓ 5% drop:           Rs. 950.00    (Hold - above stop)
↓ 10% drop:          Rs. 900.00    (HARD STOP TRIGGERS - SELL ALL)
↓ If continues down: Rs. 850.00    (You're already out - protected)
```

---

### 2. TRAILING STOP - Lock In Profits
**What it does:** Once price goes up, move your stop loss up too. Follows price higher but never moves down.

| Metric | Value |
|--------|-------|
| **Activation Level** | +10% gain (Rs. 1,100) |
| **Ratchet Mechanism** | Moves up 5% below current price |
| **Direction** | Only moves UP, never DOWN |
| **Purpose** | Let profits run while protecting gains |

**Example Timeline - Price Rises:**
```
Entry:                     Rs. 1,000.00  (10 shares)
Price rises to:            Rs. 1,010.00  (+1.0%) 
  → Stop stays at:         Rs. 900.00    (Not activated yet)

Price rises to:            Rs. 1,100.00  (+10%) 
  → TRAILING ACTIVATES!
  → New stop:              Rs. 1,045.00  (95% of current price)

Price rises to:            Rs. 1,120.00  (+12%)
  → Stop MOVES UP to:      Rs. 1,064.00  (95% of Rs. 1,120)

Price rises to:            Rs. 1,150.00  (+15%)
  → Stop MOVES UP to:      Rs. 1,092.50  (95% of Rs. 1,150)

Price drops to:            Rs. 1,140.00  (+14%)
  → Stop STAYS at:         Rs. 1,092.50  (Never moves down)

Price drops to:            Rs. 1,090.00
  → TRAILING TRIGGERS - SELL at Rs. 1,090
  → Exit profit:           Rs. 900 (from 10 shares)
```

**Key Feature:** The stop only goes up, never down. This protects your gains.

---

### 3. LADDER-IN - Accumulation on Weakness
**What it does:** Buy more shares when price drops significantly. You average down the cost.

| Drop % | Price (from Rs. 1,000) | Action | Total Shares | Avg Cost |
|--------|------------------------|--------|--------------|----------|
| 0% | Rs. 1,000 | Buy 10 initial | 10 | Rs. 1,000 |
| 20% drop | Rs. 800 | **Buy 20 more** | 30 | Rs. 933.33 |
| 30% drop | Rs. 700 | **Buy 10 more** | 40 | Rs. 850.00 |

**Example Timeline - Price Drops:**
```
Entry:                    Rs. 1,000.00  (10 shares @ Rs. 1,000)
Price drops to:           Rs. 950.00    (-5%) → Hold
Price drops to:           Rs. 850.00    (-15%) → Hold (not at 20% yet)

Price drops to:           Rs. 800.00    (-20%)
  → LADDER #1 TRIGGERS!
  → BUY 20 more shares @ Rs. 800
  → New position: 30 shares
  → New avg cost: Rs. 933.33
  → Max loss now: Rs. 2,800 (30 × Rs. 93.33)

Price continues down to:  Rs. 700.00    (-30%)
  → LADDER #2 TRIGGERS!
  → BUY 10 more shares @ Rs. 700
  → New position: 40 shares
  → New avg cost: Rs. 850.00
  → Max loss now: Rs. 3,400 (40 × Rs. 85)

Price recovers to:        Rs. 1,000.00  (+17.6% from avg cost)
  → Exit 40 shares with profit
  → Exit profit: Rs. 6,000
```

**Key Advantage:** By buying dips, you reduce your average cost and increase profit potential on recovery.

---

## Complete Decision Flow

```
                              ┌─────────────────────────┐
                              │   Current NABIL Price   │
                              └────────────┬────────────┘
                                           │
                     ┌─────────────────────┼─────────────────────┐
                     │                     │                     │
                     ↓                     ↓                     ↓
            Price Down 10%        Price in Range          Price Up 10%
            from Entry            (Holding)               from Entry
                │                   │                         │
                ↓                   ↓                         ↓
        ┌──────────────────┐   ┌──────────────────┐   ┌─────────────────┐
        │  HARD STOP HIT   │   │  NO ACTION       │   │ TRAILING ACTIVE │
        │                  │   │  Monitor price   │   │                 │
        │ SELL ALL 10      │   │  Watch for       │   │ Move stop UP    │
        │ shares at loss   │   │ • Ladder triggers│   │ by 5% below     │
        │                  │   │ • Hard stop hit  │   │ current price   │
        │ Max loss: -10%   │   │ • +10% gain      │   │                 │
        └──────────────────┘   └──────────────────┘   │ Protect profits │
        (Position closed)      (Waiting)              │ Sell if drop    │
                               │                      └─────────────────┘
                               ↓
                    ┌─────────────────────────┐
                    │ Price drops 20% or 30%? │
                    └────────┬────────────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                    ↓                 ↓
            Ladder #1 (20%)    Ladder #2 (30%)
            BUY 20 more        BUY 10 more
            @ Rs. 800          @ Rs. 700
            (if triggered)     (if triggered)
```

---

## Order Execution Workflow

### Before Each Order: Show Summary for Confirmation

```
================================================================================
                    ORDER SUMMARY - PLEASE CONFIRM                        
================================================================================

CURRENT POSITION STATE:
────────────────────────────────────────────────────────────────────────────────
Symbol:              NABIL
Current Price:       Rs. 1,000.00
Position Size:       10 shares
Avg Entry Price:     Rs. 1,000.00
Position P&L:        +0.00%
Stop Loss Level:     Rs. 900.00
Highest Price Seen:  Rs. 1,050.00
Trailing Stop Active: NO

PENDING ORDERS TO EXECUTE:
────────────────────────────────────────────────────────────────────────────────

Order #1: BUY_LADDER
  Symbol:          NABIL
  Quantity:        20 shares
  Order Price:     800.00
  Reason:          Ladder-in at 20% price drop
  Trigger:         Price 800.00 <= Trigger 800.00
  Position Change: -20.00%

================================================================================
STRATEGY PARAMETERS:
────────────────────────────────────────────────────────────────────────────────
Hard Stop Loss:      10% (Rs. 900.00)
Trailing Activation: +10% (Rs. 1,100.00)
Trailing Step:       5% (moves up as price rises)
Ladder-in Triggers:  {20: 20, 30: 10}

================================================================================

[USER CONFIRMS BEFORE ORDER EXECUTES]

✓ Press Enter to execute or Ctrl+C to cancel
```

---

## Real Trading Scenarios

### Scenario A: Stock Rises (Best Case)
```
Bought:        10 shares @ Rs. 1,000 = Rs. 10,000
Price climbs:  Rs. 1,150 (+15%)
Trailing Stop: Activated at Rs. 1,100, moved to Rs. 1,092.50

Small pullback: Rs. 1,090
Trailing triggers SELL: 10 shares @ Rs. 1,090
Profit: Rs. 900 (+9%)
```

### Scenario B: Stock Stays Flat (Patience)
```
Bought:        10 shares @ Rs. 1,000 = Rs. 10,000
Price wanders: Rs. 950 to Rs. 1,050
No orders triggered - still holding
Stop protected: Hard stop at Rs. 900 always active

Decision point: Manually close if bored, or keep waiting
```

### Scenario C: Stock Drops Sharply (Ladder-in)
```
Bought:        10 shares @ Rs. 1,000 = Rs. 10,000
Price drops:   Rs. 800 (-20%)

LADDER #1: Buy 20 more @ Rs. 800 = Rs. 16,000
New position: 30 shares
New avg cost: Rs. 933.33

Price drops:   Rs. 700 (-30%)

LADDER #2: Buy 10 more @ Rs. 700 = Rs. 7,000
New position: 40 shares
New avg cost: Rs. 850.00
Total invested: Rs. 33,000

Price recovers: Rs. 1,000 (+17.6% from avg)
Exit 40 shares @ Rs. 1,000
Total proceeds: Rs. 40,000
Profit: Rs. 7,000 (+21.2%)
```

### Scenario D: Stock Crashes (Hard Stop)
```
Bought:        10 shares @ Rs. 1,000 = Rs. 10,000
Price drops:   Rs. 900 (-10%)

HARD STOP TRIGGERS!
Sell all 10 shares @ Rs. 900
Proceeds: Rs. 9,000
Loss: Rs. 1,000 (-10%)
Position: CLOSED - Loss protected at exactly -10%
```

---

## Monthly Monitoring Checklist

Every week/day during market hours:

- [ ] Record current NABIL price
- [ ] Check if any triggers are near (20%, 30% drops, +10% gain)
- [ ] Review position P&L
- [ ] Verify trailing stop level (if active)
- [ ] Check execution history

Every month:

- [ ] Review all executions and P&L
- [ ] Adjust strategy if market conditions change
- [ ] Re-evaluate ladder-in levels if price structure changes
- [ ] Document lessons learned

---

## Key Numbers to Remember

| Component | Value |
|-----------|-------|
| **Initial Shares** | 10 |
| **Hard Stop Loss** | -10% |
| **Hard Stop Price** | Rs. 900 (assumed entry Rs. 1,000) |
| **Trailing Activation** | +10% gain |
| **Trailing Stop Step** | 5% |
| **Ladder 1 Trigger** | 20% drop → Buy 20 more |
| **Ladder 2 Trigger** | 30% drop → Buy 10 more |
| **Max Position** | 40 shares (if all ladder levels trigger) |
| **Best Case Profit** | Unlimited (stock keeps rising) |
| **Worst Case Loss** | -10% (hard stop protects you) |

---

## When to Adjust the Strategy

**Make it MORE AGGRESSIVE if:**
- You have high risk tolerance
- Market is bullish and volatile
- Historical data shows strong recoveries after drops

**Make it MORE CONSERVATIVE if:**
- You want to limit losses further (-5% instead of -10%)
- Market is uncertain
- You can't monitor constantly

---

## Questions to Ask Yourself Before Starting

1. **Q: Can I afford to lose Rs. 1,000 (-10% of initial Rs. 10,000)?**
   A: If not, reduce initial position size.

2. **Q: Will I have time to monitor and confirm orders?**
   A: Strategy needs user confirmation for each order.

3. **Q: Do I believe in NABIL long-term?**
   A: Ladder-in only works if you expect recovery.

4. **Q: What if both ladder levels trigger?**
   A: You'll have 40 shares with avg cost Rs. 850. You need capital for this.

5. **Q: Can I access the platform during market hours?**
   A: Yes, strategy requires monitoring prices and confirming orders.

---

## Files in Your Project

- `src/bot/trailing_stop_strategy.py` - Core strategy implementation
- `test_trailing_stop.py` - Demo with simulated price movements
- `NABIL_STRATEGY_INTEGRATION.md` - How to integrate with trading bot
- `NABIL_TRAILING_STOP_SUMMARY.md` - This file

---

## Next Steps

1. **Review:** Confirm all parameters match your risk tolerance
2. **Test:** Run `python test_trailing_stop.py` to see scenarios
3. **Integrate:** Connect strategy to your Trader class
4. **Paper Trade:** Test with simulated prices before real money
5. **Monitor:** Track all orders and P&L regularly

---

**Ready to start? Let me know if you want to:**
- Adjust any parameters
- See different price scenarios
- Integrate with your actual trading bot
- Create automated price monitoring

