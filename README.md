# Mobile App Testing Framework

A professional pytest-based framework for mobile app testing with Appium.

## 📁 Framework Structure

```
python-mobile-framework/
├── config/
│   └── device_config.py          # Device and app configuration
├── data/
│   └── test_data.py              # Test data and scenarios
├── tests/
│   ├── __init__.py
│   ├── fixtures/
│   │   ├── __init__.py
│   │   └── appium_fixtures.py    # Appium driver fixtures
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── text_utils.py          # Text verification utilities
│   │   └── wait_utils.py          # Professional wait strategies
│   ├── test_scopex_app.py         # Scopex app specific tests
│   └── test_basic_functionality.py # General mobile app tests
├── pytest.ini                    # Pytest configuration
├── venv/                         # Python virtual environment
└── README.md                     # This file
```

## 🚀 Quick Start

### 1. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 2. Run Tests
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_scopex_app.py

# Run with verbose output
python -m pytest -v

# Run specific test
python -m pytest tests/test_scopex_app.py::TestScopexMobileApp::test_app_launch
```

## 📱 What It Tests

### Scopex Mobile App Tests (`test_scopex_app.py`)
- ✅ App launches successfully
- ✅ Screen has elements present
- ✅ Uses native Android (not WebView)
- ✅ Text elements are present
- ✅ Individual text verification (parametrized)
- ✅ Comprehensive text verification

### Basic Functionality Tests (`test_basic_functionality.py`)
- ✅ App launch verification
- ✅ Screen elements count
- ✅ WebView detection
- ✅ Text elements presence

## 🔧 Prerequisites

- Appium server running on `http://127.0.0.1:4723`
- Android device/emulator connected
- App `com.scopex.scopexmobile` installed

## 📊 Test Output

```
============================= test session starts ==============================
collected 10 items

tests/test_basic_functionality.py::test_app_launch PASSED                [ 10%]
tests/test_basic_functionality.py::test_screen_elements_count PASSED     [ 20%]
tests/test_basic_functionality.py::test_webview_detection PASSED          [ 30%]
tests/test_basic_functionality.py::test_text_elements_present PASSED     [ 40%]
tests/test_scopex_app.py::TestScopexMobileApp::test_app_launch PASSED     [ 50%]
tests/test_scopex_app.py::TestScopexMobileApp::test_screen_elements_count PASSED [ 60%]
tests/test_scopex_app.py::TestScopexMobileApp::test_webview_detection PASSED [ 70%]
tests/test_scopex_app.py::TestScopexMobileApp::test_text_elements_present PASSED [ 80%]
tests/test_scopex_app.py::TestScopexMobileApp::test_individual_text_verification[That's more money reaching your loved ones] PASSED [ 90%]
tests/test_scopex_app.py::TestScopexMobileApp::test_individual_text_verification[0% Fees on all transactions forever] PASSED [100%]

============================== 10 passed in 45.2s ===============================
```

## 🎯 Framework Features

- **Professional Wait Strategies** - No hardcoded sleeps, proper WebDriverWait
- **Separated Configuration** - Device, app, and test data in separate files
- **Organized Structure** - Separate fixtures, utilities, and tests
- **Reusable Components** - Shared fixtures and utilities
- **Parametrized Tests** - Efficient testing of multiple scenarios
- **Professional Setup** - Industry-standard pytest framework
- **Clean Architecture** - Easy to extend and maintain
- **Configurable** - Easy to change device info, app config, and test data

## 🎉 That's It!

A clean, professional mobile app testing framework using pytest!
