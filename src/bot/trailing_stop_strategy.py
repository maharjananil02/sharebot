"""
Trailing Stop Strategy with Ladder-in Functionality
Advanced strategy for managing positions with stop losses and profitable accumulation
"""
from .logger import setup_logger
from datetime import datetime
from enum import Enum

logger = setup_logger(__name__)


class OrderType(Enum):
    """Order types"""
    BUY_INITIAL = "BUY_INITIAL"
    BUY_LADDER = "BUY_LADDER"
    SELL_STOP = "SELL_STOP"
    SELL_TRAILING = "SELL_TRAILING"


class Order:
    """Represents a single order"""
    
    def __init__(self, order_type, symbol, quantity, price=None, reason="", 
                 position_pct_change=None, trigger_condition=""):
        self.order_type = order_type
        self.symbol = symbol
        self.quantity = quantity
        self.price = price  # None if not executed yet
        self.reason = reason
        self.position_pct_change = position_pct_change  # What % change triggered this
        self.trigger_condition = trigger_condition
        self.timestamp = datetime.now()
        self.status = "PENDING"
        self.execution_price = None
        self.total_value = None
    
    def execute(self, execution_price):
        """Mark order as executed"""
        self.status = "EXECUTED"
        self.execution_price = execution_price
        self.total_value = self.quantity * execution_price
    
    def to_dict(self):
        """Convert order to dictionary for display"""
        return {
            "Type": self.order_type.value,
            "Symbol": self.symbol,
            "Quantity": self.quantity,
            "Limit Price": f"Rs. {self.price:.2f}" if self.price else "MARKET",
            "Reason": self.reason,
            "Position Change": f"{self.position_pct_change:.2f}%" if self.position_pct_change else "N/A",
            "Trigger": self.trigger_condition,
            "Status": self.status,
            "Execution Price": f"Rs. {self.execution_price:.2f}" if self.execution_price else "—",
            "Total Value": f"Rs. {self.total_value:.2f}" if self.total_value else "—",
            "Timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }


class TrailingStopStrategy:
    """
    Trailing Stop Strategy with Ladder-in Functionality
    
    Configuration:
    - initial_quantity: Initial shares to buy
    - entry_price: Price at which entry is made
    - stop_loss_pct: Percentage drop before selling all (e.g., 10 for 10%)
    - trailing_activation_pct: Percentage gain before trailing stops activates (e.g., 10 for 10%)
    - trailing_step_pct: How much to move trailing stop up each time (e.g., 5 for 5%)
    - ladder_triggers: Dict of price drops and quantities to buy
      Example: {20: 20, 30: 10} means buy 20 more at 20% drop, buy 10 more at 30% drop
    """
    
    def __init__(self, trader, symbol, initial_quantity, entry_price, 
                 stop_loss_pct=10, trailing_activation_pct=10, trailing_step_pct=5,
                 ladder_triggers=None):
        self.trader = trader
        self.symbol = symbol
        self.initial_quantity = initial_quantity
        self.entry_price = entry_price
        self.stop_loss_pct = stop_loss_pct
        self.trailing_activation_pct = trailing_activation_pct
        self.trailing_step_pct = trailing_step_pct
        self.ladder_triggers = ladder_triggers or {}
        
        # State tracking
        self.current_price = entry_price
        self.total_quantity = 0
        self.total_cost_basis = 0.0
        self.highest_price = entry_price
        self.current_stop_loss = self._calculate_initial_stop_loss()
        self.trailing_stop_active = False
        self.orders = []
        self.closed_positions = []
        self.ladder_purchases_made = set()  # Track which ladder levels we've purchased at
        
        logger.info(f"Initialized Trailing Stop Strategy for {symbol}")
        logger.info(f"Entry: {initial_quantity} shares @ Rs. {entry_price:.2f}")
        logger.info(f"Stop Loss: -{stop_loss_pct}% @ Rs. {self.current_stop_loss:.2f}")
        logger.info(f"Trailing Activation: +{trailing_activation_pct}% @ Rs. {self._calculate_trailing_activation_level():.2f}")
        logger.info(f"Ladder Triggers: {ladder_triggers}")

    def seed_position(self, quantity, avg_cost=None):
        """Seed the strategy with an already-held position."""
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")

        avg_cost = self.entry_price if avg_cost is None else avg_cost
        self.initial_quantity = quantity
        self.entry_price = avg_cost
        self.total_quantity = quantity
        self.total_cost_basis = quantity * avg_cost
        self.highest_price = avg_cost
        self.current_stop_loss = self._calculate_initial_stop_loss()
        self.trailing_stop_active = False
        self.ladder_purchases_made = set()

        logger.info(f"Seeded existing position: {quantity} shares @ Rs. {avg_cost:.2f}")
        logger.info(f"Stop Loss reset to: Rs. {self.current_stop_loss:.2f}")
    
    def _calculate_initial_stop_loss(self):
        """Calculate initial stop loss level"""
        return self.entry_price * (1 - self.stop_loss_pct / 100)
    
    def _calculate_trailing_activation_level(self):
        """Calculate price level where trailing stop activates"""
        return self.entry_price * (1 + self.trailing_activation_pct / 100)
    
    def _get_average_entry_price(self):
        """Get average entry price across all purchases"""
        if self.total_quantity == 0:
            return self.entry_price
        return self.total_cost_basis / self.total_quantity
    
    def _calculate_position_pct_change(self):
        """Calculate current position % change from average entry"""
        avg_price = self._get_average_entry_price()
        return ((self.current_price - avg_price) / avg_price) * 100
    
    def analyze(self, current_price):
        """
        Analyze current price and determine what orders should be placed
        Returns list of pending orders
        """
        self.current_price = current_price
        self.highest_price = max(self.highest_price, current_price)
        
        position_pct = self._calculate_position_pct_change()
        pending_orders = []
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Market Analysis - {self.symbol}")
        logger.info(f"{'='*60}")
        logger.info(f"Current Price: Rs. {current_price:.2f}")
        logger.info(f"Average Entry: Rs. {self._get_average_entry_price():.2f}")
        logger.info(f"Highest Price: Rs. {self.highest_price:.2f}")
        logger.info(f"Position: {self.total_quantity} shares | {position_pct:+.2f}%")
        logger.info(f"Current Stop Loss: Rs. {self.current_stop_loss:.2f}")
        logger.info(f"Trailing Stop Active: {self.trailing_stop_active}")
        
        # 1. Check for stop loss (hard floor)
        if current_price <= self.current_stop_loss and self.total_quantity > 0:
            logger.warning(f"STOP LOSS TRIGGERED! Price hit stop level.")
            order = Order(
                OrderType.SELL_STOP,
                self.symbol,
                self.total_quantity,
                price=current_price,
                reason=f"Hard stop loss at -{self.stop_loss_pct}%",
                position_pct_change=position_pct,
                trigger_condition=f"Price {current_price:.2f} <= Stop {self.current_stop_loss:.2f}"
            )
            pending_orders.append(order)
            self.total_quantity = 0  # Position is closed
            return pending_orders
        
        # 2. Activate trailing stop if price reached activation level
        if not self.trailing_stop_active and current_price >= self._calculate_trailing_activation_level():
            logger.info(f"TRAILING STOP ACTIVATED at {current_price:.2f}")
            self.trailing_stop_active = True
            self.current_stop_loss = current_price * (1 - self.trailing_step_pct / 100)
            logger.info(f"New trailing stop level: Rs. {self.current_stop_loss:.2f}")
        
        # 3. Move trailing stop up (ratchet mechanism)
        if self.trailing_stop_active:
            new_trailing_level = current_price * (1 - self.trailing_step_pct / 100)
            if new_trailing_level > self.current_stop_loss:
                old_stop = self.current_stop_loss
                self.current_stop_loss = new_trailing_level
                logger.info(f"TRAILING STOP MOVED UP: Rs. {old_stop:.2f} → Rs. {new_trailing_level:.2f}")
        
        # 4. Check for ladder-in opportunities (price dropping)
        for drop_pct, buy_quantity in sorted(self.ladder_triggers.items()):
            trigger_price = self.entry_price * (1 - drop_pct / 100)
            
            # Only trigger if we haven't already at this level and price is below trigger
            if current_price <= trigger_price and drop_pct not in self.ladder_purchases_made:
                logger.warning(f"LADDER-IN TRIGGERED at {drop_pct}% drop!")
                order = Order(
                    OrderType.BUY_LADDER,
                    self.symbol,
                    buy_quantity,
                    price=trigger_price,
                    reason=f"Ladder-in at {drop_pct}% price drop",
                    position_pct_change=position_pct,
                    trigger_condition=f"Price {current_price:.2f} <= Trigger {trigger_price:.2f}"
                )
                pending_orders.append(order)
                self.ladder_purchases_made.add(drop_pct)
                logger.info(f"Ladder-in: Buy {buy_quantity} more shares @ Rs. {trigger_price:.2f}")
        
        logger.info(f"{'='*60}\n")
        return pending_orders
    
    def create_initial_order(self):
        """Create the initial buy order"""
        order = Order(
            OrderType.BUY_INITIAL,
            self.symbol,
            self.initial_quantity,
            price=self.entry_price,
            reason="Initial position entry",
            position_pct_change=0.0,
            trigger_condition="Manual order placement"
        )
        self.orders.append(order)
        return order
    
    def execute_order(self, order, execution_price):
        """Execute an order and update position tracking"""
        logger.info(f"Executing order: {order.order_type.value} x{order.quantity} @ Rs. {execution_price:.2f}")
        
        order.execute(execution_price)
        self.orders.append(order)
        
        if order.order_type == OrderType.BUY_INITIAL:
            self.initial_quantity = order.quantity
            self.entry_price = execution_price
            self.total_quantity = order.quantity
            self.total_cost_basis = order.quantity * execution_price
            self.highest_price = max(self.highest_price, execution_price)
            self.current_stop_loss = self._calculate_initial_stop_loss()
            logger.info(f"Position initialized: {self.total_quantity} shares, "
                       f"Avg cost: Rs. {self._get_average_entry_price():.2f}")

        elif order.order_type == OrderType.BUY_LADDER:
            self.total_quantity += order.quantity
            self.total_cost_basis += order.quantity * execution_price
            logger.info(f"Position updated: {self.total_quantity} shares, "
                       f"Avg cost: Rs. {self._get_average_entry_price():.2f}")
        
        elif order.order_type == OrderType.SELL_STOP or order.order_type == OrderType.SELL_TRAILING:
            avg_cost = self._get_average_entry_price()
            self.closed_positions.append({
                'quantity': order.quantity,
                'avg_cost': avg_cost,
                'sell_price': execution_price,
                'pnl': (execution_price - avg_cost) * order.quantity,
                'pnl_pct': ((execution_price - avg_cost) / avg_cost * 100) if avg_cost else 0.0
            })
            # Guard against double-closing when analyze() already zeroed the position.
            self.total_quantity = max(0, self.total_quantity - order.quantity)
            if self.total_quantity == 0:
                self.total_cost_basis = 0.0
            logger.info(f"Position closed: P&L = Rs. {self.closed_positions[-1]['pnl']:.2f} "
                       f"({self.closed_positions[-1]['pnl_pct']:+.2f}%)")
    
    def get_order_summary(self, pending_orders):
        """Get formatted summary of orders for user confirmation"""
        summary = "\n" + "="*80 + "\n"
        summary += "                    ORDER SUMMARY - PLEASE CONFIRM                        \n"
        summary += "="*80 + "\n\n"
        
        # Current State
        summary += "CURRENT POSITION STATE:\n"
        summary += "─" * 80 + "\n"
        summary += f"Symbol:              {self.symbol}\n"
        summary += f"Current Price:       Rs. {self.current_price:.2f}\n"
        summary += f"Position Size:       {self.total_quantity} shares\n"
        summary += f"Avg Entry Price:     Rs. {self._get_average_entry_price():.2f}\n"
        summary += f"Position P&L:        {self._calculate_position_pct_change():+.2f}%\n"
        summary += f"Stop Loss Level:     Rs. {self.current_stop_loss:.2f}\n"
        summary += f"Highest Price Seen:  Rs. {self.highest_price:.2f}\n"
        summary += f"Trailing Stop Active: {'YES' if self.trailing_stop_active else 'NO'}\n\n"
        
        # Pending Orders
        if pending_orders:
            summary += "PENDING ORDERS TO EXECUTE:\n"
            summary += "─" * 80 + "\n"
            for i, order in enumerate(pending_orders, 1):
                summary += f"\nOrder #{i}: {order.order_type.value}\n"
                summary += f"  Symbol:          {order.symbol}\n"
                summary += f"  Quantity:        {order.quantity} shares\n"
                summary += f"  Order Price:     {order.price:.2f} (market if empty)\n"
                summary += f"  Reason:          {order.reason}\n"
                summary += f"  Trigger:         {order.trigger_condition}\n"
                if order.position_pct_change is not None:
                    summary += f"  Position Change: {order.position_pct_change:+.2f}%\n"
        else:
            summary += "NO PENDING ORDERS\n"
        
        summary += "\n" + "="*80 + "\n"
        summary += "STRATEGY PARAMETERS:\n"
        summary += "─" * 80 + "\n"
        summary += f"Hard Stop Loss:      {self.stop_loss_pct}% (Rs. {self._calculate_initial_stop_loss():.2f})\n"
        summary += f"Trailing Activation: +{self.trailing_activation_pct}% (Rs. {self._calculate_trailing_activation_level():.2f})\n"
        summary += f"Trailing Step:       {self.trailing_step_pct}% (moves up as price rises)\n"
        summary += f"Ladder-in Triggers:  {self.ladder_triggers}\n"
        
        summary += "\n" + "="*80 + "\n"
        summary += "EXECUTION HISTORY:\n"
        summary += "─" * 80 + "\n"
        if self.orders:
            for i, order in enumerate(self.orders, 1):
                order_dict = order.to_dict()
                summary += f"\nExecution #{i}:\n"
                for key, value in order_dict.items():
                    summary += f"  {key:.<20} {value}\n"
        else:
            summary += "No executed orders yet\n"
        
        summary += "\n" + "="*80 + "\n"
        
        return summary
    
    def get_position_report(self):
        """Get detailed position report"""
        report = "\n" + "="*80 + "\n"
        report += "                     POSITION REPORT - NABIL                            \n"
        report += "="*80 + "\n\n"
        
        report += "ENTRY TERMS:\n"
        report += "─" * 80 + "\n"
        report += f"Initial Shares:      {self.initial_quantity}\n"
        report += f"Entry Price:         Rs. {self.entry_price:.2f}\n"
        report += f"Initial Cost:        Rs. {self.initial_quantity * self.entry_price:.2f}\n\n"
        
        report += "CURRENT POSITION:\n"
        report += "─" * 80 + "\n"
        report += f"Total Shares:        {self.total_quantity}\n"
        report += f"Total Cost Basis:    Rs. {self.total_cost_basis:.2f}\n"
        report += f"Avg Entry Price:     Rs. {self._get_average_entry_price():.2f}\n"
        report += f"Current Price:       Rs. {self.current_price:.2f}\n"
        report += f"Position Value:      Rs. {self.total_quantity * self.current_price:.2f}\n"
        report += f"Unrealized P&L:      Rs. {(self.current_price - self._get_average_entry_price()) * self.total_quantity:.2f} "
        report += f"({self._calculate_position_pct_change():+.2f}%)\n\n"
        
        report += "RISK MANAGEMENT:\n"
        report += "─" * 80 + "\n"
        report += f"Stop Loss Level:     Rs. {self.current_stop_loss:.2f}\n"
        report += f"Trailing Active:     {'YES' if self.trailing_stop_active else 'NO'}\n"
        report += f"Max Loss (if triggered): Rs. {abs((self.current_stop_loss - self._get_average_entry_price()) * self.total_quantity):.2f}\n\n"
        
        if self.ladder_purchases_made:
            report += "LADDER PURCHASES MADE:\n"
            report += "─" * 80 + "\n"
            for drop_pct in sorted(self.ladder_purchases_made):
                report += f"  • {drop_pct}% drop: Executed\n"
            report += "\n"
        
        report += "="*80 + "\n"
        
        return report


def demo_nabil_strategy():
    """
    Demo showing how to set up the Nabil strategy with your specifications:
    - 10 initial shares at assumed entry price
    - 10% stop loss (hard floor)
    - Trailing stop activates at 10% gain, moves up 5% per climb
    - Ladder in: 20 shares at 20% drop, 10 shares at 30% drop
    """
    
    # NOTE: In real usage, these would come from the Trader and current market data
    logger.info("\n" + "="*80)
    logger.info("NABIL TRAILING STOP STRATEGY - SETUP")
    logger.info("="*80 + "\n")
    
    # Strategy configuration
    symbol = "NABIL"
    initial_shares = 10
    entry_price = 1000.0  # Assume current/historical price
    
    strategy_config = {
        'trader': None,  # Would be the actual Trader instance
        'symbol': symbol,
        'initial_quantity': initial_shares,
        'entry_price': entry_price,
        'stop_loss_pct': 10,           # Sell all if drops 10%
        'trailing_activation_pct': 10,  # Trailing starts at 10% gain
        'trailing_step_pct': 5,         # Move stop up by 5% each climb
        'ladder_triggers': {
            20: 20,  # Buy 20 more shares at 20% drop
            30: 10   # Buy 10 more shares at 30% drop (cumulative with above)
        }
    }
    
    return strategy_config
