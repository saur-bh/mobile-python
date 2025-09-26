"""
Wait Utilities
Professional wait strategies for mobile app testing
"""

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy
from config.device_config import WAIT_CONFIG
import time


class WaitUtils:
    """Utility class for handling waits in mobile app testing"""
    
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, WAIT_CONFIG["explicit_wait"])
    
    def wait_for_element_present(self, locator, timeout=None):
        """Wait for element to be present"""
        if timeout:
            wait = WebDriverWait(self.driver, timeout)
        else:
            wait = self.wait
        
        try:
            element = wait.until(EC.presence_of_element_located(locator))
            return element
        except Exception as e:
            raise Exception(f"Element not found within timeout: {e}")
    
    def wait_for_element_visible(self, locator, timeout=None):
        """Wait for element to be visible"""
        if timeout:
            wait = WebDriverWait(self.driver, timeout)
        else:
            wait = self.wait
        
        try:
            element = wait.until(EC.visibility_of_element_located(locator))
            return element
        except Exception as e:
            raise Exception(f"Element not visible within timeout: {e}")
    
    def wait_for_element_clickable(self, locator, timeout=None):
        """Wait for element to be clickable"""
        if timeout:
            wait = WebDriverWait(self.driver, timeout)
        else:
            wait = self.wait
        
        try:
            element = wait.until(EC.element_to_be_clickable(locator))
            return element
        except Exception as e:
            raise Exception(f"Element not clickable within timeout: {e}")
    
    def wait_for_text_in_element(self, locator, text, timeout=None):
        """Wait for specific text to appear in element"""
        if timeout:
            wait = WebDriverWait(self.driver, timeout)
        else:
            wait = self.wait
        
        try:
            element = wait.until(EC.text_to_be_present_in_element(locator, text))
            return element
        except Exception as e:
            raise Exception(f"Text '{text}' not found in element within timeout: {e}")
    
    def wait_for_elements_present(self, locator, timeout=None):
        """Wait for multiple elements to be present"""
        if timeout:
            wait = WebDriverWait(self.driver, timeout)
        else:
            wait = self.wait
        
        try:
            elements = wait.until(lambda driver: driver.find_elements(*locator))
            return elements if elements else None
        except Exception as e:
            raise Exception(f"Elements not found within timeout: {e}")
    
    def wait_for_app_ready(self, timeout=None):
        """Wait for app to be ready (custom implementation)"""
        if timeout:
            wait_time = timeout
        else:
            wait_time = WAIT_CONFIG["explicit_wait"]
        
        start_time = time.time()
        
        while time.time() - start_time < wait_time:
            try:
                # Check if app has loaded by looking for common elements
                elements = self.driver.find_elements(AppiumBy.XPATH, "//*")
                if len(elements) > 0:
                    print("✅ App is ready")
                    return True
            except Exception:
                pass
            
            time.sleep(0.5)  # Short sleep to avoid busy waiting
        
        raise Exception(f"App not ready within {wait_time} seconds")
    
    def wait_for_text_elements(self, timeout=None):
        """Wait for text elements to be present and loaded"""
        if timeout:
            wait_time = timeout
        else:
            wait_time = WAIT_CONFIG["text_extraction_timeout"]
        
        start_time = time.time()
        
        while time.time() - start_time < wait_time:
            try:
                # Wait for TextView elements to be present
                text_elements = self.driver.find_elements(
                    AppiumBy.CLASS_NAME, "android.widget.TextView"
                )
                
                if text_elements:
                    # Check if elements have text content
                    for element in text_elements:
                        if element.text and element.text.strip():
                            print("✅ Text elements are loaded")
                            return text_elements
            except Exception:
                pass
            
            time.sleep(0.5)  # Short sleep to avoid busy waiting
        
        raise Exception(f"Text elements not loaded within {wait_time} seconds")
