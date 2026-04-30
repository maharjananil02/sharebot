"""Diagnostic script to test and capture page elements"""
import time
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from .bot.browser import BrowserManager
from .bot.config import get_config
from .bot.logger import setup_logger

logger = setup_logger(__name__)

def diagnose_login_page():
    """Diagnose the login page and capture element information"""
    config = get_config()
    browser_manager = BrowserManager()
    browser_manager.launch_browser()
    
    try:
        # Navigate to login page
        logger.info("Navigating to login page...")
        browser_manager.navigate_to(config.NEPSE_LOGIN_URL)
        time.sleep(3)
        
        driver = browser_manager.driver
        
        # 1. Get page title and URL
        logger.info(f"Page Title: {driver.title}")
        logger.info(f"Current URL: {driver.current_url}")
        
        # 2. Find all input fields
        logger.info("\n=== Found INPUT FIELDS ===")
        input_fields = driver.find_elements("tag name", "input")
        for i, field in enumerate(input_fields):
            field_type = field.get_attribute("type")
            field_name = field.get_attribute("name") or "N/A"
            field_id = field.get_attribute("id") or "N/A"
            field_placeholder = field.get_attribute("placeholder") or "N/A"
            logger.info(f"Input {i}: type={field_type}, name={field_name}, id={field_id}, placeholder={field_placeholder}")
        
        # 3. Find all buttons
        logger.info("\n=== Found BUTTONS ===")
        buttons = driver.find_elements("tag name", "button")
        for i, button in enumerate(buttons):
            button_text = button.text or "N/A"
            button_id = button.get_attribute("id") or "N/A"
            button_class = button.get_attribute("class") or "N/A"
            logger.info(f"Button {i}: text='{button_text}', id={button_id}, class={button_class}")
        
        # 4. Find all submit inputs
        logger.info("\n=== Found SUBMIT INPUTS ===")
        submit_inputs = driver.find_elements("xpath", "//input[@type='submit']")
        for i, submit in enumerate(submit_inputs):
            submit_value = submit.get_attribute("value") or "N/A"
            submit_id = submit.get_attribute("id") or "N/A"
            submit_class = submit.get_attribute("class") or "N/A"
            logger.info(f"Submit {i}: value='{submit_value}', id={submit_id}, class={submit_class}")
        
        # 5. Take a screenshot
        logger.info("\n=== Taking screenshot ===")
        browser_manager.save_screenshot("diagnostics_login_page")
        
        # 6. Get page HTML (save to file)
        logger.info("\n=== Saving page HTML ===")
        page_html = driver.page_source
        html_file = "logs/login_page_html.txt"
        with open(html_file, "w") as f:
            f.write(page_html)
        logger.info(f"HTML saved to {html_file}")
        
        logger.info("\n=== DIAGNOSTICS COMPLETE ===")
        logger.info("Check logs directory for:")
        logger.info("  - diagnostics_login_page.png (screenshot)")
        logger.info("  - login_page_html.txt (page HTML)")
        
    except Exception as e:
        logger.error(f"Diagnostic error: {e}")
    finally:
        logger.info("\nClosing browser in 10 seconds...")
        time.sleep(10)
        browser_manager.close_browser()

if __name__ == "__main__":
    diagnose_login_page()
