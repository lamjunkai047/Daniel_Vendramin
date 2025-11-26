@echo off
title Sales Forecasting Application
echo ========================================
echo   Sales Forecasting with Prophet
echo ========================================
echo.
echo Starting application...
echo Please wait, this may take a moment...
echo.
echo The application will open in your browser automatically.
echo.
echo To close the application, close this window or press Ctrl+C
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

REM Check if required packages are installed
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    echo This may take a few minutes on first run...
    python -m pip install --quiet --upgrade pip
    python -m pip install --quiet -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install required packages
        pause
        exit /b 1
    )
)

REM Set environment variable to skip email prompt
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

REM Create credentials file to skip email prompt (always overwrite)
if not exist "%USERPROFILE%\.streamlit" mkdir "%USERPROFILE%\.streamlit"
(
echo # Streamlit credentials
echo email = ""
) > "%USERPROFILE%\.streamlit\credentials.toml"

REM Create config file
(
echo [browser]
echo gatherUsageStats = false
echo.
echo [server]
echo headless = false
echo runOnSave = true
echo port = 8501
) > "%USERPROFILE%\.streamlit\config.toml"

REM Run the application (headless=false so browser opens automatically)
python -m streamlit run app.py --server.headless false --browser.gatherUsageStats false --server.port 8501

pause

