@echo off
REM CryptoMinerDetector - Installation Script
REM Run as Administrator

echo ========================================
echo CryptoMinerDetector - Installation Script
echo ========================================
echo.

REM Check if running as Administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as Administrator - OK
) else (
    echo ERROR: This installation requires Administrator privileges
    echo Please right-click and select "Run as Administrator"
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if %errorLevel% == 0 (
    echo Python found - OK
) else (
    echo ERROR: Python is not installed
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

REM Create project directory structure
echo Creating directory structure...
mkdir "D:\CryptoMinerDetector" 2>nul
mkdir "D:\CryptoMinerDetector\config" 2>nul
mkdir "D:\CryptoMinerDetector\src" 2>nul
mkdir "D:\CryptoMinerDetector\src\core" 2>nul
mkdir "D:\CryptoMinerDetector\src\scanners" 2>nul
mkdir "D:\CryptoMinerDetector\src\analyzers" 2>nul
mkdir "D:\CryptoMinerDetector\src\ui" 2>nul
mkdir "D:\CryptoMinerDetector\src\utils" 2>nul
mkdir "D:\CryptoMinerDetector\data" 2>nul
mkdir "D:\CryptoMinerDetector\data\scan_results" 2>nul
mkdir "D:\CryptoMinerDetector\data\geographic_data" 2>nul
mkdir "D:\CryptoMinerDetector\data\isp_ranges" 2>nul
mkdir "D:\CryptoMinerDetector\logs" 2>nul
mkdir "D:\CryptoMinerDetector\maps" 2>nul
mkdir "D:\CryptoMinerDetector\temp" 2>nul
echo Directory structure created - OK

REM Change to project directory
cd /d D:\CryptoMinerDetector

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt
if %errorLevel% == 0 (
    echo Dependencies installed - OK
) else (
    echo ERROR: Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

REM Create desktop shortcut
echo Creating desktop shortcut...
echo @echo off > "%USERPROFILE%\Desktop\CryptoMinerDetector.bat"
echo cd /d D:\CryptoMinerDetector >> "%USERPROFILE%\Desktop\CryptoMinerDetector.bat"
echo python main.py >> "%USERPROFILE%\Desktop\CryptoMinerDetector.bat"
echo pause >> "%USERPROFILE%\Desktop\CryptoMinerDetector.bat"
echo Desktop shortcut created - OK

REM Set file permissions
echo Setting file permissions...
icacls "D:\CryptoMinerDetector" /grant "Users":(OI)(CI)F /T >nul 2>&1
echo File permissions set - OK

REM Initialize database
echo Initializing database...
python -c "from src.core.database_manager import DatabaseManager; from src.core.config_manager import ConfigManager; db = DatabaseManager(ConfigManager()); print('Database initialized successfully')" 2>nul
if %errorLevel% == 0 (
    echo Database initialized - OK
) else (
    echo Database initialization skipped (will be done on first run)
)

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Configure API keys in D:\CryptoMinerDetector\config\config.ini
echo 2. Run the application using the desktop shortcut
echo 3. Right-click the shortcut and select "Run as Administrator"
echo.
echo For more information, see README.md
echo.
pause