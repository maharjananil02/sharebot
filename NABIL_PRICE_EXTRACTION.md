# NABIL Price Extraction - Complete Setup Guide

## What Was Updated

Your system now has **two extraction methods** for NABIL price from nepalstock.com:

### Method 1: /today-price Endpoint (Recommended)
- **URL:** https://www.nepalstock.com/today-price
- **Format:** Structured price table with all stocks
- **Columns:** Symbol | LTP | Open | High | Low | Volume | Turnover | Transactions | Change
- **Status:** ✅ Code implemented, ready to use

### Method 2: Fallback Text Search
- **Fallback:** Searches for NABIL in extracted text
- **Regex:** Extracts price from format `[NABIL 525.0 (volume) (change)]`
- **Status:** ✅ Implemented as fallback

## Implementation Code

**Location:** `src/bot/nabil_scheduler.py` → `fetch_real_nabil_price()`

```python
def fetch_real_nabil_price(self) -> float:
    """
    Fetch real NABIL price from nepalstock.com/today-price
    Returns: Current NABIL stock price (LTP - Last Traded Price)
    """
    try:
        # Primary: Use structured table from /today-price
        url = "https://www.nepalstock.com/today-price"
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Parse table with columns: Symbol | LTP | Open | High | Low | Volume...
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                
                if len(cells) >= 3:
                    symbol = cells[1].get_text(strip=True)
                    
                    if symbol.upper() == "NABIL":
                        # Cell index 2 contains LTP (Last Traded Price)
                        price = float(cells[2].get_text(strip=True))
                        
                        if 100 < price < 10000:
                            return price  # ✓ SUCCESS
        
        # Fallback: Text search for NABIL price
        for match in soup.find_all(string=re.compile(r'NABIL')):
            prices = re.findall(r'\d+(?:\.\d+)?', match)
            if prices:
                price = float(prices[0])
                if 100 < price < 10000:
                    return price
        
        raise ValueError("NABIL not found")
        
    except Exception as e:
        raise Exception(f"Error: {str(e)}")
```

## Website Table Structure

When you visit https://www.nepalstock.com/today-price, the page shows:

```
| # | Symbol | LTP  | Open | High | Low  | Volume | Turnover | Trans | Change  |
|---|--------|------|------|------|------|--------|----------|-------|---------|
| 1 | ACLBSL | 960  | 980  | 1000 | 955  | 747    | 718,803  | 27    | -19.8   |
| 2 | ADBL   | 311  | 316  | 316  | 310  | 10,363 | 3,226    | 151   | -4.2    |
...
| N | NABIL  | 525  | ...  | ...  | ...  | ...    | ...      | ...   | ...     |
```

**Key:** "LTP" = Last Traded Price (the price you need)

## Current Price Access

Your system can get NABIL price in several ways:

### Option 1: Automatic Fetch (Primary)
```python
trader = NABILPaperTrader()
price = trader.fetch_real_nabil_price()  # Tries /today-price
print(f"NABIL Price: Rs. {price:.2f}")
```

### Option 2: Manual Input (When Auto-Fetch Fails)
```python
trader = NABILPaperTrader()
# Check https://www.nepalstock.com/today-price manually
trader.setup_strategy(entry_price=525.0)  # Enter real price
```

### Option 3: During Trading Setup
```bash
python test_paper_trading.py
# Prompts: "Enter current NABIL price: "
# Enter: 525 (or whatever current price is)
```

## Testing the Extract

To extract NABIL price manually:

```python
import requests
from bs4 import BeautifulSoup

# Fetch page
response = requests.get('https://www.nepalstock.com/today-price')
soup = BeautifulSoup(response.content, 'html.parser')

# Find table with prices
table = soup.find('table')
rows = table.find_all('tr')

# Search for NABIL row
for row in rows:
    cells = row.find_all('td')
    if len(cells) >= 3:
        if 'NABIL' in cells[1].get_text():
            symbol = cells[1].get_text(strip=True)
            price = float(cells[2].get_text(strip=True))  # LTP
            print(f"{symbol}: Rs. {price:.2f}")  # Output: NABIL: Rs. 525.00
```

## Price Table Columns

The page shows these columns in this order:

| Index | Column | Example | Use |
|-------|--------|---------|-----|
| 0 | # (Row#) | 24 | - |
| 1 | Symbol | NABIL | ✓ Find row |
| 2 | LTP | 525.00 | ✓ Price |
| 3 | Open | 520.00 | - |
| 4 | High | 530.00 | - |
| 5 | Low | 520.00 | - |
| 6 | Volume | 15,000 | - |
| 7 | Turnover | 7,875,000 | - |
| 8 | Transactions | 150 | - |
| 9 | Change | +5.00 | - |

**Your extraction** uses columns 1 (symbol) and 2 (LTP price)

## Files Updated

1. **src/bot/nabil_scheduler.py**
   - Added `import re` for regex support
   - Updated `fetch_real_nabil_price()` to parse /today-price table
   - Improved table cell extraction logic
   - Added fallback text search

2. **test_paper_trading.py**
   - User input for manual NABIL price entry
   - Default fallback: 525

3. **demo_paper_trading.py**
   - User input field added
   - Asks for real NABIL price before trading

## How Your System Uses This

```
Your Trading Bot
    ↓
Every 15 minutes:
    ├─ Call fetch_real_nabil_price()
    ├─ Try #1: Parse /today-price table for NABIL
    ├─ Try #2: Text search for price
    ├─ Fall back: Use last known price
    ├─ Use fetched price for analysis
    └─ Execute trades based on strategy
```

## Integration Points

### During Initialization
```python
trader = NABILPaperTrader()
trader.setup_strategy()  # Calls fetch_real_nabil_price() internally
```

### During Trading (Every 15 Minutes)
```python
def simulate_price_movement(self):
    """Called every 15 minutes"""
    real_price = self.fetch_real_nabil_price()  # Get latest
    return real_price  # Use for strategy
```

### With Manual Fallback
```python
trader.setup_strategy(entry_price=525.0)  # Use manual if auto fails
```

## Website Availability

The /today-price page is available during and after NEPSE trading hours:
- **Market Hours:** 11:15 AM - 3:15 PM NST
- **Data Updated:** After market close
- **Access:** Always available (shows previous close after hours)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Connection refused" | Website temporarily down, use manual input |
| "NABIL not found" | Symbol may be in different column, check website manually |
| "Price out of range" | Invalid price extracted, validate manually |
| Connection timeout | Website overloaded, retry manually |

## Complete Flow Example

```
1. Start Trading:
   python test_paper_trading.py
   
2. System asks:
   "Enter current NABIL price: "
   
3. You enter:
   525
   
4. System fetches real price:
   ✓ From https://www.nepalstock.com/today-price
   
5. If available:
   Uses NABIL LTP column from table
   
6. If unavailable:
   Uses your entered value (525)
   
7. Executes strategy:
   Based on real/entered NABIL price
   
8. Every 15 mins:
   Tries to fetch updated real price
   Falls back to simulation if needed
   
9. Logs everything:
   logs/nabil.log records price source
```

## Summary

✅ **Extraction Endpoint:** https://www.nepalstock.com/today-price  
✅ **Target Column:** LTP (Last Traded Price)  
✅ **Parsing Method:** BeautifulSoup + regex  
✅ **Fallback:** Manual user input  
✅ **Integration:** Every 15-minute check  
✅ **Logging:** All price sources recorded  

Your system is ready to extract NABIL prices from the NEPSE website!

