# Using Real NABIL Prices from NEPSE

## Overview
The paper trading system now attempts to fetch **real NABIL prices** from nepalstock.com every 15 minutes.

## How It Works

### Automatic Price Fetching (On Startup)
When you run the demo, it automatically fetches the current NABIL price from NEPSE:

```bash
python demo_paper_trading.py
```

**What happens:**
1. Script starts
2. Tries to connect to nepalstock.com
3. Fetches current NABIL price
4. Uses that real price as entry price
5. Every 15 minutes, fetches updated real price
6. Logs everything to `logs/nabil.log`

### Continuous Real Price Updates
Every 15 minutes, the system:
- Fetches latest NABIL price from NEPSE
- Runs strategy analysis on real market price
- Automatically executes trades if triggers hit
- Falls back to simulated prices if connection fails

## Getting Real Prices

### Option 1: Automatic (Default)
```bash
# Just run - fetches real price automatically
python demo_paper_trading.py
```

### Option 2: Manual Entry (If Auto-Fetch Fails)
If the auto-fetch can't retrieve the price, manually check and enter:

1. Visit https://www.nepalstock.com/
2. Look for NABIL in the stock list (listed as "NABIL Bank Limited")
3. Note the current price
4. Run with manual price:

```python
from src.bot.nabil_scheduler import NABILPaperTrader

trader = NABILPaperTrader()
# Get real price from nepalstock.com: e.g., 3525.00
trader.setup_strategy(entry_price=3525.0)  
trader.start()
```

### Option 3: Check Current Price Only
```bash
"/Users/anil/Coding/lets code/nepse-trading/.venv/bin/python" -c "
from src.bot.nabil_scheduler import NABILPaperTrader
trader = NABILPaperTrader()
price = trader.fetch_real_nabil_price()
print(f'Current NABIL price: Rs. {price:.2f}')
"
```

## Price Update Frequency

**Starting Price:** Fetched once at startup  
**During Trading:** Updated every 15 minutes  
**Fallback:** If website unavailable, uses simulated price

## Example Run

```
📊 Initializing Paper Trader...
📈 Setting up NABIL strategy (fetching real price)...

>>> FETCHING REAL NABIL PRICE FROM NEPSE...
    Real Price Found: Rs. 3525.50

>>> SETTING UP STRATEGY
    Entry Price: Rs. 3525.50
    Initial Quantity: 10 shares

✓ PAPER BUY EXECUTED
   Quantity: 10 shares
   Price: Rs. 3525.50
   Total Cost: Rs. 35,255.00
   Position: 10 shares (Avg: Rs. 3525.50)

STARTING AUTOMATED PAPER TRADING
Duration: CONTINUOUS (runs indefinitely until Ctrl+C)
Check interval: 900 seconds (15 minutes)

[CHECK #0001] 20:43:50 | Real Price: Rs. 3526.25
[CHECK #0002] 21:00:00 | Real Price: Rs. 3528.00
[CHECK #0003] 21:15:00 | Real Price: Rs. 3522.50
...
```

## Understanding Log Entries

### When Real Price is Fetched
```
>>> FETCHING REAL NABIL PRICE FROM NEPSE...
    Real Price Found: Rs. 3525.50
```

### When Price Check Happens
```
[CHECK #0001] 20:43:50 | Price: Rs. 3526.25
```

### When Using Fallback
```
WARNING - Connection error to nepalstock.com - using simulated price
[CHECK #0001] 20:43:50 | Price: Rs. 3521.00 (simulated - fallback)
```

## Troubleshooting

### "Connection error to nepalstock.com"
**Cause:** Network issue or website unavailable  
**Solution:** System automatically uses simulated prices, logs show which checks used simulation

### "NABIL price not found in NEPSE data"
**Cause:** Website structure changed  
**Solution:** 
1. Manually check https://www.nepalstock.com/
2. Note NABIL price
3. Run: `trader.setup_strategy(entry_price=<your_price>)`

### Want to Use Consistent Simulated Price?
```python
# Always use fixed price for testing
trader.setup_strategy(entry_price=3500.0)  # Use this fixed price every run
```

### Want to Always Fetch Real?
```python
# Force real price fetch with no fallback
try:
    price = trader.fetch_real_nabil_price()
    # If this succeeds, price is real
    if price > 100:  # Sanity check
        trader.setup_strategy(entry_price=price)
except:
    print("Could not fetch real price")
```

## Key Features

✅ **Automatic Real Price Fetching** - No manual entry needed  
✅ **Fallback Simulation** - Works even if website is down  
✅ **15-Minute Updates** - Price refreshes automatically  
✅ **Comprehensive Logging** - All price sources logged  
✅ **Error Handling** - Graceful fallback if connection fails  

## NEPSE Website Structure

NABIL is listed as "NABIL Bank Limited" under:
- **Category:** Commercial Banks
- **Type:** Equity
- **Symbol:** NABIL
- **Website:** nepalstock.com

## Current Implementation Details

### Price Fetching Methods
1. **Primary:** Web scraping from nepalstock.com
2. **Fallback:** Random walk simulation (±0.5% per 15 minutes)

### Timeout Settings
- **Connection timeout:** 10 seconds
- **Read timeout:** Included in 10-second timeout
- **Falls back gracefully** if timeout occurs

### Valid Price Range
- Minimum: Rs. 100
- Maximum: Rs. 10,000
- Outside this range: Treated as error, uses fallback

## Next Steps

1. **Run the demo with real prices:**
   ```bash
   python demo_paper_trading.py
   ```

2. **Monitor the logs:**
   ```bash
   tail -f logs/nabil.log
   ```

3. **Check real price during market hours** (11:15 AM - 3:15 PM NST)

4. **For production:** Add API key-based pricing if available

## Notes

- ✓ Real prices only available during **NEPSE market hours** (11:15 AM - 3:15 PM NST)
- ✓ Outside market hours, price fetching falls back to simulation
- ✓ System logs which source (real vs. simulated) was used for each check
- ✓ All trading is paper-based - no real money involved
- ✓ Strategy executes automatically every 15 minutes based on fetched prices

## Support

For real-time price issues:
1. Check https://www.nepalstock.com/ manually
2. Verify NABIL is listed and trading
3. Check network connectivity
4. Review logs/nabil.log for specific errors
5. Manually set price if auto-fetch fails: `trader.setup_strategy(entry_price=<price>)`

---

**Summary:** The system now uses real NABIL prices from NEPSE with automatic fallback to simulation if the connection fails. Every 15-minute check fetches the latest real market price.

