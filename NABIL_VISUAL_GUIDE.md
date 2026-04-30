# NABIL Strategy - Visual Guide

## Strategy Components at a Glance

```
                        NABIL TRAILING STOP STRATEGY
                    ════════════════════════════════════════
                                    
                              BUY: 10 SHARES
                           at current market price
                                    ↓
                    ────────────────────────────────
                    │                              │
                    │   POSITION: 10 SHARES      │
                    │   ENTRY: Rs. 1,000         │
                    │   STOP: Rs. 900 (Hard)     │
                    │                            │
                    └────────────────────────────
                                    ↓
                    
                ┌───────────────────────────────────┐
                │   CONTINUOUS PRICE MONITORING     │
                │   Every price update analyzed     │
                └───────────────────────────────────┘
                                    ↓
        ┌───────────────────────────┼──────────────────────────┐
        │                           │                          │
        ↓                           ↓                          ↓
    PRICE DOWN?              PRICE FLAT?                  PRICE UP?
        │                       │                          │
        │                       │                          │
        ↓                       ↓                          ↓
    
    ┌──────────────────┐   ┌──────────────┐   ┌─────────────────────┐
    │  DROP -10%?      │   │  HOLD        │   │  GAIN +10%?         │
    │ (Rs. 900 hit)    │   │  No action   │   │ (Rs. 1,100 hit)     │
    │                  │   │              │   │                     │
    │ ✓ YES: SELL ALL  │   │ CONTINUE     │   │ ✓ YES:              │
    │                  │   │ MONITORING   │   │ ACTIVATE TRAILING   │
    │ ✗ NO: CONTINUE   │   │              │   │                     │
    │                  │   │              │   │ Stop becomes:       │
    │ P&L: -10% LOSS   │   │              │   │ 95% of price        │
    │ Position: CLOSED │   │              │   │                     │
    │                  │   │              │   │ Follow price up but  │
    │ ═══════════════  │   │ ═════════════│   │ never down!         │
    │ TRADE DONE       │   │             │   │                     │
    │ (Protected loss) │   │             │   │ Stop = 95% × price  │
    └──────────────────┘   │             │   └─────────────────────┘
                           │             │            ↓
                           │ ┌───────────┴─────────────┐
                           │ │  DROP 20% or 30%?      │
                           │ │  (from entry)          │
                           │ │                        │
                           │ │ 20%: Buy 20 more       │
                           │ │ 30%: Buy 10 more       │
                           │ │                        │
                           │ └────────────────────────┘
                           │
                           └─→ CONTINUE HOLDING & MONITORING
```

---

## Price Scenarios - Visual Timeline

### Scenario 1: Price Rises Then Falls (Trailing Stop)

```
Price    History & Action
│
│  1150    ╔═══════════════════════════════════════════════╗
│          ║ PEAK REACHED (+15%)                          ║
│          ║ Stop moves to: 1,092.50 (95% of 1,150)      ║
│          ╚═══════════════════════════════════════════════╝
│           ▲
│  1130     |
│           |       ┌─────────────────────────────────────┐
│  1120     |       │ TRAILING ACTIVATED at 1,100        │
│           |       │ Stop = 1,045 (95% of 1,100)        │
│           |       │                                    │
│  1100     |       │ Stop RATCHETS UP each time        │
│           |       │ price rises                       │
│           |       └─────────────────────────────────────┘
│  1050     |
│  1000 ────┼──────────── ENTRY POINT (10 shares)
│  950      |
│  900      ●─────●─────●────────────── HARD STOP (10% loss limit)
│  850      
│
└──────────────────────────────────────────────────────────→ Time
  Entry           Up Phase              Down Phase     Exit
                                        @ Trailing    (Rs. 1,092.50)
                                        Stop Hit
```

### Scenario 2: Price Drops (Ladder-In)

```
Price    Ladder Purchases & Position
│
│  1,000  ┌─────────────────────────────────────────┐
│         │ ENTRY: Buy 10 shares                   │
│  950    │ at Rs. 1,000                          │
│  900    │ Price is 90% of entry (hold)          │
│  850    └─────────────────────────────────────────┘
│
│         ┌─────────────────────────────────────────┐
│  800    │ LADDER #1: Price = Rs. 800 (-20%)    │
│  │      │ Action: BUY 20 more                  │
│  │      │ Now have: 30 shares                  │
│  │      │ Avg cost: Rs. 933                    │
│  │      └─────────────────────────────────────────┘
│  │
│  700    ┌─────────────────────────────────────────┐
│  │      │ LADDER #2: Price = Rs. 700 (-30%)   │
│  │      │ Action: BUY 10 more                  │
│  │      │ Now have: 40 shares                  │
│  │      │ Avg cost: Rs. 850                    │
│  │      └─────────────────────────────────────────┘
│  │
│  650    │
│  600    │ (Could keep falling, but you own 40  │
│  │      │  shares at lower average cost)       │
│  │      │ HARD STOP: Rs. 765 (10% below avg)   │
│  │
│
└────────────────────────────────────────────────────→ Time
  Entry   -5%  -10%   -15%  -20% DROP  -25%  -30% DROP
              (Hold)        (Ladder 1)       (Ladder 2)
                                              ↓
                                         Max portfolio: 40 shares
```

### Scenario 3: Crash Protection (Hard Stop)

```
Price    Hard Stop Protection
│
│  1,050  ╱─╲
│         │  ╲
│  1,000  │   ╲ ENTRY: Buy 10 shares
│         │    ╲ at Rs. 1,000
│    950  │     ╲ (Still holding)
│         │      ╲
│    900  ●───────● HARD STOP: -10%
│         │    🛑 CRASH!
│         │    │ Sell all 10 shares
│         │    │ at Rs. 900
│         │    │ Loss: -Rs. 1,000 (-10%)
│    850  │    │ Position: CLOSED
│         │    │ Protected! Could drop to 700
│    800  │    │ but you're already out
│         │    │
│    750  │    ↓ (You don't own anymore)
│
│    700  
│    650  
│         
│ (Stock crashes further but✓ you're protected)
│
│    500
│
└─────────────────────────────────────────────→ Time
  Entry   Normal   Market Crisis    Stock bottoms
  Point   Trading  Unexpected      (You weren't harmed)
          Happens  Crash
          (Hold)   (STOP SAVES YOU)
```

---

## Decision Tree - What Happens at Each Price

```
                            ┌─ CURRENT PRICE ─┐
                            │   of NABIL      │
                            └────────┬────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
            
        Price < 900.00        900 ≤ Price ≤ 1100   Price > 1100.00
        (Hard Stop)           (Holding)            (Trailing Active)
                │                   │                      │
                │                   │                      │
          ┌─────▼─────┐         ┌───▼────┐          ┌──────▼──────┐
          │            │        │ ACTION │          │             │
          │ DECISION   │        │        │          │ Stop moves  │
          │ SELL ALL   │        │ HOLD   │          │ up by 5%    │
          │ 10 shares  │        │        │          │             │
          │            │        │ Check: │          │ If price    │
          │ P&L: -10%  │        │ • Drop │          │ drops below │
          │            │        │   20%? │          │ stop:       │
          │ Position   │        │   BUY  │          │ SELL        │
          │ CLOSED ✓   │        │   20   │          │             │
          │            │        │        │          │ P&L: PROFIT │
          └────────────┘        │ • Drop │          │             │
          STOP LOSS             │   30%? │          └─────────────┘
          EXECUTED              │   BUY  │          TRAILING STOP
          (Protected)           │   10   │          (Profit locked)
                                │        │
                                └───┬────┘
                                    │
                             ┌──────┴──────┐
                             │   CONTINUE  │
                             │ MONITORING  │
                             │   PRICES    │
                             └─────────────┘
```

---

## Position Size Evolution

```
                POTENTIAL POSITION GROWTH
        ═══════════════════════════════════════

Initial Entry:        10 shares @ Rs. 1,000 = Rs. 10,000
                      ↓
                ┌─────────────┐
                │             │
                ↓             ↓
            No Drop      20% Drop
                         (Ladder 1)
                │             │
                │             ├─→ +20 shares @ Rs. 800 = Rs. 16,000
                │
                │         ┌─────────────┐
                │         │             │
                │         ↓             ↓
                │     No More       30% Drop
                │     Drops         (Ladder 2)
                │         │             │
                │         │             └─→ +10 shares @ Rs. 700 = Rs. 7,000
                │         │
                │         └─→ 30 shares total (if only Ladder 1 triggers)
                │
                └──────────────→ 10 shares (if no drops)

FINAL POSITIONS POSSIBLE:

├─ 10 shares (No ladders triggered)
├─ 30 shares (Only 20% drop triggered - Ladder 1)
└─ 40 shares (Both 20% & 30% drops triggered - Ladder 1 + 2)

COST BASIS FOR EACH:

├─ 10 shares @ Rs. 1,000 avg = Rs. 10,000 total invested
├─ 30 shares @ Rs. 933 avg = Rs. 28,000 total invested
└─ 40 shares @ Rs. 850 avg = Rs. 34,000 total invested
```

---

## Monthly Action Checklist

```
┌─────────────────────────────────────────────────────┐
│         WEEKLY TRADING MONITORING                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ☐ Check current NABIL price                       │
│ ☐ Review position P&L                             │
│ ☐ Verify current stop level                       │
│ ☐ Note any new price highs                        │
│ ☐ Note any price approaches to stops              │
│ ☐ Confirm all pending order summaries reviewed    │
│                                                     │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│         MONTHLY POSITION REVIEW                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│ ☐ Total P&L for the month                         │
│ ☐ Trades executed and outcomes                    │
│ ☐ Were all ladder levels triggered? Why/why not? │
│ ☐ Strategy working as expected?                   │
│ ☐ Any parameter adjustments needed?               │
│ ☐ Document lessons learned                        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Stop Loss Levels Cheat Sheet

```
IF ENTRY PRICE IS:        HARD STOP (10% Drop is):   TRAILING (if +10%):
                          
Rs. 900                   Rs. 810                    Rs. 945 (@ 1% gain)
Rs. 950                   Rs. 855                    Rs. 997 (@ 1% gain)
Rs. 1,000 ← YOUR ENTRY    Rs. 900 ← YOUR STOP       Rs. 1,045 (@ 10% gain)
Rs. 1,050                 Rs. 945                    Rs. 1,097 (@ 10% gain)
Rs. 1,100                 Rs. 990                    Rs. 1,155 (@ 10% gain)
Rs. 1,200                 Rs. 1,080                  Rs. 1,260 (@ 10% gain)


LADDER-IN PRICES (From Rs. 1,000 entry):

20% DROP:          30% DROP:
Rs. 800 ← Buy 20   Rs. 700 ← Buy 10
```

---

## Risk/Reward Summary

```
┌──────────────────────────────────────────────────────────┐
│                   RISK vs REWARD                         │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  🛑 WORST CASE (Hard Stop Triggers):                    │
│     Entry:    10 shares @ Rs. 1,000 = Rs. 10,000       │
│     Exit:     10 shares @ Rs. 900 = Rs. 9,000           │
│     Loss:     -Rs. 1,000 (-10%)                         │
│     Status:   PROTECTED ✓ (Can't lose more)            │
│                                                          │
│  ─ NEUTRAL CASE (Position Flat):                       │
│     Entry:    10 shares @ Rs. 1,000 = Rs. 10,000       │
│     Price:    Still around Rs. 1,000                    │
│     P&L:      ~Rs. 0                                    │
│     Decision: Hold or manually exit                    │
│                                                          │
│  🌟 BEST CASE (Strong Rally):                          │
│     Entry:    10 shares @ Rs. 1,000 = Rs. 10,000       │
│     Peak:     Rs. 1,150 (+15%)                          │
│     Exit:     Trailing stop @ Rs. 1,100                │
│     Profit:   +Rs. 1,000 (+10%) minimum                │
│     Status:   Profits captured ✓                       │
│                                                          │
│  🪜 ACCUMULATION CASE (Sharp Drop then Recovery):      │
│     Entry:    10 @ Rs. 1,000 = Rs. 10,000              │
│     Ladder 1: 20 @ Rs. 800 = Rs. 16,000                │
│     Ladder 2: 10 @ Rs. 700 = Rs. 7,000                 │
│     Total:    40 shares @ Rs. 850 avg = Rs. 34,000    │
│     Exit:     @ Rs. 1,000 (+17.6% from avg)           │
│     Profit:   +Rs. 6,000 (18%)                         │
│     Status:   Strong gains from averaging ✓            │
│                                                          │
└──────────────────────────────────────────────────────────┘

                      KEY INSIGHT:
         You're Protected on Downside (Hard Stop)
         But Can Profit on Upside (Trailing Stop)
                  The Best of Both Worlds
```

---

## Quick Decision Guide

```
PRICE ACTION                     WHAT STRATEGY DOES         YOUR ACTION
─────────────────────────────────────────────────────────────────────────
Price is stable                  Nothing (monitoring)       Watch prices
around entry

Price rises to +10%              Activate trailing stop     Watch - you're
                                                            protected

Price rises further              Move stop up 5%            Watch for 
to +12%, +15%                    Keep chasing price         exit signal

Price drops from high            Hit trailing stop          Sell signal -
to -5% from peak                                            Confirm & exit
                                                            with profit

Price drops to -10%              Hit hard stop              Emergency sell
from entry                                                  Confirm to close
                                                            at loss limit

Price drops 20%                  Trigger ladder 1           Confirm to buy
                                                            20 more shares

Price continues down             Trigger ladder 2           Confirm to buy
to -30%                                                     10 more shares

Position still holds             None                       Can hold indefinitely
after ladder purchases                                      or manually close
```

---

## Remember

```
╔════════════════════════════════════════════════════════════╗
║                   STRATEGY PRINCIPLES                      ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  1. HARD STOP: Your loss is NEVER more than -10%         ║
║     ✓ You are protected from catastrophic losses         ║
║                                                            ║
║  2. TRAILING STOP: Your profits are LOCKED IN            ║
║     ✓ Stop only moves Up, never Down                     ║
║                                                            ║
║  3. LADDER-IN: You profit from weakness                  ║
║     ✓ Buy dips to reduce average cost                    ║
║     ✓ Profit more when price rebounds                    ║
║                                                            ║
║  4. CONFIRMATION: You control all orders                 ║
║     ✓ Every trade requires your approval                 ║
║     ✓ You can cancel any order                           ║
║                                                            ║
║  5. MONITORING: The strategy waits for you                ║
║     ✓ Triggers don't execute automatically               ║
║     ✓ You have time to review summaries                  ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

