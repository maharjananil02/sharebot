"""Trading operations module"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from .logger import setup_logger

logger = setup_logger(__name__)

class Trader:
    """Handles trading operations"""

    def __init__(self, browser_manager):
        self.browser = browser_manager
        self.driver = browser_manager.driver

    def _navigate_to_page(self, link_text):
        """Helper to navigate to different pages."""
        # Map link text to URLs
        url_map = {
            "DP Holding": "/tms/me/dp-holding",
            "DP Watchlist": "#nav-marketSummary",  # Tab on dashboard
            "Historic Order Book": "/tms/me/order-history",
            "Daily Order Book": "/tms/me/order-book"
        }
        
        try:
            logger.info(f"Navigating to {link_text} page...")
            
            # Try direct URL navigation first if it's a full page (most reliable)
            if link_text in url_map:
                url_path = url_map[link_text]
                
                # Skip URL navigation for dashboard tabs (they use anchor links)
                if url_path.startswith("#"):
                    logger.info(f"Searching for tab link: {link_text}")
                else:
                    # For full page navigation
                    try:
                        current_url = self.driver.current_url
                        # Extract base URL properly (before /tms)
                        base_url = current_url.split('://')  # ['https', 'tms17.nepsetms.com.np/tms/...']
                        if len(base_url) == 2:
                            protocol = base_url[0]
                            rest = base_url[1].split('/tms')[0]  # Get domain before /tms
                            url = f"{protocol}://{rest}{url_path}"
                            logger.info(f"Attempting direct URL navigation to: {url}")
                            self.driver.get(url)
                            time.sleep(2)
                            logger.info(f"Successfully navigated to {link_text} via URL.")
                            return True
                    except Exception as url_err:
                        logger.info(f"Direct URL navigation failed: {str(url_err)}, trying selector approach...")
            
            # Fallback: try to find by link text (for direct links and tabs)
            try:
                link = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.LINK_TEXT, link_text))
                )
                link.click()
                logger.info(f"Clicked link using LINK_TEXT: {link_text}")
                time.sleep(2)
                return True
            except:
                # If LINK_TEXT fails, try using XPath with partial text match
                logger.info(f"LINK_TEXT failed, trying XPath with contains()...")
                xpath = f"//a[contains(., '{link_text}')]"
                link = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                link.click()
                logger.info(f"Clicked link using XPath: {xpath}")
                time.sleep(2)
                return True
            
        except Exception as e:
            logger.error(f"Failed to navigate to {link_text}: {str(e)}")
            self.browser.save_screenshot(f"navigate_to_{link_text.replace(' ', '_')}_error")
            return False

    def get_portfolio(self):
        """Fetches the user's current portfolio (DP Holding)."""
        if not self._navigate_to_page("DP Holding"):
            return {}
        
        portfolio = {}
        try:
            logger.info("Fetching portfolio (DP Holding)...")
            # NOTE: The following selectors are placeholders based on a typical table structure.
            # These will need to be adjusted based on the actual HTML of the DP Holding page.
            # You will need to inspect the page and find the correct selectors for the table rows and cells.
            
            # Example: Wait for the table to be present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "dpHoldingTable")) # Replace with actual table ID/selector
            )
            
            # Example: Find all rows in the table body
            rows = self.driver.find_elements(By.XPATH, "//table[@id='dpHoldingTable']/tbody/tr") # Replace with actual table selector
            
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) > 5: # Assuming at least 6 columns
                    symbol = cells[1].text
                    quantity = cells[2].text
                    ltp = cells[4].text
                    value = cells[5].text
                    portfolio[symbol] = {
                        "quantity": int(quantity),
                        "ltp": float(ltp.replace(",", "")),
                        "value": float(value.replace(",", ""))
                    }
            logger.info("Successfully fetched portfolio.")
            
        except Exception as e:
            logger.error(f"Failed to fetch portfolio: {str(e)}")
            self.browser.save_screenshot("get_portfolio_error")
            return {}
            
        return portfolio

    def get_order_history(self):
        """Fetches the user's historic order book."""
        if not self._navigate_to_page("Historic Order Book"):
            return []

        orders = []
        try:
            logger.info("Fetching order history...")
            # NOTE: The following selectors are placeholders.
            # Adjust them based on the actual HTML of the Historic Order Book page.
            
            # Example: Wait for the order table to be present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "orderHistoryTable")) # Replace with actual table ID/selector
            )
            
            rows = self.driver.find_elements(By.XPATH, "//table[@id='orderHistoryTable']/tbody/tr") # Replace with actual table selector
            
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) > 8: # Assuming at least 9 columns
                    order = {
                        "date": cells[0].text,
                        "symbol": cells[1].text,
                        "side": cells[2].text,
                        "quantity": int(cells[3].text),
                        "price": float(cells[4].text.replace(",", "")),
                        "status": cells[8].text
                    }
                    orders.append(order)
            logger.info("Successfully fetched order history.")

        except Exception as e:
            logger.error(f"Failed to fetch order history: {str(e)}")
            self.browser.save_screenshot("get_order_history_error")
            return []
            
        return orders

    def get_daily_order_book(self):
        """Fetches the user's daily order book."""
        if not self._navigate_to_page("Daily Order Book"):
            return []
        # Implementation for parsing the daily order book would be similar to the others
        logger.info("Fetching daily order book... (Not yet implemented)")
        return []

    def place_buy_order(self, symbol, quantity, price):
        """Place a buy order"""
        if not self._navigate_to_page("Buy/Sell"):
            return False
        try:
            logger.info(f"Placing buy order: {symbol}, Qty: {quantity}, Price: {price}")
            # TODO: Implement buy order logic based on the NEPSE TMS Buy/Sell page interface
            return True
        except Exception as e:
            logger.error(f"Failed to place buy order: {str(e)}")
            self.browser.save_screenshot("place_buy_order_error")
            return False

    def place_sell_order(self, symbol, quantity, price):
        """Place a sell order"""
        if not self._navigate_to_page("Buy/Sell"):
            return False
        try:
            logger.info(f"Placing sell order: {symbol}, Qty: {quantity}, Price: {price}")
            # TODO: Implement sell order logic based on the NEPSE TMS Buy/Sell page interface
            return True
        except Exception as e:
            logger.error(f"Failed to place sell order: {str(e)}")
            self.browser.save_screenshot("place_sell_order_error")
            return False
