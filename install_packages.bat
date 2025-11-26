@echo off
title Installing Packages - Sales Forecasting App
color 0B
echo.
echo ========================================
echo   Package Installation Helper
echo ========================================
echo.
echo This script will install packages with better error handling.
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11 or 3.12 from https://www.python.org/
    pause
    exit /b 1
)

echo Step 1: Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo WARNING: Failed to upgrade pip, continuing anyway...
)

echo.
echo Step 2: Installing pyarrow (this may take a while)...
echo Trying to install pre-built wheel first...
python -m pip install --only-binary :all: pyarrow
if errorlevel 1 (
    echo Pre-built wheel not available, trying alternative...
    python -m pip install pyarrow --no-build-isolation
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install pyarrow
        echo.
        echo SOLUTION: Please install Python 3.11 or 3.12 instead of Python 3.14
        echo Python 3.11/3.12 have pre-built wheels available.
        echo.
        pause
        exit /b 1
    )
)

echo.
echo Step 3: Installing other required packages...
python -m pip install streamlit pandas numpy prophet plotly openpyxl xlrd
if errorlevel 1 (
    echo ERROR: Failed to install some packages
    pause
    exit /b 1
)

echo.
echo Step 4: Installing from requirements.txt...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo WARNING: Some packages from requirements.txt failed, but core packages are installed
)

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo You can now run the application using launch_app_auto.bat
echo.
pause

