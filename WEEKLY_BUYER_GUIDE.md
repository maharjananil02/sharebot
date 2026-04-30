# Weekly Top Stocks Buyer - Complete Guide

## 🎯 Overview

The **Weekly Top Stocks Buyer** is an automated trading system that:

1. **Analyzes NEPSE market data** - Fetches real-time stock prices, volumes, and trends from ShareSansar
2. **Identifies top 3 trending stocks** - Uses advanced scoring to find the best performing stocks
3. **Purchases automatically** - Buys top 3 stocks once per week (e.g., every Wednesday)
4. **Tracks performance** - Monitors P&L and portfolio value
5. **Logs everything** - Detailed records for review and analysis

---

## 📊 How It Works

### Selection Criteria

The system ranks stocks using **three different methods**:

#### 1. **Volume-Based Selection**
- Identifies stocks with highest trading volume
- Indicates strong market interest and liquidity
- Good for volatile stocks with high activity

```
Choose when: You want active, liquid stocks
Example: NABIL (500,000 shares) > GUFL (100,000 shares)
```

#### 2. **Gainers Selection**
- Identifies stocks with highest price gain today
- Positive momentum indicator
- Good for trending upward stocks

```
Choose when: You want high momentum stocks
Example: Stock up +5% > Stock up +2%
```

#### 3. **Combined Scoring** (Default)
- 60% weight on trading volume
- 40% weight on price gain/momentum
- Balanced approach combining both factors

```
Score = (Volume Rank × 0.6) + (Momentum Rank × 0.4)

Example:
NABIL: High volume + small gain = 0.750
GUFL:  Medium volume + big gain = 0.725
EBL:   High volume + big gain = 0.890 ← BEST
```

---

## 🚀 Quick Start

### 1. Test the Market Analyzer (No Purchases)

```bash
python3 test_weekly_buyer.py
```

Output shows:
- All stocks fetched from NEPSE
- Top 5 by volume
- Top 5 gainers
- Top 3 for this week's purchase

---

### 2. Run Full Weekly Buyer Demo

```bash
python3 demo_weekly_buyer.py
```

Follow prompts:
```
1. Capital per stock? (press Enter for Rs. 10,000)
2. Purchase day? (default: wednesday)
3. Purchase time? (default: 12:00)
4. Confirm to start? (y/n)
```

Then:
- Shows real-time market analysis
- Shows top 3 stocks to be purchased
- Waits for scheduled purchase time
- Automatically runs until Ctrl+C

---

## 📋 Configuration Options

### Capital per Stock
```python
WeeklyTopStocksBuyer(
    capital_per_stock=10000.0,  # Rs. 10,000 per stock
    # Total = 30,000 for 3 stocks
)
```

Adjust based on:
- Total budget available
- Risk tolerance
- Number of weeks of purchases planned

### Purchase Schedule
```python
WeeklyTopStocksBuyer(
    buy_day="wednesday",      # monday, tuesday, wednesday (default), thursday, friday
    buy_time="12:00",         # HH:MM format
    check_interval_minutes=60 # Check every 60 minutes
)
```

**Recommended:** Wednesday 12:00 (mid-week, mid-day for stable stock picks)

### Selection Method
```python
buyer.analyze_and_select_stocks(method="combined")  # "volume", "gainers", or "combined"
```

---

## 📈 Understanding the Scoring

### Combined Score Example

```
Market Data on 2026-04-29:

Stock      Volume    % Change   Volume Rank   Momentum Rank   Final Score
─────────────────────────────────────────────────────────────────────────
NABIL      500,000   +3.5%      1.00          0.70           0.86  ← 1st
EBL        450,000   +4.2%      0.90          0.84           0.89  ← 1st (BEST!)
GUFL       300,000   +2.1%      0.60          0.42           0.54  ← 3rd

Final Top 3 to Buy: EBL, NABIL, GUFL
Investment: Rs. 30,000 (Rs. 10,000 each)
```

---

## 💾 File Structure

### Generated Files

```
logs/
├── weekly_buyer.log                 # Main log file
├── weekly_portfolio.json            # Portfolio state
├── NABIL_weekly.log                 # Individual stock logs
├── GUFL_weekly.log
├── EBL_weekly.log
└── ...

gufl_position.json, nabil_position.json, etc. (individual stock positions)
```

### Portfolio File Structure

```json
{
  "last_purchase_date": "2026-04-29 12:00:45",
  "history": [
    {
      "date": "2026-04-29",
      "purchases": [
        {
          "symbol": "EBL",
          "quantity": 19,
          "price": 525.50,
          "total": 9984.50,
          "timestamp": "2026-04-29 12:00:45",
          "status": "PURCHASED"
        },
        ...
      ],
      "total_invested": 30000.00
    }
  ],
  "current_holdings": {
    "EBL": {
      "shares": 19,
      "avg_cost": 525.50,
      "total_invested": 9984.50
    },
    ...
  }
}
```

---

## 📊 Viewing Results

### During Execution
```bash
tail -f logs/weekly_buyer.log
```

Shows:
- Market analysis updates
- Stock selection process
- Purchase confirmations
- Error messages (if any)

### After Execution (Final Report)
```bash
tail -50 logs/weekly_buyer.log
```

Shows:
- Summary of all purchases
- Portfolio value
- Unrealized P&L
- Performance metrics

### Portfolio Status
```bash
cat logs/weekly_portfolio.json | python -m json.tool
```

Shows:
- Current holdings
- Average cost per stock
- Purchase history
- Last purchase date

---

## 🔧 Advanced Customization

### Custom Selection Logic

```python
from src.bot.market_analyzer import MarketAnalyzer

analyzer = MarketAnalyzer()
all_stocks = analyzer.fetch_all_stocks_data(source="sharesansar")

# Custom selection: Only tech stocks with volume > 20,000
tech_stocks = {k: v for k, v in all_stocks.items() 
               if k in ['NEPAL', 'ADBL', 'CIT'] and v['volume'] > 20000}

# Sort by momentum
top_3 = sorted(tech_stocks.items(), 
               key=lambda x: x[1]['pct_change'], reverse=True)[:3]
```

### Custom Purchase Logic

```python
from src.bot.weekly_buyer import WeeklyTopStocksBuyer

buyer = WeeklyTopStocksBuyer(
    capital_per_stock=5000.0,
    buy_day="friday",
    buy_time="14:30"
)

# Analyze and select
buyer.analyze_and_select_stocks(method="volume")

# Modify selection before buying
buyer.top_stocks = buyer.top_stocks[:2]  # Buy only top 2

# Execute
buyer.buy_top_stocks()
```

### Custom Scheduling

```python
buyer = WeeklyTopStocksBuyer(check_interval_minutes=30)  # Check every 30 min
buyer.start(duration_minutes=1440)  # Run for 1 day
```

---

## 📈 Performance Tracking

### Key Metrics

1. **Total Invested** - Sum of all purchases
2. **Portfolio Value** - Current holdings + cash
3. **Unrealized P&L** - Gain/Loss if sold at current price
4. **Return %** - Percentage return on invested capital

Example:
```
Total Invested:     Rs. 30,000.00
Portfolio Value:    Rs. 31,500.00
Unrealized P&L:     Rs. +1,500.00 (+5.00%)
```

### Weekly Comparison

Track across weeks:
```
Week 1 (Apr 29): Stocks purchased: EBL, NABIL, GUFL | Entered @ Rs. 525/540/510
Week 2 (May 06): Stocks purchased: ADBL, CIT, HBL | Entered @ Rs. 850/600/320
Week 3 (May 13): Stocks purchased: SBI, IFIC, JBLB | Entered @ Rs. 320/280/1250

Overall Portfolio:
- 9 positions open
- Total invested: Rs. 90,000
- Current value: Rs. 94,500
- Return: +5%
```

---

## ⚠️ Important Notes

### Risks & Limitations

1. **Past Performance** - Volume/momentum don't guarantee future gains
2. **Market Volatility** - Prices can drop after purchase
3. **Liquidity** - Some stocks may be hard to sell quickly
4. **Selection Bias** - High volume can indicate panic selling too
5. **No Dividend** - Paper trading doesn't include dividends

### Risk Management

1. **Position Sizing** - Start with Rs. 5,000-10,000 per stock
2. **Diversification** - Rolling weekly purchases reduce timing risk
3. **Review Schedule** - Monitor portfolio weekly
4. **Adjust Capital** - Reduce if losses accumulate
5. **Stop Loss** - Can be configured per stock (future feature)

---

## 🔄 Integration with Existing Trading

### Using with Individual Stock Traders

```python
from src.bot.market_analyzer import MarketAnalyzer
from src.bot.stock_trader import StockPaperTrader
from src.bot.weekly_buyer import WeeklyTopStocksBuyer

# Weekly buyer for automatic weekly purchases
buyer = WeeklyTopStocksBuyer(
    capital_per_stock=10000,
    buy_day="wednesday"
)

# Plus individual stock trader for specific stock
trader = StockPaperTrader(symbol="GUFL")
trader.setup_strategy(entry_price=510)

# Run both in parallel (in separate terminals)
buyer.start()       # Buys top 3 weekly
# trader.start()    # Monitors GUFL for trailing stop
```

### Using with Paper Trading Portfolio

```python
# Start weekly buyer
buyer = WeeklyTopStocksBuyer()
buyer.start()

# Monitor portfolio
status = buyer.get_status()
print(f"Portfolio Value: Rs. {status['portfolio']['portfolio']['cash']:,.2f}")
print(f"Holdings: {list(status['portfolio']['portfolio']['holdings'].keys())}")
```

---

## 📚 Example Workflows

### Workflow 1: Conservative (Low Risk)

```
Capital per stock: Rs. 5,000
Buy frequency: Once per week (Wednesday)
Selection: Combined (volume + momentum)
Duration: 12 weeks

Total investment: Rs. 180,000
Risk: You're betting on 36 different stocks over 12 weeks
Benefit: Diversification, consistent entry prices
```

### Workflow 2: Aggressive (High Volume)

```
Capital per stock: Rs. 25,000
Buy frequency: Once every 2 days
Selection: Volume-based (highest trading activity)
Duration: 2 weeks

Total investment: Rs. 375,000
Risk: High capital deployed, multiple large positions
Benefit: Capture all liquidity, fast position building
```

### Workflow 3: Trend Following

```
Capital per stock: Rs. 10,000
Buy frequency: Once per week (Friday afternoon)
Selection: Gainers (highest price momentum)
Duration: 8 weeks

Total investment: Rs. 240,000
Risk: Trend reversal after Friday
Benefit: Ride momentum into next week
```

---

## 🐛 Troubleshooting

### Issue: "No stocks with volume >= 5000"

**Cause:** Market closed or very low trading

**Solution:**
```python
# Lower minimum volume requirement
top_stocks = analyzer.get_top_stocks_combined(top_n=3, min_volume=1000)
```

### Issue: "Failed to fetch market data"

**Cause:** Network issue or ShareSansar down

**Solution:**
```bash
# Test connectivity
curl https://www.sharesansar.com/live-trading

# Try alternative source
viewer.market_analyzer.fetch_all_stocks_data(source="nepalstock")
```

### Issue: "Insufficient cash"

**Cause:** Portfolio cash < investment needed

**Solution:**
```python
# Reduce capital per stock
buyer = WeeklyTopStocksBuyer(capital_per_stock=3000)
```

---

## 📞 Support & Questions

### To Debug Issues

1. Check `logs/weekly_buyer.log` for error messages
2. Verify internet connection
3. Test with `test_weekly_buyer.py` first
4. Review `logs/weekly_portfolio.json` for state

### To Customize Further

Edit the strategy files:
- `src/bot/market_analyzer.py` - Change selection logic
- `src/bot/weekly_buyer.py` - Change purchase logic
- `demo_weekly_buyer.py` - Change user interaction

---

## ✅ Checklist Before Running

- [ ] Internet connection is stable
- [ ] ShareSansar or NEPSE is accessible
- [ ] Python 3.8+ is installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Virtual environment activated (`.venv/bin/activate`)
- [ ] `logs/` directory exists
- [ ] Capital budget is defined
- [ ] Purchase day/time chosen

---

## 🎓 Key Learnings

1. **Volume Analysis** - High trading volume = market interest
2. **Momentum Analysis** - Price momentum = trend continuation
3. **Diversification** - Buying 3 different stocks reduces risk
4. **Frequency** - Weekly purchases help with dollar-cost averaging
5. **Automation** - Scheduled purchases remove emotion from trading

---

**Ready to start? Run:**
```bash
python3 demo_weekly_buyer.py
```
