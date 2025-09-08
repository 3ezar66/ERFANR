#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Script for CryptoMinerDetector Executable
Creates a standalone Windows executable using PyInstaller.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed."""
    try:
        import PyInstaller
        print("✓ PyInstaller already installed")
        return True
    except ImportError:
        print("Installing PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("✗ Failed to install PyInstaller")
            return False

def create_spec_file():
    """Create PyInstaller spec file for the application."""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config/config.ini', 'config'),
        ('src', 'src'),
        ('requirements.txt', '.'),
        ('README.md', '.'),
        ('install.bat', '.'),
        ('run.bat', '.'),
        ('test_system.py', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'sqlite3',
        'configparser',
        'logging',
        'threading',
        'multiprocessing',
        'datetime',
        'json',
        'pathlib',
        'scapy',
        'folium',
        'geocoder',
        'geopy',
        'requests',
        'shodan',
        'censys',
        'pandas',
        'numpy',
        'nmap',
        'psutil',
        'matplotlib',
        'seaborn',
        'plotly',
        'cryptography',
        'geopandas',
        'shapely',
        'scikit-learn',
        'joblib',
        'beautifulsoup4',
        'selenium',
        'pywin32',
        'wmi',
        'pyyaml',
        'pytest',
        'pytest-cov',
        'black',
        'flake8',
        'ipaddress',
        'concurrent.futures',
        'hmac',
        'hashlib',
        'base64',
        'csv',
        'xml.etree.ElementTree',
        'urllib.parse',
        'socket',
        'ssl',
        'time',
        'random',
        're',
        'collections',
        'itertools',
        'functools',
        'contextlib',
        'typing',
        'enum',
        'dataclasses',
        'asyncio',
        'aiohttp',
        'websockets',
        'jinja2',
        'markdown',
        'yaml',
        'toml',
        'configparser',
        'argparse',
        'getpass',
        'platform',
        'subprocess',
        'tempfile',
        'zipfile',
        'tarfile',
        'gzip',
        'pickle',
        'shelve',
        'dbm',
        'sqlite3',
        'xml',
        'html',
        'email',
        'http',
        'urllib',
        'ftplib',
        'telnetlib',
        'smtplib',
        'poplib',
        'imaplib',
        'nntplib',
        'socketserver',
        'xmlrpc',
        'webbrowser',
        'cgi',
        'cgitb',
        'wsgiref',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
        'requests_toolbelt',
        'requests_oauthlib',
        'requests_ntlm',
        'requests_kerberos',
        'requests_aws4auth',
        'requests_mock',
        'responses',
        'httpretty',
        'httmock',
        'freezegun',
        'factory_boy',
        'faker',
        'mimesis',
        'fake_useragent',
        'user_agents',
        'python_dateutil',
        'pytz',
        'tzlocal',
        'python_utils',
        'python_utils_plus',
        'python_utils_plus_plus',
        'python_utils_plus_plus_plus',
        'python_utils_plus_plus_plus_plus',
        'python_utils_plus_plus_plus_plus_plus',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CryptoMinerDetector',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
    version_file=None,
    uac_admin=True,
    uac_uiaccess=False,
)
'''
    
    with open('CryptoMinerDetector.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✓ PyInstaller spec file created")

def create_icon():
    """Create a simple icon file if it doesn't exist."""
    icon_dir = Path("assets")
    icon_dir.mkdir(exist_ok=True)
    
    icon_path = icon_dir / "icon.ico"
    if not icon_path.exists():
        # Create a simple text-based icon (placeholder)
        print("⚠ Icon file not found. Using default icon.")
        # You can replace this with a real .ico file later

def build_executable():
    """Build the executable using PyInstaller."""
    print("Building executable...")
    
    try:
        # Run PyInstaller
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            "--uac-admin",
            "--name=CryptoMinerDetector",
            "--add-data=config/config.ini;config",
            "--add-data=src;src",
            "--add-data=requirements.txt;.",
            "--add-data=README.md;.",
            "--add-data=install.bat;.",
            "--add-data=run.bat;.",
            "--add-data=test_system.py;.",
            "--hidden-import=tkinter",
            "--hidden-import=tkinter.ttk",
            "--hidden-import=tkinter.messagebox",
            "--hidden-import=tkinter.filedialog",
            "--hidden-import=sqlite3",
            "--hidden-import=configparser",
            "--hidden-import=logging",
            "--hidden-import=threading",
            "--hidden-import=multiprocessing",
            "--hidden-import=datetime",
            "--hidden-import=json",
            "--hidden-import=pathlib",
            "--hidden-import=scapy",
            "--hidden-import=folium",
            "--hidden-import=geocoder",
            "--hidden-import=geopy",
            "--hidden-import=requests",
            "--hidden-import=shodan",
            "--hidden-import=censys",
            "--hidden-import=pandas",
            "--hidden-import=numpy",
            "--hidden-import=nmap",
            "--hidden-import=psutil",
            "--hidden-import=matplotlib",
            "--hidden-import=seaborn",
            "--hidden-import=plotly",
            "--hidden-import=cryptography",
            "--hidden-import=geopandas",
            "--hidden-import=shapely",
            "--hidden-import=scikit-learn",
            "--hidden-import=joblib",
            "--hidden-import=beautifulsoup4",
            "--hidden-import=selenium",
            "--hidden-import=pywin32",
            "--hidden-import=wmi",
            "--hidden-import=pyyaml",
            "--hidden-import=ipaddress",
            "--hidden-import=concurrent.futures",
            "--hidden-import=hmac",
            "--hidden-import=hashlib",
            "--hidden-import=base64",
            "--hidden-import=csv",
            "--hidden-import=xml.etree.ElementTree",
            "--hidden-import=urllib.parse",
            "--hidden-import=socket",
            "--hidden-import=ssl",
            "--hidden-import=time",
            "--hidden-import=random",
            "--hidden-import=re",
            "--hidden-import=collections",
            "--hidden-import=itertools",
            "--hidden-import=functools",
            "--hidden-import=contextlib",
            "--hidden-import=typing",
            "--hidden-import=enum",
            "--hidden-import=dataclasses",
            "--hidden-import=asyncio",
            "--hidden-import=aiohttp",
            "--hidden-import=websockets",
            "--hidden-import=jinja2",
            "--hidden-import=markdown",
            "--hidden-import=yaml",
            "--hidden-import=toml",
            "--hidden-import=argparse",
            "--hidden-import=getpass",
            "--hidden-import=platform",
            "--hidden-import=subprocess",
            "--hidden-import=tempfile",
            "--hidden-import=zipfile",
            "--hidden-import=tarfile",
            "--hidden-import=gzip",
            "--hidden-import=pickle",
            "--hidden-import=shelve",
            "--hidden-import=dbm",
            "--hidden-import=xml",
            "--hidden-import=html",
            "--hidden-import=email",
            "--hidden-import=http",
            "--hidden-import=urllib",
            "--hidden-import=ftplib",
            "--hidden-import=telnetlib",
            "--hidden-import=smtplib",
            "--hidden-import=poplib",
            "--hidden-import=imaplib",
            "--hidden-import=nntplib",
            "--hidden-import=socketserver",
            "--hidden-import=xmlrpc",
            "--hidden-import=webbrowser",
            "--hidden-import=cgi",
            "--hidden-import=cgitb",
            "--hidden-import=wsgiref",
            "--hidden-import=urllib3",
            "--hidden-import=certifi",
            "--hidden-import=charset_normalizer",
            "--hidden-import=idna",
            "--hidden-import=requests_toolbelt",
            "--hidden-import=requests_oauthlib",
            "--hidden-import=requests_ntlm",
            "--hidden-import=requests_kerberos",
            "--hidden-import=requests_aws4auth",
            "--hidden-import=requests_mock",
            "--hidden-import=responses",
            "--hidden-import=httpretty",
            "--hidden-import=httmock",
            "--hidden-import=freezegun",
            "--hidden-import=factory_boy",
            "--hidden-import=faker",
            "--hidden-import=mimesis",
            "--hidden-import=fake_useragent",
            "--hidden-import=user_agents",
            "--hidden-import=python_dateutil",
            "--hidden-import=pytz",
            "--hidden-import=tzlocal",
            "--hidden-import=python_utils",
            "--hidden-import=python_utils_plus",
            "--hidden-import=python_utils_plus_plus",
            "--hidden-import=python_utils_plus_plus_plus",
            "--hidden-import=python_utils_plus_plus_plus_plus",
            "--hidden-import=python_utils_plus_plus_plus_plus_plus",
            "main.py"
        ]
        
        # Add icon if exists
        if os.path.exists("assets/icon.ico"):
            cmd.extend(["--icon=assets/icon.ico"])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Executable built successfully!")
            return True
        else:
            print(f"✗ Build failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Build failed with exception: {e}")
        return False

def create_launcher_script():
    """Create a launcher script for the executable."""
    launcher_content = '''@echo off
REM CryptoMinerDetector Launcher
REM This script launches the standalone executable

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

REM Check if executable exists
if exist "CryptoMinerDetector.exe" (
    echo Executable found - OK
) else (
    echo ERROR: CryptoMinerDetector.exe not found
    echo Please ensure the executable is in the same directory
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

REM Create necessary directories
if not exist "D:\CryptoMinerDetector" mkdir "D:\CryptoMinerDetector"
if not exist "D:\CryptoMinerDetector\data" mkdir "D:\CryptoMinerDetector\data"
if not exist "D:\CryptoMinerDetector\logs" mkdir "D:\CryptoMinerDetector\logs"
if not exist "D:\CryptoMinerDetector\maps" mkdir "D:\CryptoMinerDetector\maps"
if not exist "D:\CryptoMinerDetector\temp" mkdir "D:\CryptoMinerDetector\temp"

echo.
echo Starting CryptoMinerDetector...
echo.

REM Launch the executable
start "" "CryptoMinerDetector.exe"

echo Application launched successfully!
pause
'''
    
    with open('launch.bat', 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    print("✓ Launcher script created")

def create_installer_script():
    """Create an installer script for the executable."""
    installer_content = '''@echo off
REM CryptoMinerDetector Installer
REM Installs the standalone executable

echo ========================================
echo CryptoMinerDetector - Installation
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

REM Check if executable exists
if exist "CryptoMinerDetector.exe" (
    echo Executable found - OK
) else (
    echo ERROR: CryptoMinerDetector.exe not found
    echo Please ensure the executable is in the same directory
    pause
    exit /b 1
)

REM Create installation directory
set INSTALL_DIR=C:\Program Files\CryptoMinerDetector
echo Creating installation directory: %INSTALL_DIR%
mkdir "%INSTALL_DIR%" 2>nul

REM Copy files
echo Copying files...
copy "CryptoMinerDetector.exe" "%INSTALL_DIR%\" >nul
copy "launch.bat" "%INSTALL_DIR%\" >nul
copy "README.md" "%INSTALL_DIR%\" >nul

REM Create data directory on D: drive
if not exist "D:\CryptoMinerDetector" mkdir "D:\CryptoMinerDetector"
if not exist "D:\CryptoMinerDetector\data" mkdir "D:\CryptoMinerDetector\data"
if not exist "D:\CryptoMinerDetector\logs" mkdir "D:\CryptoMinerDetector\logs"
if not exist "D:\CryptoMinerDetector\maps" mkdir "D:\CryptoMinerDetector\maps"
if not exist "D:\CryptoMinerDetector\temp" mkdir "D:\CryptoMinerDetector\temp"

REM Create desktop shortcut
echo Creating desktop shortcut...
echo @echo off > "%USERPROFILE%\Desktop\CryptoMinerDetector.bat"
echo cd /d "%INSTALL_DIR%" >> "%USERPROFILE%\Desktop\CryptoMinerDetector.bat"
echo launch.bat >> "%USERPROFILE%\Desktop\CryptoMinerDetector.bat"

REM Create start menu shortcut
echo Creating start menu shortcut...
set START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs\CryptoMinerDetector
mkdir "%START_MENU%" 2>nul
echo @echo off > "%START_MENU%\CryptoMinerDetector.bat"
echo cd /d "%INSTALL_DIR%" >> "%START_MENU%\CryptoMinerDetector.bat"
echo launch.bat >> "%START_MENU%\CryptoMinerDetector.bat"

REM Set file permissions
echo Setting file permissions...
icacls "%INSTALL_DIR%" /grant "Users":(OI)(CI)RX /T >nul 2>&1
icacls "D:\CryptoMinerDetector" /grant "Users":(OI)(CI)F /T >nul 2>&1

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo Installation location: %INSTALL_DIR%
echo Data location: D:\CryptoMinerDetector
echo.
echo Shortcuts created:
echo - Desktop: %USERPROFILE%\Desktop\CryptoMinerDetector.bat
echo - Start Menu: %START_MENU%\CryptoMinerDetector.bat
echo.
echo To run the application:
echo 1. Right-click the desktop shortcut
echo 2. Select "Run as Administrator"
echo.
pause
'''
    
    with open('install_exe.bat', 'w', encoding='utf-8') as f:
        f.write(installer_content)
    
    print("✓ Installer script created")

def cleanup():
    """Clean up build artifacts."""
    print("Cleaning up build artifacts...")
    
    # Remove build and dist directories
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # Remove spec file
    if os.path.exists("CryptoMinerDetector.spec"):
        os.remove("CryptoMinerDetector.spec")
    
    print("✓ Cleanup completed")

def main():
    """Main build process."""
    print("=" * 60)
    print("CryptoMinerDetector - Executable Builder")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("✗ Error: main.py not found in current directory")
        print("Please run this script from the project root directory")
        return 1
    
    # Install PyInstaller
    if not install_pyinstaller():
        return 1
    
    # Create icon
    create_icon()
    
    # Create spec file
    create_spec_file()
    
    # Build executable
    if not build_executable():
        return 1
    
    # Create launcher script
    create_launcher_script()
    
    # Create installer script
    create_installer_script()
    
    # Clean up
    cleanup()
    
    print("\n" + "=" * 60)
    print("🎉 Executable built successfully!")
    print("=" * 60)
    print("\nGenerated files:")
    print("- CryptoMinerDetector.exe (main executable)")
    print("- launch.bat (launcher script)")
    print("- install_exe.bat (installer script)")
    print("\nTo install:")
    print("1. Run install_exe.bat as Administrator")
    print("2. Use the desktop shortcut to launch")
    print("\nTo run directly:")
    print("1. Right-click launch.bat")
    print("2. Select 'Run as Administrator'")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())