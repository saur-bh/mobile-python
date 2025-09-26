"""
Appium Server Management Utilities
Provides functionality to start, stop, and manage Appium server instances.
"""

import os
import time
import signal
import subprocess
import threading
from typing import Optional, Dict, Any
import requests
from requests.exceptions import RequestException

from config.config_manager import config_manager
from utils.logger import get_logger


class AppiumServer:
    """Appium server management class with thread-safe operations."""
    
    def __init__(self):
        """Initialize Appium server manager."""
        self.logger = get_logger(self.__class__.__name__)
        self.server_config = config_manager.get_appium_server_config()
        self.process: Optional[subprocess.Popen] = None
        self.lock = threading.Lock()
        
        # Server configuration
        self.host = self.server_config['host']
        self.port = self.server_config['port']
        self.server_url = f"http://{self.host}:{self.port}"
        self.status_url = f"{self.server_url}/wd/hub/status"
    
    def is_server_running(self) -> bool:
        """Check if Appium server is running."""
        try:
            response = requests.get(self.status_url, timeout=5)
            if response.status_code == 200:
                self.logger.debug("Appium server is running")
                return True
        except RequestException:
            pass
        
        self.logger.debug("Appium server is not running")
        return False
    
    def start_server(self, 
                    log_file: Optional[str] = None,
                    additional_args: Optional[Dict[str, Any]] = None,
                    timeout: int = 30) -> bool:
        """
        Start Appium server with specified configuration.
        
        Args:
            log_file: Path to log file for server output
            additional_args: Additional arguments for Appium server
            timeout: Timeout in seconds to wait for server to start
            
        Returns:
            bool: True if server started successfully, False otherwise
        """
        with self.lock:
            if self.is_server_running():
                self.logger.info("Appium server is already running")
                return True
            
            try:
                # Build command arguments
                cmd = self._build_server_command(log_file, additional_args)
                
                self.logger.info(f"Starting Appium server: {' '.join(cmd)}")
                
                # Start server process
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                # Wait for server to start
                if self._wait_for_server_start(timeout):
                    self.logger.info(f"Appium server started successfully on {self.server_url}")
                    return True
                else:
                    self.logger.error("Appium server failed to start within timeout")
                    self.stop_server()
                    return False
                    
            except Exception as e:
                self.logger.error(f"Failed to start Appium server: {str(e)}")
                return False
    
    def stop_server(self) -> bool:
        """
        Stop Appium server.
        
        Returns:
            bool: True if server stopped successfully, False otherwise
        """
        with self.lock:
            try:
                if self.process:
                    self.logger.info("Stopping Appium server...")
                    
                    # Terminate process gracefully
                    self.process.terminate()
                    
                    # Wait for process to terminate
                    try:
                        self.process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        self.logger.warning("Server didn't terminate gracefully, forcing kill")
                        self.process.kill()
                        self.process.wait()
                    
                    self.process = None
                    self.logger.info("Appium server stopped successfully")
                    return True
                
                # Try to kill any running Appium processes
                self._kill_appium_processes()
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to stop Appium server: {str(e)}")
                return False
    
    def restart_server(self, 
                      log_file: Optional[str] = None,
                      additional_args: Optional[Dict[str, Any]] = None,
                      timeout: int = 30) -> bool:
        """
        Restart Appium server.
        
        Args:
            log_file: Path to log file for server output
            additional_args: Additional arguments for Appium server
            timeout: Timeout in seconds to wait for server to start
            
        Returns:
            bool: True if server restarted successfully, False otherwise
        """
        self.logger.info("Restarting Appium server...")
        
        if not self.stop_server():
            self.logger.error("Failed to stop server during restart")
            return False
        
        # Wait a moment before starting
        time.sleep(2)
        
        return self.start_server(log_file, additional_args, timeout)
    
    def get_server_logs(self) -> Optional[str]:
        """
        Get server logs if process is running.
        
        Returns:
            str: Server logs or None if not available
        """
        if self.process and self.process.stdout:
            try:
                # Read available output without blocking
                output = self.process.stdout.read()
                return output
            except Exception as e:
                self.logger.error(f"Failed to read server logs: {str(e)}")
        
        return None
    
    def _build_server_command(self, 
                             log_file: Optional[str] = None,
                             additional_args: Optional[Dict[str, Any]] = None) -> list:
        """Build Appium server command with arguments."""
        cmd = ['appium']
        
        # Basic server configuration
        cmd.extend(['--address', self.host])
        cmd.extend(['--port', str(self.port)])
        
        # Log configuration
        if log_file:
            cmd.extend(['--log', log_file])
        
        # Additional arguments
        if additional_args:
            for key, value in additional_args.items():
                if value is True:
                    cmd.append(f'--{key}')
                elif value is not False and value is not None:
                    cmd.extend([f'--{key}', str(value)])
        
        return cmd
    
    def _wait_for_server_start(self, timeout: int) -> bool:
        """Wait for server to start and become responsive."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.is_server_running():
                return True
            
            # Check if process is still running
            if self.process and self.process.poll() is not None:
                self.logger.error("Appium server process terminated unexpectedly")
                return False
            
            time.sleep(1)
        
        return False
    
    def _kill_appium_processes(self) -> None:
        """Kill any running Appium processes."""
        try:
            if os.name == 'nt':  # Windows
                subprocess.run(['taskkill', '/f', '/im', 'node.exe'], 
                             capture_output=True, check=False)
            else:  # Unix-like systems
                subprocess.run(['pkill', '-f', 'appium'], 
                             capture_output=True, check=False)
            
            self.logger.info("Killed existing Appium processes")
        except Exception as e:
            self.logger.warning(f"Failed to kill Appium processes: {str(e)}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure server is stopped."""
        self.stop_server()


class AppiumServerManager:
    """Singleton Appium server manager."""
    
    _instance: Optional[AppiumServer] = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls) -> AppiumServer:
        """Get singleton instance of Appium server."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = AppiumServer()
        return cls._instance
    
    @classmethod
    def start_server(cls, **kwargs) -> bool:
        """Start Appium server using singleton instance."""
        return cls.get_instance().start_server(**kwargs)
    
    @classmethod
    def stop_server(cls) -> bool:
        """Stop Appium server using singleton instance."""
        return cls.get_instance().stop_server()
    
    @classmethod
    def restart_server(cls, **kwargs) -> bool:
        """Restart Appium server using singleton instance."""
        return cls.get_instance().restart_server(**kwargs)
    
    @classmethod
    def is_server_running(cls) -> bool:
        """Check if server is running using singleton instance."""
        return cls.get_instance().is_server_running()


# Convenience functions
def start_appium_server(**kwargs) -> bool:
    """Start Appium server with optional arguments."""
    return AppiumServerManager.start_server(**kwargs)


def stop_appium_server() -> bool:
    """Stop Appium server."""
    return AppiumServerManager.stop_server()


def restart_appium_server(**kwargs) -> bool:
    """Restart Appium server with optional arguments."""
    return AppiumServerManager.restart_server(**kwargs)


def is_appium_server_running() -> bool:
    """Check if Appium server is running."""
    return AppiumServerManager.is_server_running()