# Python Environment Setup Guide

## 🚀 Quick Setup (Automated)

The easiest way to set up your Python environment is using our automated setup script:

```bash
# Run the automated setup script
python3 setup_env.py
```

This script will:
- ✅ Check Python version compatibility (3.8+)
- 🏗️ Create a virtual environment
- 📦 Install all dependencies
- 🔍 Verify installation
- 📝 Create activation scripts

## 📋 Manual Setup (Step by Step)

If you prefer manual setup or need to troubleshoot:

### 1. Prerequisites

**Required:**
- Python 3.8 or higher
- pip (Python package manager)

**Check your Python version:**
```bash
python3 --version
# Should show Python 3.8.x or higher
```

### 2. Create Virtual Environment

```bash
# Navigate to project directory
cd python-appium-mobile-scopex

# Create virtual environment
python3 -m venv mobile_automation_env

# Activate virtual environment
# On macOS/Linux:
source mobile_automation_env/bin/activate

# On Windows:
mobile_automation_env\Scripts\activate
```

### 3. Upgrade pip

```bash
# Upgrade pip to latest version
pip install --upgrade pip
```

### 4. Install Dependencies

```bash
# Install all project dependencies
pip install -r requirements.txt
```

### 5. Verify Installation

```bash
# Test key imports
python -c "import appium; import pytest; import selenium; print('✅ All packages installed successfully')"
```

## 🔧 Environment Activation

### Using Activation Scripts

After running the automated setup, you'll have activation scripts:

**On macOS/Linux:**
```bash
# Make executable (if needed)
chmod +x activate_env.sh

# Activate environment
source activate_env.sh
```

**On Windows:**
```cmd
# Activate environment
activate_env.bat
```

### Manual Activation

**On macOS/Linux:**
```bash
source mobile_automation_env/bin/activate
```

**On Windows:**
```cmd
mobile_automation_env\Scripts\activate
```

### Verify Activation

When activated, your terminal prompt should show:
```bash
(mobile_automation_env) your-username@your-machine:~/python-appium-mobile-scopex$
```

## 📦 Dependencies Overview

Our `requirements.txt` includes:

### Core Testing Framework
- `appium-python-client` - Appium Python bindings
- `selenium` - WebDriver for mobile automation
- `pytest` - Testing framework
- `pytest-html` - HTML test reports
- `pytest-xdist` - Parallel test execution

### Data Management
- `pyyaml` - YAML data file support
- `jsonschema` - JSON schema validation
- `pandas` - Data processing
- `openpyxl` - Excel file support

### Reporting & Logging
- `allure-pytest` - Advanced test reporting
- `loguru` - Enhanced logging
- `rich` - Beautiful terminal output

### Development Tools
- `black` - Code formatting
- `flake8` - Code linting
- `pytest-cov` - Code coverage

## 🧪 Testing Your Setup

### 1. Run Sample Tests

```bash
# Activate environment first
source mobile_automation_env/bin/activate

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_login.py

# Run with HTML report
pytest --html=reports/report.html tests/
```

### 2. Test Data Management

```bash
# Test data-driven tests
pytest tests/test_data_driven.py

# Test with specific environment
pytest tests/test_data_driven.py --env=staging
```

### 3. Generate Reports

```bash
# HTML Report
pytest --html=reports/report.html --self-contained-html tests/

# Allure Report
pytest --alluredir=reports/allure-results tests/
allure serve reports/allure-results
```

## 🔍 Troubleshooting

### Common Issues

**1. Python Version Error**
```
Error: Python 3.8 or higher is required!
```
**Solution:** Install Python 3.8+ from [python.org](https://python.org)

**2. Permission Denied (macOS/Linux)**
```
Permission denied: './activate_env.sh'
```
**Solution:** 
```bash
chmod +x activate_env.sh
```

**3. Module Not Found**
```
ModuleNotFoundError: No module named 'appium'
```
**Solution:** Ensure virtual environment is activated:
```bash
source mobile_automation_env/bin/activate
pip install -r requirements.txt
```

**4. Pip Install Fails**
```
ERROR: Could not install packages due to an EnvironmentError
```
**Solution:** Upgrade pip and try again:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root for environment-specific settings:

```bash
# .env file
APPIUM_SERVER_URL=http://localhost:4723
TEST_ENVIRONMENT=development
DEVICE_PLATFORM=android
LOG_LEVEL=INFO
```

### IDE Configuration

**VS Code:**
1. Open project folder
2. Select Python interpreter: `Ctrl+Shift+P` → "Python: Select Interpreter"
3. Choose: `./mobile_automation_env/bin/python`

**PyCharm:**
1. File → Settings → Project → Python Interpreter
2. Add → Existing Environment
3. Select: `./mobile_automation_env/bin/python`

## 🚀 Quick Commands Reference

```bash
# Environment Management
source mobile_automation_env/bin/activate  # Activate environment
deactivate                                 # Deactivate environment

# Testing
pytest tests/                              # Run all tests
pytest tests/test_login.py                 # Run specific test
pytest -v tests/                           # Verbose output
pytest -x tests/                           # Stop on first failure
pytest --lf tests/                         # Run last failed tests

# Reporting
pytest --html=reports/report.html tests/   # HTML report
pytest --alluredir=reports/allure tests/   # Allure report
pytest --cov=utils tests/                  # Coverage report

# Data-Driven Testing
pytest tests/test_data_driven.py           # Data-driven tests
pytest --env=staging tests/                # Environment-specific
pytest -k "login" tests/                   # Run tests matching pattern

# Development
black .                                    # Format code
flake8 .                                   # Lint code
pytest --cov=. --cov-report=html tests/   # Coverage with HTML
```

## 📁 Project Structure After Setup

```
python-appium-mobile-scopex/
├── mobile_automation_env/          # Virtual environment
├── setup_env.py                    # Automated setup script
├── activate_env.sh                 # Environment activation (Unix)
├── activate_env.bat                # Environment activation (Windows)
├── requirements.txt                # Updated dependencies
├── .env                           # Environment variables (create this)
├── test_data/                     # Test data files
├── tests/                         # Test cases
├── utils/                         # Utility modules
├── reports/                       # Test reports
└── config/                        # Configuration files
```

## 🎯 Next Steps

1. **Activate Environment:** Use activation scripts or manual activation
2. **Run Tests:** Start with `pytest tests/test_login.py`
3. **Explore Data-Driven Testing:** Check `tests/test_data_driven.py`
4. **Configure Appium:** Set up Appium server and device connections
5. **Customize Configuration:** Edit `config/config.ini` for your needs

## 📞 Support

If you encounter issues:
1. Check this troubleshooting guide
2. Verify Python version and virtual environment activation
3. Ensure all dependencies are installed correctly
4. Check project documentation in `README.md`

Happy Testing! 🚀