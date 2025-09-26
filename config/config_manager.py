"""
Configuration Manager for Mobile Automation Framework
Handles reading and parsing of configuration files with thread-safe implementation.
"""

import configparser
import os
import threading
from typing import Dict, Any, Optional


class ConfigManager:
    """Thread-safe configuration manager for handling application settings."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern implementation with thread safety."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ConfigManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize configuration manager."""
        if not self._initialized:
            self.config = configparser.ConfigParser()
            self.config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
            self._load_config()
            self._initialized = True
    
    def _load_config(self) -> None:
        """Load configuration from config.ini file."""
        try:
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
            self.config.read(self.config_path)
        except Exception as e:
            raise Exception(f"Failed to load configuration: {str(e)}")
    
    def get_android_capabilities(self) -> Dict[str, Any]:
        """Get Android device capabilities from configuration."""
        capabilities = {}
        android_section = self.config['ANDROID']
        
        capabilities.update({
            'platformName': android_section.get('platform_name'),
            'platformVersion': android_section.get('platform_version'),
            'deviceName': android_section.get('device_name'),
            'automationName': android_section.get('automation_name'),
            'appPackage': android_section.get('app_package'),
            'appActivity': android_section.get('app_activity'),
            'noReset': android_section.getboolean('no_reset'),
            'fullReset': android_section.getboolean('full_reset'),
            'newCommandTimeout': android_section.getint('new_command_timeout'),
            'autoGrantPermissions': android_section.getboolean('auto_grant_permissions'),
            'autoAcceptAlerts': android_section.getboolean('auto_accept_alerts')
        })
        
        return capabilities
    
    def get_ios_capabilities(self) -> Dict[str, Any]:
        """Get iOS device capabilities from configuration."""
        capabilities = {}
        ios_section = self.config['IOS']
        
        capabilities.update({
            'platformName': ios_section.get('platform_name'),
            'platformVersion': ios_section.get('platform_version'),
            'deviceName': ios_section.get('device_name'),
            'automationName': ios_section.get('automation_name'),
            'bundleId': ios_section.get('bundle_id'),
            'noReset': ios_section.getboolean('no_reset'),
            'fullReset': ios_section.getboolean('full_reset'),
            'newCommandTimeout': ios_section.getint('new_command_timeout'),
            'autoAcceptAlerts': ios_section.getboolean('auto_accept_alerts'),
            'wdaLocalPort': ios_section.getint('wda_local_port')
        })
        
        return capabilities
    
    def get_appium_server_config(self) -> Dict[str, Any]:
        """Get Appium server configuration."""
        default_section = self.config['DEFAULT']
        
        return {
            'host': default_section.get('appium_host'),
            'port': default_section.getint('appium_port'),
            'command_timeout': default_section.getint('command_timeout')
        }
    
    def get_timeout_config(self) -> Dict[str, int]:
        """Get timeout configuration."""
        default_section = self.config['DEFAULT']
        
        return {
            'implicit_wait': default_section.getint('implicit_wait'),
            'explicit_wait': default_section.getint('explicit_wait'),
            'page_load_timeout': default_section.getint('page_load_timeout')
        }
    
    def get_logging_config(self) -> Dict[str, str]:
        """Get logging configuration."""
        default_section = self.config['DEFAULT']
        
        return {
            'log_level': default_section.get('log_level'),
            'log_file': default_section.get('log_file')
        }
    
    def get_environment_config(self) -> Dict[str, Any]:
        """Get environment specific configuration."""
        env_section = self.config['ENVIRONMENT']
        
        return {
            'test_environment': env_section.get('test_environment'),
            'base_url': env_section.get('base_url'),
            'api_timeout': env_section.getint('api_timeout'),
            'screenshot_on_failure': env_section.getboolean('screenshot_on_failure'),
            'video_recording': env_section.getboolean('video_recording'),
            'parallel_execution': env_section.getboolean('parallel_execution'),
            'max_workers': env_section.getint('max_workers')
        }
    
    def get_config_value(self, section: str, key: str, fallback: Optional[str] = None) -> str:
        """Get a specific configuration value."""
        try:
            return self.config.get(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            if fallback is not None:
                return fallback
            raise
    
    def reload_config(self) -> None:
        """Reload configuration from file."""
        with self._lock:
            self._load_config()


# Global configuration instance
config_manager = ConfigManager()