"""
Login Page Object - Example implementation of Page Factory pattern
Demonstrates how to create page objects using the base page functionality.
"""

from typing import Tuple
from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage


class LoginPage(BasePage):
    """Login page object implementing Page Factory pattern."""
    
    # Page locators - using both Android and iOS strategies
    USERNAME_FIELD = (AppiumBy.ID, "username")
    PASSWORD_FIELD = (AppiumBy.ID, "password")
    LOGIN_BUTTON = (AppiumBy.ID, "login_button")
    FORGOT_PASSWORD_LINK = (AppiumBy.ID, "forgot_password")
    SIGNUP_LINK = (AppiumBy.ID, "signup_link")
    ERROR_MESSAGE = (AppiumBy.ID, "error_message")
    LOADING_INDICATOR = (AppiumBy.ID, "loading")
    
    # Alternative locators for different platforms
    USERNAME_FIELD_ANDROID = (AppiumBy.XPATH, "//android.widget.EditText[@resource-id='username']")
    USERNAME_FIELD_IOS = (AppiumBy.XPATH, "//XCUIElementTypeTextField[@name='username']")
    
    PASSWORD_FIELD_ANDROID = (AppiumBy.XPATH, "//android.widget.EditText[@resource-id='password']")
    PASSWORD_FIELD_IOS = (AppiumBy.XPATH, "//XCUIElementTypeSecureTextField[@name='password']")
    
    LOGIN_BUTTON_ANDROID = (AppiumBy.XPATH, "//android.widget.Button[@text='Login']")
    LOGIN_BUTTON_IOS = (AppiumBy.XPATH, "//XCUIElementTypeButton[@name='Login']")
    
    def __init__(self, driver):
        """Initialize login page."""
        super().__init__(driver)
        self.logger.info("Login page initialized")
    
    def is_page_loaded(self, timeout: int = 10) -> bool:
        """Check if login page is loaded."""
        try:
            self.wait_for_element_visible(self.USERNAME_FIELD, timeout)
            self.wait_for_element_visible(self.PASSWORD_FIELD, timeout)
            self.wait_for_element_visible(self.LOGIN_BUTTON, timeout)
            self.logger.info("Login page loaded successfully")
            return True
        except Exception as e:
            self.logger.error(f"Login page not loaded: {str(e)}")
            return False
    
    def enter_username(self, username: str) -> 'LoginPage':
        """Enter username in the username field."""
        try:
            self.send_keys(self.USERNAME_FIELD, username, clear_first=True)
            self.logger.info(f"Entered username: {username}")
        except Exception:
            # Try platform-specific locator
            platform = self.driver.capabilities.get('platformName', '').lower()
            if platform == 'android':
                self.send_keys(self.USERNAME_FIELD_ANDROID, username, clear_first=True)
            elif platform == 'ios':
                self.send_keys(self.USERNAME_FIELD_IOS, username, clear_first=True)
            else:
                raise
            self.logger.info(f"Entered username using platform-specific locator: {username}")
        
        return self
    
    def enter_password(self, password: str) -> 'LoginPage':
        """Enter password in the password field."""
        try:
            self.send_keys(self.PASSWORD_FIELD, password, clear_first=True)
            self.logger.info("Password entered")
        except Exception:
            # Try platform-specific locator
            platform = self.driver.capabilities.get('platformName', '').lower()
            if platform == 'android':
                self.send_keys(self.PASSWORD_FIELD_ANDROID, password, clear_first=True)
            elif platform == 'ios':
                self.send_keys(self.PASSWORD_FIELD_IOS, password, clear_first=True)
            else:
                raise
            self.logger.info("Password entered using platform-specific locator")
        
        return self
    
    def click_login_button(self) -> 'LoginPage':
        """Click the login button."""
        try:
            self.click_element(self.LOGIN_BUTTON)
            self.logger.info("Login button clicked")
        except Exception:
            # Try platform-specific locator
            platform = self.driver.capabilities.get('platformName', '').lower()
            if platform == 'android':
                self.click_element(self.LOGIN_BUTTON_ANDROID)
            elif platform == 'ios':
                self.click_element(self.LOGIN_BUTTON_IOS)
            else:
                raise
            self.logger.info("Login button clicked using platform-specific locator")
        
        return self
    
    def login(self, username: str, password: str) -> 'LoginPage':
        """Perform complete login action."""
        self.logger.info(f"Performing login with username: {username}")
        
        self.enter_username(username)
        self.enter_password(password)
        self.click_login_button()
        
        # Hide keyboard if present
        self.hide_keyboard()
        
        self.logger.info("Login action completed")
        return self
    
    def click_forgot_password(self) -> 'LoginPage':
        """Click forgot password link."""
        self.click_element(self.FORGOT_PASSWORD_LINK)
        self.logger.info("Forgot password link clicked")
        return self
    
    def click_signup_link(self) -> 'LoginPage':
        """Click signup link."""
        self.click_element(self.SIGNUP_LINK)
        self.logger.info("Signup link clicked")
        return self
    
    def get_error_message(self) -> str:
        """Get error message text."""
        try:
            error_text = self.get_text(self.ERROR_MESSAGE)
            self.logger.info(f"Error message retrieved: {error_text}")
            return error_text
        except Exception as e:
            self.logger.warning(f"No error message found: {str(e)}")
            return ""
    
    def is_error_message_displayed(self) -> bool:
        """Check if error message is displayed."""
        is_displayed = self.is_element_visible(self.ERROR_MESSAGE, timeout=5)
        self.logger.info(f"Error message displayed: {is_displayed}")
        return is_displayed
    
    def wait_for_loading_to_complete(self, timeout: int = 30) -> bool:
        """Wait for loading indicator to disappear."""
        try:
            # Wait for loading indicator to appear first (optional)
            if self.is_element_present(self.LOADING_INDICATOR, timeout=2):
                self.logger.info("Loading indicator appeared")
                
                # Wait for it to disappear
                if self.wait_for_element_invisible(self.LOADING_INDICATOR, timeout):
                    self.logger.info("Loading completed")
                    return True
                else:
                    self.logger.warning("Loading indicator did not disappear within timeout")
                    return False
            else:
                self.logger.info("No loading indicator found")
                return True
        except Exception as e:
            self.logger.error(f"Error waiting for loading to complete: {str(e)}")
            return False
    
    def is_login_successful(self) -> bool:
        """Check if login was successful by verifying page navigation."""
        try:
            # Wait for loading to complete
            self.wait_for_loading_to_complete()
            
            # Check if we're no longer on login page
            # This could be checking for absence of login elements or presence of home page elements
            login_elements_present = (
                self.is_element_present(self.USERNAME_FIELD, timeout=3) and
                self.is_element_present(self.PASSWORD_FIELD, timeout=3) and
                self.is_element_present(self.LOGIN_BUTTON, timeout=3)
            )
            
            success = not login_elements_present
            self.logger.info(f"Login successful: {success}")
            return success
            
        except Exception as e:
            self.logger.error(f"Error checking login success: {str(e)}")
            return False
    
    def clear_username_field(self) -> 'LoginPage':
        """Clear username field."""
        element = self.find_element(self.USERNAME_FIELD)
        element.clear()
        self.logger.info("Username field cleared")
        return self
    
    def clear_password_field(self) -> 'LoginPage':
        """Clear password field."""
        element = self.find_element(self.PASSWORD_FIELD)
        element.clear()
        self.logger.info("Password field cleared")
        return self
    
    def get_username_field_text(self) -> str:
        """Get current text in username field."""
        text = self.get_attribute(self.USERNAME_FIELD, "text")
        self.logger.info(f"Username field text: {text}")
        return text
    
    def is_login_button_enabled(self) -> bool:
        """Check if login button is enabled."""
        enabled = self.get_attribute(self.LOGIN_BUTTON, "enabled") == "true"
        self.logger.info(f"Login button enabled: {enabled}")
        return enabled
    
    def take_login_page_screenshot(self, filename: str = None) -> str:
        """Take screenshot of login page."""
        if not filename:
            filename = "login_page_screenshot.png"
        
        screenshot_path = self.take_screenshot(filename)
        self.logger.info(f"Login page screenshot taken: {screenshot_path}")
        return screenshot_path