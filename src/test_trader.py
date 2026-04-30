"""Test script for the Trader class"""
import time
from .bot.login import LoginManager
from .bot.browser import BrowserManager
from .bot.trader import Trader
from .bot.config import get_config
from .bot.logger import setup_logger

logger = setup_logger(__name__)

def main():
    """Main function to test the Trader class"""
    config = get_config()
    browser_manager = BrowserManager()
    browser_manager.launch_browser()
    
    try:
        login_manager = LoginManager(browser_manager)
        if login_manager.login():
            print("Login successful. Testing Trader functionality...")
            
            # Capture dashboard page for debugging
            try:
                import time
                time.sleep(2)
                browser_manager.save_screenshot("dashboard_after_login")
                page_html = browser_manager.driver.page_source
                with open("logs/dashboard_html.txt", "w") as f:
                    f.write(page_html)
                logger.info("Dashboard HTML saved to logs/dashboard_html.txt")
            except Exception as e:
                logger.error(f"Could not save dashboard HTML: {e}")
            
            trader = Trader(browser_manager)
            
            # --- Test Get Portfolio ---
            print("\nAttempting to fetch portfolio (DP Holding)...")
            portfolio = trader.get_portfolio()
            if portfolio:
                print("Successfully fetched portfolio:")
                for symbol, data in portfolio.items():
                    print(f"  - {symbol}: Qty={data['quantity']}, LTP={data['ltp']}, Value={data['value']}")
            else:
                print("Could not fetch portfolio or portfolio is empty. Check logs for details.")
                print("NOTE: This is expected if the page structure has changed. The selectors in 'trader.py' may need to be updated.")

            # Wait a moment before the next action
            time.sleep(3)

            # --- Test Get Order History ---
            print("\nAttempting to fetch order history...")
            order_history = trader.get_order_history()
            if order_history:
                print("Successfully fetched order history:")
                for order in order_history[:5]: # Print first 5 for brevity
                    print(f"  - {order['date']} | {order['symbol']} | {order['side']} | Qty: {order['quantity']} @ {order['price']} | Status: {order['status']}")
            else:
                print("Could not fetch order history or no orders found. Check logs for details.")
                print("NOTE: This is expected if the page structure has changed. The selectors in 'trader.py' may need to be updated.")

            print("\nTrader tests finished.")

        else:
            print("Login failed. Cannot run Trader tests.")
            
    except Exception as e:
        print(f"An error occurred during the test: {e}")
    finally:
        print("\nClosing browser in 10 seconds...")
        time.sleep(10)
        browser_manager.close_browser()

if __name__ == "__main__":
    main()
