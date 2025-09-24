"""
Appium fixtures for mobile app testing
"""

import pytest
from appium import webdriver
from appium.options.common.base import AppiumOptions
from config.device_config import DEVICE_CONFIG, APP_CONFIG, WAIT_CONFIG
from data.test_data import SCOPEX_TEST_DATA


@pytest.fixture(scope="session")
def appium_options():
    """Setup Appium driver options with required capabilities"""
    options = AppiumOptions()
    
    # Device configuration
    options.load_capabilities({
        "appium:automationName": DEVICE_CONFIG["automation_name"],
        "appium:deviceName": DEVICE_CONFIG["device_name"],
        "platformName": DEVICE_CONFIG["platform_name"],
    })
    
    # App configuration
    if APP_CONFIG["package_name"]:
        options.load_capabilities({
            "appium:appPackage": APP_CONFIG["package_name"],
            "appium:appActivity": APP_CONFIG["activity_name"],
        })
    
    if APP_CONFIG["app_path"]:
        options.load_capabilities({
            "appium:app": APP_CONFIG["app_path"]
        })
    
    # Additional capabilities
    options.load_capabilities({
        "appium:autoGrantPermissions": APP_CONFIG["auto_grant_permissions"],
        "appium:ensureWebviewsHavePages": APP_CONFIG["ensure_webviews_have_pages"],
        "appium:nativeWebScreenshot": APP_CONFIG["native_web_screenshot"],
        "appium:newCommandTimeout": APP_CONFIG["new_command_timeout"],
        "appium:connectHardwareKeyboard": APP_CONFIG["connect_hardware_keyboard"]
    })
    
    return options


@pytest.fixture(scope="session")
def driver(appium_options):
    """Setup and teardown Appium driver for the test session"""
    print("🔌 Connecting to Appium server...")
    driver = webdriver.Remote(DEVICE_CONFIG["appium_server_url"], options=appium_options)
    print("✅ Connected successfully!")
    
    # Set implicit wait
    driver.implicitly_wait(WAIT_CONFIG["implicit_wait"])
    
    yield driver
    
    print("🔚 Closing driver...")
    driver.quit()


@pytest.fixture
def app_config():
    """App configuration fixture"""
    return {
        "package": APP_CONFIG["package_name"],
        "activity": APP_CONFIG["activity_name"],
        "expected_texts": SCOPEX_TEST_DATA["expected_texts"]
    }


@pytest.fixture
def test_data():
    """Test data fixture"""
    return SCOPEX_TEST_DATA


@pytest.fixture
def wait_config():
    """Wait configuration fixture"""
    return WAIT_CONFIG
