"""Login automation for NEPSE TMS"""
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from .logger import setup_logger
from .config import get_config

logger = setup_logger(__name__)
config = get_config()

class LoginManager:
    """Handles login to NEPSE TMS"""
    
    def __init__(self, browser_manager):
        self.browser = browser_manager
        self.driver = browser_manager.driver
        self.wait = browser_manager.wait
    
    def login(self, username=None, password=None, captcha=None):
        """Login to NEPSE TMS
        
        Args:
            username: NEPSE username/client code
            password: NEPSE password
            captcha: Captcha code (required - must be provided or entered manually)
        """
        try:
            username = username or config.NEPSE_USERNAME
            password = password or config.NEPSE_PASSWORD
            
            if not username or not password:
                raise ValueError("Username and password are required")
            
            logger.info("Attempting to login to NEPSE TMS...")
            
            # Navigate to login page
            self.browser.navigate_to(config.NEPSE_LOGIN_URL)
            time.sleep(2)
            
            # Find username field and enter username
            # Username field has placeholder="Client Code/ User Name", no name attribute
            username_field = self.browser.wait_for_element(By.XPATH, "//input[@placeholder='Client Code/ User Name']")
            username_field.clear()
            username_field.send_keys(username)
            logger.debug(f"Username entered: {username}")
            
            # Find password field and enter password
            password_field = self.browser.wait_for_element(By.ID, "password-field")
            password_field.clear()
            password_field.send_keys(password)
            logger.debug("Password entered")
            
            # Handle captcha field
            captcha_field = self.browser.wait_for_element(By.ID, "captchaEnter")
            
            if captcha:
                captcha_field.clear()
                captcha_field.send_keys(captcha)
                logger.debug(f"Captcha entered: {captcha}")
            else:
                logger.warning("CAPTCHA required but not provided")
                logger.info("CAPTCHA field is focused. Please enter captcha manually.")
                # Wait for user to enter captcha manually
                time.sleep(10)
            
            # Find and click login button
            # Try to close any error dialogs first
            try:
                error_close = self.driver.find_elements(By.XPATH, "//button[contains(@class, 'close')]")
                for close_btn in error_close:
                    try:
                        close_btn.click()
                        logger.info("Closed error dialog")
                        time.sleep(1)
                    except:
                        pass
            except:
                pass
            
            # Try the submit input first, then fallback to button
            try:
                login_button = self.browser.wait_for_clickable(By.XPATH, "//input[@type='submit'][@value='Login']")
                logger.info("Found login submit button")
            except:
                logger.info("Submit button not found, trying button element")
                login_button = self.browser.wait_for_clickable(By.XPATH, "//button[contains(text(), 'Login')]")
                logger.info("Found login button element")
            
            login_button.click()
            logger.info("Login button clicked")
            
            # Wait for login to complete
            time.sleep(3)
            
            # Check if login was successful
            if self._is_login_successful():
                logger.info("Login successful!")
                return True
            else:
                logger.error("Login failed - check credentials and captcha")
                return False
        
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False
    
    def _is_login_successful(self):
        """Check if login was successful"""
        try:
            # Check if URL changed from login page
            current_url = self.driver.current_url
            if "login" not in current_url.lower():
                logger.info(f"URL changed to: {current_url}")
                return True
            
            # Check for error messages
            error_elements = self.driver.find_elements(By.CLASS_NAME, "alert-danger")
            if error_elements:
                for error in error_elements:
                    if error.text:
                        logger.error(f"Login error: {error.text}")
                return False
            
            # If still on login page after wait, check for form presence
            login_form = self.driver.find_elements(By.CLASS_NAME, "login__form")
            if login_form:
                logger.warning("Still on login page")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error checking login status: {str(e)}")
            return False
    
    def logout(self):
        """Logout from NEPSE TMS"""
        try:
            logger.info("Attempting to logout...")
            # Find and click logout button - adjust selector based on actual interface
            logout_button = self.driver.find_element(By.XPATH, "//a[@href='#logout']")
            logout_button.click()
            time.sleep(2)
            logger.info("Logout successful")
            return True
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            return False
