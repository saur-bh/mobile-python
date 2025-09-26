"""
Setup script for Python Appium Mobile Automation Framework
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="python-appium-mobile-framework",
    version="1.0.0",
    author="Mobile Automation Team",
    author_email="automation@example.com",
    description="A minimal yet robust Python framework for mobile automation using Appium and pytest",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/python-appium-mobile-framework",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "pre-commit>=2.17.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mobile-test=utils.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "config": ["*.ini"],
        "reports": ["*.html", "*.css", "*.js"],
    },
    keywords="appium mobile automation testing pytest android ios",
    project_urls={
        "Bug Reports": "https://github.com/example/python-appium-mobile-framework/issues",
        "Source": "https://github.com/example/python-appium-mobile-framework",
        "Documentation": "https://python-appium-mobile-framework.readthedocs.io/",
    },
)