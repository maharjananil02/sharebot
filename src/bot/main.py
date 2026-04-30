"""Main bot orchestrator"""
import time
import schedule
from .browser import BrowserManager
from .login import LoginManager
from .trader import Trader
from .strategy import SimpleMovingAverageStrategy
from .logger import setup_logger
from .config import get_config

logger = setup_logger(__name__)
config = get_config()

class TradingBot:
    """Main trading bot class"""
    
    def __init__(self):
        self.browser_manager = None
        self.login_manager = None
        self.trader = None
        self.strategy = None
        self.running = False
    
    def initialize(self):
        """Initialize the bot"""
        try:
            logger.info("Initializing trading bot...")
            
            # Setup browser
            self.browser_manager = BrowserManager()
            self.browser_manager.launch_browser()
            
            # Create directory for screenshots
            import os
            if not os.path.exists("screenshots"):
                os.makedirs("screenshots")
            
            # Setup login
            self.login_manager = LoginManager(self.browser_manager)
            
            # Setup trader
            self.trader = Trader(self.browser_manager)
            
            # Setup strategy
            self.strategy = SimpleMovingAverageStrategy(self.trader)
            
            logger.info("Bot initialized successfully")
            return True
        
        except Exception as e:
            logger.error(f"Failed to initialize bot: {str(e)}")
            self.cleanup()
            return False
    
    def login(self):
        """Login to NEPSE TMS"""
        try:
            if config.DEMO_MODE:
                logger.info("Running in DEMO mode - skipping actual login")
                return True
            
            return self.login_manager.login()
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False
    
    def run_trading_cycle(self):
        """Run one trading cycle"""
        try:
            logger.info("Running trading cycle...")
            
            if config.DEMO_MODE:
                logger.info("DEMO MODE: Not executing trades")
                return
            
            # Fetch market data
            prices = self.trader.get_stock_prices()
            if not prices:
                logger.warning("No market data available")
                return
            
            # Analyze with strategy
            signals = self.strategy.analyze(prices)
            
            # Execute signals
            if config.TRADING_ENABLED:
                self.strategy.execute_signals(signals)
            else:
                logger.info(f"Trading disabled. Signals: {signals}")
        
        except Exception as e:
            logger.error(f"Trading cycle failed: {str(e)}")
    
    def start(self):
        """Start the bot"""
        try:
            logger.info("Starting trading bot...")
            
            if not self.initialize():
                logger.error("Failed to initialize bot")
                return False
            
            if not self.login():
                logger.error("Failed to login")
                self.cleanup()
                return False
            
            self.running = True
            logger.info("Bot started successfully")
            
            # Schedule trading cycles
            schedule.every(5).minutes.do(self.run_trading_cycle)
            
            # Main loop
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("Bot interrupted by user")
        except Exception as e:
            logger.error(f"Bot error: {str(e)}")
        finally:
            self.cleanup()
    
    def stop(self):
        """Stop the bot"""
        logger.info("Stopping trading bot...")
        self.running = False
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            logger.info("Cleaning up resources...")
            
            if self.login_manager:
                self.login_manager.logout()
            
            if self.browser_manager:
                self.browser_manager.close_browser()
            
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")

def main():
    """Main entry point"""
    bot = TradingBot()
    bot.start()

if __name__ == "__main__":
    main()
