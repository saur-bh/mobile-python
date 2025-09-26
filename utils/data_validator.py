"""
Data Validator Module

This module provides comprehensive data validation and schema support for test data.
It ensures data integrity, validates data structures, and provides schema-based validation.

Features:
- JSON Schema validation
- Custom validation rules
- Data type validation
- Required field validation
- Format validation (email, phone, URL, etc.)
- Range and length validation
- Cross-field validation
"""

import json
import re
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime
from pathlib import Path
import logging
from dataclasses import dataclass, field
from enum import Enum


class ValidationLevel(Enum):
    """Validation severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationResult:
    """Validation result container"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: List[str] = field(default_factory=list)
    
    def add_message(self, message: str, level: ValidationLevel):
        """Add validation message"""
        if level == ValidationLevel.ERROR:
            self.errors.append(message)
            self.is_valid = False
        elif level == ValidationLevel.WARNING:
            self.warnings.append(message)
        else:
            self.info.append(message)
    
    def get_all_messages(self) -> List[str]:
        """Get all validation messages"""
        messages = []
        messages.extend([f"ERROR: {msg}" for msg in self.errors])
        messages.extend([f"WARNING: {msg}" for msg in self.warnings])
        messages.extend([f"INFO: {msg}" for msg in self.info])
        return messages


class DataValidator:
    """
    Comprehensive data validator with schema support
    
    Features:
    - Schema-based validation
    - Built-in format validators
    - Custom validation rules
    - Nested object validation
    - Array validation
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Built-in format validators
        self._format_validators = {
            'email': self._validate_email,
            'phone': self._validate_phone,
            'url': self._validate_url,
            'date': self._validate_date,
            'datetime': self._validate_datetime,
            'uuid': self._validate_uuid,
            'password': self._validate_password,
            'username': self._validate_username
        }
        
        # Common regex patterns
        self._patterns = {
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'phone': r'^\+?[\d\s\-\(\)]{10,}$',
            'url': r'^https?://[^\s/$.?#].[^\s]*$',
            'uuid': r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            'username': r'^[a-zA-Z0-9._-]{3,30}$',
            'password': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        }
    
    def validate_data(self, data: Any, schema: Dict[str, Any]) -> ValidationResult:
        """
        Validate data against schema
        
        Args:
            data: Data to validate
            schema: Validation schema
            
        Returns:
            ValidationResult object
        """
        result = ValidationResult(is_valid=True)
        
        try:
            self._validate_object(data, schema, result, "root")
        except Exception as e:
            result.add_message(f"Validation error: {str(e)}", ValidationLevel.ERROR)
        
        return result
    
    def _validate_object(self, data: Any, schema: Dict[str, Any], result: ValidationResult, path: str):
        """Validate object against schema"""
        
        # Check type
        expected_type = schema.get('type')
        if expected_type and not self._check_type(data, expected_type):
            result.add_message(f"{path}: Expected type {expected_type}, got {type(data).__name__}", ValidationLevel.ERROR)
            return
        
        # Check required fields
        if isinstance(data, dict) and 'required' in schema:
            for field in schema['required']:
                if field not in data:
                    result.add_message(f"{path}: Missing required field '{field}'", ValidationLevel.ERROR)
        
        # Check properties
        if isinstance(data, dict) and 'properties' in schema:
            for field, field_schema in schema['properties'].items():
                field_path = f"{path}.{field}" if path != "root" else field
                
                if field in data:
                    self._validate_field(data[field], field_schema, result, field_path)
                elif field_schema.get('required', False):
                    result.add_message(f"{field_path}: Required field is missing", ValidationLevel.ERROR)
        
        # Check array items
        if isinstance(data, list) and 'items' in schema:
            for i, item in enumerate(data):
                item_path = f"{path}[{i}]"
                self._validate_object(item, schema['items'], result, item_path)
        
        # Check additional validations
        self._validate_constraints(data, schema, result, path)
    
    def _validate_field(self, value: Any, schema: Dict[str, Any], result: ValidationResult, path: str):
        """Validate individual field"""
        
        # Check if value is None and nullable
        if value is None:
            if not schema.get('nullable', False):
                result.add_message(f"{path}: Value cannot be null", ValidationLevel.ERROR)
            return
        
        # Check type
        expected_type = schema.get('type')
        if expected_type and not self._check_type(value, expected_type):
            result.add_message(f"{path}: Expected type {expected_type}, got {type(value).__name__}", ValidationLevel.ERROR)
            return
        
        # Check format
        format_name = schema.get('format')
        if format_name and format_name in self._format_validators:
            if not self._format_validators[format_name](value):
                result.add_message(f"{path}: Invalid {format_name} format", ValidationLevel.ERROR)
        
        # Check constraints
        self._validate_constraints(value, schema, result, path)
        
        # Recursive validation for objects and arrays
        if isinstance(value, dict) and 'properties' in schema:
            self._validate_object(value, schema, result, path)
        elif isinstance(value, list) and 'items' in schema:
            self._validate_object(value, schema, result, path)
    
    def _validate_constraints(self, value: Any, schema: Dict[str, Any], result: ValidationResult, path: str):
        """Validate value constraints"""
        
        # String constraints
        if isinstance(value, str):
            min_length = schema.get('minLength')
            max_length = schema.get('maxLength')
            pattern = schema.get('pattern')
            
            if min_length is not None and len(value) < min_length:
                result.add_message(f"{path}: String too short (min: {min_length})", ValidationLevel.ERROR)
            
            if max_length is not None and len(value) > max_length:
                result.add_message(f"{path}: String too long (max: {max_length})", ValidationLevel.ERROR)
            
            if pattern and not re.match(pattern, value):
                result.add_message(f"{path}: String doesn't match pattern", ValidationLevel.ERROR)
        
        # Numeric constraints
        if isinstance(value, (int, float)):
            minimum = schema.get('minimum')
            maximum = schema.get('maximum')
            
            if minimum is not None and value < minimum:
                result.add_message(f"{path}: Value too small (min: {minimum})", ValidationLevel.ERROR)
            
            if maximum is not None and value > maximum:
                result.add_message(f"{path}: Value too large (max: {maximum})", ValidationLevel.ERROR)
        
        # Array constraints
        if isinstance(value, list):
            min_items = schema.get('minItems')
            max_items = schema.get('maxItems')
            
            if min_items is not None and len(value) < min_items:
                result.add_message(f"{path}: Too few items (min: {min_items})", ValidationLevel.ERROR)
            
            if max_items is not None and len(value) > max_items:
                result.add_message(f"{path}: Too many items (max: {max_items})", ValidationLevel.ERROR)
        
        # Enum validation
        enum_values = schema.get('enum')
        if enum_values and value not in enum_values:
            result.add_message(f"{path}: Value must be one of {enum_values}", ValidationLevel.ERROR)
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type"""
        type_mapping = {
            'string': str,
            'integer': int,
            'number': (int, float),
            'boolean': bool,
            'array': list,
            'object': dict,
            'null': type(None)
        }
        
        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type:
            return isinstance(value, expected_python_type)
        
        return True
    
    def _validate_email(self, value: str) -> bool:
        """Validate email format"""
        if not isinstance(value, str):
            return False
        return bool(re.match(self._patterns['email'], value))
    
    def _validate_phone(self, value: str) -> bool:
        """Validate phone number format"""
        if not isinstance(value, str):
            return False
        return bool(re.match(self._patterns['phone'], value))
    
    def _validate_url(self, value: str) -> bool:
        """Validate URL format"""
        if not isinstance(value, str):
            return False
        return bool(re.match(self._patterns['url'], value))
    
    def _validate_date(self, value: str) -> bool:
        """Validate date format (YYYY-MM-DD)"""
        if not isinstance(value, str):
            return False
        try:
            datetime.strptime(value, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def _validate_datetime(self, value: str) -> bool:
        """Validate datetime format (ISO 8601)"""
        if not isinstance(value, str):
            return False
        try:
            datetime.fromisoformat(value.replace('Z', '+00:00'))
            return True
        except ValueError:
            return False
    
    def _validate_uuid(self, value: str) -> bool:
        """Validate UUID format"""
        if not isinstance(value, str):
            return False
        return bool(re.match(self._patterns['uuid'], value.lower()))
    
    def _validate_password(self, value: str) -> bool:
        """Validate password strength"""
        if not isinstance(value, str):
            return False
        return bool(re.match(self._patterns['password'], value))
    
    def _validate_username(self, value: str) -> bool:
        """Validate username format"""
        if not isinstance(value, str):
            return False
        return bool(re.match(self._patterns['username'], value))
    
    def add_custom_validator(self, format_name: str, validator_func: Callable[[Any], bool]):
        """
        Add custom format validator
        
        Args:
            format_name: Name of the format
            validator_func: Function that takes a value and returns bool
        """
        self._format_validators[format_name] = validator_func
        self.logger.info(f"Added custom validator: {format_name}")
    
    def validate_user_data(self, user_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate user data with predefined schema
        
        Args:
            user_data: User data to validate
            
        Returns:
            ValidationResult object
        """
        schema = {
            'type': 'object',
            'required': ['id', 'username', 'password'],
            'properties': {
                'id': {
                    'type': 'string',
                    'minLength': 1,
                    'maxLength': 50
                },
                'username': {
                    'type': 'string',
                    'format': 'email'
                },
                'password': {
                    'type': 'string',
                    'minLength': 8,
                    'format': 'password'
                },
                'first_name': {
                    'type': 'string',
                    'minLength': 1,
                    'maxLength': 50
                },
                'last_name': {
                    'type': 'string',
                    'minLength': 1,
                    'maxLength': 50
                },
                'phone': {
                    'type': 'string',
                    'format': 'phone'
                },
                'role': {
                    'type': 'string',
                    'enum': ['standard_user', 'admin_user', 'premium_user']
                },
                'status': {
                    'type': 'string',
                    'enum': ['active', 'inactive', 'blocked', 'expired']
                },
                'profile': {
                    'type': 'object',
                    'properties': {
                        'age': {
                            'type': 'integer',
                            'minimum': 13,
                            'maximum': 120
                        },
                        'country': {
                            'type': 'string',
                            'minLength': 2,
                            'maxLength': 2
                        },
                        'language': {
                            'type': 'string',
                            'minLength': 2,
                            'maxLength': 5
                        }
                    }
                }
            }
        }
        
        return self.validate_data(user_data, schema)
    
    def validate_device_data(self, device_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate device data with predefined schema
        
        Args:
            device_data: Device data to validate
            
        Returns:
            ValidationResult object
        """
        schema = {
            'type': 'object',
            'required': ['device_name', 'platform', 'platform_version'],
            'properties': {
                'device_name': {
                    'type': 'string',
                    'minLength': 1,
                    'maxLength': 100
                },
                'platform': {
                    'type': 'string',
                    'enum': ['iOS', 'Android']
                },
                'platform_version': {
                    'type': 'string',
                    'pattern': r'^\d+\.\d+(\.\d+)?$'
                },
                'screen_resolution': {
                    'type': 'string',
                    'pattern': r'^\d+x\d+$'
                },
                'screen_density': {
                    'type': 'integer',
                    'minimum': 100,
                    'maximum': 1000
                },
                'ram_gb': {
                    'type': 'integer',
                    'minimum': 1,
                    'maximum': 32
                },
                'storage_gb': {
                    'type': 'integer',
                    'minimum': 16,
                    'maximum': 1024
                },
                'test_priority': {
                    'type': 'string',
                    'enum': ['high', 'medium', 'low']
                }
            }
        }
        
        return self.validate_data(device_data, schema)
    
    def validate_test_scenario(self, scenario_data: List[Dict[str, Any]]) -> ValidationResult:
        """
        Validate test scenario data
        
        Args:
            scenario_data: Test scenario steps to validate
            
        Returns:
            ValidationResult object
        """
        schema = {
            'type': 'array',
            'minItems': 1,
            'items': {
                'type': 'object',
                'required': ['step'],
                'properties': {
                    'step': {
                        'type': 'string',
                        'minLength': 1,
                        'maxLength': 100
                    }
                }
            }
        }
        
        return self.validate_data(scenario_data, schema)


class SchemaManager:
    """
    Schema management for test data validation
    
    Features:
    - Load schemas from files
    - Cache schemas for performance
    - Schema versioning support
    """
    
    def __init__(self, schema_directory: str = None):
        """
        Initialize SchemaManager
        
        Args:
            schema_directory: Directory containing schema files
        """
        self.logger = logging.getLogger(__name__)
        
        if schema_directory:
            self.schema_directory = Path(schema_directory)
        else:
            # Default to schemas directory in test_data
            project_root = Path(__file__).parent.parent
            self.schema_directory = project_root / "test_data" / "schemas"
        
        self._schemas: Dict[str, Dict[str, Any]] = {}
        self.validator = DataValidator()
        
        # Ensure schema directory exists
        self.schema_directory.mkdir(parents=True, exist_ok=True)
    
    def load_schema(self, schema_name: str) -> Optional[Dict[str, Any]]:
        """
        Load schema from file
        
        Args:
            schema_name: Name of the schema file (without extension)
            
        Returns:
            Schema dictionary or None if not found
        """
        if schema_name in self._schemas:
            return self._schemas[schema_name]
        
        schema_file = self.schema_directory / f"{schema_name}.json"
        
        if not schema_file.exists():
            self.logger.warning(f"Schema file not found: {schema_file}")
            return None
        
        try:
            with open(schema_file, 'r', encoding='utf-8') as file:
                schema = json.load(file)
                self._schemas[schema_name] = schema
                self.logger.info(f"Loaded schema: {schema_name}")
                return schema
        except Exception as e:
            self.logger.error(f"Failed to load schema {schema_name}: {e}")
            return None
    
    def validate_with_schema(self, data: Any, schema_name: str) -> ValidationResult:
        """
        Validate data using named schema
        
        Args:
            data: Data to validate
            schema_name: Name of the schema to use
            
        Returns:
            ValidationResult object
        """
        schema = self.load_schema(schema_name)
        
        if not schema:
            result = ValidationResult(is_valid=False)
            result.add_message(f"Schema '{schema_name}' not found", ValidationLevel.ERROR)
            return result
        
        return self.validator.validate_data(data, schema)
    
    def create_default_schemas(self):
        """Create default schema files"""
        
        # User schema
        user_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "User Data Schema",
            "type": "object",
            "required": ["id", "username", "password"],
            "properties": {
                "id": {"type": "string", "minLength": 1},
                "username": {"type": "string", "format": "email"},
                "password": {"type": "string", "minLength": 8},
                "first_name": {"type": "string", "minLength": 1},
                "last_name": {"type": "string", "minLength": 1},
                "phone": {"type": "string", "format": "phone"},
                "role": {"type": "string", "enum": ["standard_user", "admin_user", "premium_user"]},
                "status": {"type": "string", "enum": ["active", "inactive", "blocked", "expired"]}
            }
        }
        
        # Device schema
        device_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Device Data Schema",
            "type": "object",
            "required": ["device_name", "platform", "platform_version"],
            "properties": {
                "device_name": {"type": "string", "minLength": 1},
                "platform": {"type": "string", "enum": ["iOS", "Android"]},
                "platform_version": {"type": "string", "pattern": "^\\d+\\.\\d+(\\.\\d+)?$"},
                "test_priority": {"type": "string", "enum": ["high", "medium", "low"]}
            }
        }
        
        # Save schemas
        schemas = {
            "user": user_schema,
            "device": device_schema
        }
        
        for name, schema in schemas.items():
            schema_file = self.schema_directory / f"{name}.json"
            try:
                with open(schema_file, 'w', encoding='utf-8') as file:
                    json.dump(schema, file, indent=2)
                self.logger.info(f"Created default schema: {name}")
            except Exception as e:
                self.logger.error(f"Failed to create schema {name}: {e}")


# Global validator instance
_validator_instance = None


def get_validator() -> DataValidator:
    """Get global DataValidator instance"""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = DataValidator()
    return _validator_instance


def validate_test_data(data: Any, schema: Dict[str, Any]) -> ValidationResult:
    """Convenience function to validate test data"""
    return get_validator().validate_data(data, schema)