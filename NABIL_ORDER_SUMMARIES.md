# NABIL Strategy - Example Order Summaries

When a trading trigger occurs, here's exactly what you'll see before execution.

---

## Example 1: Initial Buy Order

**Scenario:** You're starting the strategy at current market price

```
================================================================================
                    ORDER SUMMARY - PLEASE CONFIRM                        
================================================================================

CURRENT POSITION STATE:
────────────────────────────────────────────────────────────────────────────────
Symbol:              NABIL
Current Price:       Rs. 1,000.00
Position Size:       0 shares (Not yet bought)
Avg Entry Price:     N/A
Position P&L:        N/A
Stop Loss Level:     Rs. 900.00 (will be active after entry)
Highest Price Seen:  Rs. 1,000.00
Trailing Stop Active: NO

PENDING ORDERS TO EXECUTE:
────────────────────────────────────────────────────────────────────────────────

Order #1: BUY_INITIAL
  Symbol:          NABIL
  Quantity:        10 shares
  Order Price:     1000.00
  Reason:          Initial position entry
  Trigger:         Manual order placement
  Position Change: 0.00%

================================================================================
STRATEGY PARAMETERS:
────────────────────────────────────────────────────────────────────────────────
Hard Stop Loss:      10% (Rs. 900.00)
Trailing Activation: +10% (Rs. 1,100.00)
Trailing Step:       5% (moves up as price rises)
Ladder-in Triggers:  {20: 20, 30: 10}

================================================================================
EXECUTION HISTORY:
────────────────────────────────────────────────────────────────────────────────
No executed orders yet

================================================================================

⚠️  USER CONFIRMATION REQUIRED
Press Enter to execute (or Ctrl+C to cancel)

→ Your action: PRESS ENTER to buy 10 shares @ Rs. 1,000
                OR Ctrl+C to cancel
```

---

## Example 2: Ladder-In Trigger (20% Drop)

**Scenario:** Price has dropped to Rs. 800 (20% below entry)

```
================================================================================
                    ORDER SUMMARY - PLEASE CONFIRM                        
================================================================================

CURRENT POSITION STATE:
────────────────────────────────────────────────────────────────────────────────
Symbol:              NABIL
Current Price:       Rs. 800.00
Position Size:       10 shares (from earlier entry)
Avg Entry Price:     Rs. 1,000.00
Position P&L:        -20.00% (-Rs. 2,000 unrealized)
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

📊 What happens if you confirm:
   • Current holding:  10 shares @ Rs. 1,000.00 avg = Rs. 10,000
   • New purchase:     20 shares @ Rs. 800.00     = Rs. 16,000
   • New position:     30 shares total
   • New avg cost:     Rs. 933.33
   • New stop loss:    Rs. 840.00 (10% below average)
   • Investment:       Rs. 26,000 total

================================================================================
STRATEGY PARAMETERS:
────────────────────────────────────────────────────────────────────────────────
Hard Stop Loss:      10% (Rs. 900.00 for original entry)
Trailing Activation: +10% (Rs. 1,100.00)
Trailing Step:       5% (moves up as price rises)
Ladder-in Triggers:  {20: 20 ← YOU'RE HERE, 30: 10}

================================================================================
EXECUTION HISTORY:
────────────────────────────────────────────────────────────────────────────────

Execution #1:
  Type................ BUY_INITIAL
  Symbol.............. NABIL
  Quantity............ 10
  Limit Price......... Rs. 1,000.00
  Reason.............. Initial position entry
  Position Change..... 0.00%
  Trigger............. Manual order placement
  Status.............. EXECUTED
  Execution Price..... Rs. 1,000.00
  Total Value......... Rs. 10,000.00
  Timestamp........... 2026-04-28 14:30:00

================================================================================

⚠️  USER CONFIRMATION REQUIRED
You're buying 20 more shares to average down your position.

→ Your action: PRESS ENTER to buy 20 shares @ Rs. 800
                OR Ctrl+C to cancel and wait
```

---

## Example 3: Ladder-In Trigger (30% Drop)

**Scenario:** Price continues down to Rs. 700 (30% below entry)

```
================================================================================
                    ORDER SUMMARY - PLEASE CONFIRM                        
================================================================================

CURRENT POSITION STATE:
────────────────────────────────────────────────────────────────────────────────
Symbol:              NABIL
Current Price:       Rs. 700.00
Position Size:       30 shares (10 initial + 20 ladder)
Avg Entry Price:     Rs. 933.33
Position P&L:        -25.00% (-Rs. 7,000 unrealized)
Stop Loss Level:     Rs. 840.00
Highest Price Seen:  Rs. 1,050.00
Trailing Stop Active: NO

PENDING ORDERS TO EXECUTE:
────────────────────────────────────────────────────────────────────────────────

Order #1: BUY_LADDER
  Symbol:          NABIL
  Quantity:        10 shares
  Order Price:     700.00
  Reason:          Ladder-in at 30% price drop
  Trigger:         Price 700.00 <= Trigger 700.00
  Position Change: -25.00%

📊 What happens if you confirm:
   • Current holding:  30 shares @ Rs. 933.33 avg = Rs. 28,000
   • New purchase:     10 shares @ Rs. 700.00    = Rs. 7,000
   • New position:     40 shares total
   • New avg cost:     Rs. 850.00
   • New stop loss:    Rs. 765.00 (10% below average)
   • Total investment: Rs. 35,000

⚠️  WARNING: You're now investing Rs. 35,000 total
   Make sure you have capital for this!

================================================================================
STRATEGY PARAMETERS:
────────────────────────────────────────────────────────────────────────────────
Hard Stop Loss:      10% (Rs. 900.00 for original entry)
Trailing Activation: +10% (Rs. 1,100.00)
Trailing Step:       5% (moves up as price rises)
Ladder-in Triggers:  {20: 20 ✓ DONE, 30: 10 ← YOU'RE HERE}

================================================================================
EXECUTION HISTORY:
────────────────────────────────────────────────────────────────────────────────

Execution #1:
  Type................ BUY_INITIAL
  Symbol.............. NABIL
  Position Change..... 0.00%
  Status.............. EXECUTED
  Execution Price..... Rs. 1,000.00
  Total Value......... Rs. 10,000.00

Execution #2:
  Type................ BUY_LADDER
  Symbol.............. NABIL
  Position Change..... -20.00%
  Status.............. EXECUTED
  Execution Price..... Rs. 800.00
  Total Value......... Rs. 16,000.00

================================================================================

⚠️  USER CONFIRMATION REQUIRED
You're adding the last ladder level - 10 more shares @ Rs. 700

→ Your action: PRESS ENTER to buy 10 shares @ Rs. 700
                OR Ctrl+C to cancel (hold current 30 shares)
```

---

## Example 4: Trailing Stop Activation (Price Rises)

**Scenario:** Price rises from Rs. 1,000 to Rs. 1,100 (+10% gain)

```
================================================================================
                    ORDER SUMMARY - PLEASE CONFIRM                        
================================================================================

CURRENT POSITION STATE:
────────────────────────────────────────────────────────────────────────────────
Symbol:              NABIL
Current Price:       Rs. 1,100.00
Position Size:       10 shares
Avg Entry Price:     Rs. 1,000.00
Position P&L:        +10.00% (+Rs. 1,000 unrealized)
Stop Loss Level:     Rs. 1,045.00 ← TRAILING STOP NOW ACTIVE
Highest Price Seen:  Rs. 1,100.00
Trailing Stop Active: YES

PENDING ORDERS TO EXECUTE:
────────────────────────────────────────────────────────────────────────────────
None currently - Trailing Stop is now protecting your profits

📊 What just happened:
   • Your 10 shares were worth Rs. 10,000 (entry)
   • Now worth Rs. 11,000 (+Rs. 1,000 profit)
   • TRAILING STOP ACTIVATED! ✓
   • Trailing stop set at: Rs. 1,045 (5% below current Rs. 1,100)
   • You will be sold if price drops to Rs. 1,045 or below
   • But if price keeps rising, stop will move up too!

📈 What happens next:
   
   If price rises to Rs. 1,120 → Stop moves up to Rs. 1,064
   If price rises to Rs. 1,150 → Stop moves up to Rs. 1,092.50
   If price drops to Rs. 1,040 → AUTO SELL (trailing stop hit)

================================================================================
STRATEGY PARAMETERS:
────────────────────────────────────────────────────────────────────────────────
Hard Stop Loss:      10% (Rs. 900.00 = not active, trailing is better)
Trailing Activation: +10% ✓ ACTIVE (Rs. 1,100.00)
Trailing Step:       5% (moves up as price rises)
Ladder-in Triggers:  {20: 20, 30: 10}

================================================================================
EXECUTION HISTORY:
────────────────────────────────────────────────────────────────────────────────

Execution #1:
  Type................ BUY_INITIAL
  Symbol.............. NABIL
  Status.............. EXECUTED
  Execution Price..... Rs. 1,000.00
  Total Value......... Rs. 10,000.00

================================================================================

ℹ️  NO ACTION NEEDED - Just monitoring now

Your position is protected:
  • Minimum exit: Rs. 1,045 (if price drops)
  • If price rises more, your stop moves up too!
  • You're letting profits run with downside protection

→ Your action: Nothing needed. Strategy is monitoring.
              Press Ctrl+C anytime to manually close position.
```

---

## Example 5: Trailing Stop Execution (Sell Order)

**Scenario:** Price rose to Rs. 1,150, then drops back to Rs. 1,092.50 (below trailing stop)

```
================================================================================
                    ORDER SUMMARY - PLEASE CONFIRM                        
================================================================================

CURRENT POSITION STATE:
────────────────────────────────────────────────────────────────────────────────
Symbol:              NABIL
Current Price:       Rs. 1,092.50
Position Size:       10 shares
Avg Entry Price:     Rs. 1,000.00
Position P&L:        +9.25% (+Rs. 925 unrealized)
Stop Loss Level:     Rs. 1,092.50 ← YOU'RE AT THE STOP LEVEL!
Highest Price Seen:  Rs. 1,150.00
Trailing Stop Active: YES

PENDING ORDERS TO EXECUTE:
────────────────────────────────────────────────────────────────────────────────

Order #1: SELL_TRAILING
  Symbol:          NABIL
  Quantity:        10 shares
  Order Price:     1,092.50
  Reason:          Trailing stop protection
  Trigger:         Price 1,092.50 <= Stop 1,092.50
  Position Change: +9.25%

📊 Exit Summary:
   • Entry:        10 shares @ Rs. 1,000.00 = Rs. 10,000
   • Exit:         10 shares @ Rs. 1,092.50 = Rs. 10,925
   • Profit:       Rs. 925 (+9.25%) ✓
   • Highest high:  Rs. 1,150.00 (+15%)
   • Exit reason:   Trailing stop hit (price came down 5%)

================================================================================
STRATEGY PARAMETERS:
────────────────────────────────────────────────────────────────────────────────
Hard Stop Loss:      10% (Rs. 900.00)
Trailing Activation: +10% (Rs. 1,100.00) ✓ WAS ACTIVE
Trailing Step:       5% (moved up as price rose)
Ladder-in Triggers:  {20: 20, 30: 10}

================================================================================
EXECUTION HISTORY:
────────────────────────────────────────────────────────────────────────────────

Execution #1:
  Type................ BUY_INITIAL
  Execution Price..... Rs. 1,000.00
  Status.............. EXECUTED

Execution #2:
  Type................ SELL_TRAILING
  Execution Price..... Rs. 1,092.50
  Status.............. EXECUTED
  P&L:................. +Rs. 925 (9.25%)

================================================================================

✅ TRADE COMPLETE - Profit Secured!

Your trailing stop worked perfectly:
  • You caught the upside (from Rs. 1,000 to Rs. 1,150)
  • You exited with profit (Rs. 925 gain)
  • Protection kicked in when price dropped

→ Your action: PRESS ENTER to confirm sale execution
              OR Ctrl+C to cancel and hold for higher price
```

---

## Example 6: Hard Stop Loss (Worst Case)

**Scenario:** Market crashes and price hits Rs. 900.00 (hard stop)

```
================================================================================
                    ORDER SUMMARY - PLEASE CONFIRM                        
================================================================================

CURRENT POSITION STATE:
────────────────────────────────────────────────────────────────────────────────
Symbol:              NABIL
Current Price:       Rs. 900.00
Position Size:       10 shares
Avg Entry Price:     Rs. 1,000.00
Position P&L:        -10.00% (-Rs. 1,000 unrealized)
Stop Loss Level:     Rs. 900.00 ← YOU'VE HIT THE HARD FLOOR!
Highest Price Seen:  Rs. 1,050.00
Trailing Stop Active: NO (hard stop takes priority)

PENDING ORDERS TO EXECUTE:
────────────────────────────────────────────────────────────────────────────────

Order #1: SELL_STOP
  Symbol:          NABIL
  Quantity:        10 shares
  Order Price:     900.00
  Reason:          Hard stop loss at -10%
  Trigger:         Price 900.00 <= Stop 900.00
  Position Change: -10.00%

⚠️  HARD STOP TRIGGERED - POSITION CLOSING AT LOSS

📊 Exit Summary:
   • Entry:        10 shares @ Rs. 1,000.00 = Rs. 10,000
   • Exit:         10 shares @ Rs. 900.00   = Rs. 9,000
   • Loss:         -Rs. 1,000 (-10.00%) ✓ LIMITED
   • Why:          Hard stop protected maximum loss

✓ Good news: Your loss is LIMITED to exactly -10%!
  If price keeps dropping to Rs. 850 or Rs. 700, you're already out.

================================================================================
STRATEGY PARAMETERS:
────────────────────────────────────────────────────────────────────────────────
Hard Stop Loss:      10% (Rs. 900.00) ← PROTECTING YOU RIGHT NOW
Trailing Activation: +10% (Rs. 1,100.00)
Trailing Step:       5%
Ladder-in Triggers:  {20: 20, 30: 10}

================================================================================
EXECUTION HISTORY:
────────────────────────────────────────────────────────────────────────────────

Execution #1:
  Type................ BUY_INITIAL
  Status.............. EXECUTED
  Execution Price..... Rs. 1,000.00

Execution #2:
  Type................ SELL_STOP
  Status.............. EXECUTED
  Execution Price..... Rs. 900.00
  P&L:................. -Rs. 1,000 (-10.00%)

================================================================================

⚠️  STOP LOSS EXECUTED - POSITION CLOSED

Your strategy did its job:
  • Market dropped 10%+ unexpectedly
  • Hard stop protected your downside
  • Loss limited to exactly -10%

Next steps:
  → You can restart strategy when market stabilizes
  → Or adjust parameters and try a different stock

→ Your action: PRESS ENTER to confirm sale execution
              POSITION WILL BE CLOSED.
```

---

## Key Takeaways from Order Summaries

### What You'll See:
✓ **Position State** - Current shares, entry price, P&L  
✓ **Pending Orders** - What action the strategy wants to take  
✓ **What Happens If You Confirm** - New totals after execution  
✓ **Execution History** - All past orders and P&L  
✓ **Strategy Parameters** - Current active triggers  

### Before You Confirm:
1. **Read the reason** - Why is this order happening?
2. **Check the math** - Does the P&L calculation make sense?
3. **Verify quantities** - Are you OK with buying/selling this many?
4. **Check capital** - Do you have funds for a buy order?
5. **Make a decision** - PRESS ENTER (confirm) or Ctrl+C (cancel)

### After You Confirm:
- Order is EXECUTED immediately
- Strategy continues to monitor
- Next price update will show new position

---

## Common Questions About Summaries

**Q: Can I cancel an order after seeing the summary?**  
A: YES! Press Ctrl+C before pressing Enter. Order won't execute.

**Q: What if price changes between updates?**  
A: The summary shows prices at analysis time. Market may have moved slightly.

**Q: Do I have to confirm every order?**  
A: YES. This prevents accidental trades. You must press Enter for each order.

**Q: How often will I see summaries?**  
A: Only when a trigger fires (ladder, trailing stop, hard stop). Otherwise just monitoring.

**Q: Can I modify the order quantities?**  
A: Current system: No. You either execute or cancel. Future enhancement could add this.

**Q: What if I'm not available to confirm?**  
A: You should stay near the terminal. The strategy waits for your confirmation.

