"""
Base Page Class for Mobile Automation Framework
Implements Page Factory pattern with common functionality for mobile elements.
"""

import time
from typing import List, Optional, Tuple, Union, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    ElementNotVisibleException,
    ElementNotInteractableException
)
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.common.multi_action import MultiAction

from config.config_manager import config_manager
from utils.logger import get_logger


class BasePage:
    """Base page class implementing Page Factory pattern for mobile automation."""
    
    def __init__(self, driver):
        """Initialize base page with driver instance."""
        self.driver = driver
        self.logger = get_logger(self.__class__.__name__)
        self.timeout_config = config_manager.get_timeout_config()
        self.wait = WebDriverWait(driver, self.timeout_config['explicit_wait'])
        self.short_wait = WebDriverWait(driver, 5)
        
    # Element Finding Methods
    def find_element(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> WebElement:
        """Find a single element with explicit wait."""
        wait_time = timeout or self.timeout_config['explicit_wait']
        try:
            element = WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located(locator)
            )
            self.logger.debug(f"Element found: {locator}")
            return element
        except TimeoutException:
            self.logger.error(f"Element not found within {wait_time} seconds: {locator}")
            raise NoSuchElementException(f"Element not found: {locator}")
    
    def find_elements(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> List[WebElement]:
        """Find multiple elements with explicit wait."""
        wait_time = timeout or self.timeout_config['explicit_wait']
        try:
            WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located(locator)
            )
            elements = self.driver.find_elements(*locator)
            self.logger.debug(f"Found {len(elements)} elements: {locator}")
            return elements
        except TimeoutException:
            self.logger.warning(f"No elements found within {wait_time} seconds: {locator}")
            return []
    
    def is_element_present(self, locator: Tuple[str, str], timeout: int = 5) -> bool:
        """Check if element is present without raising exception."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False
    
    def is_element_visible(self, locator: Tuple[str, str], timeout: int = 5) -> bool:
        """Check if element is visible without raising exception."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False
    
    def is_element_clickable(self, locator: Tuple[str, str], timeout: int = 5) -> bool:
        """Check if element is clickable without raising exception."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            return True
        except TimeoutException:
            return False
    
    # Element Interaction Methods
    def click_element(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> None:
        """Click on an element with explicit wait."""
        try:
            element = self.wait_for_element_clickable(locator, timeout)
            element.click()
            self.logger.info(f"Clicked element: {locator}")
        except Exception as e:
            self.logger.error(f"Failed to click element {locator}: {str(e)}")
            raise
    
    def send_keys(self, locator: Tuple[str, str], text: str, clear_first: bool = True, timeout: Optional[int] = None) -> None:
        """Send keys to an element with explicit wait."""
        try:
            element = self.wait_for_element_visible(locator, timeout)
            if clear_first:
                element.clear()
            element.send_keys(text)
            self.logger.info(f"Sent keys '{text}' to element: {locator}")
        except Exception as e:
            self.logger.error(f"Failed to send keys to element {locator}: {str(e)}")
            raise
    
    def get_text(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> str:
        """Get text from an element."""
        try:
            element = self.wait_for_element_visible(locator, timeout)
            text = element.text
            self.logger.debug(f"Got text '{text}' from element: {locator}")
            return text
        except Exception as e:
            self.logger.error(f"Failed to get text from element {locator}: {str(e)}")
            raise
    
    def get_attribute(self, locator: Tuple[str, str], attribute: str, timeout: Optional[int] = None) -> str:
        """Get attribute value from an element."""
        try:
            element = self.find_element(locator, timeout)
            value = element.get_attribute(attribute)
            self.logger.debug(f"Got attribute '{attribute}' = '{value}' from element: {locator}")
            return value
        except Exception as e:
            self.logger.error(f"Failed to get attribute '{attribute}' from element {locator}: {str(e)}")
            raise
    
    # Wait Methods
    def wait_for_element_visible(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> WebElement:
        """Wait for element to be visible."""
        wait_time = timeout or self.timeout_config['explicit_wait']
        try:
            element = WebDriverWait(self.driver, wait_time).until(
                EC.visibility_of_element_located(locator)
            )
            return element
        except TimeoutException:
            raise ElementNotVisibleException(f"Element not visible within {wait_time} seconds: {locator}")
    
    def wait_for_element_clickable(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> WebElement:
        """Wait for element to be clickable."""
        wait_time = timeout or self.timeout_config['explicit_wait']
        try:
            element = WebDriverWait(self.driver, wait_time).until(
                EC.element_to_be_clickable(locator)
            )
            return element
        except TimeoutException:
            raise ElementNotInteractableException(f"Element not clickable within {wait_time} seconds: {locator}")
    
    def wait_for_element_invisible(self, locator: Tuple[str, str], timeout: Optional[int] = None) -> bool:
        """Wait for element to become invisible."""
        wait_time = timeout or self.timeout_config['explicit_wait']
        try:
            return WebDriverWait(self.driver, wait_time).until(
                EC.invisibility_of_element_located(locator)
            )
        except TimeoutException:
            return False
    
    def wait_for_text_in_element(self, locator: Tuple[str, str], text: str, timeout: Optional[int] = None) -> bool:
        """Wait for specific text to appear in element."""
        wait_time = timeout or self.timeout_config['explicit_wait']
        try:
            return WebDriverWait(self.driver, wait_time).until(
                EC.text_to_be_present_in_element(locator, text)
            )
        except TimeoutException:
            return False
    
    # Mobile Specific Methods
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 1000) -> None:
        """Perform swipe gesture."""
        try:
            self.driver.swipe(start_x, start_y, end_x, end_y, duration)
            self.logger.info(f"Swiped from ({start_x}, {start_y}) to ({end_x}, {end_y})")
        except Exception as e:
            self.logger.error(f"Failed to swipe: {str(e)}")
            raise
    
    def scroll_to_element(self, locator: Tuple[str, str], max_scrolls: int = 10) -> WebElement:
        """Scroll to find an element."""
        for i in range(max_scrolls):
            if self.is_element_present(locator, timeout=2):
                return self.find_element(locator)
            
            # Scroll down
            size = self.driver.get_window_size()
            start_x = size['width'] // 2
            start_y = size['height'] * 0.8
            end_y = size['height'] * 0.2
            
            self.swipe(start_x, int(start_y), start_x, int(end_y))
            time.sleep(1)
        
        raise NoSuchElementException(f"Element not found after {max_scrolls} scrolls: {locator}")
    
    def tap(self, x: int, y: int) -> None:
        """Tap at specific coordinates."""
        try:
            TouchAction(self.driver).tap(x=x, y=y).perform()
            self.logger.info(f"Tapped at coordinates ({x}, {y})")
        except Exception as e:
            self.logger.error(f"Failed to tap at ({x}, {y}): {str(e)}")
            raise
    
    def long_press(self, locator: Tuple[str, str], duration: int = 1000) -> None:
        """Long press on an element."""
        try:
            element = self.find_element(locator)
            TouchAction(self.driver).long_press(element, duration=duration).perform()
            self.logger.info(f"Long pressed element: {locator}")
        except Exception as e:
            self.logger.error(f"Failed to long press element {locator}: {str(e)}")
            raise
    
    def pinch(self, locator: Tuple[str, str]) -> None:
        """Pinch gesture on an element."""
        try:
            element = self.find_element(locator)
            action1 = TouchAction(self.driver)
            action2 = TouchAction(self.driver)
            
            # Get element location and size
            location = element.location
            size = element.size
            
            # Define pinch coordinates
            x1 = location['x'] + size['width'] * 0.25
            y1 = location['y'] + size['height'] * 0.25
            x2 = location['x'] + size['width'] * 0.75
            y2 = location['y'] + size['height'] * 0.75
            
            action1.press(x=x1, y=y1).move_to(x=location['x'] + size['width'] * 0.4, 
                                            y=location['y'] + size['height'] * 0.4).release()
            action2.press(x=x2, y=y2).move_to(x=location['x'] + size['width'] * 0.6, 
                                            y=location['y'] + size['height'] * 0.6).release()
            
            MultiAction(self.driver).add(action1).add(action2).perform()
            self.logger.info(f"Pinched element: {locator}")
        except Exception as e:
            self.logger.error(f"Failed to pinch element {locator}: {str(e)}")
            raise
    
    # Utility Methods
    def take_screenshot(self, filename: Optional[str] = None) -> str:
        """Take screenshot and return file path."""
        try:
            if not filename:
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}.png"
            
            screenshot_path = f"screenshots/{filename}"
            self.driver.save_screenshot(screenshot_path)
            self.logger.info(f"Screenshot saved: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {str(e)}")
            raise
    
    def get_page_source(self) -> str:
        """Get current page source."""
        try:
            source = self.driver.page_source
            self.logger.debug("Retrieved page source")
            return source
        except Exception as e:
            self.logger.error(f"Failed to get page source: {str(e)}")
            raise
    
    def hide_keyboard(self) -> None:
        """Hide mobile keyboard if present."""
        try:
            self.driver.hide_keyboard()
            self.logger.info("Keyboard hidden")
        except Exception as e:
            self.logger.debug(f"Keyboard hide failed (may not be present): {str(e)}")
    
    def go_back(self) -> None:
        """Navigate back (Android back button)."""
        try:
            self.driver.back()
            self.logger.info("Navigated back")
        except Exception as e:
            self.logger.error(f"Failed to navigate back: {str(e)}")
            raise
    
    def wait(self, seconds: float) -> None:
        """Explicit wait for specified seconds."""
        time.sleep(seconds)
        self.logger.debug(f"Waited for {seconds} seconds")
    
    def refresh_page(self) -> None:
        """Refresh current page/screen."""
        try:
            self.driver.refresh()
            self.logger.info("Page refreshed")
        except Exception as e:
            self.logger.error(f"Failed to refresh page: {str(e)}")
            raise