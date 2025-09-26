"""
Soft Assertions Implementation for Mobile Automation Framework
Allows tests to continue execution even after assertion failures.
"""

import traceback
from typing import List, Dict, Any, Optional, Callable
from utils.logger import get_logger


class AssertionError(Exception):
    """Custom assertion error for soft assertions."""
    pass


class SoftAssertions:
    """Soft assertions implementation that collects failures without stopping test execution."""
    
    def __init__(self, test_name: str = ""):
        """Initialize soft assertions collector."""
        self.test_name = test_name
        self.logger = get_logger(f"SoftAssert.{test_name}" if test_name else "SoftAssert")
        self.failures: List[Dict[str, Any]] = []
        self.passed_assertions = 0
        self.failed_assertions = 0
    
    def assert_true(self, condition: bool, message: str = "") -> bool:
        """Assert that condition is True."""
        return self._assert(condition, message, f"Expected True, but got {condition}")
    
    def assert_false(self, condition: bool, message: str = "") -> bool:
        """Assert that condition is False."""
        return self._assert(not condition, message, f"Expected False, but got {condition}")
    
    def assert_equal(self, actual: Any, expected: Any, message: str = "") -> bool:
        """Assert that actual equals expected."""
        condition = actual == expected
        default_message = f"Expected '{expected}', but got '{actual}'"
        return self._assert(condition, message, default_message)
    
    def assert_not_equal(self, actual: Any, expected: Any, message: str = "") -> bool:
        """Assert that actual does not equal expected."""
        condition = actual != expected
        default_message = f"Expected '{actual}' to not equal '{expected}'"
        return self._assert(condition, message, default_message)
    
    def assert_greater(self, actual: Any, expected: Any, message: str = "") -> bool:
        """Assert that actual is greater than expected."""
        condition = actual > expected
        default_message = f"Expected '{actual}' to be greater than '{expected}'"
        return self._assert(condition, message, default_message)
    
    def assert_greater_equal(self, actual: Any, expected: Any, message: str = "") -> bool:
        """Assert that actual is greater than or equal to expected."""
        condition = actual >= expected
        default_message = f"Expected '{actual}' to be greater than or equal to '{expected}'"
        return self._assert(condition, message, default_message)
    
    def assert_less(self, actual: Any, expected: Any, message: str = "") -> bool:
        """Assert that actual is less than expected."""
        condition = actual < expected
        default_message = f"Expected '{actual}' to be less than '{expected}'"
        return self._assert(condition, message, default_message)
    
    def assert_less_equal(self, actual: Any, expected: Any, message: str = "") -> bool:
        """Assert that actual is less than or equal to expected."""
        condition = actual <= expected
        default_message = f"Expected '{actual}' to be less than or equal to '{expected}'"
        return self._assert(condition, message, default_message)
    
    def assert_in(self, item: Any, container: Any, message: str = "") -> bool:
        """Assert that item is in container."""
        condition = item in container
        default_message = f"Expected '{item}' to be in '{container}'"
        return self._assert(condition, message, default_message)
    
    def assert_not_in(self, item: Any, container: Any, message: str = "") -> bool:
        """Assert that item is not in container."""
        condition = item not in container
        default_message = f"Expected '{item}' to not be in '{container}'"
        return self._assert(condition, message, default_message)
    
    def assert_is_none(self, value: Any, message: str = "") -> bool:
        """Assert that value is None."""
        condition = value is None
        default_message = f"Expected None, but got '{value}'"
        return self._assert(condition, message, default_message)
    
    def assert_is_not_none(self, value: Any, message: str = "") -> bool:
        """Assert that value is not None."""
        condition = value is not None
        default_message = f"Expected value to not be None"
        return self._assert(condition, message, default_message)
    
    def assert_contains(self, text: str, substring: str, message: str = "") -> bool:
        """Assert that text contains substring."""
        condition = substring in text
        default_message = f"Expected '{text}' to contain '{substring}'"
        return self._assert(condition, message, default_message)
    
    def assert_not_contains(self, text: str, substring: str, message: str = "") -> bool:
        """Assert that text does not contain substring."""
        condition = substring not in text
        default_message = f"Expected '{text}' to not contain '{substring}'"
        return self._assert(condition, message, default_message)
    
    def assert_starts_with(self, text: str, prefix: str, message: str = "") -> bool:
        """Assert that text starts with prefix."""
        condition = text.startswith(prefix)
        default_message = f"Expected '{text}' to start with '{prefix}'"
        return self._assert(condition, message, default_message)
    
    def assert_ends_with(self, text: str, suffix: str, message: str = "") -> bool:
        """Assert that text ends with suffix."""
        condition = text.endswith(suffix)
        default_message = f"Expected '{text}' to end with '{suffix}'"
        return self._assert(condition, message, default_message)
    
    def assert_regex_match(self, text: str, pattern: str, message: str = "") -> bool:
        """Assert that text matches regex pattern."""
        import re
        condition = bool(re.search(pattern, text))
        default_message = f"Expected '{text}' to match pattern '{pattern}'"
        return self._assert(condition, message, default_message)
    
    def assert_length(self, container: Any, expected_length: int, message: str = "") -> bool:
        """Assert that container has expected length."""
        actual_length = len(container)
        condition = actual_length == expected_length
        default_message = f"Expected length {expected_length}, but got {actual_length}"
        return self._assert(condition, message, default_message)
    
    def assert_empty(self, container: Any, message: str = "") -> bool:
        """Assert that container is empty."""
        condition = len(container) == 0
        default_message = f"Expected empty container, but got length {len(container)}"
        return self._assert(condition, message, default_message)
    
    def assert_not_empty(self, container: Any, message: str = "") -> bool:
        """Assert that container is not empty."""
        condition = len(container) > 0
        default_message = f"Expected non-empty container, but got empty container"
        return self._assert(condition, message, default_message)
    
    def custom_assert(self, condition: bool, message: str) -> bool:
        """Custom assertion with user-defined condition and message."""
        return self._assert(condition, message, message)
    
    def _assert(self, condition: bool, user_message: str, default_message: str) -> bool:
        """Internal assertion method."""
        assertion_message = user_message if user_message else default_message
        
        if condition:
            self.passed_assertions += 1
            self.logger.debug(f"PASS: {assertion_message}")
            return True
        else:
            self.failed_assertions += 1
            
            # Capture stack trace
            stack_trace = traceback.format_stack()
            
            failure_info = {
                'message': assertion_message,
                'stack_trace': ''.join(stack_trace[:-1]),  # Exclude current frame
                'test_name': self.test_name
            }
            
            self.failures.append(failure_info)
            self.logger.error(f"FAIL: {assertion_message}")
            return False
    
    def has_failures(self) -> bool:
        """Check if there are any assertion failures."""
        return len(self.failures) > 0
    
    def get_failures(self) -> List[Dict[str, Any]]:
        """Get list of all assertion failures."""
        return self.failures.copy()
    
    def get_failure_count(self) -> int:
        """Get number of failed assertions."""
        return self.failed_assertions
    
    def get_passed_count(self) -> int:
        """Get number of passed assertions."""
        return self.passed_assertions
    
    def get_total_count(self) -> int:
        """Get total number of assertions."""
        return self.passed_assertions + self.failed_assertions
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all assertions."""
        return {
            'total_assertions': self.get_total_count(),
            'passed_assertions': self.passed_assertions,
            'failed_assertions': self.failed_assertions,
            'success_rate': (self.passed_assertions / max(1, self.get_total_count())) * 100,
            'has_failures': self.has_failures(),
            'failures': self.failures
        }
    
    def assert_all(self, raise_exception: bool = True) -> bool:
        """
        Verify all soft assertions and optionally raise exception if there are failures.
        
        Args:
            raise_exception: Whether to raise exception if there are failures
            
        Returns:
            bool: True if all assertions passed, False otherwise
            
        Raises:
            AssertionError: If there are failures and raise_exception is True
        """
        if self.has_failures():
            failure_messages = [f"- {failure['message']}" for failure in self.failures]
            summary_message = (
                f"Soft assertion failures in {self.test_name}:\n"
                f"Total assertions: {self.get_total_count()}\n"
                f"Passed: {self.passed_assertions}\n"
                f"Failed: {self.failed_assertions}\n"
                f"Failures:\n" + "\n".join(failure_messages)
            )
            
            self.logger.error(summary_message)
            
            if raise_exception:
                raise AssertionError(summary_message)
            
            return False
        
        self.logger.info(f"All {self.passed_assertions} soft assertions passed in {self.test_name}")
        return True
    
    def reset(self) -> None:
        """Reset all assertion counters and failures."""
        self.failures.clear()
        self.passed_assertions = 0
        self.failed_assertions = 0
        self.logger.debug("Soft assertions reset")
    
    def log_summary(self) -> None:
        """Log summary of all assertions."""
        summary = self.get_summary()
        
        self.logger.info("=" * 60)
        self.logger.info(f"SOFT ASSERTIONS SUMMARY - {self.test_name}")
        self.logger.info("=" * 60)
        self.logger.info(f"Total Assertions: {summary['total_assertions']}")
        self.logger.info(f"Passed: {summary['passed_assertions']}")
        self.logger.info(f"Failed: {summary['failed_assertions']}")
        self.logger.info(f"Success Rate: {summary['success_rate']:.1f}%")
        
        if summary['has_failures']:
            self.logger.info("\nFAILURES:")
            for i, failure in enumerate(summary['failures'], 1):
                self.logger.info(f"{i}. {failure['message']}")
        
        self.logger.info("=" * 60)


def create_soft_assertions(test_name: str = "") -> SoftAssertions:
    """Create a new soft assertions instance."""
    return SoftAssertions(test_name)