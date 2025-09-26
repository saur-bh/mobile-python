"""
Scopex Mobile App Test Suite
Comprehensive tests for the Scopex Mobile application
"""

import pytest
from appium.webdriver.common.appiumby import AppiumBy
from tests.utils.text_utils import get_text_elements, check_text_match, verify_webview_context
from tests.utils.wait_utils import WaitUtils


class TestScopexMobileApp:
    """Test class for Scopex Mobile App functionality"""
    
    def test_app_launch(self, driver, wait_config):
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
    
    def test_screen_elements_count(self, driver, wait_config):
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
    
    def test_webview_detection(self, driver):
        """Test that the app is detected as native Android (not WebView)"""
        print("🔍 Testing WebView detection...")
        
        # Check for WebView elements
        webview_elements = driver.find_elements(by=AppiumBy.CLASS_NAME, value='android.webkit.WebView')
        print(f"📱 Found {len(webview_elements)} WebView elements")
        
        # App should use native Android elements (no WebView)
        assert len(webview_elements) == 0, "App should use native Android elements, not WebView"
        print("✅ App uses native Android elements (no WebView)")
    
    def test_text_elements_present(self, driver):
        """Test that text elements are present on the screen"""
        print("🔍 Testing text elements presence...")
        
        all_texts = get_text_elements(driver)
        
        # Should have some text elements
        assert len(all_texts) > 0, "No text elements found on the screen"
        print(f"✅ Found {len(all_texts)} text elements")
    
    @pytest.mark.parametrize("expected_text", [
        "That's more money reaching your loved ones",
        "0% Fees on all transactions forever",
        "25 Paisa better than Google rates",
        "€10 on successful onboarding"
    ])
    def test_individual_text_verification(self, driver, expected_text):
        """Test individual text verification for each expected text"""
        print(f"🔍 Testing text: '{expected_text}'")
        
        all_texts = get_text_elements(driver)
        found, matched_text = check_text_match(expected_text, all_texts)
        
        if found:
            print(f"✅ FOUND: '{expected_text}' (matched: '{matched_text}')")
        else:
            print(f"❌ NOT FOUND: '{expected_text}'")
        
        assert found, f"Expected text '{expected_text}' not found on screen"
    
    def test_all_texts_verification(self, driver, test_data):
        """Test that all expected texts are present"""
        print("🔍 Testing all expected texts verification...")
        
        all_texts = get_text_elements(driver)
        verification_results = {}
        
        for expected_text in test_data["expected_texts"]:
            found, matched_text = check_text_match(expected_text, all_texts)
            verification_results[expected_text] = found
            
            status = "✅ FOUND" if found else "❌ NOT FOUND"
            if found:
                print(f"  {status}: '{expected_text}' (matched: '{matched_text}')")
            else:
                print(f"  {status}: '{expected_text}'")
        
        # Summary
        found_count = sum(verification_results.values())
        total_count = len(test_data["expected_texts"])
        
        print(f"\n📊 Summary: {found_count}/{total_count} expected texts found")
        
        assert found_count == total_count, f"Only {found_count}/{total_count} expected texts found"
        print("🎉 ALL TEXTS VERIFIED SUCCESSFULLY!")
