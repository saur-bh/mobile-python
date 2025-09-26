"""
Login Test Cases - Example implementation demonstrating framework usage
Shows how to use page objects, soft assertions, fixtures, and logging.
"""

import pytest
from pages.login_page import LoginPage


class TestLogin:
    """Test class for login functionality."""
    
    def test_login_page_elements_visibility(self, driver, test_logger, soft_assert):
        """Test that all login page elements are visible."""
        test_logger.test_start("Verify login page elements visibility")
        
        # Create page object
        login_page = LoginPage(driver)
        
        test_logger.step("Navigate to login page and verify it's loaded")
        page_loaded = login_page.is_page_loaded()
        soft_assert.assert_true(page_loaded, "Login page should be loaded")
        
        if page_loaded:
            test_logger.step("Verify username field is visible")
            username_visible = login_page.is_element_visible(login_page.USERNAME_FIELD)
            soft_assert.assert_true(username_visible, "Username field should be visible")
            
            test_logger.step("Verify password field is visible")
            password_visible = login_page.is_element_visible(login_page.PASSWORD_FIELD)
            soft_assert.assert_true(password_visible, "Password field should be visible")
            
            test_logger.step("Verify login button is visible")
            login_button_visible = login_page.is_element_visible(login_page.LOGIN_BUTTON)
            soft_assert.assert_true(login_button_visible, "Login button should be visible")
            
            test_logger.step("Verify login button is enabled")
            login_button_enabled = login_page.is_login_button_enabled()
            soft_assert.assert_true(login_button_enabled, "Login button should be enabled")
        
        test_logger.test_end("COMPLETED")
    
    def test_valid_login(self, driver, test_logger, soft_assert, test_data):
        """Test login with valid credentials."""
        test_logger.test_start("Test login with valid credentials")
        
        # Create page object
        login_page = LoginPage(driver)
        
        test_logger.step("Verify login page is loaded")
        page_loaded = login_page.is_page_loaded()
        soft_assert.assert_true(page_loaded, "Login page should be loaded")
        
        if page_loaded:
            # Get valid credentials from test data
            credentials = test_data['valid_credentials']
            username = credentials['username']
            password = credentials['password']
            
            test_logger.step(f"Enter username: {username}")
            login_page.enter_username(username)
            
            # Verify username was entered
            entered_username = login_page.get_username_field_text()
            soft_assert.assert_equal(entered_username, username, "Username should be entered correctly")
            
            test_logger.step("Enter password")
            login_page.enter_password(password)
            
            test_logger.step("Click login button")
            login_page.click_login_button()
            
            test_logger.step("Wait for login process to complete")
            loading_completed = login_page.wait_for_loading_to_complete()
            soft_assert.assert_true(loading_completed, "Loading should complete")
            
            test_logger.step("Verify login success")
            login_successful = login_page.is_login_successful()
            soft_assert.assert_true(login_successful, "Login should be successful with valid credentials")
            
            if not login_successful:
                # Take screenshot on failure
                screenshot_path = login_page.take_login_page_screenshot("valid_login_failure.png")
                test_logger.screenshot(screenshot_path, "Login failure with valid credentials")
        
        test_logger.test_end("COMPLETED")
    
    def test_invalid_login(self, driver, test_logger, soft_assert, test_data):
        """Test login with invalid credentials."""
        test_logger.test_start("Test login with invalid credentials")
        
        # Create page object
        login_page = LoginPage(driver)
        
        test_logger.step("Verify login page is loaded")
        page_loaded = login_page.is_page_loaded()
        soft_assert.assert_true(page_loaded, "Login page should be loaded")
        
        if page_loaded:
            # Get invalid credentials from test data
            credentials = test_data['invalid_credentials']
            username = credentials['username']
            password = credentials['password']
            
            test_logger.step(f"Perform login with invalid credentials: {username}")
            login_page.login(username, password)
            
            test_logger.step("Wait for login process to complete")
            login_page.wait_for_loading_to_complete()
            
            test_logger.step("Verify error message is displayed")
            error_displayed = login_page.is_error_message_displayed()
            soft_assert.assert_true(error_displayed, "Error message should be displayed for invalid credentials")
            
            if error_displayed:
                error_message = login_page.get_error_message()
                test_logger.step(f"Error message: {error_message}")
                soft_assert.assert_not_empty(error_message, "Error message should not be empty")
                soft_assert.assert_contains(error_message.lower(), "invalid", "Error message should indicate invalid credentials")
            
            test_logger.step("Verify login was not successful")
            login_successful = login_page.is_login_successful()
            soft_assert.assert_false(login_successful, "Login should not be successful with invalid credentials")
        
        test_logger.test_end("COMPLETED")
    
    @pytest.mark.parametrize("username,password,expected_result", [
        ("", "", "empty_credentials"),
        ("valid@email.com", "", "empty_password"),
        ("", "password123", "empty_username"),
        ("invalid_email", "password123", "invalid_email_format"),
        ("test@email.com", "short", "short_password")
    ])
    def test_login_validation(self, driver, test_logger, soft_assert, username, password, expected_result):
        """Test login validation with various input combinations."""
        test_logger.test_start(f"Test login validation: {expected_result}")
        
        # Create page object
        login_page = LoginPage(driver)
        
        test_logger.step("Verify login page is loaded")
        page_loaded = login_page.is_page_loaded()
        soft_assert.assert_true(page_loaded, "Login page should be loaded")
        
        if page_loaded:
            test_logger.step(f"Clear existing field values")
            login_page.clear_username_field()
            login_page.clear_password_field()
            
            test_logger.step(f"Enter credentials - Username: '{username}', Password: '[HIDDEN]'")
            if username:
                login_page.enter_username(username)
            if password:
                login_page.enter_password(password)
            
            test_logger.step("Click login button")
            login_page.click_login_button()
            
            test_logger.step("Wait for response")
            login_page.wait_for_loading_to_complete()
            
            # Verify appropriate behavior based on expected result
            if expected_result in ["empty_credentials", "empty_password", "empty_username"]:
                test_logger.step("Verify validation for empty fields")
                # Should either show error or prevent login
                login_successful = login_page.is_login_successful()
                error_displayed = login_page.is_error_message_displayed()
                
                validation_working = not login_successful or error_displayed
                soft_assert.assert_true(validation_working, f"Validation should work for {expected_result}")
                
            elif expected_result in ["invalid_email_format", "short_password"]:
                test_logger.step("Verify validation for invalid format")
                error_displayed = login_page.is_error_message_displayed()
                soft_assert.assert_true(error_displayed, f"Error should be displayed for {expected_result}")
        
        test_logger.test_end("COMPLETED")
    
    @pytest.mark.smoke
    def test_login_page_load_performance(self, driver, test_logger, soft_assert):
        """Test login page load performance."""
        test_logger.test_start("Test login page load performance")
        
        import time
        
        start_time = time.time()
        
        # Create page object
        login_page = LoginPage(driver)
        
        test_logger.step("Measure page load time")
        page_loaded = login_page.is_page_loaded(timeout=15)
        
        load_time = time.time() - start_time
        test_logger.step(f"Page load time: {load_time:.2f} seconds")
        
        soft_assert.assert_true(page_loaded, "Login page should load successfully")
        soft_assert.assert_less(load_time, 10.0, "Page should load within 10 seconds")
        
        if load_time > 5.0:
            test_logger.warning(f"Page load time ({load_time:.2f}s) is slower than expected (5s)")
        
        test_logger.test_end("COMPLETED")
    
    @pytest.mark.android
    def test_android_specific_login(self, driver, test_logger, soft_assert):
        """Test Android-specific login functionality."""
        test_logger.test_start("Test Android-specific login functionality")
        
        # Verify we're running on Android
        platform = driver.capabilities.get('platformName', '').lower()
        if platform != 'android':
            pytest.skip("This test is for Android platform only")
        
        login_page = LoginPage(driver)
        
        test_logger.step("Test Android back button behavior")
        # Test back button functionality if applicable
        login_page.go_back()
        
        # Verify we can navigate back to login page
        page_loaded = login_page.is_page_loaded()
        soft_assert.assert_true(page_loaded, "Should be able to navigate back to login page")
        
        test_logger.test_end("COMPLETED")
    
    @pytest.mark.ios
    def test_ios_specific_login(self, driver, test_logger, soft_assert):
        """Test iOS-specific login functionality."""
        test_logger.test_start("Test iOS-specific login functionality")
        
        # Verify we're running on iOS
        platform = driver.capabilities.get('platformName', '').lower()
        if platform != 'ios':
            pytest.skip("This test is for iOS platform only")
        
        login_page = LoginPage(driver)
        
        test_logger.step("Verify iOS-specific elements")
        page_loaded = login_page.is_page_loaded()
        soft_assert.assert_true(page_loaded, "Login page should load on iOS")
        
        # Test iOS-specific functionality here
        test_logger.step("Test iOS keyboard handling")
        login_page.enter_username("test@example.com")
        login_page.hide_keyboard()
        
        test_logger.test_end("COMPLETED")
    
    def test_login_accessibility(self, driver, test_logger, soft_assert):
        """Test login page accessibility features."""
        test_logger.test_start("Test login page accessibility")
        
        login_page = LoginPage(driver)
        
        test_logger.step("Verify page is loaded")
        page_loaded = login_page.is_page_loaded()
        soft_assert.assert_true(page_loaded, "Login page should be loaded")
        
        if page_loaded:
            test_logger.step("Check accessibility attributes")
            
            # Check if elements have accessibility labels/descriptions
            username_element = login_page.find_element(login_page.USERNAME_FIELD)
            password_element = login_page.find_element(login_page.PASSWORD_FIELD)
            login_button_element = login_page.find_element(login_page.LOGIN_BUTTON)
            
            # Check for accessibility attributes (platform-specific)
            platform = driver.capabilities.get('platformName', '').lower()
            
            if platform == 'android':
                username_desc = username_element.get_attribute('content-desc')
                password_desc = password_element.get_attribute('content-desc')
                button_desc = login_button_element.get_attribute('content-desc')
            else:  # iOS
                username_desc = username_element.get_attribute('name')
                password_desc = password_element.get_attribute('name')
                button_desc = login_button_element.get_attribute('name')
            
            soft_assert.assert_is_not_none(username_desc, "Username field should have accessibility description")
            soft_assert.assert_is_not_none(password_desc, "Password field should have accessibility description")
            soft_assert.assert_is_not_none(button_desc, "Login button should have accessibility description")
        
        test_logger.test_end("COMPLETED")