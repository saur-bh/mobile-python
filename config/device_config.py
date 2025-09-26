"""
Device Configuration
Centralized device and app configuration
"""

# Device Configuration
DEVICE_CONFIG = {
    "platform_name": "Android",
    "device_name": "Android",
    "automation_name": "uiautomator2",
    "appium_server_url": "http://127.0.0.1:4723"
}

# App Configuration
APP_CONFIG = {
    "package_name": "com.scopex.scopexmobile",
    "activity_name": ".MainActivity",
    "app_path": None,  # Set if using APK file
    "auto_grant_permissions": True,
    "ensure_webviews_have_pages": True,
    "native_web_screenshot": True,
    "new_command_timeout": 3600,
    "connect_hardware_keyboard": True
}

# Wait Configuration
WAIT_CONFIG = {
    "implicit_wait": 10,
    "explicit_wait": 30,
    "page_load_timeout": 30,
    "script_timeout": 30
}

# Test Configuration
TEST_CONFIG = {
    "screenshot_on_failure": True,
    "video_recording": False,
    "log_level": "INFO"
}
