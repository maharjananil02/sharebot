# NABIL Price Fetching - API & Data Sources

## Current Implementation
Your system uses **web scraping** from nepalstock.com which requires parsing HTML.

## Available Options for NABIL Price Fetching

### Option 1: Web Scraping (Current - Most Reliable)
**Method:** Parse nepalstock.com website HTML  
**Reliability:** ⭐⭐⭐ (Works when website is up)  
**Speed:** 1-5 seconds per request  
**Cost:** Free  

**Current Implementation:**
```python
def fetch_real_nabil_price(self) -> float:
    url = "https://www.nepalstock.com/"
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Parse and extract NABIL price
    return price
```

**Pros:**
- Works with publicly available website
- No API key needed
- Covers all stocks
- Real-time data

**Cons:**
- Website changes can break scraping
- Slower than API
- Rate limiting possible

---

### Option 2: NEPSE Official API
**Status:** ❌ **Not Publicly Available**  
**Details:** NEPSE does not offer a public REST API for real-time data

**Contact for API Access:**
```
Nepal Stock Exchange Ltd.
Phone: +977-01-5350758
Email: mparajuli@nepalstock.com
Website: https://www.nepalstock.com/
```

**What to Ask For:**
- Real-time market data API
- Historical data API
- Developer registration

---

### Option 3: Third-Party Data Providers

#### 3a. meroStock (Community Project)
**URL:** Try searching GitHub for "nepal-stock-exchange-api"  
**Community:** Some developers have created unofficial APIs  
**Example:** `https://merostock.com` (if available)

```python
# Example (if API exists):
import requests

response = requests.get('https://api.merostock.com/stocks/NABIL')
price = response.json()['ltp']  # Last traded price
```

#### 3b. TradingView / Yahoo Finance
**Coverage:** Not comprehensive for Nepal stocks  
**Limitation:** Limited NEPSE support

---

### Option 4: Manual Input (Current Fallback)
**Method:** User enters price manually from website  
**Reliability:** ⭐⭐⭐⭐⭐ (100% accurate)  
**Speed:** Instant after user input  
**Cost:** Free  

**Your Implementation:**
```python
price_input = input("Enter NABIL price: ")
nabil_price = float(price_input)
trader.setup_strategy(entry_price=nabil_price)
```

---

## Current API Code

### Method 1: Web Scraping (In Use)
```python
def fetch_real_nabil_price(self) -> float:
    """Fetch NABIL price from nepalstock.com"""
    try:
        url = "https://www.nepalstock.com/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        content = response.text
        soup = BeautifulSoup(content, 'html.parser')
        
        # Parse looking for NABIL price in format:
        # [NABIL 525.0 (15000) (+25.0)]
        for match in soup.find_all(string=re.compile(r'NABIL')):
            line = match.strip()
            if line.startswith('NABIL'):
                parts = line.split()
                if len(parts) >= 2:
                    price = float(parts[1].replace(',', ''))
                    if 100 < price < 10000:
                        return price
        
        raise ValueError("NABIL not found")
        
    except Exception as e:
        raise Exception(f"Error: {str(e)}")
```

### Method 2: Direct API Call (If Available)
```python
def fetch_from_api(symbol='NABIL') -> float:
    """
    Future: Use official NEPSE API when available
    """
    try:
        # Once NEPSE provides public API:
        # response = requests.get(f'https://api.nepalstock.com/stock/{symbol}')
        # return response.json()['ltp']  # Last Traded Price
        pass
    except Exception as e:
        print(f"API Error: {e}")
```

---

## How to Implement Additional Methods

### Add Another Price Source
```python
class NABILPriceProvider:
    
    @staticmethod
    def fetch_from_nepalstock():
        """Web scraping"""
        # Your current method
        pass
    
    @staticmethod
    def fetch_from_merostock():
        """If merostock API available"""
        try:
            response = requests.get('https://api.merostock.com/stock/NABIL')
            if response.status_code == 200:
                return response.json()['price']
        except:
            return None
    
    @staticmethod
    def fetch_from_nepse_api(api_key=None):
        """Official NEPSE API (when available)"""
        try:
            headers = {'Authorization': f'Bearer {api_key}'}
            response = requests.get(
                'https://api.nepalstock.com/v1/stock/NABIL',
                headers=headers
            )
            return response.json()['ltp']
        except:
            return None
    
    @classmethod
    def get_price_with_fallback(cls):
        """Try multiple sources"""
        sources = [
            cls.fetch_from_nepse_api,  # Try official API first
            cls.fetch_from_merostock,  # Try community API
            cls.fetch_from_nepalstock, # Fallback to web scraping
        ]
        
        for source in sources:
            try:
                price = source()
                if price:
                    return price
            except:
                continue
        
        raise ValueError("All price sources failed")
```

---

## Integration Into Your System

### Current Flow
```
User Input (125) → Strategy Setup → Trading
      OR
Web Scraping → Strategy Setup → Trading
      OR
Manual Input → Strategy Setup → Trading
```

### Enhanced Flow
```
NEPSE API (best)
    ↓
MeroStock API (fallback)
    ↓
Web Scraping (fallback)
    ↓
User Manual Input (final fallback)
    ↓
Strategy Setup → Trading
```

---

## Testing Different Methods

### Test Web Scraping (Current)
```python
from src.bot.nabil_scheduler import NABILPaperTrader

trader = NABILPaperTrader()
try:
    price = trader.fetch_real_nabil_price()
    print(f"Web Scraping: Rs. {price}")
except Exception as e:
    print(f"Web Scraping failed: {e}")
```

### Test Manual Input
```python
trader = NABILPaperTrader()
trader.setup_strategy(entry_price=525.0)  # Manual price
```

---

## Recommendations

### For Development (Current)
✅ Use manual input or web scraping  
✅ Reliable and works immediately  
✅ No API key needed  

### For Production
1. **Contact NEPSE** - Request official API access
2. **Document the API** - Once available, integrate it
3. **Setup with API Key** - Secure credential storage
4. **Maintain Fallback** - Keep web scraping as backup

### Best Practice
```python
# configuration.py / .env
NEPSE_API_KEY = os.getenv("NEPSE_API_KEY", None)
NEPSE_API_ENDPOINT = "https://api.nepalstock.com/v1"

if NEPSE_API_KEY:
    # Use official API
    price = fetch_from_official_api(NEPSE_API_KEY)
else:
    # Fallback to web scraping
    price = fetch_from_web_scraping()
```

---

## Current Status in Your System

**What's Implemented:**
- ✅ Web scraping from nepalstock.com
- ✅ Regex pattern matching for NABIL
- ✅ HTML parsing with BeautifulSoup
- ✅ Error handling with fallback
- ✅ User manual input support

**What's Not Available:**
- ❌ Official NEPSE API (not public)
- ❌ MeroStock API integration
- ❌ Real-time WebSocket stream

---

## Next Steps

### Option A: Explore Community APIs
```bash
# Search for Python packages
pip search nepse
pip search nepal-stock

# Check GitHub
# - Look for "nepse-api" or "nepal-stock-exchange"
# - Check if any community projects expose data
```

### Option B: Wait for Official API
Contact NEPSE and request API access for production trading bots

### Option C: Enhance Current Implementation
```python
# Add caching to reduce requests
# Add parallel fetching attempts
# Add price validation and smoothing
```

---

## Summary

| Method | Status | Speed | Cost | Reliability |
|--------|--------|-------|------|-------------|
| Web Scraping | ✅ Ready | 1-5s | Free | ⭐⭐⭐ |
| NEPSE API | ❌ NA | - | TBD | - |
| MeroStock | ⚠️ Unknown | - | Free | ? |
| Manual Input | ✅ Ready | Instant | Free | ⭐⭐⭐⭐⭐ |

**Current:** Your system uses web scraping with manual input fallback ✅

