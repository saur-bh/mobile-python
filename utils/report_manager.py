"""
Report Manager - Enhanced HTML reporting functionality
Provides utilities for customizing pytest-html reports with additional test information.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
import pytest
from py.xml import html


class ReportManager:
    """Manager class for handling test reporting functionality."""
    
    def __init__(self):
        self.test_results = []
        self.start_time = None
        self.end_time = None
        self.environment_info = {}
    
    def set_environment_info(self, info: Dict[str, Any]):
        """Set environment information for the report."""
        self.environment_info = info
    
    def add_test_result(self, test_name: str, status: str, duration: float, 
                       error_message: Optional[str] = None, screenshot_path: Optional[str] = None):
        """Add a test result to the report data."""
        result = {
            'test_name': test_name,
            'status': status,
            'duration': duration,
            'timestamp': datetime.now().isoformat(),
            'error_message': error_message,
            'screenshot_path': screenshot_path
        }
        self.test_results.append(result)
    
    def start_session(self):
        """Mark the start of test session."""
        self.start_time = time.time()
    
    def end_session(self):
        """Mark the end of test session."""
        self.end_time = time.time()
    
    def get_session_duration(self) -> float:
        """Get total session duration in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0
    
    def get_test_summary(self) -> Dict[str, int]:
        """Get summary of test results."""
        summary = {'passed': 0, 'failed': 0, 'skipped': 0, 'error': 0}
        for result in self.test_results:
            status = result['status'].lower()
            if status in summary:
                summary[status] += 1
        return summary
    
    def export_results_json(self, filepath: str):
        """Export test results to JSON file."""
        data = {
            'environment': self.environment_info,
            'session_duration': self.get_session_duration(),
            'summary': self.get_test_summary(),
            'test_results': self.test_results,
            'generated_at': datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


# Global report manager instance
report_manager = ReportManager()


def pytest_html_report_title(report):
    """Customize the HTML report title."""
    report.title = "Mobile Automation Test Report"


def pytest_html_results_table_header(cells):
    """Customize the results table header."""
    cells.insert(2, html.th('Time', class_='sortable time', col='time'))
    cells.insert(3, html.th('Platform', class_='sortable platform', col='platform'))
    cells.insert(4, html.th('Device', class_='sortable device', col='device'))
    cells.pop()  # Remove the default 'Links' column


def pytest_html_results_table_row(report, cells):
    """Customize the results table row."""
    # Add timestamp
    cells.insert(2, html.td(datetime.now().strftime('%H:%M:%S'), class_='col-time'))
    
    # Add platform info
    platform = getattr(report, 'platform', 'Unknown')
    cells.insert(3, html.td(platform, class_='col-platform'))
    
    # Add device info
    device = getattr(report, 'device', 'Unknown')
    cells.insert(4, html.td(device, class_='col-device'))
    
    # Remove the default 'Links' cell
    cells.pop()


def pytest_html_results_table_html(report, data):
    """Add custom HTML to the results table."""
    if report.passed:
        del data[:]
        data.append(html.div('✓ Passed', class_='passed'))
    elif report.failed:
        del data[:]
        data.append(html.div('✗ Failed', class_='failed'))
        
        # Add screenshot if available
        screenshot_path = getattr(report, 'screenshot_path', None)
        if screenshot_path and os.path.exists(screenshot_path):
            # Convert absolute path to relative for HTML report
            rel_path = os.path.relpath(screenshot_path, os.path.dirname(report.config.option.htmlpath))
            data.append(html.div([
                html.a('Screenshot', href=rel_path, target='_blank', class_='screenshot-link')
            ]))


def pytest_configure(config):
    """Configure pytest with custom metadata."""
    config._metadata = {
        'Framework': 'Python Appium Mobile Automation',
        'Python Version': f"{config.option.python_version if hasattr(config.option, 'python_version') else 'Unknown'}",
        'Platform': f"{config.option.platform if hasattr(config.option, 'platform') else 'All'}",
        'Device': f"{config.option.device_name if hasattr(config.option, 'device_name') else 'Default'}",
        'Test Environment': 'Automated Testing',
        'Generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


def pytest_sessionstart(session):
    """Called after the Session object has been created."""
    report_manager.start_session()
    
    # Set environment info
    env_info = {
        'python_version': session.config.option.python_version if hasattr(session.config.option, 'python_version') else 'Unknown',
        'platform': session.config.option.platform if hasattr(session.config.option, 'platform') else 'All',
        'device_name': session.config.option.device_name if hasattr(session.config.option, 'device_name') else 'Default',
        'appium_server': session.config.option.appium_server if hasattr(session.config.option, 'appium_server') else 'auto'
    }
    report_manager.set_environment_info(env_info)


def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished."""
    report_manager.end_session()
    
    # Export JSON report
    if hasattr(session.config.option, 'htmlpath') and session.config.option.htmlpath:
        json_path = session.config.option.htmlpath.replace('.html', '_results.json')
        report_manager.export_results_json(json_path)


def pytest_runtest_makereport(item, call):
    """Called to create a TestReport for each of the setup, call and teardown runtest phases."""
    outcome = yield
    report = outcome.get_result()
    
    # Add custom attributes to the report
    if hasattr(item.config.option, 'platform'):
        report.platform = item.config.option.platform
    if hasattr(item.config.option, 'device_name'):
        report.device = item.config.option.device_name
    
    # Add test result to report manager
    if call.when == 'call':
        status = 'passed' if report.passed else 'failed' if report.failed else 'skipped'
        error_message = str(report.longrepr) if report.failed else None
        
        # Look for screenshot in test extras
        screenshot_path = None
        if hasattr(report, 'extra') and report.extra:
            for extra in report.extra:
                if extra.get('name') == 'screenshot':
                    screenshot_path = extra.get('content')
                    break
        
        report_manager.add_test_result(
            test_name=item.nodeid,
            status=status,
            duration=report.duration,
            error_message=error_message,
            screenshot_path=screenshot_path
        )


def add_screenshot_to_report(driver, test_name: str = "screenshot"):
    """Utility function to add screenshot to pytest-html report."""
    try:
        screenshot_dir = "reports/screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(screenshot_dir, f"{test_name}_{timestamp}.png")
        
        driver.save_screenshot(screenshot_path)
        
        # Add to pytest-html extras
        pytest_html = pytest.current_request.config.pluginmanager.get_plugin('html')
        if pytest_html:
            extra = pytest_html.extras.png(screenshot_path)
            pytest_html.extras.append(extra)
        
        return screenshot_path
    except Exception as e:
        print(f"Failed to capture screenshot: {e}")
        return None


def add_text_to_report(text: str, name: str = "Additional Info"):
    """Utility function to add text information to pytest-html report."""
    try:
        pytest_html = pytest.current_request.config.pluginmanager.get_plugin('html')
        if pytest_html:
            extra = pytest_html.extras.text(text, name=name)
            pytest_html.extras.append(extra)
    except Exception as e:
        print(f"Failed to add text to report: {e}")


def add_html_to_report(html_content: str, name: str = "HTML Content"):
    """Utility function to add HTML content to pytest-html report."""
    try:
        pytest_html = pytest.current_request.config.pluginmanager.get_plugin('html')
        if pytest_html:
            extra = pytest_html.extras.html(html_content, name=name)
            pytest_html.extras.append(extra)
    except Exception as e:
        print(f"Failed to add HTML to report: {e}")


class TestReportHelper:
    """Helper class for adding information to test reports."""
    
    @staticmethod
    def log_test_step(step_description: str):
        """Log a test step to the report."""
        add_text_to_report(f"Step: {step_description}", "Test Step")
    
    @staticmethod
    def log_test_data(data: Dict[str, Any]):
        """Log test data to the report."""
        data_str = json.dumps(data, indent=2)
        add_text_to_report(data_str, "Test Data")
    
    @staticmethod
    def log_device_info(driver):
        """Log device information to the report."""
        try:
            capabilities = driver.capabilities
            device_info = {
                'Platform': capabilities.get('platformName', 'Unknown'),
                'Platform Version': capabilities.get('platformVersion', 'Unknown'),
                'Device Name': capabilities.get('deviceName', 'Unknown'),
                'App Package': capabilities.get('appPackage', 'N/A'),
                'App Activity': capabilities.get('appActivity', 'N/A'),
                'Bundle ID': capabilities.get('bundleId', 'N/A'),
                'Automation Name': capabilities.get('automationName', 'Unknown')
            }
            
            TestReportHelper.log_test_data(device_info)
        except Exception as e:
            add_text_to_report(f"Failed to get device info: {e}", "Device Info Error")
    
    @staticmethod
    def capture_failure_screenshot(driver, test_name: str):
        """Capture screenshot on test failure."""
        return add_screenshot_to_report(driver, f"failure_{test_name}")
    
    @staticmethod
    def add_performance_metrics(metrics: Dict[str, float]):
        """Add performance metrics to the report."""
        metrics_html = "<table class='performance-metrics'>"
        metrics_html += "<tr><th>Metric</th><th>Value</th></tr>"
        
        for metric, value in metrics.items():
            metrics_html += f"<tr><td>{metric}</td><td>{value:.2f}s</td></tr>"
        
        metrics_html += "</table>"
        add_html_to_report(metrics_html, "Performance Metrics")