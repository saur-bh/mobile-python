#!/usr/bin/env python3
"""
Python Environment Setup Script for Mobile Automation Framework
================================================================

This script automates the setup of a Python virtual environment for the
mobile automation testing framework with Appium.

Features:
- Creates virtual environment
- Installs all required dependencies
- Validates installation
- Provides setup verification

Usage:
    python3 setup_env.py
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


class EnvironmentSetup:
    """Handles Python environment setup for mobile automation framework."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_name = "mobile_automation_env"
        self.venv_path = self.project_root / self.venv_name
        self.requirements_file = self.project_root / "requirements.txt"
        self.python_executable = sys.executable
        
    def print_header(self):
        """Print setup header."""
        print("=" * 60)
        print("🚀 Mobile Automation Framework - Environment Setup")
        print("=" * 60)
        print(f"Python Version: {platform.python_version()}")
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Project Root: {self.project_root}")
        print("-" * 60)
    
    def check_python_version(self):
        """Check if Python version is compatible."""
        print("🔍 Checking Python version...")
        
        version_info = sys.version_info
        if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 8):
            print("❌ Error: Python 3.8 or higher is required!")
            print(f"Current version: {platform.python_version()}")
            return False
        
        print(f"✅ Python {platform.python_version()} is compatible")
        return True
    
    def create_virtual_environment(self):
        """Create virtual environment."""
        print(f"🏗️  Creating virtual environment: {self.venv_name}")
        
        if self.venv_path.exists():
            print(f"⚠️  Virtual environment already exists at: {self.venv_path}")
            response = input("Do you want to recreate it? (y/N): ").lower().strip()
            if response == 'y':
                print("🗑️  Removing existing virtual environment...")
                self._run_command(f"rm -rf {self.venv_path}")
            else:
                print("📁 Using existing virtual environment")
                return True
        
        try:
            # Create virtual environment
            self._run_command(f"{self.python_executable} -m venv {self.venv_path}")
            print(f"✅ Virtual environment created successfully at: {self.venv_path}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    
    def get_venv_python(self):
        """Get the Python executable path in virtual environment."""
        if platform.system() == "Windows":
            return self.venv_path / "Scripts" / "python.exe"
        else:
            return self.venv_path / "bin" / "python"
    
    def get_venv_pip(self):
        """Get the pip executable path in virtual environment."""
        if platform.system() == "Windows":
            return self.venv_path / "Scripts" / "pip"
        else:
            return self.venv_path / "bin" / "pip"
    
    def upgrade_pip(self):
        """Upgrade pip in virtual environment."""
        print("📦 Upgrading pip...")
        
        try:
            pip_path = self.get_venv_pip()
            self._run_command(f"{pip_path} install --upgrade pip")
            print("✅ Pip upgraded successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Failed to upgrade pip: {e}")
            return False
    
    def install_dependencies(self):
        """Install project dependencies."""
        print("📚 Installing project dependencies...")
        
        if not self.requirements_file.exists():
            print(f"❌ Requirements file not found: {self.requirements_file}")
            return False
        
        try:
            pip_path = self.get_venv_pip()
            self._run_command(f"{pip_path} install -r {self.requirements_file}")
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def verify_installation(self):
        """Verify the installation by checking key packages."""
        print("🔍 Verifying installation...")
        
        key_packages = [
            "appium-python-client",
            "pytest",
            "selenium",
            "allure-pytest",
            "loguru",
            "pyyaml"
        ]
        
        python_path = self.get_venv_python()
        failed_packages = []
        
        for package in key_packages:
            try:
                result = subprocess.run(
                    [str(python_path), "-c", f"import {package.replace('-', '_')}"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"  ✅ {package}")
            except subprocess.CalledProcessError:
                print(f"  ❌ {package}")
                failed_packages.append(package)
        
        if failed_packages:
            print(f"⚠️  Some packages failed to import: {', '.join(failed_packages)}")
            return False
        
        print("✅ All key packages verified successfully")
        return True
    
    def create_activation_script(self):
        """Create activation script for easy environment activation."""
        print("📝 Creating activation script...")
        
        if platform.system() == "Windows":
            script_name = "activate_env.bat"
            script_content = f"""@echo off
echo Activating Mobile Automation Environment...
call "{self.venv_path}\\Scripts\\activate.bat"
echo Environment activated! You can now run tests.
echo.
echo Quick commands:
echo   pytest tests/                    - Run all tests
echo   pytest tests/test_login.py       - Run specific test
echo   pytest --html=reports/report.html - Generate HTML report
echo.
"""
        else:
            script_name = "activate_env.sh"
            script_content = f"""#!/bin/bash
echo "Activating Mobile Automation Environment..."
source "{self.venv_path}/bin/activate"
echo "Environment activated! You can now run tests."
echo ""
echo "Quick commands:"
echo "  pytest tests/                    - Run all tests"
echo "  pytest tests/test_login.py       - Run specific test"
echo "  pytest --html=reports/report.html - Generate HTML report"
echo ""
"""
        
        script_path = self.project_root / script_name
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        if platform.system() != "Windows":
            os.chmod(script_path, 0o755)
        
        print(f"✅ Activation script created: {script_name}")
        return script_path
    
    def print_success_message(self, activation_script):
        """Print success message with next steps."""
        print("\n" + "=" * 60)
        print("🎉 Environment Setup Complete!")
        print("=" * 60)
        
        if platform.system() == "Windows":
            activate_cmd = f".\\{activation_script.name}"
        else:
            activate_cmd = f"source {activation_script.name}"
        
        print(f"""
📋 Next Steps:
1. Activate the environment:
   {activate_cmd}

2. Or manually activate:
   {"source " + str(self.venv_path / "bin" / "activate") if platform.system() != "Windows" else str(self.venv_path / "Scripts" / "activate.bat")}

3. Run tests:
   pytest tests/

4. Generate reports:
   pytest --html=reports/report.html

📁 Project Structure:
   {self.venv_name}/          - Virtual environment
   test_data/                 - Test data files
   tests/                     - Test cases
   reports/                   - Test reports
   utils/                     - Utility modules

🔧 Configuration:
   Edit config/config.ini for environment settings
   
Happy Testing! 🚀
""")
    
    def _run_command(self, command):
        """Run shell command and handle errors."""
        print(f"  Running: {command}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result
    
    def setup(self):
        """Main setup process."""
        self.print_header()
        
        # Check Python version
        if not self.check_python_version():
            return False
        
        # Create virtual environment
        if not self.create_virtual_environment():
            return False
        
        # Upgrade pip
        self.upgrade_pip()
        
        # Install dependencies
        if not self.install_dependencies():
            return False
        
        # Verify installation
        if not self.verify_installation():
            print("⚠️  Installation verification failed, but environment is created")
        
        # Create activation script
        activation_script = self.create_activation_script()
        
        # Print success message
        self.print_success_message(activation_script)
        
        return True


def main():
    """Main function."""
    try:
        setup = EnvironmentSetup()
        success = setup.setup()
        
        if success:
            sys.exit(0)
        else:
            print("\n❌ Environment setup failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()