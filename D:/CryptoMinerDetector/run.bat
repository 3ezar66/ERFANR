@echo off
REM CryptoMinerDetector - National Security System
REM Run as Administrator

echo ========================================
echo CryptoMinerDetector - National Security System
echo ========================================
echo.

REM Check if running as Administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as Administrator - OK
) else (
    echo ERROR: This application requires Administrator privileges
    echo Please right-click and select "Run as Administrator"
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if %errorLevel% == 0 (
    echo Python found - OK
) else (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

REM Check if D: drive exists
if exist D:\ (
    echo D: drive found - OK
) else (
    echo ERROR: D: drive not found
    echo Please ensure D: drive is available
    pause
    exit /b 1
)

REM Check if project directory exists
if exist D:\CryptoMinerDetector\ (
    echo Project directory found - OK
) else (
    echo ERROR: Project directory not found
    echo Please ensure D:\CryptoMinerDetector\ exists
    pause
    exit /b 1
)

REM Change to project directory
cd /d D:\CryptoMinerDetector

REM Check if main.py exists
if exist main.py (
    echo Main application file found - OK
) else (
    echo ERROR: main.py not found
    echo Please ensure all project files are copied to D:\CryptoMinerDetector\
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking dependencies...
python -c "import scapy, folium, requests, sqlite3, tkinter" >nul 2>&1
if %errorLevel% == 0 (
    echo Dependencies found - OK
) else (
    echo Installing dependencies...
    pip install -r requirements.txt
    if %errorLevel% == 0 (
        echo Dependencies installed - OK
    ) else (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting CryptoMinerDetector...
echo.

REM Start the application
python main.py

REM If we get here, the application has closed
echo.
echo Application closed.
pause