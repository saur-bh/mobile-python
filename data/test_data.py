"""
Test Data
Centralized test data for mobile app testing
"""

# Scopex Mobile App Test Data
SCOPEX_TEST_DATA = {
    "app_name": "Scopex Mobile",
    "expected_texts": [
        "That's more money reaching your loved ones",
        "0% Fees on all transactions forever",
        "25 Paisa better than Google rates",
        "€10 on successful onboarding"
    ],
    "expected_elements": {
        "text_views": "android.widget.TextView",
        "buttons": "android.widget.Button",
        "edit_texts": "android.widget.EditText"
    },
    "test_scenarios": {
        "onboarding": {
            "name": "Onboarding Screen",
            "expected_elements": ["text_views", "buttons"],
            "verification_texts": [
                "That's more money reaching your loved ones",
                "0% Fees on all transactions forever",
                "25 Paisa better than Google rates",
                "€10 on successful onboarding"
            ]
        }
    }
}

# General Mobile App Test Data
GENERAL_TEST_DATA = {
    "common_elements": {
        "text_views": "android.widget.TextView",
        "buttons": "android.widget.Button",
        "edit_texts": "android.widget.EditText",
        "image_views": "android.widget.ImageView",
        "web_views": "android.webkit.WebView"
    },
    "validation_rules": {
        "min_elements_on_screen": 1,
        "max_wait_time": 30,
        "text_extraction_timeout": 10
    }
}

# Test Environment Data
ENVIRONMENT_DATA = {
    "development": {
        "appium_server": "http://127.0.0.1:4723",
        "device_name": "Android Emulator",
        "log_level": "DEBUG"
    },
    "staging": {
        "appium_server": "http://staging-appium:4723",
        "device_name": "Android Device",
        "log_level": "INFO"
    },
    "production": {
        "appium_server": "http://prod-appium:4723",
        "device_name": "Production Device",
        "log_level": "WARNING"
    }
}
