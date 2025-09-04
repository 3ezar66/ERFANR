@echo off
REM CryptoMinerDetector - Executable Builder
REM Builds a standalone Windows executable

echo ========================================
echo CryptoMinerDetector - Executable Builder
echo ========================================
echo.

REM Check if running as Administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as Administrator - OK
) else (
    echo ERROR: This build process requires Administrator privileges
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

REM Check if we're in the right directory
if not exist "main.py" (
    echo ERROR: main.py not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

REM Install PyInstaller
echo Installing PyInstaller...
pip install pyinstaller==6.3.0
if %errorLevel% == 0 (
    echo PyInstaller installed - OK
) else (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

REM Install all dependencies
echo Installing dependencies...
pip install -r requirements.txt
if %errorLevel% == 0 (
    echo Dependencies installed - OK
) else (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Run the build script
echo Building executable...
python build_exe.py
if %errorLevel% == 0 (
    echo Build completed successfully!
) else (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Generated files:
echo - CryptoMinerDetector.exe (main executable)
echo - launch.bat (launcher script)
echo - install_exe.bat (installer script)
echo.
echo To install:
echo 1. Run install_exe.bat as Administrator
echo 2. Use the desktop shortcut to launch
echo.
echo To run directly:
echo 1. Right-click launch.bat
echo 2. Select "Run as Administrator"
echo.
pause