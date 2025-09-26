# Test Data Management

This directory contains all test data files and schemas for the mobile automation framework.

## Directory Structure

```
test_data/
├── __init__.py
├── users.json          # User test data (valid/invalid users, scenarios)
├── app_data.yaml       # Application configuration and test data
├── devices.csv         # Device configuration data
├── schemas/            # JSON schemas for data validation
│   ├── user.json       # User data validation schema
│   └── device.json     # Device data validation schema
└── README.md          # This file
```

## Data Files

### users.json
Contains user test data including:
- **valid_users**: Valid user credentials for successful login tests
- **invalid_users**: Invalid user credentials for negative testing
- **test_scenarios**: Login validation scenarios with expected results
- **environment_configs**: Environment-specific user configurations

### app_data.yaml
Contains application-specific test data:
- **app_settings**: Platform-specific app configurations
- **test_data**: Products, search terms, form data, navigation elements
- **ui_elements**: Timeouts, gesture settings, localization data
- **test_scenarios**: Complex test flows (checkout, registration)
- **performance_benchmarks**: Expected performance metrics
- **error_messages**: Expected error messages by category

### devices.csv
Contains device configuration data:
- Device specifications (name, platform, version, resolution)
- Hardware details (RAM, storage, network type)
- Test priority and configuration notes

## Data Validation

### Schemas
JSON schemas in the `schemas/` directory define the structure and validation rules for test data:

- **user.json**: Validates user data structure, required fields, and data types
- **device.json**: Validates device configuration data

### Validation Features
- **Type checking**: Ensures data types match expected formats
- **Required fields**: Validates presence of mandatory fields
- **Format validation**: Checks email, phone, and other format-specific fields
- **Enum validation**: Validates against predefined value sets

## Usage Examples

### Using DataManager
```python
from utils.data_manager import get_data_manager

# Get data manager instance
data_manager = get_data_manager()

# Load user data
valid_users = data_manager.get_user_data("valid_users")
admin_user = data_manager.get_user_by_id("user_002", "valid_users")

# Load device data
android_devices = data_manager.get_device_data(platform="Android")
high_priority_devices = data_manager.get_device_data(priority="high")

# Load app configuration
app_config = data_manager.get_app_config("iOS")
```

### Using Pytest Fixtures
```python
def test_login_with_valid_user(self, test_user):
    """Test using the test_user fixture"""
    # test_user fixture provides the first valid user
    assert test_user['username'] is not None

def test_login_with_multiple_users(self, test_users):
    """Test using the test_users fixture"""
    # test_users fixture provides all valid users
    for user in test_users:
        # Test logic for each user
        pass

def test_with_device_config(self, device_configs):
    """Test using device configuration"""
    # device_configs fixture provides platform-specific devices
    for device in device_configs:
        # Test logic for each device
        pass
```

### Data Validation
```python
from utils.data_validator import DataValidator

validator = DataValidator()

# Validate user data
user_data = {"username": "testuser", "password": "password123"}
result = validator.validate_user_data(user_data)

if result.is_valid:
    print("User data is valid")
else:
    print(f"Validation errors: {result.errors}")
```

## Environment-Specific Data

The framework supports environment-specific data filtering:

```python
# Get environment-specific data
staging_config = data_manager.get_environment_data("staging")
production_config = data_manager.get_environment_data("production")

# Environment-specific user data
staging_users = data_manager.get_user_data("valid_users", environment="staging")
```

## Adding New Test Data

### Adding User Data
1. Add new user entries to the appropriate section in `users.json`
2. Ensure the data follows the schema defined in `schemas/user.json`
3. Include all required fields: `id`, `username`, `password`
4. Add optional fields as needed: `first_name`, `last_name`, `role`, etc.

### Adding Device Data
1. Add new device entries to `devices.csv`
2. Include all required columns: `device_name`, `platform`, `platform_version`
3. Specify test priority and any relevant notes

### Adding App Data
1. Add new test data to the appropriate section in `app_data.yaml`
2. Follow the existing structure and naming conventions
3. Include platform-specific configurations when needed

## Data Caching

The DataManager implements caching to improve performance:
- Data files are loaded once and cached in memory
- Cache is thread-safe for parallel test execution
- Cache can be cleared using `data_manager.clear_cache()`

## Best Practices

1. **Data Separation**: Keep different types of data in separate files
2. **Schema Validation**: Always validate data against schemas before use
3. **Environment Isolation**: Use environment-specific data for different test environments
4. **Data Maintenance**: Regularly review and update test data
5. **Security**: Never include real credentials or sensitive data
6. **Documentation**: Document the purpose and structure of test data
7. **Versioning**: Consider versioning test data for different releases

## Troubleshooting

### Common Issues

1. **File Not Found**: Ensure data files are in the correct directory
2. **Validation Errors**: Check data against the corresponding schema
3. **Encoding Issues**: Ensure files are saved with UTF-8 encoding
4. **YAML Syntax**: Validate YAML syntax using online validators
5. **CSV Format**: Ensure CSV files have proper headers and formatting

### Debug Mode
Enable debug logging to troubleshoot data loading issues:
```python
import logging
logging.getLogger('data_manager').setLevel(logging.DEBUG)
```