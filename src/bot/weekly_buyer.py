"""
Weekly Top Stocks Buyer
Automatically buys top 3 trending stocks once per week
Analyzes market data to identify and purchase trending shares
"""
import schedule
import time
import logging
import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from enum import Enum

from .market_analyzer import MarketAnalyzer
from .stock_trader import StockPaperTrader
from .paper_trader import PaperTrader
from .logger import setup_logger

logger = setup_logger(__name__)


class DayOfWeek(Enum):
    """Days of the week for scheduling"""
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class WeeklyTopStocksBuyer:
    """Buys 1-3 trending stocks once per week based on market conditions"""
    
    def __init__(self, 
                 capital_per_stock: float = 10000.0,
                 buy_day: str = "wednesday",
                 buy_time: str = "12:00",
                 check_interval_minutes: int = 60,
                 min_volume: int = 50000,
                 log_file: str = "logs/weekly_buyer.log"):
        """
        Initialize weekly top stocks buyer (buys 1-3 stocks based on quality)
        
        Args:
            capital_per_stock: Amount to invest in each stock (default Rs. 10,000)
            buy_day: Day to execute purchases (default "wednesday")
            buy_time: Time to execute purchases (default "12:00", format HH:MM)
            check_interval_minutes: How often to check for updates (default 60 minutes)
            min_volume: Minimum daily volume for stock selection (default 50,000)
            log_file: Log file path
        """
        self.capital_per_stock = capital_per_stock
        self.buy_day = buy_day.lower()
        self.buy_time = buy_time
        self.check_interval_minutes = check_interval_minutes
        self.min_volume = min_volume
        self.log_file = log_file
        
        # Setup logger
        self.logger = setup_logger(__name__)
        self._setup_logger()
        
        # Components
        self.market_analyzer = MarketAnalyzer()
        self.paper_trader = PaperTrader(logger=self.logger)
        self.traders: Dict[str, StockPaperTrader] = {}  # {symbol: trader}
        
        # State
        self.running = False
        self.top_stocks: List[Tuple[str, Dict]] = []
        self.purchases_history = []
        self.last_purchase_date = None
        self.portfolio_file = "logs/weekly_portfolio.json"
        
        self.logger.info("\n" + "="*90)
        self.logger.info("WEEKLY TOP STOCKS BUYER INITIALIZED (Buys 1-3 stocks)")
        self.logger.info(f"Buy Day: {self.buy_day}")
        self.logger.info(f"Buy Time: {self.buy_time}")
        self.logger.info(f"Capital per Stock: Rs. {self.capital_per_stock:,.2f}")
        self.logger.info(f"Minimum Volume Threshold: {self.min_volume:,} shares")
        self.logger.info("="*90 + "\n")
    
    def _setup_logger(self):
        """Setup dedicated logger for weekly buyer"""
        os.makedirs("logs", exist_ok=True)
        
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def analyze_and_select_stocks(self, method: str = "combined") -> List[Tuple[str, Dict, float]]:
        """
        Analyze market and select top stocks (1-3 based on quality criteria)
        
        Args:
            method: Selection method ("volume", "gainers", or "combined")
            
        Returns:
            List of 1-3 stocks with data (fewer if fewer qualify)
        """
        self.logger.info("\n" + "="*90)
        self.logger.info("ANALYZING MARKET FOR TOP STOCKS (1-3)")
        self.logger.info("="*90)
        
        # Fetch latest market data
        all_stocks = self.market_analyzer.fetch_all_stocks_data(source="sharesansar")
        
        if not all_stocks:
            self.logger.error("Failed to fetch market data")
            return []
        
        self.logger.info(f"Fetched data for {len(all_stocks)} stocks")
        
        # Select top 3 based on method
        if method == "volume":
            top_stocks = self.market_analyzer.get_top_stocks_by_volume(top_n=3, min_volume=5000)
        elif method == "gainers":
            top_stocks = self.market_analyzer.get_top_stocks_by_price_change(top_n=3, min_volume=5000)
        else:  # combined (default)
            # Only select stocks with positive or zero momentum (min_momentum=0.0)
            # Use configurable minimum volume for liquidity
            top_stocks = self.market_analyzer.get_top_stocks_combined(
                top_n=3, 
                min_volume=self.min_volume,
                min_momentum=0.0   # Only positive/zero change stocks
            )
        
        self.logger.info(f"Selected {len(top_stocks)} stocks for purchase")
        
        if method == "combined":
            # Return format for combined method includes score
            self.top_stocks = [(s, d) for s, d, _ in top_stocks]
            return top_stocks
        else:
            self.top_stocks = top_stocks
            return [(s, d, 0.0) for s, d in top_stocks]  # Add dummy score for consistency
    
    def buy_top_stocks(self) -> Dict:
        """Execute purchases of the selected stocks (1-3 based on market analysis)"""
        if not self.top_stocks:
            self.logger.warning("No stocks selected for purchase")
            return {'success': False, 'message': 'No qualifying stocks found'}
        
        self.logger.info("\n" + "="*90)
        self.logger.info(f"BUYING {len(self.top_stocks)} STOCK(S)")
        self.logger.info("="*90 + "\n")
        
        purchase_records = []
        total_invested = 0
        
        for i, (symbol, data) in enumerate(self.top_stocks, 1):
            try:
                price = data['ltp']
                quantity = int(self.capital_per_stock / price)
                total_cost = quantity * price
                
                self.logger.info(f"\n>>> STOCK #{i}: {symbol}")
                self.logger.info(f"    Current Price: Rs. {price:.2f}")
                self.logger.info(f"    Quantity to Buy: {quantity} shares")
                self.logger.info(f"    Total Investment: Rs. {total_cost:,.2f}")
                
                # Execute buy order
                result = self.paper_trader.place_buy_order(
                    symbol=symbol,
                    quantity=quantity,
                    price=price
                )
                
                if result['success']:
                    self.logger.info(f"    ✓ Order PLACED successfully")
                    
                    # Initialize trader for this stock for ongoing monitoring
                    if symbol not in self.traders:
                        self.traders[symbol] = StockPaperTrader(
                            symbol=symbol,
                            check_interval=900,
                            log_file=f"logs/{symbol.lower()}_weekly.log"
                        )
                    
                    purchase_records.append({
                        'symbol': symbol,
                        'quantity': quantity,
                        'price': price,
                        'total': total_cost,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'status': 'PURCHASED'
                    })
                    
                    total_invested += total_cost
                else:
                    self.logger.warning(f"    ✗ Order FAILED: {result.get('reason', 'Unknown error')}")
                    purchase_records.append({
                        'symbol': symbol,
                        'quantity': quantity,
                        'price': price,
                        'total': total_cost,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'status': 'FAILED',
                        'reason': result.get('reason', 'Unknown error')
                    })
            
            except Exception as e:
                self.logger.error(f"    ✗ Error buying {symbol}: {str(e)}")
                purchase_records.append({
                    'symbol': symbol,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'status': 'ERROR',
                    'error': str(e)
                })
        
        # Log summary
        successful = len([r for r in purchase_records if r['status'] == 'PURCHASED'])
        
        self.logger.info("\n" + "="*90)
        self.logger.info(f"PURCHASE SUMMARY")
        self.logger.info("="*90)
        self.logger.info(f"Total Stocks Purchased: {successful}/{len(self.top_stocks)}")
        self.logger.info(f"Total Amount Invested: Rs. {total_invested:,.2f}")
        self.logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("="*90 + "\n")
        
        # Update history
        self.purchases_history.append({
            'date': datetime.now().strftime('%Y-%m-%d'),
            'purchases': purchase_records,
            'total_invested': total_invested
        })
        self.last_purchase_date = datetime.now()
        
        # Save portfolio
        self._save_portfolio()
        
        return {
            'success': successful > 0,
            'purchases': purchase_records,
            'total_invested': total_invested,
            'successful_count': successful
        }
    
    def check_and_execute(self):
        """Check if it's time to buy and execute"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_day = now.strftime("%A").lower()
        
        # Check if it's the right day and time
        if current_day == self.buy_day and current_time == self.buy_time:
            self.logger.info(f"\n>>> It's {self.buy_day.upper()} at {self.buy_time}!")
            self.logger.info(">>> Executing weekly stock purchase...")
            
            self.analyze_and_select_stocks(method="combined")
            self.buy_top_stocks()
        else:
            self.logger.debug(f"Not yet time to buy. Next purchase: {self.buy_day} at {self.buy_time}")
    
    def start(self, duration_minutes: Optional[int] = None):
        """
        Start the weekly buyer scheduler
        
        Args:
            duration_minutes: How long to run (None = continuous)
        """
        self.running = True
        
        self.logger.info(f"\n{'='*90}")
        self.logger.info(f"STARTING WEEKLY TOP STOCKS BUYER")
        if duration_minutes:
            self.logger.info(f"Duration: {duration_minutes} minutes")
        else:
            self.logger.info(f"Duration: CONTINUOUS (runs indefinitely until Ctrl+C)")
        self.logger.info(f"Check Interval: Every {self.check_interval_minutes} minutes")
        self.logger.info(f"Setup: Buy {self.buy_day.upper()} at {self.buy_time}")
        self.logger.info(f"{'='*90}\n")
        
        # Schedule the check
        schedule.every(self.check_interval_minutes).minutes.do(self.check_and_execute)
        
        start_time = time.time()
        duration_seconds = (duration_minutes * 60) if duration_minutes else float('inf')
        
        try:
            while time.time() - start_time < duration_seconds and self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        except KeyboardInterrupt:
            self.logger.info("\n\n>>> STOPPED BY USER")
        
        finally:
            self.stop()
    
    def stop(self):
        """Stop the buyer and generate final report"""
        self.running = False
        schedule.clear()
        
        self.logger.info(f"\n{'='*90}")
        self.logger.info(f"WEEKLY BUYER STOPPED")
        self.logger.info(f"{'='*90}\n")
        
        # Generate final report
        self._generate_final_report()
    
    def _save_portfolio(self):
        """Save current portfolio state to file"""
        portfolio_data = {
            'last_purchase_date': self.last_purchase_date.strftime('%Y-%m-%d %H:%M:%S') if self.last_purchase_date else None,
            'history': self.purchases_history,
            'current_holdings': {}
        }
        
        # Add current holdings from paper trader
        for symbol, position in self.paper_trader.portfolio.items():
            portfolio_data['current_holdings'][symbol] = {
                'shares': position['shares'],
                'avg_cost': position['avg_cost'],
                'total_invested': position['total_invested']
            }
        
        os.makedirs(os.path.dirname(self.portfolio_file), exist_ok=True)
        with open(self.portfolio_file, 'w', encoding='utf-8') as f:
            json.dump(portfolio_data, f, indent=2)
        
        self.logger.info(f"Portfolio saved to {self.portfolio_file}")
    
    def load_portfolio(self):
        """Load portfolio state from file"""
        if not os.path.exists(self.portfolio_file):
            self.logger.info("No saved portfolio found")
            return False
        
        try:
            with open(self.portfolio_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.purchases_history = data.get('history', [])
            if data.get('last_purchase_date'):
                self.last_purchase_date = datetime.strptime(
                    data['last_purchase_date'],
                    '%Y-%m-%d %H:%M:%S'
                )
            
            self.logger.info(f"✓ Portfolio loaded: {len(self.purchases_history)} purchase records")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to load portfolio: {str(e)}")
            return False
    
    def _generate_final_report(self):
        """Generate final report with statistics"""
        report = "\n" + "="*90 + "\n"
        report += "                    WEEKLY BUYER - FINAL REPORT\n"
        report += "="*90 + "\n\n"
        
        report += f"Execution Period:\n"
        report += f"  Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"  Total Purchases: {len(self.purchases_history)}\n\n"
        
        if self.purchases_history:
            report += "PURCHASE HISTORY:\n"
            report += "-" * 90 + "\n"
            
            for i, history in enumerate(self.purchases_history, 1):
                report += f"\nPurchase #{i} ({history['date']}):\n"
                report += f"  Total Invested: Rs. {history['total_invested']:,.2f}\n"
                report += f"  Stocks Purchased:\n"
                
                for purchase in history['purchases']:
                    if purchase['status'] == 'PURCHASED':
                        report += (
                            f"    • {purchase['symbol']}: {purchase['quantity']} shares "
                            f"@ Rs. {purchase['price']:.2f} = Rs. {purchase['total']:,.2f}\n"
                        )
        
        # Portfolio summary
        portfolio = self.paper_trader.get_portfolio_value(
            {symbol: data['ltp'] for symbol, data in self.market_analyzer.stock_data.items()}
        )
        
        report += "\nCURRENT PORTFOLIO:\n"
        report += "-" * 90 + "\n"
        report += f"Cash Balance: Rs. {portfolio['cash']:,.2f}\n"
        report += f"Holdings Value: Rs. {sum(h['position_value'] for h in portfolio['holdings'].values()):,.2f}\n"
        report += f"Total Portfolio: Rs. {portfolio['total_value']:,.2f}\n"
        report += f"Unrealized P&L: Rs. {portfolio['total_unrealized_pnl']:,.2f} "
        report += f"({portfolio['total_return_pct']:+.2f}%)\n"
        
        report += "\n" + "="*90 + "\n"
        
        self.logger.info(report)
    
    def get_portfolio(self) -> Dict:
        """Get current portfolio state"""
        return {
            'cash': self.paper_trader.cash,
            'holdings': self.paper_trader.portfolio,
            'purchase_history': self.purchases_history,
            'last_purchase_date': self.last_purchase_date
        }
    
    def get_status(self) -> Dict:
        """Get current buyer status"""
        return {
            'running': self.running,
            'buy_day': self.buy_day,
            'buy_time': self.buy_time,
            'capital_per_stock': self.capital_per_stock,
            'top_stocks': [(s, d['ltp']) for s, d in self.top_stocks],
            'total_purchases': len(self.purchases_history),
            'last_purchase_date': self.last_purchase_date,
            'portfolio': self.get_portfolio()
        }
