"""
Example test file demonstrating data-driven testing capabilities
using the test data management framework.
"""

import pytest
import time
from pages.login_page import LoginPage
from utils.soft_assert import SoftAssert


class TestDataDrivenLogin:
    """Test class demonstrating data-driven login testing"""
    
    def test_login_with_valid_users(self, driver, test_users, soft_assert, test_logger):
        """Test login with all valid users from test data"""
        test_logger.test_start("Testing login with multiple valid users")
        login_page = LoginPage(driver)
        
        for user in test_users:
            test_logger.step(f"Testing login for user: {user['username']}")
            
            # Navigate to login page
            login_page.navigate_to_login()
            
            # Perform login
            login_page.login(user['username'], user['password'])
            
            # Verify login success
            soft_assert.assert_true(
                login_page.is_login_successful(),
                f"Login should be successful for user: {user['username']}"
            )
            
            # Logout for next iteration
            if login_page.is_login_successful():
                login_page.logout()
        
        soft_assert.assert_all()
        test_logger.test_end("COMPLETED")
    
    def test_login_with_invalid_users(self, driver, invalid_users, soft_assert, test_logger):
        """Test login with invalid users and verify error messages"""
        test_logger.test_start("Testing login with invalid users")
        login_page = LoginPage(driver)
        
        for user in invalid_users:
            test_logger.step(f"Testing invalid login for: {user['username']}")
            
            # Navigate to login page
            login_page.navigate_to_login()
            
            # Attempt login with invalid credentials
            login_page.login(user['username'], user['password'])
            
            # Verify login failure
            soft_assert.assert_true(
                login_page.is_error_displayed(),
                f"Error should be displayed for invalid user: {user['username']}"
            )
            
            # Verify specific error message if provided
            if 'expected_error' in user:
                actual_error = login_page.get_error_message()
                soft_assert.assert_equal(
                    actual_error, 
                    user['expected_error'],
                    f"Expected specific error message for user: {user['username']}"
                )
        
        soft_assert.assert_all()
        test_logger.test_end("COMPLETED")
    
    def test_login_scenarios(self, driver, login_scenarios, test_logger):
        """Test login using predefined scenarios"""
        test_logger.test_start("Testing login scenarios")
        login_page = LoginPage(driver)
        
        for scenario in login_scenarios:
            test_logger.step(f"Testing scenario: {scenario['description']}")
            
            # Navigate to login page
            login_page.navigate_to_login()
            
            # Perform login
            login_page.login(scenario['username'], scenario['password'])
            
            # Verify expected outcome
            if scenario['should_succeed']:
                assert login_page.is_login_successful(), f"Login should succeed: {scenario['description']}"
                login_page.logout()  # Logout for next scenario
            else:
                assert login_page.is_error_displayed(), f"Login should fail: {scenario['description']}"
        
        test_logger.test_end("COMPLETED")
    
    @pytest.mark.parametrize("user_id", ["user_001", "user_002", "user_003"])
    def test_parametrized_login(self, driver, data_manager, user_id, test_logger):
        """Test login using parametrized user IDs"""
        test_logger.test_start(f"Testing parametrized login for {user_id}")
        
        # Get user data by ID
        user = data_manager.get_user_by_id(user_id, "valid_users")
        assert user is not None, f"User {user_id} not found in test data"
        
        login_page = LoginPage(driver)
        
        # Navigate and login
        login_page.navigate_to_login()
        login_page.login(user['username'], user['password'])
        
        # Verify login success
        assert login_page.is_login_successful(), f"Login failed for user: {user_id}"
        
        test_logger.test_end("COMPLETED")


class TestDataDrivenDeviceConfiguration:
    """Test class demonstrating device configuration testing"""
    
    def test_device_compatibility(self, device_configs, test_logger):
        """Test app compatibility across different devices"""
        test_logger.test_start("Testing device compatibility")
        
        for device in device_configs:
            test_logger.step(f"Testing device: {device['device_name']}")
            
            # Verify device configuration
            assert device['platform'] in ['Android', 'iOS'], f"Invalid platform: {device['platform']}"
            assert device['platform_version'] is not None, f"Platform version missing for {device['device_name']}"
            
            # Log device information
            test_logger.info(f"Device: {device['device_name']}, Platform: {device['platform']} {device['platform_version']}")
        
        test_logger.test_end("COMPLETED")
    
    def test_high_priority_devices(self, high_priority_devices, test_logger):
        """Test with high priority devices only"""
        test_logger.test_start("Testing high priority devices")
        
        assert len(high_priority_devices) > 0, "No high priority devices found"
        
        for device in high_priority_devices:
            test_logger.step(f"Testing high priority device: {device['device_name']}")
            
            # Verify it's actually high priority
            assert device['test_priority'] == 'high', f"Device {device['device_name']} is not high priority"
            
            # Additional high priority device tests
            test_logger.info(f"High priority device validated: {device['device_name']}")
        
        test_logger.test_end("COMPLETED")


class TestDataDrivenAppConfiguration:
    """Test class demonstrating app configuration testing"""
    
    @pytest.mark.android
    def test_android_app_config(self, app_config, test_logger):
        """Test Android-specific app configuration"""
        test_logger.test_start("Testing Android app configuration")
        
        android_config = app_config.get('android', {})
        assert android_config, "Android configuration not found"
        
        # Verify required Android settings
        assert 'app_package' in android_config, "Android app package not configured"
        assert 'app_activity' in android_config, "Android app activity not configured"
        
        test_logger.info(f"Android package: {android_config['app_package']}")
        test_logger.info(f"Android activity: {android_config['app_activity']}")
        
        test_logger.test_end("COMPLETED")
    
    @pytest.mark.ios
    def test_ios_app_config(self, app_config, test_logger):
        """Test iOS-specific app configuration"""
        test_logger.test_start("Testing iOS app configuration")
        
        ios_config = app_config.get('ios', {})
        assert ios_config, "iOS configuration not found"
        
        # Verify required iOS settings
        assert 'bundle_id' in ios_config, "iOS bundle ID not configured"
        
        test_logger.info(f"iOS bundle ID: {ios_config['bundle_id']}")
        
        test_logger.test_end("COMPLETED")


class TestDataDrivenPerformance:
    """Test class demonstrating performance testing with data"""
    
    def test_login_performance(self, driver, test_user, performance_benchmarks, test_logger):
        """Test login performance against benchmarks"""
        test_logger.test_start("Testing login performance")
        
        # Get performance benchmark
        login_benchmark = performance_benchmarks.get('page_load_times', {}).get('login_page', 5.0)
        test_logger.info(f"Login benchmark: {login_benchmark}s")
        
        login_page = LoginPage(driver)
        
        # Measure login performance
        start_time = time.time()
        
        login_page.navigate_to_login()
        login_page.login(test_user['username'], test_user['password'])
        
        end_time = time.time()
        login_duration = end_time - start_time
        
        test_logger.info(f"Actual login duration: {login_duration:.2f}s")
        
        # Verify performance
        assert login_duration <= login_benchmark, f"Login took {login_duration:.2f}s, expected <= {login_benchmark}s"
        
        test_logger.test_end("COMPLETED")
    
    def test_api_response_performance(self, performance_benchmarks, test_logger):
        """Test API response time against benchmarks"""
        test_logger.test_start("Testing API performance")
        
        api_benchmarks = performance_benchmarks.get('api_response_times', {})
        
        for endpoint, expected_time in api_benchmarks.items():
            test_logger.step(f"Testing {endpoint} API performance")
            
            # Simulate API call timing (replace with actual API calls)
            start_time = time.time()
            time.sleep(0.1)  # Simulate API call
            end_time = time.time()
            
            actual_time = end_time - start_time
            test_logger.info(f"{endpoint} response time: {actual_time:.2f}s (expected <= {expected_time}s)")
            
            assert actual_time <= expected_time, f"{endpoint} API too slow: {actual_time:.2f}s > {expected_time}s"
        
        test_logger.test_end("COMPLETED")


class TestDataValidation:
    """Test class demonstrating data validation"""
    
    def test_validated_user_data(self, validated_user_data, test_logger):
        """Test with pre-validated user data"""
        test_logger.test_start("Testing with validated user data")
        
        # Data is already validated by the fixture
        assert validated_user_data['username'] is not None
        assert validated_user_data['password'] is not None
        
        test_logger.info(f"Using validated user: {validated_user_data['username']}")
        test_logger.test_end("COMPLETED")
    
    def test_validated_device_config(self, validated_device_config, test_logger):
        """Test with pre-validated device configuration"""
        test_logger.test_start("Testing with validated device configuration")
        
        # All devices are pre-validated by the fixture
        for device in validated_device_config:
            assert device['device_name'] is not None
            assert device['platform'] in ['Android', 'iOS']
            assert device['platform_version'] is not None
            
            test_logger.info(f"Using validated device: {device['device_name']}")
        
        test_logger.test_end("COMPLETED")
    
    def test_data_validation_errors(self, data_validator, test_logger):
        """Test data validation with invalid data"""
        test_logger.test_start("Testing data validation errors")
        
        # Test with invalid user data
        invalid_user = {
            "username": "",  # Invalid: empty username
            "password": "123"  # Invalid: too short
        }
        
        result = data_validator.validate_user_data(invalid_user)
        
        assert not result.is_valid, "Validation should fail for invalid user data"
        assert len(result.errors) > 0, "Should have validation errors"
        
        test_logger.info(f"Validation errors (expected): {result.errors}")
        test_logger.test_end("COMPLETED")


class TestCrossPlatformData:
    """Test class demonstrating cross-platform testing with data"""
    
    def test_cross_platform_compatibility(self, platform_config, test_user, test_logger):
        """Test app compatibility across platforms"""
        test_logger.test_start(f"Testing {platform_config['platform']} compatibility")
        
        platform = platform_config['platform']
        devices = platform_config['devices']
        
        test_logger.info(f"Testing on {platform} with {len(devices)} devices")
        
        # Platform-specific test logic
        if platform == "iOS":
            # iOS-specific validations
            for device in devices:
                assert device['platform'] == 'iOS', f"Expected iOS device, got {device['platform']}"
                test_logger.step(f"iOS device validated: {device['device_name']}")
        
        elif platform == "Android":
            # Android-specific validations
            for device in devices:
                assert device['platform'] == 'Android', f"Expected Android device, got {device['platform']}"
                test_logger.step(f"Android device validated: {device['device_name']}")
        
        test_logger.test_end("COMPLETED")
    
    def test_orientation_support(self, orientation_config, test_user, test_logger):
        """Test app orientation support"""
        test_logger.test_start(f"Testing {orientation_config} orientation")
        
        # Orientation-specific test logic
        assert orientation_config in ['portrait', 'landscape'], f"Invalid orientation: {orientation_config}"
        
        test_logger.info(f"Testing in {orientation_config} mode")
        # Add actual orientation testing logic here
        
        test_logger.test_end("COMPLETED")