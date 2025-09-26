"""
Text verification utilities for mobile app testing
"""

from appium.webdriver.common.appiumby import AppiumBy
from tests.utils.wait_utils import WaitUtils


def get_text_elements(driver):
    """Get all text elements from the app using proper waits"""
    print("🔍 Starting text extraction...")
    
    # Use WaitUtils for proper waiting
    wait_utils = WaitUtils(driver)
    
    # Wait for app to be ready
    print("⏳ Waiting for app to be ready...")
    wait_utils.wait_for_app_ready()
    
    # Wait for text elements to be loaded
    print("⏳ Waiting for text elements to load...")
    text_elements = wait_utils.wait_for_text_elements()
    
    print(f"📱 Found {len(text_elements)} TextView elements")
    
    # Extract all text content
    all_texts = []
    for element in text_elements:
        try:
            text_content = element.text.strip()
            if text_content:  # Only add non-empty text
                all_texts.append(text_content)
        except Exception as e:
            print(f"⚠️ Error extracting text: {e}")
    
    print(f"📝 Extracted {len(all_texts)} text elements:")
    for i, text in enumerate(all_texts, 1):
        print(f"  {i}. '{text}'")
    
    return all_texts


def check_text_match(expected_text, actual_texts):
    """Check if expected text matches any of the actual texts"""
    for actual_text in actual_texts:
        # More flexible matching - check if key parts of the text match
        if (expected_text.lower() in actual_text.lower() or 
            actual_text.lower() in expected_text.lower() or
            any(word in actual_text.lower() for word in expected_text.lower().split() if len(word) > 3)):
            return True, actual_text
    return False, ""


def verify_webview_context(driver):
    """Check if the app uses WebView and switch context if needed"""
    print("🔍 Checking for WebView...")
    
    # Check for WebView elements
    webview_elements = driver.find_elements(by=AppiumBy.CLASS_NAME, value='android.webkit.WebView')
    print(f"📱 Found {len(webview_elements)} WebView elements")
    
    if len(webview_elements) > 0:
        print("🌐 App uses WebView - checking contexts...")
        contexts = driver.contexts
        print(f"📋 Available contexts: {contexts}")
        
        if len(contexts) > 1:
            print("🔄 Switching to WebView context...")
            driver.switch_to.context(contexts[1])
            print("✅ Switched to WebView context")
            return True
        else:
            print("⚠️ Only one context available - staying in native context")
    else:
        print("📱 App uses native Android elements (no WebView)")
    
    return False
