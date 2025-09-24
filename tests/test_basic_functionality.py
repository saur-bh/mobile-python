"""
Basic Mobile App Functionality Tests
General tests that can be applied to any mobile app
"""

import pytest
from appium.webdriver.common.appiumby import AppiumBy
from tests.utils.text_utils import get_text_elements, verify_webview_context
from tests.utils.wait_utils import WaitUtils


def test_app_launch(driver, wait_config):
    """Test that the app launches successfully"""
    print("🚀 Testing app launch...")
    
    # Use WaitUtils for proper waiting
    wait_utils = WaitUtils(driver)
    
    # Wait for app to be ready
    wait_utils.wait_for_app_ready()
    
    # Check if we can get the current activity
    try:
        current_activity = driver.current_activity
        print(f"📱 Current activity: {current_activity}")
        assert current_activity is not None, "Could not get current activity"
        print("✅ App launched successfully")
    except Exception as e:
        pytest.fail(f"App launch failed: {e}")


def test_screen_elements_count(driver, wait_config):
    """Test that the screen has a reasonable number of elements"""
    print("🔍 Testing screen elements count...")
    
    # Use WaitUtils for proper waiting
    wait_utils = WaitUtils(driver)
    
    # Wait for app to be ready
    wait_utils.wait_for_app_ready()
    
    # Get all elements on screen
    all_elements = driver.find_elements(by=AppiumBy.XPATH, value="//*")
    print(f"📱 Total elements on screen: {len(all_elements)}")
    
    # Should have some elements (not empty screen)
    assert len(all_elements) > 0, "Screen appears to be empty"
    print("✅ Screen has elements present")


def test_webview_detection(driver):
    """Test WebView detection and context switching"""
    print("🔍 Testing WebView detection...")
    
    is_webview = verify_webview_context(driver)
    
    # For this app, we expect native Android (not WebView)
    assert not is_webview, "App should use native Android elements"
    print("✅ App uses native Android elements")


def test_text_elements_present(driver):
    """Test that text elements are present on the screen"""
    print("🔍 Testing text elements presence...")
    
    all_texts = get_text_elements(driver)
    
    # Should have some text elements
    assert len(all_texts) > 0, "No text elements found on the screen"
    print(f"✅ Found {len(all_texts)} text elements")
