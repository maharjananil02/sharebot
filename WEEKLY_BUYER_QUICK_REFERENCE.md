# Weekly Top Stocks Buyer - Quick Reference

## 🚀 Quick Start (2 Minutes)

```bash
# 1. Test without purchases
python3 test_weekly_buyer.py

# 2. Run full demo with purchases (choose options when prompted)
python3 demo_weekly_buyer.py

# 3. Monitor in another terminal
tail -f logs/weekly_buyer.log
```

---

## 📊 Three Selection Methods

| Method | Best For | Formula | Example |
|--------|----------|---------|---------|
| **Volume** | Liquid stocks | Top by trades | NABIL (500K) > EBL (400K) > GUFL (300K) |
| **Gainers** | Momentum | Top by % gain | Stock +5% > +3% > +2% |
| **Combined** | Balanced (DEFAULT | Vol(60%) + Momentum(40%) | EBL best score |

---

## ⚙️ Configuration Cheat Sheet

### Capital Per Stock
```python
WeeklyTopStocksBuyer(capital_per_stock=10000.0)
# Total/week: 10K × 3 = Rs. 30,000
```

### Purchase Schedule
```python
WeeklyTopStocksBuyer(
    buy_day="wednesday",  # monday-friday, saturday, sunday
    buy_time="12:00"      # 24-hour format HH:MM
)
```

### Analysis Frequency
```python
WeeklyTopStocksBuyer(check_interval_minutes=60)  # Check every hour
```

### Full Config Example
```python
from src.bot.weekly_buyer import WeeklyTopStocksBuyer

buyer = WeeklyTopStocksBuyer(
    capital_per_stock=15000.0,
    buy_day="friday",
    buy_time="14:30",
    check_interval_minutes=120
)

buyer.analyze_and_select_stocks(method="combined")
buyer.buy_top_stocks()
buyer.start()
```

---

## 📈 Workflow Summary

```
START
  ↓
Initialize buyer with capital, day, time
  ↓
Fetch market data for ALL stocks (200+)
  ↓
Analyze and rank by volume + momentum
  ↓
Select top 3 stocks
  ↓
Wait for scheduled day/time
  ↓
Execute purchases on schedule
  ↓
Log all transactions
  ↓
Update portfolio
  ↓
Generate report
  ↓
Ready for next week
```

---

## 📁 Output Files

| File | Purpose |
|------|---------|
| `logs/weekly_buyer.log` | Main log file |
| `logs/weekly_portfolio.json` | Portfolio state |
| `logs/SYMBOL_weekly.log` | Individual stock logs |

---

## 👀 Monitoring Commands

```bash
# Real-time log view
tail -f logs/weekly_buyer.log

# Show last 50 lines (final report)
tail -50 logs/weekly_buyer.log

# Count purchases
grep "PURCHASED" logs/weekly_buyer.log | wc -l

# Show portfolio
cat logs/weekly_portfolio.json | python -m json.tool

# Check for errors
grep -i error logs/weekly_buyer.log
```

---

## 🎯 Selection Examples

### Most Liquid Stocks
```python
buyer.analyze_and_select_stocks(method="volume")
# Result: Top 3 by trading volume
```

### Highest Gainers
```python
buyer.analyze_and_select_stocks(method="gainers")
# Result: Top 3 by % price increase
```

### Balanced (RECOMMENDED)
```python
buyer.analyze_and_select_stocks(method="combined")
# Result: Top 3 by combined score (volume + momentum)
```

---

## 💰 Capital Examples

| Scenario | Capital/Stock | Total/Week | 12 Weeks |
|----------|---------------|-----------|----------|
| Conservative | Rs. 5,000 | Rs. 15,000 | Rs. 180,000 |
| Standard | Rs. 10,000 | Rs. 30,000 | Rs. 360,000 |
| Aggressive | Rs. 25,000 | Rs. 75,000 | Rs. 900,000 |

---

## ⏰ Schedule Examples

| Day | Time | Use Case |
|-----|------|----------|
| Monday | 09:00 | Start of week |
| Wednesday | 12:00 | Mid-week (RECOMMENDED) |
| Friday | 14:30 | End of week before weekend |

---

## 🔍 Interpreting Results

### Portfolio Status
```json
{
  "NABIL": {
    "shares": 18,
    "avg_cost": 550.00,
    "total_invested": 9900.00
  }
}
```
→ Own 18 shares, paid Rs. 550 avg, invested Rs. 9,900 total

### Performance Calculation
```
Current Price: Rs. 575/share
Position Value: 18 × Rs. 575 = Rs. 10,350
P&L: Rs. 10,350 - Rs. 9,900 = +Rs. 450 (+4.5%)
```

---

## ⚠️ Common Issues

| Issue | Solution |
|-------|----------|
| "No stocks with volume >= 5000" | Lower min_volume: `min_volume=1000` |
| "Failed to fetch market data" | Check internet, try again |
| "Insufficient cash" | Reduce `capital_per_stock` |
| "Import error" | Run from project root with `sys.path.insert` |

---

## 🎓 Key Concepts

**Volume Score:** Normalized trading volume → Liquidity indicator
**Momentum Score:** Normalized price change → Trend indicator
**Combined Score:** 60% volume + 40% momentum → Balanced approach

**Why 60/40?**
- Volume is stable (big drops/spikes are clear)
- Momentum is volatile (changes daily)
- Weighting volume more = less affected by daily swings

---

## 🚀 Next Steps After First Run

1. **Monitor Results** - Check logs for errors/successes
2. **Review Portfolio** - See which stocks were bought
3. **Track Performance** - Note P&L after first purchase
4. **Adjust Capital** - Increase/decrease based on comfort
5. **Automate** - Set to run continuously with scheduler
6. **Analyze Trends** - Review which selection method works best

---

## 📊 Market Data Available

From ShareSansar real-time data:
- Stock symbol
- Last traded price (LTP)
- Point change
- Percentage change
- Open price
- High/Low
- Trading volume
- Previous close

All automatically fetched and analyzed.

---

## 🔗 Related Files

- `src/bot/market_analyzer.py` - Market analysis engine
- `src/bot/weekly_buyer.py` - Weekly buyer engine
- `src/bot/paper_trader.py` - Paper trading simulator
- `demo_weekly_buyer.py` - Interactive demo
- `test_weekly_buyer.py` - Quick test
- `WEEKLY_BUYER_GUIDE.md` - Full documentation

---

## 💡 Pro Tips

1. **Start Small** - Begin with Rs. 5,000/stock to test
2. **Monitor Fridays** - Check weekend holdings Friday afternoon
3. **Use Combined** - Most balanced approach for beginners
4. **Check Logs** - Always review logs after first run
5. **Track Manually** - Note portfolio value weekly for trends
6. **Diversify** - Multiple weeks of purchases reduce timing risk
7. **Be Patient** - Results take time, trading is long-term

---

## ✅ Pre-Launch Checklist

```
[ ] Python 3.8+
[ ] Dependencies: pip install -r requirements.txt
[ ] Virtual env activated
[ ] Internet working
[ ] ShareSansar accessible (curl test)
[ ] logs/ directory exists
[ ] Capital amount decided
[ ] Day/time chosen
[ ] Ready to run!
```

---

## 🎯 Success Criteria

After first run, you should see:
- ✓ Market data fetched for 200+ stocks
- ✓ Top 3 stocks identified and logged
- ✓ Purchases executed on schedule
- ✓ Portfolio updated with holdings
- ✓ Detailed logs in `logs/weekly_buyer.log`
- ✓ Portfolio state saved to JSON

---

## 📞 Quick Help

```bash
# Test market fetch
python3 test_weekly_buyer.py

# Run full demo
python3 demo_weekly_buyer.py

# Monitor
tail -f logs/weekly_buyer.log

# Check portfolio
cat logs/weekly_portfolio.json

# View guide
cat WEEKLY_BUYER_GUIDE.md

# View implementation details
cat WEEKLY_BUYER_IMPLEMENTATION.md
```

---

**Ready to start?**
```bash
python3 demo_weekly_buyer.py
```

Good luck! 🚀
