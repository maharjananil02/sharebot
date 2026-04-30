"""
Integration Guide: Using Trailing Stop Strategy with Your Trading Bot
Shows how to integrate the TrailingStopStrategy into your main bot
"""

# IMPLEMENTATION GUIDE
# ===================================================================================

"""
STEP 1: Import the strategy in your main.py or trading module
"""

from src.bot.trailing_stop_strategy import TrailingStopStrategy, Order, OrderType


"""
STEP 2: Initialize the strategy in your trading bot
"""

def setup_nabil_trailing_stop_strategy(trader, current_price):
    """
    Set up the Nabil trailing stop strategy with your specifications
    
    Args:
        trader: Your Trader instance
        current_price: Current market price of Nabil
    
    Returns:
        TrailingStopStrategy instance
    """
    
    strategy = TrailingStopStrategy(
        trader=trader,
        symbol="NABIL",
        initial_quantity=10,              # Buy 10 shares initially
        entry_price=current_price,        # Entry at current market price
        stop_loss_pct=10,                 # Hard floor: -10%
        trailing_activation_pct=10,       # Trailing starts at +10%
        trailing_step_pct=5,              # Ratchet by 5% each rise
        ladder_triggers={
            20: 20,   # Buy 20 more shares if price drops 20%
            30: 10    # Buy 10 more shares if price drops 30%
        }
    )
    
    return strategy


"""
STEP 3: In your market price monitoring loop, check for orders
"""

def monitor_nabil_strategy(strategy, trader):
    """
    Continuously monitor market and execute strategy orders
    This would run in your main trading loop
    """
    
    import time
    
    while True:
        try:
            # Get current price (implement based on your data source)
            current_price = get_current_nabil_price()  # Your method to fetch price
            
            # Analyze current price with strategy
            pending_orders = strategy.analyze(current_price)
            
            # If there are pending orders, show summary and ask for confirmation
            if pending_orders:
                print(strategy.get_order_summary(pending_orders))
                
                # USER MUST CONFIRM BEFORE EXECUTION
                user_input = input("\nConfirm execution? (yes/no): ").strip().lower()
                
                if user_input == "yes":
                    for order in pending_orders:
                        # Execute the order through your trader
                        execution_price = execute_order_through_tms(trader, order)
                        
                        # Update strategy with executed order
                        strategy.execute_order(order, execution_price)
                        
                        print(f"✓ Order executed: {order.order_type.value} x{order.quantity}")
                else:
                    print("✗ Order execution cancelled")
            
            # Wait before next price check (adjust based on your needs)
            time.sleep(60)  # Check every minute
            
        except Exception as e:
            print(f"Error in monitoring: {e}")
            time.sleep(60)


"""
STEP 4: Execute orders through your TMS trader
"""

def execute_order_through_tms(trader, order):
    """
    Execute order through NEPSE TMS
    Integrate with your Trader class methods
    
    Args:
        trader: Your Trader instance
        order: Order object from strategy
    
    Returns:
        execution_price: Price at which order was executed
    """
    
    if order.order_type == OrderType.BUY_INITIAL or order.order_type == OrderType.BUY_LADDER:
        # Place BUY order
        result = trader.place_buy_order(
            symbol=order.symbol,
            quantity=order.quantity,
            price=order.price,  # Limit order price
            order_type="LIMIT"   # or "MARKET"
        )
        
    elif order.order_type == OrderType.SELL_STOP or order.order_type == OrderType.SELL_TRAILING:
        # Place SELL order
        result = trader.place_sell_order(
            symbol=order.symbol,
            quantity=order.quantity,
            price=order.price,
            order_type="LIMIT"
        )
    
    # Extract execution price from result
    execution_price = result.get('executed_price', order.price)
    return execution_price


"""
STEP 5: Get reports anytime
"""

def generate_nabil_reports(strategy):
    """Generate strategy status reports"""
    
    # Detailed position report
    print(strategy.get_position_report())
    
    # Order execution history
    print("\nEXECUTION HISTORY:")
    for execution in strategy.orders:
        order_dict = execution.to_dict()
        print(f"\n{execution.order_type.value}:")
        for key, value in order_dict.items():
            print(f"  {key}: {value}")


# ===================================================================================
# REAL-WORLD USAGE EXAMPLE
# ===================================================================================

"""
Here's how you'd use this in your actual trading bot:
"""

class NabilTradingBot:
    """Example: Bot that trades Nabil with trailing stop"""
    
    def __init__(self, trader):
        self.trader = trader
        self.strategy = None
    
    def start_trading(self):
        """Start the Nabil trading strategy"""
        
        # Get current price (from your data source)
        current_price = self.trader.get_current_price("NABIL")
        
        # Initialize strategy
        self.strategy = setup_nabil_trailing_stop_strategy(
            self.trader, 
            current_price
        )
        
        print(f"Starting Nabil Trading Strategy at Rs. {current_price:.2f}")
        print(f"Initial position: 10 shares @ Rs. {current_price:.2f}")
        print(f"Hard stop: Rs. {self.strategy._calculate_initial_stop_loss():.2f}")
        
        # Start monitoring
        monitor_nabil_strategy(self.strategy, self.trader)
    
    def get_status(self):
        """Get current strategy status"""
        if self.strategy:
            return self.strategy.get_position_report()
        else:
            return "Strategy not initialized"
    
    def close_position(self):
        """Manually close the position"""
        if self.strategy and self.strategy.total_quantity > 0:
            current_price = self.trader.get_current_price("NABIL")
            
            # Create manual sell order
            order = Order(
                OrderType.SELL_TRAILING,
                "NABIL",
                self.strategy.total_quantity,
                price=current_price,
                reason="Manual position close",
                position_pct_change=self.strategy._calculate_position_pct_change(),
                trigger_condition="Manual request"
            )
            
            print(self.strategy.get_order_summary([order]))
            
            if input("Close position? (yes/no): ").lower() == "yes":
                execution_price = execute_order_through_tms(self.trader, order)
                self.strategy.execute_order(order, execution_price)
                print("Position closed")


# ===================================================================================
# CONFIGURATION CHECKLIST
# ===================================================================================

"""
Before running the strategy, ensure:

□ Your Trader class can fetch current stock prices
□ Your Trader class has place_buy_order() method
□ Your Trader class has place_sell_order() method
□ Order execution returns execution_price
□ You're connected to NEPSE TMS
□ DEMO_MODE is True initially (in .env)
□ You have proper error handling for network issues

If any prices are hardcoded, implement your price fetching method.
"""


# ===================================================================================
# ADAPTING THE STRATEGY - KEY PARAMETERS YOU CAN MODIFY
# ===================================================================================

"""
To adjust the strategy for different risk profiles, modify these values:

CONSERVATIVE (Lower Risk):
    stop_loss_pct=5,              # Sell if drops 5%
    trailing_activation_pct=5,    # Trailing starts at 5% gain
    trailing_step_pct=3,          # Move stop 3% per climb
    ladder_triggers={10: 10}      # Only 1 ladder level

BALANCED (Medium Risk - Your Current Setup):
    stop_loss_pct=10,             # Sell if drops 10%
    trailing_activation_pct=10,   # Trailing starts at 10% gain
    trailing_step_pct=5,          # Move stop 5% per climb
    ladder_triggers={20: 20, 30: 10}

AGGRESSIVE (Higher Risk):
    stop_loss_pct=20,             # Sell if drops 20%
    trailing_activation_pct=15,   # Trailing starts at 15% gain
    trailing_step_pct=7,          # Move stop 7% per climb
    ladder_triggers={15: 20, 25: 15, 40: 10}  # More ladder levels
"""


# ===================================================================================
# TROUBLESHOOTING
# ===================================================================================

"""
Issue: Orders not triggering at certain prices
Solution: Check that strategy.analyze() is being called with latest prices

Issue: Trailing stop not moving up
Solution: Ensure prices are passed in sequence, not out of order

Issue: Ladder-in not triggering
Solution: Check that price actually falls below trigger level

Issue: Position shows negative shares
Solution: Ensure you're not double-executing orders

For detailed debugging, enable logging:
    from src.bot.logger import setup_logger
    logger = setup_logger(__name__)
    logger.setLevel('DEBUG')
"""
