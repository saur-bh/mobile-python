# Python Appium Mobile Automation Framework

A minimal yet robust Python framework for mobile automation using Appium and pytest. This framework implements industry best practices including Page Object Model with Page Factory pattern, comprehensive configuration management, and advanced reporting capabilities.

## 🚀 Features

- **Page Object Model**: Clean separation of concerns with Page Factory pattern
- **Cross-Platform Support**: Unified testing for both Android and iOS
- **Configuration Management**: Centralized config.ini for device capabilities and environment settings
- **Appium Server Management**: Automated server start/stop operations
- **Soft Assertions**: Non-critical validations that don't stop test execution
- **Advanced Reporting**: HTML reports with screenshots, device info, and performance metrics
- **Configurable Logging**: Multi-level logging with file and console output
- **Pytest Integration**: Full pytest support with fixtures and parameterization
- **Thread-Safe**: Designed for parallel test execution
- **Exception Handling**: Robust error handling throughout the framework
- **Test Data Management**: Centralized data management with JSON, YAML, and CSV support
- **Data Validation**: Schema-based validation for test data integrity
- **Pytest Fixtures**: Rich set of fixtures for data-driven testing
- **Environment Management**: Automated Python environment setup and dependency management
- **Cross-Platform Compatibility**: Tested with Python 3.8+ including latest Python 3.13

## 📁 Project Structure

```
python-appium-mobile-scopex/
├── config/
│   ├── __init__.py
│   ├── config.ini              # Configuration settings
│   └── config_manager.py       # Configuration management
├── pages/
│   ├── __init__.py
│   ├── base_page.py           # Base page class with common functionality
│   └── login_page.py          # Example page object
├── tests/
│   ├── __init__.py
│   ├── test_login.py          # Example login tests
│   └── test_gestures.py       # Example gesture tests
├── test_data/                 # Test data management
│   ├── __init__.py
│   ├── users.json             # User test data
│   ├── app_data.yaml          # Application configuration data
│   ├── devices.csv            # Device configuration data
│   └── schemas/               # Data validation schemas
│       ├── user.json          # User data schema
│       └── device.json        # Device data schema
├── utils/
│   ├── __init__.py
│   ├── appium_server.py       # Appium server management
│   ├── logger.py              # Logging utilities
│   ├── report_manager.py      # Enhanced reporting
│   ├── soft_assertions.py     # Soft assertion utilities
│   ├── data_manager.py        # Test data management
│   └── data_validator.py      # Data validation and schemas
├── reports/
│   └── screenshots/           # Test screenshots
├── venv/                      # Virtual environment (created by setup)
├── conftest.py                # Pytest configuration and fixtures
├── pytest.ini                # Pytest settings
├── requirements.txt           # Python dependencies
├── setup_env.py               # Automated environment setup script
├── activate_env.sh            # Environment activation script (macOS/Linux)
├── ENVIRONMENT_SETUP.md       # Detailed setup instructions
└── README.md                  # This file
```

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.8 or higher (Python 3.13+ recommended)
- Node.js (for Appium)
- Java JDK 8 or higher
- Android SDK (for Android testing)
- Xcode (for iOS testing on macOS)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd python-appium-mobile-scopex
```

### 2. Automated Environment Setup (Recommended)

The framework includes an automated setup script that handles virtual environment creation, dependency installation, and environment configuration:

```bash
# Run the automated setup script
python setup_env.py

# Activate the environment (macOS/Linux)
source activate_env.sh

# Or activate manually
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

The automated setup will:
- ✅ Check Python version compatibility
- ✅ Create a virtual environment
- ✅ Upgrade pip to the latest version
- ✅ Install all required dependencies
- ✅ Verify package installations
- ✅ Generate activation scripts
- ✅ Provide quick start commands

### 3. Manual Environment Setup (Alternative)

If you prefer manual setup or encounter issues with the automated script:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import appium, pytest, selenium; print('All packages installed successfully!')"
```

### 4. Environment Verification

```bash
# Quick verification
python -c "
import appium
import pytest
import selenium
from loguru import logger
import yaml
print('✅ All core packages are working!')
print(f'Appium version: {appium.__version__}')
print(f'Pytest version: {pytest.__version__}')
print(f'Selenium version: {selenium.__version__}')
"
```

### 4. Install Appium

```bash
npm install -g appium
npm install -g @appium/doctor

# Install drivers
appium driver install uiautomator2  # For Android
appium driver install xcuitest      # For iOS
```

### 5. Verify Setup

```bash
appium-doctor --android  # Check Android setup
appium-doctor --ios      # Check iOS setup (macOS only)
```

### 6. Quick Start Commands

After successful setup, you can use these quick commands:

```bash
# Run all tests
pytest

# Run tests with HTML report
pytest --html=reports/report.html --self-contained-html

# Run data-driven tests
pytest tests/test_data_driven.py

# Run with performance monitoring
pytest --benchmark-only

# Generate comprehensive report
pytest --html=reports/report.html --self-contained-html --tb=short -v
```

For detailed environment setup instructions, see [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md).

### 7. Configure Settings

Edit `config/config.ini` to match your environment:

```ini
[android_capabilities]
platformName = Android
platformVersion = 11.0
deviceName = emulator-5554
app = /path/to/your/app.apk

[ios_capabilities]
platformName = iOS
platformVersion = 15.0
deviceName = iPhone 13
bundleId = com.yourapp.bundle
```

## 🎯 Usage Examples

### Basic Test Execution

```bash
# Run all tests
pytest

# Run tests with HTML report
pytest --html=reports/report.html --self-contained-html

# Run tests for specific platform
pytest -m android
pytest -m ios

# Run tests in parallel
pytest -n 4

# Run with specific log level
pytest --log-level=DEBUG
```

### Advanced Test Execution

```bash
# Run tests with custom configuration
pytest --config-file=config/staging.ini

# Run specific test file
pytest tests/test_login.py

# Run tests with tags
pytest -m "smoke and not slow"

# Generate Allure report
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

### Data-Driven Testing Examples

```bash
# Run tests with specific user data
pytest tests/test_login.py::test_login_with_valid_user

# Run parametrized tests with multiple users
pytest tests/test_login.py::test_parametrized_login

# Run tests with device-specific data
pytest -m android tests/test_gestures.py

# Run tests with validation
pytest --validate-data tests/
```

### Writing Tests

#### 1. Create a Page Object

```python
from pages.base_page import BasePage
from appium.webdriver.common.appiumby import AppiumBy

class HomePage(BasePage):
    # Locators
    WELCOME_MESSAGE = (AppiumBy.ID, "com.app:id/welcome")
    MENU_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "menu")
    
    def __init__(self, driver):
        super().__init__(driver)
    
    def is_page_loaded(self):
        return self.is_element_visible(self.WELCOME_MESSAGE)
    
    def click_menu(self):
        self.click_element(self.MENU_BUTTON)
```

#### 2. Write Test Cases

```python
import pytest
from pages.login_page import LoginPage
from utils.soft_assert import SoftAssert

class TestLogin:
    def test_valid_login(self, driver, config, soft_assert, test_user):
        """Test login with valid credentials using test data"""
        login_page = LoginPage(driver)
        
        # Navigate to login page
        login_page.navigate_to_login()
        
        # Perform login using test data
        login_page.login(test_user['username'], test_user['password'])
        
        # Verify login success
        soft_assert.assert_true(
            login_page.is_login_successful(),
            "Login should be successful"
        )
        
        # Assert all soft assertions
        soft_assert.assert_all()

    def test_login_with_invalid_users(self, driver, invalid_users, soft_assert):
        """Test login with multiple invalid users"""
        login_page = LoginPage(driver)
        
        for user in invalid_users:
            login_page.navigate_to_login()
            login_page.login(user['username'], user['password'])
            
            soft_assert.assert_true(
                login_page.is_error_displayed(),
                f"Error should be displayed for user: {user['username']}"
            )
            
            if 'expected_error' in user:
                actual_error = login_page.get_error_message()
                soft_assert.assert_equal(
                    actual_error, user['expected_error'],
                    f"Expected error message for user: {user['username']}"
                )
        
        soft_assert.assert_all()

    @pytest.mark.parametrize("user_id", ["user_001", "user_002", "user_003"])
    def test_parametrized_login(self, driver, data_manager, user_id):
        """Test login with parametrized user data"""
        user = data_manager.get_user_by_id(user_id, "valid_users")
        login_page = LoginPage(driver)
        
        login_page.navigate_to_login()
        login_page.login(user['username'], user['password'])
        
        assert login_page.is_login_successful(), f"Login failed for user: {user_id}"

    def test_data_driven_login(self, driver, login_scenarios):
        """Test login using data-driven scenarios"""
        login_page = LoginPage(driver)
        
        for scenario in login_scenarios:
            login_page.navigate_to_login()
            login_page.login(scenario['username'], scenario['password'])
            
            if scenario['should_succeed']:
                assert login_page.is_login_successful(), f"Login should succeed: {scenario['description']}"
            else:
                assert login_page.is_error_displayed(), f"Login should fail: {scenario['description']}"

    @pytest.mark.android
    def test_android_specific_feature(self, driver, app_config):
        """Test Android-specific functionality with app config"""
        android_config = app_config.get('android', {})
        # Android-specific test logic using configuration
        pass

    @pytest.mark.ios
    def test_ios_specific_feature(self, driver, app_config):
        """Test iOS-specific functionality with app config"""
        ios_config = app_config.get('ios', {})
        # iOS-specific test logic using configuration
        pass

    def test_with_performance_validation(self, driver, performance_benchmarks, test_user):
        """Test with performance validation"""
        login_page = LoginPage(driver)
        
        # Get performance benchmarks
        login_benchmark = performance_benchmarks.get('page_load_times', {}).get('login_page', 5.0)
        
        # Measure login performance
        import time
        start_time = time.time()
        
        login_page.navigate_to_login()
        login_page.login(test_user['username'], test_user['password'])
        
        end_time = time.time()
        login_duration = end_time - start_time
        
        assert login_duration <= login_benchmark, f"Login took {login_duration}s, expected <= {login_benchmark}s"

    def test_with_localization(self, driver, localization_data, test_user):
        """Test with localization data"""
        login_page = LoginPage(driver)
        
        # Get localized text
        login_button_text = localization_data.get('login_button', {}).get('en', 'Login')
        
        login_page.navigate_to_login()
        
        # Verify localized text
        assert login_page.get_login_button_text() == login_button_text
```

### Using Framework Features

#### Soft Assertions

```python
def test_with_soft_assertions(self, driver, soft_assert, test_products):
    page = ProductPage(driver)
    
    for product in test_products:
        page.search_product(product['name'])
        
        soft_assert.assert_true(
            page.is_product_found(), 
            f"Product {product['name']} should be found"
        )
        soft_assert.assert_equal(
            page.get_product_price(), 
            product['expected_price'], 
            f"Price validation for {product['name']}"
        )
    
    # All failures will be reported at the end
    soft_assert.assert_all()
```

#### Logging

```python
def test_with_logging(self, driver, test_logger, validated_user_data):
    test_logger.test_start("Login test with validated data")
    test_logger.step(f"Using user: {validated_user_data['username']}")
    test_logger.info("Additional information")
    test_logger.warning("This is a warning")
    test_logger.error("This is an error")
    test_logger.test_end("COMPLETED")

# Using data manager directly
def test_with_data_manager(self, data_manager):
    # Load specific data
    user = data_manager.get_user_by_id("user_001", "valid_users")
    devices = data_manager.get_device_data(platform="Android", priority="high")
    
    # Use data in test logic

# Using parametrized fixtures
def test_cross_platform(self, platform_config, test_user):
    """Test that runs on multiple platforms"""
    platform = platform_config['platform']
    devices = platform_config['devices']
    
    # Platform-specific test logic
    if platform == "iOS":
        # iOS-specific assertions
        pass
    elif platform == "Android":
        # Android-specific assertions
        pass
```

#### Screenshots

```python
def test_with_screenshots(self, driver):
    from utils.report_manager import add_screenshot_to_report
    
    # Automatic screenshot on failure (configured in conftest.py)
    # Or manual screenshot
    screenshot_path = add_screenshot_to_report(driver, "manual_screenshot")
```

## 🔧 Configuration

### config.ini Sections

#### Appium Server Settings
```ini
[appium_server]
host = 127.0.0.1
port = 4723
command_timeout = 60
```

#### Android Capabilities
```ini
[android_capabilities]
platformName = Android
platformVersion = 11.0
deviceName = emulator-5554
automationName = UiAutomator2
app = /path/to/app.apk
appPackage = com.example.app
appActivity = .MainActivity
```

#### iOS Capabilities
```ini
[ios_capabilities]
platformName = iOS
platformVersion = 15.0
deviceName = iPhone 13
automationName = XCUITest
bundleId = com.example.app
```

#### Environment Settings
```ini
[environment]
test_environment = staging
base_url = https://api.staging.example.com
screenshot_on_failure = true
video_recording = false
parallel_execution = true
```

#### Test Data Configuration
```ini
[test_data]
data_directory = test_data
validate_schemas = true
cache_data = true
environment_filter = true
```

### Pytest Configuration

The framework uses `pytest.ini` for test configuration:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --html=reports/report.html
    --self-contained-html
    --tb=short
    -v
markers =
    smoke: Smoke tests
    android: Android-specific tests
    ios: iOS-specific tests
```

## 📊 Reporting

The framework provides comprehensive reporting capabilities:

### HTML Reports
- Detailed test execution reports with screenshots
- Test duration and performance metrics
- Environment and device information
- Custom test metadata and logs
- Test data validation results

### JSON Reports
- Machine-readable test results
- Integration with CI/CD pipelines
- Custom data export capabilities
- Test data usage tracking

### Allure Reports
- Interactive test reports with rich visualizations
- Test history and trends
- Detailed step-by-step execution logs
- Screenshot and video attachments
- Data-driven test parameters

### Report Customization
```python
# Add custom information to reports
@pytest.fixture(autouse=True)
def add_test_info(request, data_manager):
    # Add custom metadata to test reports
    request.config._metadata['Test Data Version'] = data_manager.get_data_version()
    request.config._metadata['Environment'] = data_manager.get_current_environment()
    
# Add test data information to reports
def test_with_data_reporting(self, test_user, report_helper):
    report_helper.log_test_data("User Data", test_user)
    report_helper.log_step("Login with test user")
    # Test logic here
```

Additional JSON reports are generated for programmatic analysis:
```json
{
  "environment": {
    "platform": "Android",
    "device_name": "emulator-5554"
  },
  "summary": {
    "passed": 15,
    "failed": 2,
    "skipped": 1
  },
  "test_results": [...]
}
```

For advanced reporting, use Allure:
```bash
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

## 🧪 Testing Best Practices

### Test Organization
- Use descriptive test names that explain the test purpose
- Group related tests in classes
- Use appropriate test markers for categorization
- Keep tests independent and atomic
- Leverage parametrized fixtures for data-driven testing

### Page Object Model
- Create separate page classes for each screen/page
- Use meaningful method names that describe user actions
- Keep locators organized and maintainable
- Implement wait strategies for dynamic elements

### Data Management
- Use the centralized DataManager for all test data access
- Implement schema validation for data integrity
- Separate test data by environment and platform
- Use fixtures for consistent data injection
- Validate data before using in tests

### Test Data Best Practices
```python
# Good: Use fixtures for data access
def test_login(self, test_user, validated_user_data):
    # Data is pre-validated and ready to use
    pass

# Good: Use parametrized fixtures for multiple scenarios
@pytest.mark.parametrize("user_type", ["admin", "regular", "premium"])
def test_user_permissions(self, data_manager, user_type):
    user = data_manager.get_user_by_role(user_type)
    # Test logic here

# Good: Environment-specific data
def test_api_integration(self, environment_config):
    api_url = environment_config['api_base_url']
    # Use environment-specific configuration
```

### Assertions
- Use soft assertions for multiple validations
- Provide meaningful assertion messages
- Validate both positive and negative scenarios
- Include performance validations where applicable
- Use data-driven assertions with expected results

### Error Handling
- Implement proper exception handling
- Use try-catch blocks for unstable operations
- Provide meaningful error messages
- Include cleanup operations in finally blocks
- Validate error messages against expected data

### Parallel Execution
- Design tests to be independent
- Avoid shared state between tests
- Use unique test data

## 🔍 Troubleshooting

### Common Issues

#### Appium Server Connection
```bash
# Check if Appium server is running
curl http://localhost:4723/wd/hub/status

# Start Appium server manually
appium --port 4723
```

#### Device Connection
```bash
# Check connected Android devices
adb devices

# Check iOS simulators
xcrun simctl list devices
```

#### Element Not Found
- Verify locators using Appium Inspector
- Check element timing with explicit waits
- Ensure app state is correct

#### Performance Issues
- Use explicit waits instead of implicit waits
- Optimize locator strategies
- Reduce screenshot frequency

### Debug Mode

Enable debug logging:
```bash
pytest --log-level=DEBUG -s
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the example tests

## 🔄 Version History

- **v1.0.0**: Initial release with core functionality
  - Page Object Model implementation
  - Cross-platform support
  - Configuration management
  - HTML reporting
  - Soft assertions
  - Logging system

---

**Happy Testing! 🚀**