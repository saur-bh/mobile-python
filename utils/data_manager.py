"""
Data Manager Module

This module provides centralized test data management with support for multiple formats:
- JSON files for structured data
- YAML files for configuration and hierarchical data
- CSV files for tabular data

Features:
- Thread-safe data loading and caching
- Environment-specific data filtering
- Data validation and schema support
- Parameterized test data generation
- Performance optimized with caching
"""

import json
import csv
import yaml
import os
import threading
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import logging
from dataclasses import dataclass
from datetime import datetime

# Import configuration manager
from utils.config_manager import ConfigManager


@dataclass
class DataSource:
    """Data source configuration"""
    file_path: str
    format: str
    cache_enabled: bool = True
    last_modified: Optional[datetime] = None
    data: Optional[Any] = None


class DataValidationError(Exception):
    """Custom exception for data validation errors"""
    pass


class DataManager:
    """
    Centralized test data manager with support for multiple data formats
    
    Features:
    - Multi-format support (JSON, YAML, CSV)
    - Thread-safe operations
    - Data caching for performance
    - Environment-specific filtering
    - Data validation
    """
    
    def __init__(self, data_directory: str = None):
        """
        Initialize DataManager
        
        Args:
            data_directory: Path to test data directory
        """
        self.config = ConfigManager()
        self.logger = logging.getLogger(__name__)
        
        # Set data directory
        if data_directory:
            self.data_directory = Path(data_directory)
        else:
            # Default to test_data directory in project root
            project_root = Path(__file__).parent.parent
            self.data_directory = project_root / "test_data"
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Data cache
        self._cache: Dict[str, DataSource] = {}
        
        # Supported formats
        self._supported_formats = {
            '.json': self._load_json,
            '.yaml': self._load_yaml,
            '.yml': self._load_yaml,
            '.csv': self._load_csv
        }
        
        # Initialize data directory
        self._ensure_data_directory()
        
        self.logger.info(f"DataManager initialized with directory: {self.data_directory}")
    
    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        try:
            self.data_directory.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.logger.error(f"Failed to create data directory: {e}")
            raise
    
    def _get_file_path(self, filename: str) -> Path:
        """Get full file path"""
        return self.data_directory / filename
    
    def _get_file_format(self, file_path: Path) -> str:
        """Get file format from extension"""
        return file_path.suffix.lower()
    
    def _is_file_modified(self, file_path: Path, cached_time: Optional[datetime]) -> bool:
        """Check if file has been modified since last cache"""
        if not cached_time:
            return True
        
        try:
            file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            return file_mtime > cached_time
        except Exception:
            return True
    
    def _load_json(self, file_path: Path) -> Any:
        """Load JSON data"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            raise DataValidationError(f"Invalid JSON in {file_path}: {e}")
        except Exception as e:
            raise DataValidationError(f"Failed to load JSON {file_path}: {e}")
    
    def _load_yaml(self, file_path: Path) -> Any:
        """Load YAML data"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise DataValidationError(f"Invalid YAML in {file_path}: {e}")
        except Exception as e:
            raise DataValidationError(f"Failed to load YAML {file_path}: {e}")
    
    def _load_csv(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load CSV data as list of dictionaries"""
        try:
            data = []
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Convert numeric strings to appropriate types
                    converted_row = {}
                    for key, value in row.items():
                        converted_row[key] = self._convert_csv_value(value)
                    data.append(converted_row)
            return data
        except Exception as e:
            raise DataValidationError(f"Failed to load CSV {file_path}: {e}")
    
    def _convert_csv_value(self, value: str) -> Any:
        """Convert CSV string value to appropriate type"""
        if not value or value.strip() == '':
            return None
        
        value = value.strip()
        
        # Try boolean
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Try integer
        try:
            if '.' not in value:
                return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def load_data(self, filename: str, force_reload: bool = False) -> Any:
        """
        Load data from file with caching
        
        Args:
            filename: Name of the data file
            force_reload: Force reload even if cached
            
        Returns:
            Loaded data
            
        Raises:
            DataValidationError: If file format is not supported or data is invalid
            FileNotFoundError: If file doesn't exist
        """
        with self._lock:
            file_path = self._get_file_path(filename)
            
            if not file_path.exists():
                raise FileNotFoundError(f"Data file not found: {file_path}")
            
            file_format = self._get_file_format(file_path)
            
            if file_format not in self._supported_formats:
                raise DataValidationError(f"Unsupported file format: {file_format}")
            
            # Check cache
            cache_key = str(file_path)
            cached_source = self._cache.get(cache_key)
            
            if (not force_reload and 
                cached_source and 
                cached_source.cache_enabled and
                not self._is_file_modified(file_path, cached_source.last_modified)):
                
                self.logger.debug(f"Using cached data for {filename}")
                return cached_source.data
            
            # Load data
            self.logger.info(f"Loading data from {filename}")
            loader = self._supported_formats[file_format]
            data = loader(file_path)
            
            # Cache data
            self._cache[cache_key] = DataSource(
                file_path=str(file_path),
                format=file_format,
                cache_enabled=True,
                last_modified=datetime.fromtimestamp(file_path.stat().st_mtime),
                data=data
            )
            
            return data
    
    def get_user_data(self, user_type: str = "valid_users") -> List[Dict[str, Any]]:
        """
        Get user test data
        
        Args:
            user_type: Type of users to retrieve (valid_users, invalid_users)
            
        Returns:
            List of user data dictionaries
        """
        try:
            users_data = self.load_data("users.json")
            return users_data.get(user_type, [])
        except Exception as e:
            self.logger.error(f"Failed to get user data: {e}")
            return []
    
    def get_user_by_id(self, user_id: str, user_type: str = "valid_users") -> Optional[Dict[str, Any]]:
        """
        Get specific user by ID
        
        Args:
            user_id: User ID to find
            user_type: Type of users to search in
            
        Returns:
            User data dictionary or None if not found
        """
        users = self.get_user_data(user_type)
        for user in users:
            if user.get("id") == user_id:
                return user
        return None
    
    def get_app_config(self, platform: str = None) -> Dict[str, Any]:
        """
        Get application configuration data
        
        Args:
            platform: Platform to get config for (android/ios)
            
        Returns:
            Application configuration dictionary
        """
        try:
            app_data = self.load_data("app_data.yaml")
            
            if platform:
                platform = platform.lower()
                if platform in app_data.get("app_settings", {}):
                    return app_data["app_settings"][platform]
            
            return app_data
        except Exception as e:
            self.logger.error(f"Failed to get app config: {e}")
            return {}
    
    def get_device_data(self, platform: str = None, priority: str = None) -> List[Dict[str, Any]]:
        """
        Get device configuration data with filtering
        
        Args:
            platform: Filter by platform (iOS/Android)
            priority: Filter by test priority (high/medium/low)
            
        Returns:
            List of device configuration dictionaries
        """
        try:
            devices = self.load_data("devices.csv")
            
            # Apply filters
            if platform:
                devices = [d for d in devices if d.get("platform", "").lower() == platform.lower()]
            
            if priority:
                devices = [d for d in devices if d.get("test_priority", "").lower() == priority.lower()]
            
            return devices
        except Exception as e:
            self.logger.error(f"Failed to get device data: {e}")
            return []
    
    def get_test_scenario(self, scenario_name: str) -> Optional[Dict[str, Any]]:
        """
        Get specific test scenario data
        
        Args:
            scenario_name: Name of the scenario to retrieve
            
        Returns:
            Test scenario data or None if not found
        """
        try:
            app_data = self.load_data("app_data.yaml")
            scenarios = app_data.get("test_data", {}).get("test_scenarios", {})
            return scenarios.get(scenario_name)
        except Exception as e:
            self.logger.error(f"Failed to get test scenario: {e}")
            return None
    
    def get_environment_data(self, environment: str = None) -> Dict[str, Any]:
        """
        Get environment-specific data
        
        Args:
            environment: Environment name (staging/production/development)
            
        Returns:
            Environment configuration dictionary
        """
        try:
            users_data = self.load_data("users.json")
            env_data = users_data.get("environment_specific", {})
            
            if environment:
                return env_data.get(environment, {})
            
            # Return current environment data based on config
            current_env = self.config.get_environment()
            return env_data.get(current_env, env_data.get("development", {}))
        except Exception as e:
            self.logger.error(f"Failed to get environment data: {e}")
            return {}
    
    def get_localization_data(self, language_code: str = None) -> Dict[str, Any]:
        """
        Get localization data
        
        Args:
            language_code: Language code (en, es, fr, de)
            
        Returns:
            Localization data dictionary
        """
        try:
            app_data = self.load_data("app_data.yaml")
            languages = app_data.get("test_data", {}).get("localization", {}).get("languages", [])
            
            if language_code:
                for lang in languages:
                    if lang.get("code") == language_code:
                        return lang
            
            return {"languages": languages}
        except Exception as e:
            self.logger.error(f"Failed to get localization data: {e}")
            return {}
    
    def get_performance_benchmarks(self) -> Dict[str, Any]:
        """
        Get performance benchmark data
        
        Returns:
            Performance benchmarks dictionary
        """
        try:
            app_data = self.load_data("app_data.yaml")
            return app_data.get("performance_benchmarks", {})
        except Exception as e:
            self.logger.error(f"Failed to get performance benchmarks: {e}")
            return {}
    
    def get_error_messages(self, category: str = None) -> Dict[str, Any]:
        """
        Get error message data
        
        Args:
            category: Error category (validation, network, authentication)
            
        Returns:
            Error messages dictionary
        """
        try:
            app_data = self.load_data("app_data.yaml")
            error_messages = app_data.get("error_messages", {})
            
            if category:
                return error_messages.get(category, {})
            
            return error_messages
        except Exception as e:
            self.logger.error(f"Failed to get error messages: {e}")
            return {}
    
    def validate_data_structure(self, data: Any, expected_keys: List[str]) -> bool:
        """
        Validate data structure has expected keys
        
        Args:
            data: Data to validate
            expected_keys: List of expected keys
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(data, dict):
            return False
        
        for key in expected_keys:
            if key not in data:
                self.logger.warning(f"Missing expected key: {key}")
                return False
        
        return True
    
    def clear_cache(self, filename: str = None):
        """
        Clear data cache
        
        Args:
            filename: Specific file to clear from cache, or None to clear all
        """
        with self._lock:
            if filename:
                file_path = str(self._get_file_path(filename))
                if file_path in self._cache:
                    del self._cache[file_path]
                    self.logger.info(f"Cleared cache for {filename}")
            else:
                self._cache.clear()
                self.logger.info("Cleared all data cache")
    
    def list_data_files(self) -> List[str]:
        """
        List all available data files
        
        Returns:
            List of data file names
        """
        try:
            files = []
            for file_path in self.data_directory.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in self._supported_formats:
                    files.append(file_path.name)
            return sorted(files)
        except Exception as e:
            self.logger.error(f"Failed to list data files: {e}")
            return []
    
    def get_data_info(self) -> Dict[str, Any]:
        """
        Get information about loaded data
        
        Returns:
            Dictionary with data information
        """
        info = {
            "data_directory": str(self.data_directory),
            "supported_formats": list(self._supported_formats.keys()),
            "cached_files": len(self._cache),
            "available_files": self.list_data_files()
        }
        
        return info


# Singleton instance for global access
_data_manager_instance = None
_data_manager_lock = threading.Lock()


def get_data_manager() -> DataManager:
    """
    Get singleton DataManager instance
    
    Returns:
        DataManager instance
    """
    global _data_manager_instance
    
    if _data_manager_instance is None:
        with _data_manager_lock:
            if _data_manager_instance is None:
                _data_manager_instance = DataManager()
    
    return _data_manager_instance


# Convenience functions for common operations
def load_test_data(filename: str) -> Any:
    """Load test data from file"""
    return get_data_manager().load_data(filename)


def get_test_users(user_type: str = "valid_users") -> List[Dict[str, Any]]:
    """Get test user data"""
    return get_data_manager().get_user_data(user_type)


def get_test_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Get specific test user by ID"""
    return get_data_manager().get_user_by_id(user_id)


def get_device_configs(platform: str = None) -> List[Dict[str, Any]]:
    """Get device configuration data"""
    return get_data_manager().get_device_data(platform=platform)