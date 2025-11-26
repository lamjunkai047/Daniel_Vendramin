@echo off
title Sales Forecasting Application
color 0A
echo.
echo ========================================
echo   Sales Forecasting with Prophet
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Setting up Streamlit configuration...
REM Create .streamlit directory in user profile
if not exist "%USERPROFILE%\.streamlit" mkdir "%USERPROFILE%\.streamlit"

REM Create credentials file (overwrite to ensure it's correct)
(
echo email = ""
) > "%USERPROFILE%\.streamlit\credentials.toml"

REM Create config file
(
echo [browser]
echo gatherUsageStats = false
echo.
echo [server]
echo headless = false
echo port = 8501
) > "%USERPROFILE%\.streamlit\config.toml"

echo [2/4] Checking packages...
python -c "import streamlit, pandas, prophet" >nul 2>&1
if errorlevel 1 (
    echo [3/4] Installing required packages...
    echo This may take 5-10 minutes on first run...
    python -m pip install --quiet --upgrade pip
    python -m pip install --quiet --upgrade setuptools wheel
    echo Installing pyarrow with pre-built wheels...
    python -m pip install --quiet --only-binary :all: pyarrow || python -m pip install --quiet pyarrow
    echo Installing other packages...
    python -m pip install --quiet -r requirements.txt
    if errorlevel 1 (
        echo.
        echo WARNING: Some packages failed to install.
        echo Trying alternative installation method...
        python -m pip install --quiet streamlit pandas numpy prophet plotly openpyxl xlrd
        python -m pip install --quiet --only-binary :all: pyarrow 2>nul || echo PyArrow will use source build if needed
        python -m pip install --quiet -r requirements.txt --no-deps
        python -m pip install --quiet -r requirements.txt
    )
) else (
    echo [3/4] Packages already installed
)

echo [4/4] Starting application...
echo.
echo The browser will open automatically.
echo Keep this window open while using the application.
echo Press Ctrl+C to stop the application.
echo.

REM Set environment variable
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

REM Run Streamlit - browser will open automatically
python -m streamlit run app.py --server.headless false --browser.gatherUsageStats false

pause

