"""
Paper Trading Module - Simulates trading without real money
All trades logged to nabil.log
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional


class PaperTrader:
    """Simulates trades in paper trading mode"""
    
    def __init__(self, logger=None):
        """
        Initialize paper trader
        
        Args:
            logger: Logger instance for logging trades
        """
        self.logger = logger or logging.getLogger(__name__)
        self.portfolio = {}  # {symbol: {shares: qty, avg_cost: price, total_invested: amount}}
        self.cash = 1000000  # Starting paper cash (1 million Rs)
        self.trades_history = []  # List of all trades executed
        self.order_id_counter = 0
        
        self.logger.info("="*80)
        self.logger.info("PAPER TRADING INITIALIZED")
        self.logger.info(f"Starting Cash: Rs. {self.cash:,.2f}")
        self.logger.info("="*80)

    def seed_position(self, symbol: str, quantity: int, avg_cost: float, total_invested: Optional[float] = None) -> Dict:
        """
        Seed the portfolio with an existing position without recording a trade.

        This is used when resuming paper trading from a previously bought stock
        so the bot can continue using the stored entry price as its reference.

        Args:
            symbol: Stock symbol
            quantity: Shares already held
            avg_cost: Average entry price for the held shares
            total_invested: Optional total invested amount (defaults to quantity * avg_cost)

        Returns:
            Seeded position dictionary
        """
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")
        if avg_cost < 0:
            raise ValueError("Average cost cannot be negative")

        total_invested = quantity * avg_cost if total_invested is None else total_invested

        self.portfolio[symbol] = {
            'shares': quantity,
            'avg_cost': avg_cost,
            'total_invested': total_invested,
            'trade_list': []
        }

        self.logger.info(
            f"✓ EXISTING POSITION SEEDED\n"
            f"   Symbol: {symbol}\n"
            f"   Quantity: {quantity} shares\n"
            f"   Avg Cost: Rs. {avg_cost:.2f}\n"
            f"   Total Invested: Rs. {total_invested:,.2f}"
        )

        return {
            'symbol': symbol,
            'shares': quantity,
            'avg_cost': avg_cost,
            'total_invested': total_invested
        }
    
    def place_buy_order(self, symbol: str, quantity: int, price: float) -> Dict:
        """
        Execute a buy order in paper trading
        
        Args:
            symbol: Stock symbol (e.g., 'NABIL')
            quantity: Number of shares
            price: Price per share
            
        Returns:
            Order result dictionary
        """
        total_cost = quantity * price
        
        # Check if enough cash
        if total_cost > self.cash:
            self.logger.warning(
                f"⚠️  INSUFFICIENT CASH for {symbol} BUY\n"
                f"   Required: Rs. {total_cost:,.2f}\n"
                f"   Available: Rs. {self.cash:,.2f}\n"
                f"   CANCELLED"
            )
            return {
                'success': False,
                'reason': 'Insufficient cash',
                'required': total_cost,
                'available': self.cash
            }
        
        # Execute buy
        self.order_id_counter += 1
        order_id = f"PAPER-BUY-{self.order_id_counter}"
        timestamp = datetime.now()
        
        # Update cash
        self.cash -= total_cost
        
        # Update portfolio
        if symbol not in self.portfolio:
            self.portfolio[symbol] = {
                'shares': 0,
                'avg_cost': 0,
                'total_invested': 0,
                'trade_list': []
            }
        
        # Calculate new average cost
        old_shares = self.portfolio[symbol]['shares']
        old_invested = self.portfolio[symbol]['total_invested']
        
        new_shares = old_shares + quantity
        new_invested = old_invested + total_cost
        new_avg_cost = new_invested / new_shares if new_shares > 0 else 0
        
        self.portfolio[symbol]['shares'] = new_shares
        self.portfolio[symbol]['avg_cost'] = new_avg_cost
        self.portfolio[symbol]['total_invested'] = new_invested
        
        # Record trade
        trade_record = {
            'order_id': order_id,
            'type': 'BUY',
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'total': total_cost,
            'timestamp': timestamp,
            'cash_after': self.cash
        }
        self.portfolio[symbol]['trade_list'].append(trade_record)
        self.trades_history.append(trade_record)
        
        # Log trade
        self.logger.info(
            f"✓ PAPER BUY EXECUTED\n"
            f"   Order ID: {order_id}\n"
            f"   Symbol: {symbol}\n"
            f"   Quantity: {quantity} shares\n"
            f"   Price: Rs. {price:.2f} per share\n"
            f"   Total Cost: Rs. {total_cost:,.2f}\n"
            f"   Position: {new_shares} shares (Avg: Rs. {new_avg_cost:.2f})\n"
            f"   Cash Remaining: Rs. {self.cash:,.2f}\n"
            f"   Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        return {
            'success': True,
            'order_id': order_id,
            'executed_price': price,
            'quantity': quantity,
            'total': total_cost,
            'timestamp': timestamp
        }
    
    def place_sell_order(self, symbol: str, quantity: int, price: float) -> Dict:
        """
        Execute a sell order in paper trading
        
        Args:
            symbol: Stock symbol
            quantity: Number of shares
            price: Price per share
            
        Returns:
            Order result dictionary
        """
        # Check if we own the shares
        if symbol not in self.portfolio or self.portfolio[symbol]['shares'] < quantity:
            owned = self.portfolio.get(symbol, {}).get('shares', 0)
            self.logger.warning(
                f"⚠️  INSUFFICIENT SHARES for {symbol} SELL\n"
                f"   Trying to sell: {quantity} shares\n"
                f"   Owned: {owned} shares\n"
                f"   CANCELLED"
            )
            return {
                'success': False,
                'reason': 'Insufficient shares',
                'requested': quantity,
                'owned': owned
            }
        
        # Execute sell
        self.order_id_counter += 1
        order_id = f"PAPER-SELL-{self.order_id_counter}"
        timestamp = datetime.now()
        
        total_proceeds = quantity * price
        avg_cost = self.portfolio[symbol]['avg_cost']
        pnl = total_proceeds - (quantity * avg_cost)
        pnl_pct = (pnl / (quantity * avg_cost) * 100) if avg_cost > 0 else 0
        
        # Update cash
        self.cash += total_proceeds
        
        # Update portfolio
        self.portfolio[symbol]['shares'] -= quantity
        self.portfolio[symbol]['total_invested'] -= (quantity * avg_cost)
        
        # Record trade
        trade_record = {
            'order_id': order_id,
            'type': 'SELL',
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'total': total_proceeds,
            'avg_cost': avg_cost,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'timestamp': timestamp,
            'cash_after': self.cash
        }
        self.portfolio[symbol]['trade_list'].append(trade_record)
        self.trades_history.append(trade_record)
        
        # Log trade
        status = "✓ PROFIT" if pnl > 0 else "✗ LOSS" if pnl < 0 else "= BREAKEVEN"
        self.logger.info(
            f"{status} PAPER SELL EXECUTED\n"
            f"   Order ID: {order_id}\n"
            f"   Symbol: {symbol}\n"
            f"   Quantity: {quantity} shares\n"
            f"   Sell Price: Rs. {price:.2f} per share\n"
            f"   Avg Cost: Rs. {avg_cost:.2f}\n"
            f"   Total Proceeds: Rs. {total_proceeds:,.2f}\n"
            f"   P&L: Rs. {pnl:,.2f} ({pnl_pct:+.2f}%)\n"
            f"   Remaining Shares: {self.portfolio[symbol]['shares']}\n"
            f"   Cash After: Rs. {self.cash:,.2f}\n"
            f"   Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        # Close position if no shares left
        if self.portfolio[symbol]['shares'] == 0:
            self.logger.info(f"   [Position CLOSED for {symbol}]")
        
        return {
            'success': True,
            'order_id': order_id,
            'executed_price': price,
            'quantity': quantity,
            'total': total_proceeds,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'timestamp': timestamp
        }
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> Dict:
        """
        Get current portfolio value with unrealized P&L
        
        Args:
            current_prices: {symbol: current_price}
            
        Returns:
            Portfolio value details
        """
        total_value = self.cash
        total_unrealized_pnl = 0
        holdings = {}
        
        for symbol, position in self.portfolio.items():
            if position['shares'] > 0:
                current_price = current_prices.get(symbol, position['avg_cost'])
                position_value = position['shares'] * current_price
                unrealized_pnl = position_value - position['total_invested']
                unrealized_pnl_pct = (unrealized_pnl / position['total_invested'] * 100) if position['total_invested'] > 0 else 0
                
                total_value += position_value
                total_unrealized_pnl += unrealized_pnl
                
                holdings[symbol] = {
                    'shares': position['shares'],
                    'avg_cost': position['avg_cost'],
                    'current_price': current_price,
                    'position_value': position_value,
                    'unrealized_pnl': unrealized_pnl,
                    'unrealized_pnl_pct': unrealized_pnl_pct
                }
        
        return {
            'cash': self.cash,
            'holdings': holdings,
            'total_unrealized_pnl': total_unrealized_pnl,
            'total_value': total_value,
            'total_return_pct': (total_unrealized_pnl / 1000000 * 100)  # % from initial capital
        }
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """Get current position for a symbol"""
        if symbol not in self.portfolio:
            return None
        
        pos = self.portfolio[symbol]
        return {
            'symbol': symbol,
            'shares': pos['shares'],
            'avg_cost': pos['avg_cost'],
            'total_invested': pos['total_invested']
        }
    
    def generate_report(self, current_prices: Dict[str, float]) -> str:
        """Generate trading report"""
        portfolio_value = self.get_portfolio_value(current_prices)
        
        report = "\n" + "="*90 + "\n"
        report += "                        PAPER TRADING PORTFOLIO REPORT                         \n"
        report += "="*90 + "\n\n"
        
        report += "ACCOUNT SUMMARY:\n"
        report += "─" * 90 + "\n"
        report += f"Cash Balance:           Rs. {portfolio_value['cash']:>15,.2f}\n"
        report += f"Holdings Value:         Rs. {sum(h['position_value'] for h in portfolio_value['holdings'].values()):>15,.2f}\n"
        report += f"Total Portfolio Value:  Rs. {portfolio_value['total_value']:>15,.2f}\n"
        report += f"Unrealized P&L:         Rs. {portfolio_value['total_unrealized_pnl']:>15,.2f} "
        report += f"({portfolio_value['total_return_pct']:+.2f}%)\n\n"
        
        if portfolio_value['holdings']:
            report += "CURRENT HOLDINGS:\n"
            report += "─" * 90 + "\n"
            for symbol, holding in portfolio_value['holdings'].items():
                report += f"\n{symbol}:\n"
                report += f"  Shares:          {holding['shares']}\n"
                report += f"  Avg Cost:        Rs. {holding['avg_cost']:.2f}\n"
                report += f"  Current Price:   Rs. {holding['current_price']:.2f}\n"
                report += f"  Position Value:  Rs. {holding['position_value']:,.2f}\n"
                report += f"  Unrealized P&L:  Rs. {holding['unrealized_pnl']:,.2f} ({holding['unrealized_pnl_pct']:+.2f}%)\n"
        else:
            report += "CURRENT HOLDINGS: None\n"
        
        report += "\n" + "="*90 + "\n"
        report += f"Total Trades Executed: {len(self.trades_history)}\n"
        report += f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "="*90 + "\n\n"
        
        return report
    
    def get_trade_history(self, symbol: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get recent trades"""
        trades = self.trades_history
        if symbol:
            trades = [t for t in trades if t['symbol'] == symbol]
        return trades[-limit:]
    
    def log_summary(self, current_prices: Dict[str, float]):
        """Log portfolio summary to logger"""
        portfolio_value = self.get_portfolio_value(current_prices)
        
        self.logger.info("\n" + "="*90)
        self.logger.info("PORTFOLIO SUMMARY")
        self.logger.info("="*90)
        self.logger.info(f"Cash: Rs. {portfolio_value['cash']:,.2f}")
        self.logger.info(f"Holdings Value: Rs. {sum(h['position_value'] for h in portfolio_value['holdings'].values()):,.2f}")
        self.logger.info(f"Total Value: Rs. {portfolio_value['total_value']:,.2f}")
        self.logger.info(f"Unrealized P&L: Rs. {portfolio_value['total_unrealized_pnl']:,.2f} ({portfolio_value['total_return_pct']:+.2f}%)")
        
        if portfolio_value['holdings']:
            self.logger.info("Holdings:")
            for symbol, holding in portfolio_value['holdings'].items():
                self.logger.info(
                    f"  {symbol}: {holding['shares']} @ Rs. {holding['avg_cost']:.2f} "
                    f"→ Rs. {holding['current_price']:.2f} = {holding['unrealized_pnl_pct']:+.2f}%"
                )
        
        self.logger.info("="*90 + "\n")
