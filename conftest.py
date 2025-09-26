"""
Pytest Configuration and Fixtures for Mobile Automation Framework
Provides driver management, parameterization, and test setup/teardown functionality.
"""

import os
import pytest
from typing import Generator, Dict, Any
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions

from config.config_manager import config_manager
from utils.logger import get_logger, create_test_logger
from utils.appium_server import AppiumServerManager
from utils.soft_assertions import create_soft_assertions
from utils.data_manager import DataManager, get_data_manager
from utils.data_validator import DataValidator, SchemaManager


# Global logger
logger = get_logger("conftest")


def pytest_addoption(parser):
    """Add custom command line options for pytest."""
    parser.addoption(
        "--platform",
        action="store",
        default="android",
        help="Platform to run tests on: android or ios"
    )
    
    parser.addoption(
        "--device-name",
        action="store",
        default=None,
        help="Device name to run tests on"
    )
    
    parser.addoption(
        "--app-path",
        action="store",
        default=None,
        help="Path to the application file (.apk for Android, .app/.ipa for iOS)"
    )
    
    parser.addoption(
        "--start-server",
        action="store_true",
        default=False,
        help="Start Appium server automatically"
    )
    
    parser.addoption(
        "--keep-server",
        action="store_true",
        default=False,
        help="Keep Appium server running after tests"
    )


def pytest_configure(config):
    """Configure pytest with custom markers and setup."""
    # Register custom markers
    config.addinivalue_line(
        "markers", "android: mark test to run only on Android platform"
    )
    config.addinivalue_line(
        "markers", "ios: mark test to run only on iOS platform"
    )
    config.addinivalue_line(
        "markers", "smoke: mark test as smoke test"
    )
    config.addinivalue_line(
        "markers", "regression: mark test as regression test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)
    os.makedirs("reports", exist_ok=True)


def pytest_sessionstart(session):
    """Session start hook - start Appium server if requested."""
    if session.config.getoption("--start-server"):
        logger.info("Starting Appium server...")
        if AppiumServerManager.start_server():
            logger.info("Appium server started successfully")
        else:
            logger.error("Failed to start Appium server")
            pytest.exit("Failed to start Appium server", returncode=1)


def pytest_sessionfinish(session, exitstatus):
    """Session finish hook - stop Appium server if not keeping it."""
    if session.config.getoption("--start-server") and not session.config.getoption("--keep-server"):
        logger.info("Stopping Appium server...")
        AppiumServerManager.stop_server()


def pytest_runtest_setup(item):
    """Setup hook for each test - platform filtering."""
    platform = item.config.getoption("--platform").lower()
    
    # Skip tests based on platform markers
    if item.get_closest_marker("android") and platform != "android":
        pytest.skip("Test marked for Android platform only")
    
    if item.get_closest_marker("ios") and platform != "ios":
        pytest.skip("Test marked for iOS platform only")


@pytest.fixture(scope="session")
def test_config(request):
    """Provide test configuration from command line and config files."""
    return {
        'platform': request.config.getoption("--platform").lower(),
        'device_name': request.config.getoption("--device-name"),
        'app_path': request.config.getoption("--app-path"),
        'start_server': request.config.getoption("--start-server"),
        'keep_server': request.config.getoption("--keep-server"),
        'config_manager': config_manager
    }


@pytest.fixture(scope="session")
def appium_server():
    """Manage Appium server for the test session."""
    server_manager = AppiumServerManager.get_instance()
    
    if not server_manager.is_server_running():
        logger.info("Starting Appium server for test session...")
        if not server_manager.start_server():
            pytest.fail("Failed to start Appium server")
    
    yield server_manager
    
    # Server cleanup is handled by session hooks


@pytest.fixture(scope="function")
def driver(request, test_config, appium_server):
    """Provide Appium WebDriver instance for tests."""
    platform = test_config['platform']
    
    # Get capabilities based on platform
    if platform == "android":
        capabilities = config_manager.get_android_capabilities()
        options = UiAutomator2Options()
    elif platform == "ios":
        capabilities = config_manager.get_ios_capabilities()
        options = XCUITestOptions()
    else:
        pytest.fail(f"Unsupported platform: {platform}")
    
    # Override with command line options if provided
    if test_config['device_name']:
        capabilities['deviceName'] = test_config['device_name']
    
    if test_config['app_path']:
        capabilities['app'] = test_config['app_path']
    
    # Load capabilities into options
    options.load_capabilities(capabilities)
    
    # Get server configuration
    server_config = config_manager.get_appium_server_config()
    server_url = f"http://{server_config['host']}:{server_config['port']}/wd/hub"
    
    # Create driver
    driver_instance = None
    try:
        logger.info(f"Creating {platform} driver with capabilities: {capabilities}")
        driver_instance = webdriver.Remote(server_url, options=options)
        
        # Set timeouts
        timeout_config = config_manager.get_timeout_config()
        driver_instance.implicitly_wait(timeout_config['implicit_wait'])
        
        logger.info(f"Driver created successfully for {platform}")
        
    except Exception as e:
        logger.error(f"Failed to create driver: {str(e)}")
        pytest.fail(f"Failed to create driver: {str(e)}")
    
    yield driver_instance
    
    # Cleanup
    if driver_instance:
        try:
            # Take screenshot on failure
            if request.node.rep_call.failed:
                screenshot_name = f"failure_{request.node.name}_{platform}.png"
                screenshot_path = f"screenshots/{screenshot_name}"
                driver_instance.save_screenshot(screenshot_path)
                logger.info(f"Failure screenshot saved: {screenshot_path}")
        except Exception as e:
            logger.warning(f"Failed to take failure screenshot: {str(e)}")
        
        try:
            driver_instance.quit()
            logger.info("Driver quit successfully")
        except Exception as e:
            logger.warning(f"Error quitting driver: {str(e)}")


@pytest.fixture(scope="function")
def test_logger(request):
    """Provide test-specific logger."""
    test_name = request.node.name
    return create_test_logger(test_name)


@pytest.fixture(scope="function")
def soft_assert(request):
    """Provide soft assertions for tests."""
    test_name = request.node.name
    soft_assertions = create_soft_assertions(test_name)
    
    yield soft_assertions
    
    # Verify all soft assertions at the end of the test
    try:
        soft_assertions.assert_all(raise_exception=True)
    except Exception as e:
        # Log summary even if assertions fail
        soft_assertions.log_summary()
        raise


@pytest.fixture(params=["android", "ios"])
def cross_platform_driver(request, appium_server):
    """Provide driver for cross-platform testing."""
    platform = request.param
    
    # Get capabilities based on platform
    if platform == "android":
        capabilities = config_manager.get_android_capabilities()
        options = UiAutomator2Options()
    else:  # ios
        capabilities = config_manager.get_ios_capabilities()
        options = XCUITestOptions()
    
    options.load_capabilities(capabilities)
    
    # Get server configuration
    server_config = config_manager.get_appium_server_config()
    server_url = f"http://{server_config['host']}:{server_config['port']}/wd/hub"
    
    # Create driver
    driver_instance = None
    try:
        driver_instance = webdriver.Remote(server_url, options=options)
        
        # Set timeouts
        timeout_config = config_manager.get_timeout_config()
        driver_instance.implicitly_wait(timeout_config['implicit_wait'])
        
    except Exception as e:
        pytest.skip(f"Failed to create {platform} driver: {str(e)}")
    
    yield driver_instance, platform
    
    # Cleanup
    if driver_instance:
        try:
            driver_instance.quit()
        except Exception as e:
            logger.warning(f"Error quitting {platform} driver: {str(e)}")


@pytest.fixture(scope="function")
def page_factory(driver):
    """Provide page factory for creating page objects."""
    from pages.base_page import BasePage
    
    class PageFactory:
        def __init__(self, driver_instance):
            self.driver = driver_instance
        
        def create_page(self, page_class):
            """Create page object instance."""
            if not issubclass(page_class, BasePage):
                raise ValueError("Page class must inherit from BasePage")
            return page_class(self.driver)
    
    return PageFactory(driver)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test results for failure handling."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture(scope="session")
def data_manager():
    """
    Provide DataManager instance for test data access
    
    Returns:
        DataManager: Configured data manager instance
    """
    return get_data_manager()


@pytest.fixture(scope="session")
def data_validator():
    """
    Provide DataValidator instance for data validation
    
    Returns:
        DataValidator: Data validator instance
    """
    return DataValidator()


@pytest.fixture(scope="session")
def schema_manager():
    """
    Provide SchemaManager instance for schema-based validation
    
    Returns:
        SchemaManager: Schema manager instance
    """
    return SchemaManager()


@pytest.fixture
def test_users(data_manager):
    """
    Provide test user data
    
    Args:
        data_manager: DataManager fixture
        
    Returns:
        List[Dict]: List of valid test users
    """
    return data_manager.get_user_data("valid_users")


@pytest.fixture
def invalid_users(data_manager):
    """
    Provide invalid test user data
    
    Args:
        data_manager: DataManager fixture
        
    Returns:
        List[Dict]: List of invalid test users
    """
    return data_manager.get_user_data("invalid_users")


@pytest.fixture
def test_user(data_manager):
    """
    Provide a single test user (first valid user)
    
    Args:
        data_manager: DataManager fixture
        
    Returns:
        Dict: Single test user data
    """
    users = data_manager.get_user_data("valid_users")
    return users[0] if users else {}


@pytest.fixture
def admin_user(data_manager):
    """
    Provide admin test user
    
    Args:
        data_manager: DataManager fixture
        
    Returns:
        Dict: Admin user data
    """
    return data_manager.get_user_by_id("user_002", "valid_users") or {}


@pytest.fixture
def premium_user(data_manager):
    """
    Provide premium test user
    
    Args:
        data_manager: DataManager fixture
        
    Returns:
        Dict: Premium user data
    """
    return data_manager.get_user_by_id("user_003", "valid_users") or {}


@pytest.fixture
def device_configs(data_manager, request):
    """
    Provide device configuration data with optional filtering
    
    Args:
        data_manager: DataManager fixture
        request: pytest request object
        
    Returns:
        List[Dict]: List of device configurations
    """
    # Get platform from command line or test marker
    platform = getattr(request.config.option, 'platform', None)
    
    # Check for platform marker on test
    if hasattr(request, 'node'):
        for marker in request.node.iter_markers():
            if marker.name in ['android', 'ios']:
                platform = 'Android' if marker.name == 'android' else 'iOS'
                break
    
    return data_manager.get_device_data(platform=platform)


@pytest.fixture
def high_priority_devices(data_manager, request):
    """
    Provide high priority device configurations
    
    Args:
        data_manager: DataManager fixture
        request: pytest request object
        
    Returns:
        List[Dict]: List of high priority device configurations
    """
    platform = getattr(request.config.option, 'platform', None)
    return data_manager.get_device_data(platform=platform, priority="high")


@pytest.fixture
def app_config(data_manager, request):
    """
    Provide application configuration data
    
    Args:
        data_manager: DataManager fixture
        request: pytest request object
        
    Returns:
        Dict: Application configuration
    """
    platform = getattr(request.config.option, 'platform', None)
    return data_manager.get_app_config(platform)


@pytest.fixture
def environment_config(data_manager, config):
    """
    Provide environment-specific configuration
    
    Args:
        data_manager: DataManager fixture
        config: ConfigManager fixture
        
    Returns:
        Dict: Environment configuration
    """
    environment = config.get_environment()
    return data_manager.get_environment_data(environment)


@pytest.fixture
def performance_benchmarks(data_manager):
    """
    Provide performance benchmark data
    
    Args:
        data_manager: DataManager fixture
        
    Returns:
        Dict: Performance benchmarks
    """
    return data_manager.get_performance_benchmarks()


@pytest.fixture
def error_messages(data_manager):
    """
    Provide error message data
    
    Args:
        data_manager: DataManager fixture
        
    Returns:
        Dict: Error messages by category
    """
    return data_manager.get_error_messages()


@pytest.fixture
def localization_data(data_manager):
    """
    Provide localization data
    
    Args:
        data_manager: DataManager fixture
        
    Returns:
        Dict: Localization data
    """
    return data_manager.get_localization_data()


@pytest.fixture(params=["user_001", "user_002", "user_003"])
def parametrized_user(request, data_manager):
    """
    Parametrized fixture for testing with multiple users
    
    Args:
        request: pytest request object
        data_manager: DataManager fixture
        
    Returns:
        Dict: User data for current parameter
    """
    user_id = request.param
    return data_manager.get_user_by_id(user_id, "valid_users")


@pytest.fixture(params=["high", "medium"])
def parametrized_devices(request, data_manager):
    """
    Parametrized fixture for testing with different device priorities
    
    Args:
        request: pytest request object
        data_manager: DataManager fixture
        
    Returns:
        List[Dict]: Device configurations for current priority
    """
    priority = request.param
    return data_manager.get_device_data(priority=priority)


@pytest.fixture
def login_scenarios(data_manager):
    """
    Provide login test scenarios
    
    Args:
        data_manager: DataManager fixture
        
    Returns:
        List[Dict]: Login test scenarios
    """
    users_data = data_manager.load_data("users.json")
    return users_data.get("test_scenarios", {}).get("login_validation", [])


@pytest.fixture
def checkout_scenario(data_manager):
    """
    Provide checkout flow test scenario
    
    Args:
        data_manager: DataManager fixture
        
    Returns:
        List[Dict]: Checkout scenario steps
    """
    return data_manager.get_test_scenario("checkout_flow")


@pytest.fixture
def registration_scenario(data_manager):
    """
    Provide user registration test scenario
    
    Args:
        data_manager: DataManager fixture
        
    Returns:
        List[Dict]: Registration scenario steps
    """
    return data_manager.get_test_scenario("user_registration")


@pytest.fixture
def test_products(data_manager):
    """
    Provide test product data
    
    Args:
        data_manager: DataManager fixture
        
    Returns:
        List[Dict]: Test product data
    """
    app_data = data_manager.load_data("app_data.yaml")
    return app_data.get("test_data", {}).get("products", [])


@pytest.fixture
def search_terms(data_manager):
    """
    Provide search term test data
    
    Args:
        data_manager: DataManager fixture
        
    Returns:
        Dict: Search terms by category (valid, invalid, special_characters)
    """
    app_data = data_manager.load_data("app_data.yaml")
    return app_data.get("test_data", {}).get("search_terms", {})


@pytest.fixture
def form_data(data_manager):
    """
    Provide form test data
    
    Args:
        data_manager: DataManager fixture
        
    Returns:
        Dict: Form data (valid and invalid)
    """
    app_data = data_manager.load_data("app_data.yaml")
    return app_data.get("test_data", {}).get("form_data", {})


@pytest.fixture
def ui_timeouts(data_manager):
    """
    Provide UI timeout configurations
    
    Args:
        data_manager: DataManager fixture
        
    Returns:
        Dict: Timeout values for different operations
    """
    app_data = data_manager.load_data("app_data.yaml")
    return app_data.get("test_data", {}).get("ui_elements", {}).get("timeouts", {})


@pytest.fixture
def gesture_settings(data_manager):
    """
    Provide gesture configuration data
    
    Args:
        data_manager: DataManager fixture
        
    Returns:
        Dict: Gesture settings (durations, scale factors)
    """
    app_data = data_manager.load_data("app_data.yaml")
    return app_data.get("test_data", {}).get("ui_elements", {}).get("gestures", {})


@pytest.fixture
def validated_user_data(test_user, data_validator):
    """
    Provide validated user data
    
    Args:
        test_user: Test user fixture
        data_validator: DataValidator fixture
        
    Returns:
        Dict: Validated user data
        
    Raises:
        AssertionError: If user data validation fails
    """
    validation_result = data_validator.validate_user_data(test_user)
    
    if not validation_result.is_valid:
        pytest.fail(f"User data validation failed: {validation_result.errors}")
    
    return test_user


@pytest.fixture
def validated_device_config(device_configs, data_validator):
    """
    Provide validated device configuration
    
    Args:
        device_configs: Device configs fixture
        data_validator: DataValidator fixture
        
    Returns:
        List[Dict]: Validated device configurations
        
    Raises:
        AssertionError: If device data validation fails
    """
    validated_configs = []
    
    for device in device_configs:
        validation_result = data_validator.validate_device_data(device)
        
        if not validation_result.is_valid:
            pytest.fail(f"Device data validation failed for {device.get('device_name', 'unknown')}: {validation_result.errors}")
        
        validated_configs.append(device)
    
    return validated_configs


# Parametrized fixtures for cross-platform testing
@pytest.fixture(params=[
    {"platform": "iOS", "version": "16.0"},
    {"platform": "Android", "version": "13"}
])
def platform_config(request, data_manager):
    """
    Parametrized fixture for cross-platform testing
    
    Args:
        request: pytest request object
        data_manager: DataManager fixture
        
    Returns:
        Dict: Platform configuration
    """
    platform_info = request.param
    devices = data_manager.get_device_data(platform=platform_info["platform"])
    
    # Filter by version if specified
    if platform_info["version"]:
        devices = [d for d in devices if d.get("platform_version", "").startswith(platform_info["version"])]
    
    return {
        "platform": platform_info["platform"],
        "version": platform_info["version"],
        "devices": devices
    }


@pytest.fixture(params=["portrait", "landscape"])
def orientation_config(request):
    """
    Parametrized fixture for orientation testing
    
    Args:
        request: pytest request object
        
    Returns:
        str: Device orientation
    """
    return request.param


# Data-driven test fixtures
@pytest.fixture
def data_driven_login_tests(login_scenarios):
    """
    Provide data-driven login test cases
    
    Args:
        login_scenarios: Login scenarios fixture
        
    Returns:
        List[Dict]: Login test cases with expected results
    """
    return login_scenarios


@pytest.fixture
def data_driven_device_tests(device_configs):
    """
    Provide data-driven device test cases
    
    Args:
        device_configs: Device configs fixture
        
    Returns:
        List[Dict]: Device test cases
    """
    return device_configs


# Utility fixtures for common test data
@pytest.fixture
def test_data():
    """Provide common test data."""
    return {
        'valid_credentials': {
            'username': 'testuser@example.com',
            'password': 'TestPassword123'
        },
        'invalid_credentials': {
            'username': 'invalid@example.com',
            'password': 'wrongpassword'
        },
        'test_text': 'Hello, Mobile Automation!',
        'timeout': 10
    }


# Parametrized fixtures for different test scenarios
@pytest.fixture(params=[
    {'platform': 'android', 'orientation': 'portrait'},
    {'platform': 'android', 'orientation': 'landscape'},
    {'platform': 'ios', 'orientation': 'portrait'},
    {'platform': 'ios', 'orientation': 'landscape'}
])
def platform_orientation(request):
    """Provide platform and orientation combinations."""
    return request.param


@pytest.fixture(params=['small', 'medium', 'large'])
def screen_size(request):
    """Provide different screen size categories for responsive testing."""
    sizes = {
        'small': {'width': 320, 'height': 568},   # iPhone SE
        'medium': {'width': 375, 'height': 667},  # iPhone 8
        'large': {'width': 414, 'height': 896}    # iPhone 11
    }
    return sizes[request.param]