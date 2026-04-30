# Weekly Top Stocks Buyer - Implementation Summary

## ✅ What Was Built

### 1. Market Analyzer Module (`src/bot/market_analyzer.py`)

**Purpose:** Fetches and analyzes NEPSE market data to identify trending stocks

**Key Features:**
- Fetches real-time data for ALL stocks from ShareSansar or NEPSE
- Multiple selection methods:
  - **Volume-based:** Top stocks by trading volume
  - **Gainers-based:** Top stocks by price gain
  - **Combined:** Balanced scoring (60% volume + 40% momentum)
- Generates detailed market analysis reports
- Filters stocks by minimum volume threshold

**Main Methods:**
```python
analyzer = MarketAnalyzer()
analyzer.fetch_all_stocks_data(source="sharesansar")
analyzer.get_top_stocks_combined(top_n=3, min_volume=10000)
```

---

### 2. Weekly Buyer Module (`src/bot/weekly_buyer.py`)

**Purpose:** Automatically purchases top 3 stocks once per week

**Key Features:**
- Analyzes market and selects top 3 stocks
- Executes purchases on scheduled day/time (e.g., Wednesday 12:00)
- Tracks purchase history and portfolio state
- Manages multiple stock positions simultaneously
- Persists portfolio to disk for recovery
- Generates comprehensive performance reports

**Main Methods:**
```python
buyer = WeeklyTopStocksBuyer(
    capital_per_stock=10000.0,
    buy_day="wednesday",
    buy_time="12:00"
)
buyer.start()  # Runs continuously
```

---

### 3. Demo Script (`demo_weekly_buyer.py`)

**Purpose:** Interactive demo showing how to use the weekly buyer

**Features:**
- User-friendly prompts for configuration
- Real-time market analysis display
- Shows which top 3 stocks will be purchased
- Starts automated weekly buying
- All activity logged to `logs/weekly_buyer.log`

**Run with:**
```bash
python3 demo_weekly_buyer.py
```

---

### 4. Test Script (`test_weekly_buyer.py`)

**Purpose:** Quick test without executing purchases

**Features:**
- Fetches and displays market data
- Shows top 5 by volume
- Shows top 5 gainers
- Shows top 3 for weekly purchase
- Perfect for testing before full deployment

**Run with:**
```bash
python3 test_weekly_buyer.py
```

---

### 5. Comprehensive Guide (`WEEKLY_BUYER_GUIDE.md`)

**Purpose:** Complete documentation and usage guide

**Sections:**
- How the system works
- Three selection methods explained
- Quick start instructions
- Configuration options
- File structure
- Viewing results
- Advanced customization
- Performance tracking
- Risk management
- Troubleshooting
- Example workflows

---

## 🎯 Core Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. LAUNCH WEEKLY BUYER                                          │
│    python3 demo_weekly_buyer.py                                 │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. ANALYZE MARKET (Every hour)                                  │
│    • Fetch data for 200+ stocks from ShareSansar              │
│    • Calculate combined scores (volume + momentum)            │
│    • Display top 3 stocks                                     │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. WAIT FOR PURCHASE TIME (Wednesday 12:00)                    │
│    • System checks current day and time                       │
│    • Continues monitoring market trends                       │
│    • Updates top 3 stocks hourly                             │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. EXECUTE WEEKLY PURCHASES                                     │
│    • Buy top 3 stocks: Rs. 10,000 each                        │
│    • Log all transactions                                     │
│    • Update portfolio                                        │
│    • Track P&L                                               │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. MONITOR & REPORT                                             │
│    • Continue market analysis                                 │
│    • Track position values                                   │
│    • Generate performance reports                           │
│    • Ready for next week's purchase                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Selection Methodology

### Three Available Methods

#### 1. Volume-Based Selection
```
What: Stocks with highest trading volume today
Why: High volume = market interest & liquidity
When to use: When you want liquid, active stocks
Example: NABIL (500K) > EBL (400K) > GUFL (300K)
```

#### 2. Gainers-Based Selection
```
What: Stocks with highest positive price change today
Why: Positive momentum = uptrend indication
When to use: When you want trending stocks
Example: Stock +5% > Stock +3.5% > Stock +2%
```

#### 3. Combined Selection (DEFAULT)
```
What: Balanced score using both volume and momentum
Why: Combines market interest + positive momentum
When to use: Balanced, long-term strategy (RECOMMENDED)

Score = (Volume Rank × 0.6) + (Momentum Rank × 0.4)

Why 60/40?: Volume is more stable, momentum can be volatile
Result: Stocks with high activity AND positive direction
```

---

## 🚀 Quick Start

### Step 1: Test Market Analyzer (No Purchases)
```bash
python3 test_weekly_buyer.py
```
Output shows top 3 stocks to be purchased based on current market data.

### Step 2: Run Demo (With Automatic Purchases)
```bash
python3 demo_weekly_buyer.py
```
- Enter capital amount (e.g., Rs. 10,000 per stock)
- Choose purchase day (e.g., Wednesday)
- System waits for scheduled time and buys automatically

### Step 3: Monitor Results
```bash
# View logs in real-time
tail -f logs/weekly_buyer.log

# View portfolio state
cat logs/weekly_portfolio.json | python -m json.tool

# View final report
tail -50 logs/weekly_buyer.log
```

---

## 💾 Output Files

### 1. `logs/weekly_buyer.log`
```
2026-04-29 12:00:45 - INFO - WEEKLY TOP STOCKS BUYER INITIALIZED
2026-04-29 12:01:30 - INFO - Fetched data for 234 stocks from ShareSansar
2026-04-29 12:01:45 - INFO - TOP 3 TRENDING STOCKS (Combined Score)
2026-04-29 12:01:45 - INFO - 1. EBL (Score: 0.890)
2026-04-29 12:01:45 - INFO - 2. NABIL (Score: 0.850)
2026-04-29 12:01:45 - INFO - 3. GUFL (Score: 0.720)
2026-04-29 12:02:00 - INFO - ✓ BUY 19 EBL @ Rs. 525.00 = Rs. 9,975.00
2026-04-29 12:02:00 - INFO - ✓ BUY 18 NABIL @ Rs. 550.00 = Rs. 9,900.00
2026-04-29 12:02:00 - INFO - ✓ BUY 20 GUFL @ Rs. 510.00 = Rs. 10,200.00
...
```

### 2. `logs/weekly_portfolio.json`
```json
{
  "last_purchase_date": "2026-04-29 12:02:00",
  "current_holdings": {
    "EBL": {"shares": 19, "avg_cost": 525.00, "total_invested": 9975.00},
    "NABIL": {"shares": 18, "avg_cost": 550.00, "total_invested": 9900.00},
    "GUFL": {"shares": 20, "avg_cost": 510.00, "total_invested": 10200.00}
  },
  "history": [
    {
      "date": "2026-04-29",
      "purchases": [...],
      "total_invested": 30075.00
    }
  ]
}
```

### 3. Individual Stock Logs
```
logs/NABIL_weekly.log  - NABIL position tracking
logs/GUFL_weekly.log   - GUFL position tracking
logs/EBL_weekly.log    - EBL position tracking
...
```

---

## ⚙️ Configuration Options

### Capital Investment
```python
WeeklyTopStocksBuyer(
    capital_per_stock=10000.0,  # Rs. 10,000 per stock
)
# Total for 3 stocks: Rs. 30,000/week
```

### Purchase Schedule
```python
WeeklyTopStocksBuyer(
    buy_day="wednesday",        # Pick any day
    buy_time="12:00",           # HH:MM format in 24-hour
)
```

### Market Analysis Frequency
```python
WeeklyTopStocksBuyer(
    check_interval_minutes=60,  # Analyze every 60 minutes
)
```

### Selection Method
```python
buyer.analyze_and_select_stocks(method="combined")
# Options: "volume", "gainers", "combined"
```

---

## 🎓 Understanding the Scores

### Example with Real Data

```
Stock Data (2026-04-29):

SYMBOL    VOLUME      % CHANGE    VOL SCORE    MOMENTUM     FINAL
─────────────────────────────────────────────────────────────────
EBL       500,000     +4.2%       1.00         0.84         0.920  ✓ 1st
NABIL     480,000     +3.5%       0.96         0.70         0.850  ✓ 2nd
GUFL      300,000     +2.1%       0.60         0.42         0.540  ✓ 3rd
SBI       250,000     -1.5%       0.50        -0.30         0.220
ADBL      400,000     +1.0%       0.80         0.20         0.640

Top 3 by Combined Score: EBL, NABIL, GUFL
This Week's Investment: Rs. 10K × 3 = Rs. 30,000
```

**Why This Works:**
- EBL: Highest volume (500K) + strong gain (+4.2%) → Best score
- NABIL: Very high volume (480K) + good gain (+3.5%) → Second best
- GUFL: Medium volume (300K) + decent gain (+2.1%) → Third best
- SBI: Ignored because negative change
- ADBL: Ignored despite high volume due to low momentum

---

## 📈 Expected Outcomes

### Conservative Scenario (5% Gain)
```
Week 1 Purchase: Rs. 30,000 @ avg Rs. 525/share
Week 2 Market: Stocks rise to avg Rs. 551/share
P&L: +5% = +Rs. 1,500
```

### Moderate Scenario (0% Return)
```
3 Week Purchases: Rs. 90,000 total
Average entry price holds steady
P&L: 0% = 0
But: Positioned for growth over time
```

### Risk Scenario (-5% Loss)
```
Stocks decline 5% from average entry
P&L: -5% = -Rs. 1,500
Recovery: Just need 5% gain to break even
```

---

## 🔄 Integration with Existing System

### Works With Paper Trading
The weekly buyer uses the existing paper trading infrastructure:
- Uses `PaperTrader` for simulated purchases
- Integrates with `StockPaperTrader` for position tracking
- Compatible with trailing stop strategies (future integration)

### Works With Individual Stock Traders
Run in separate terminals:
```bash
# Terminal 1: Weekly buyer (schedules 3 stocks)
python3 demo_weekly_buyer.py

# Terminal 2: Monitor GUFL specifically (trailing stop)
python3 demo_gufl_trading.py --resume
```

---

## 🛠️ Customization Examples

### Buy Only on Gainers
```python
buyer.analyze_and_select_stocks(method="gainers")
buyer.buy_top_stocks()
```

### Buy More Capital per Stock
```python
buyer = WeeklyTopStocksBuyer(capital_per_stock=25000.0)
# Now: Rs. 75,000/week = Rs. 25K × 3 stocks
```

### Buy on Friday Afternoon
```python
buyer = WeeklyTopStocksBuyer(
    buy_day="friday",
    buy_time="14:30"
)
```

### Buy More Frequently
```python
# Modify to buy top 5 stocks twice per week
buyer.analyze_and_select_stocks()
top_5 = buyer.market_analyzer.get_top_stocks_combined(top_n=5)
buyer.top_stocks = top_5
buyer.buy_top_stocks()
```

---

## 📊 Performance Tracking

### Key Metrics to Monitor

1. **Total Invested** - Cumulative capital deployed
2. **Portfolio Value** - Current holdings + cash
3. **Unrealized P&L** - Gain/loss if sold today
4. **Win Rate** - % of positive positions
5. **Return %** - Profit as % of invested capital

### Example 4-Week Performance
```
Week 1 (Apr 29): Bought EBL, NABIL, GUFL @ Avg Rs. 525 = Rs. 30K
                 Current: Rs. 30.2K (+0.7%)

Week 2 (May 06): Bought ADBL, CIT, HBL @ Avg Rs. 650 = Rs. 30K
                 Current: Rs. 29.1K (-3.0%)

Week 3 (May 13): Bought SBI, IFIC, JBLB @ Avg Rs. 300 = Rs. 30K
                 Current: Rs. 31.5K (+5.0%)

Week 4 (May 20): Bought NEPAL, JFL, KBLPO @ Avg Rs. 250 = Rs. 30K
                 Current: Rs. 32.1K (+7.0%)

TOTAL PORTFOLIO:
  Invested:       Rs. 120,000
  Current Value:  Rs. 122,900
  Unrealized P&L: +Rs. 2,900 (+2.4%)
```

---

## ⚠️ Important Considerations

### Market Risks
- Past volume/momentum don't guarantee future returns
- Market can reverse suddenly
- Liquidity may be lower after hours

### Technical Risks
- Network issues can prevent data fetch
- ShareSansar may be temporarily unavailable
- System clock must be accurate for scheduling

### Strategy Risks
- All 3 stocks could be in same sector
- Selection method may not capture best performers
- No stop losses implemented (manual monitoring needed)

### Mitigation Strategies
1. Start with small capital (Rs. 5,000 per stock)
2. Monitor portfolio weekly
3. Review and adjust capital based on results
4. Implement manual stop losses if needed
5. Diversify across multiple weeks of purchases

---

## 📞 Getting Help

### Test Basic Functionality
```bash
python3 test_weekly_buyer.py
```

### Check Logs for Errors
```bash
tail logs/weekly_buyer.log | grep -i error
```

### Verify Market Data
```bash
curl https://www.sharesansar.com/live-trading | head -50
```

### Check Portfolio State
```bash
cat logs/weekly_portfolio.json
```

---

## ✅ Launching Checklist

Before running:
- [ ] Python 3.8+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Virtual environment activated
- [ ] Internet connection is stable
- [ ] ShareSansar website is accessible
- [ ] `logs/` directory exists
- [ ] Capital budget determined
- [ ] Purchase schedule chosen

---

## 🎉 You're Ready!

Run your first weekly buyer with:
```bash
python3 demo_weekly_buyer.py
```

Then:
1. Review market analysis
2. Confirm top 3 stocks
3. Start automated weekly buying
4. Monitor results in `logs/weekly_buyer.log`

**Happy trading!**
