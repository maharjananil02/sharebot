# TMS (Trading Management System) - Knowledge Base

## 1. System Overview

**TMS** = Trading Management System for NEPSE (Nepal Stock Exchange)  
**Target Users**: Brokers and traders managing daily trading transactions  
**Reference**: Official NEPSE TMS Manual

### Key Components
- **TMS**: Order management frontend interface
- **DNA (Direct NOTS Access)**: Bridge between TMS and NEPSE system - **MUST be enabled before placing orders**
- **NOTS**: NEPSE Online Trading System (backend)
- **CLI**: Client interface

---

## 2. Glossary & Key Terms

| Term | Definition |
|------|-----------|
| **TMS** | Trading Management System |
| **NOTS** | NEPSE Online Trading System |
| **DNA** | Direct NOTS Access (connection layer) |
| **UCC** | User/Client Code (account identifier) |
| **LTP** | Last Traded Price |
| **CNC** | Cash & Carry trading mode |
| **Board Lot** | Minimum quantity unit for trading |
| **Tick Size** | Minimum price increment |
| **BOID** | Beneficial Owner ID |

---

## 3. Account & Login

### Account Creation
1. **New Investors**: Provide KYC details to broker → Broker creates Account + UCC
2. **Existing Investors**: Provide registration info → UCC generation → Account access required
3. **KYC Requirements**:
   - Individual: Citizenship number, issue date, issued district
   - Organization: Registration number, registration date, registered district

### TMS Login Flow
1. Get login URL from broker (unique per broker)
2. First login → Email with "Create Password" link
3. Password requirements:
   - Length: 5-10 characters
   - Must contain: 1 UPPERCASE, 1 SPECIAL CHARACTER, 1 DIGIT
4. Email verification required
5. Forgot password → Reset link via email

### DNA Login (Critical!)
- **Must be verified BEFORE placing orders**
- Status indicator: Green light (top-right of screen)
- Without DNA login → Error: "ME not logged in"
- Contact broker if DNA login not active

---

## 4. Order Management

### 4.1 Order Types

#### Limit Order
- User specifies exact price
- Price must be within: `Valid Low ≤ Price ≤ Valid High`
- Price must be multiple of **Tick Size**
- Quantity must be multiple of **Board Lot Quantity**

#### Market Order
- Price set automatically by system
- Based on current market conditions
- No price control by user

### 4.2 Trading Sessions
- **Continuous**: Regular trading hours
- **Pre-open**: Pre-market session
- **Odd-lot**: For fractional amounts

### 4.3 Order Statuses

```
Order Lifecycle:
┌─────────────────────────────────────────────────────┐
│                                                     │
│  1. PLACED → 2. OPEN → 3. Match Attempt            │
│                           │                        │
│                    ┌──────┼──────┐                 │
│                    ↓      ↓      ↓                  │
│              COMPLETE PARTIAL REJECTED             │
│                    │      ↓      │                  │
│                    │   OPEN→   │                  │
│                    │   Waiting  │                  │
│                    │   for more │                  │
│                    │   matches  │                  │
│                    ↓             │                  │
│             AUTO-CANCELLED   REJECTED              │
│            (at market close)                       │
│                                                     │
└─────────────────────────────────────────────────────┘
```

#### Status Descriptions
- **OPEN**: Waiting for counter order to match
- **PARTIALLY MATCHED**: Some quantity traded, remainder waiting
- **COMPLETELY MATCHED/COMPLETED**: Full order executed
- **REJECTED**: TMS/ME validation failed
- **CANCELLED**: User cancelled or auto-cancelled at market close
- **NEW**: After editing an order

### 4.4 Buy Order Workflow

1. **Navigate**: Order Management → Buy Order
2. **Screen Color**: Blue (for Buy orders)
3. **Enter Details**:
   - Client Name/Code (auto-populated)
   - Order Type: Limit or Market
   - Instrument: Equity
   - Security Symbol
   - Price (within valid range, multiple of tick size)
   - Quantity (multiple of board lot)
   - Validity: Day
4. **Verify**: Check trading parameters
5. **Submit**: Place Order
6. **Check**: Order Book to verify status

#### Matching Logic
- Completely Matched: Counter SELL order arrives with exact quantity at same price
- Partially Matched: Counter SELL order arrives with different quantity at same price
- Unmatched portions auto-cancel at market close

### 4.5 Sell Order Workflow

1. **Navigate**: Order Management → Sell Order
2. **Screen Color**: Red (for Sell orders)
3. **Enter Details**:
   - Client Name/Code (auto-populated)
   - Order Type: Limit or Market
   - Instrument: Equity
   - Security Symbol
   - Price (within valid range)
   - Quantity (multiple of board lot)
   - **Disclosed Quantity**: Optional, must be ≥10% of total quantity
   - Validity: Day
4. **Submit**: Place Order
5. **Check**: Order Book

#### Matching Logic
- Same as Buy orders
- Counter BUY order triggers matching

### 4.6 Order Editing

#### Edit Open Order
- Can modify: Quantity, Price, Validity
- **Cannot modify**: Client code, instrument type, security
- After edit: Status becomes "NEW"
- Location: Order Book → Open Orders tab → Edit icon

#### Edit Partially Matched Order
- Can modify remaining (untraded) quantity
- Status remains: "Partially Matched"
- Location: Order Book → Edit icon

**Constraint**: Only remaining quantity can be modified

### 4.7 Order Cancellation

#### Cancel Open Order
1. Navigate: Order Book
2. Find open order
3. Click: Cancel icon (Action bar)
4. Confirm cancellation
5. Status → "CANCELLED"

#### Cancel Partially Matched Order
1. Only remaining untraded quantity cancelled
2. Traded quantity stays in Trade Book
3. Cancel icon in Action bar
4. Confirm cancellation
5. Status → "CANCELLED"

#### Auto-Cancellation
- Triggers: Market close (end of day)
- Applies to: ALL open and partially matched orders
- Auto-cancelled if no matching counter orders arrived

### 4.8 Rejected Orders

#### Rejection Causes
- TMS validation failed (price/quantity constraints)
- ME (Market Engine) validation failed
- Order parameters invalid

#### Viewing Rejection Details
1. Order Book → Status: "REJECTED"
2. Click: View icon (Action bar)
3. Check: Rejection reason in order details

#### Characteristics
- No EXCHANGE ORDER ID (not entered into market)
- Cannot be edited or traded
- Visible in Order Book with status

---

## 5. Trade Management

### 5.1 Trade Book
- **Location**: Trade Management → Trade Book
- **Shows**: Only MATCHED quantities
- **For Partially Matched Orders**: Only traded portion appears
- **Content**: Execution details of completed trades

### 5.2 Trade Lifecycle
```
Order Matched → Trade Created → Trade Book Entry → Settlement
```

---

## 6. Order Parameters & Constraints

### Price Constraints
```
Valid Low ≤ Price ≤ Valid High
AND
Price must be = n × Tick_Size  (where n = positive integer)
```

### Quantity Constraints
```
Quantity must be = m × Board_Lot_Quantity  (where m = positive integer)
```

### Disclosed Quantity (Sell Orders)
- **Optional parameter**
- **Minimum**: 10% of total quantity
- **Visibility**: Only disclosed quantity visible to market

---

## 7. Current Implementation Status

### ✅ Completed
- [x] Login automation with CAPTCHA handling
- [x] URL-based navigation (DNA Login, Dashboard)
- [x] Dashboard HTML capture
- [x] Order status tracking structure
- [x] Error handling and logging

### 🔄 In Progress
- [ ] Portfolio data extraction (DP Holding page)
- [ ] Order placement (Buy/Sell)

### ⏳ To Implement
- [ ] Order editing and cancellation
- [ ] Trade book parsing
- [ ] Order status polling
- [ ] Settlement tracking
- [ ] Collateral management
- [ ] Fund transfer operations

---

## 8. Navigation URLs

### Mapped URLs
| Page | URL Endpoint | Purpose |
|------|--------------|---------|
| Dashboard | `/tms/client/dashboard` | Main dashboard |
| DP Holding | `/tms/me/dp-holding` | Portfolio holdings |
| Order History | `/tms/me/order-history` | Historic orders |
| Daily Orders | `/tms/me/order-book` | Today's orders |
| DP Watchlist | `#nav-marketSummary` | Dashboard tab (market data) |

### Base URL Pattern
```
https://tms17.nepsetms.com.np/tms/[endpoint]
```

---

## 9. Key Selectors & Page Elements

### Dashboard (DP Watchlist Tab)
- Tab Link: `<a aria-controls="nav-marketSummary">DP Watchlist</a>`
- Table: Market watchlist with Symbol, LTP, High, Low, Open, Close, % Change

### DP Holding Page
- Status: **Navigation working** ✓
- Data extraction: **Selectors needed** (in progress)

### Order Book Tab
- Open Orders: `data-toggle="tab"` with status filter
- Status options: Open, Partially Matched, Matched, Rejected, Cancelled

---

## 10. Error Handling

### Common Errors
| Error | Cause | Solution |
|-------|-------|----------|
| "ME not logged in" | DNA not connected | Contact broker to enable DNA login |
| Price out of range | Not within Valid Low/High | Check trading parameters before order |
| Invalid quantity | Not multiple of Board Lot | Verify board lot size |
| Order rejected | TMS/ME validation failed | Check order details, see rejection reason |

---

## 11. Development Notes

### Important Constraints
1. **DNA Login Required**: Must verify green light before order placement
2. **Market Hours**: Orders only valid during trading sessions
3. **Auto-Cancellation**: Unmatched orders cancelled at market close
4. **Partial Matching**: Remaining untraded quantity auto-cancels
5. **Board Lot**: All quantities must be multiples of board lot size

### API Interaction Points
1. Login → Authentication
2. Order Placement → TMS → ME (Market Engine)
3. Order Status → Real-time polling from order book
4. Trade Confirmation → ME → TMS → Trade Book

---

## 12. Knowledge Rating

**Current: 8.5/10**

### Strengths
- System architecture and workflow
- Order lifecycle and status tracking
- Buy/Sell order mechanics
- Parameter constraints and validation rules
- Navigation structure

### Gaps
- Exact HTML selectors for data extraction
- Settlement and collateral workflows
- Detailed error codes
- API endpoints (if any)

### To Reach 9.5/10
- Extract and document DP Holding page HTML structure
- Map all page selectors for automated data extraction
- Document all error codes and validation rules

---

*Last Updated: 2026-04-28*  
*Source: Official NEPSE TMS Manual*  
*Status: Active Development*
