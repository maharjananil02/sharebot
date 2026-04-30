"""Browser management for Selenium automation"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from .logger import setup_logger
from .config import get_config
import time

logger = setup_logger(__name__)
config = get_config()

class BrowserManager:
    """Manages Selenium WebDriver"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
    
    def launch_browser(self):
        """Launch Chrome browser"""
        try:
            options = Options()
            
            if config.HEADLESS_MODE:
                options.add_argument("--headless")
            
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, config.IMPLICIT_WAIT)
            
            logger.info("Browser launched successfully")
            return self.driver
        
        except Exception as e:
            logger.error(f"Failed to launch browser: {str(e)}")
            raise
    
    def close_browser(self):
        """Close the browser"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")
    
    def navigate_to(self, url):
        """Navigate to a URL"""
        try:
            self.driver.get(url)
            logger.info(f"Navigated to {url}")
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {str(e)}")
            raise
    
    def wait_for_element(self, by, value, timeout=None):
        """Wait for element to be present"""
        try:
            timeout = timeout or config.IMPLICIT_WAIT
            element = self.wait.until(EC.presence_of_element_located((by, value)))
            logger.debug(f"Element found: {value}")
            return element
        except Exception as e:
            logger.error(f"Timeout waiting for element: {value}")
            raise
    
    def wait_for_clickable(self, by, value, timeout=None):
        """Wait for element to be clickable"""
        try:
            timeout = timeout or config.IMPLICIT_WAIT
            element = self.wait.until(EC.element_to_be_clickable((by, value)))
            return element
        except Exception as e:
            logger.error(f"Timeout waiting for clickable element: {value}")
            raise
    
    def take_screenshot(self, filename):
        """Take screenshot"""
        try:
            self.driver.save_screenshot(f"screenshots/{filename}.png")
            logger.info(f"Screenshot saved: {filename}.png")
        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")
    
    def save_screenshot(self, filename):
        """Alias for take_screenshot"""
        return self.take_screenshot(filename)
