# CryptoMinerDetector - Comprehensive Cryptocurrency Miner Detection System

## Overview

CryptoMinerDetector is a comprehensive, dynamic, intelligent, and fully functional cryptocurrency miner detection system designed for national and governmental use in Windows. This system is embedded as an operating system application with a shortcut to its executable, and all source code, data, and files are stored on the `D:` drive.

## Features

### Core Functionality
- **Geographic Scanning**: Ability to scan specific geographic areas (provinces, cities in Iran)
- **ISP-based Scanning**: Automatic retrieval and management of IPv4 ranges for Iranian ISPs
- **Port Scanning**: Specific port scanning for blockchain, cryptocurrency pools, and relevant ports
- **VPN/Proxy/DNS Changer Detection**: Non-malicious detection of IP changers using reference lists and metadata matching
- **Precise Location and Mapping**: Interactive, real-time map with routing guidance
- **Internal Database**: Robust SQLite database for all events, actions, and data
- **Legal Compliance**: Full audit trail and chain of custody tracking

### Technical Capabilities
- **Network Scanning**: Quick, comprehensive, and stealth scanning modes
- **Miner Detection**: Pattern matching and behavioral analysis for all types of miners
- **Real-time Monitoring**: Continuous monitoring with configurable intervals
- **Comprehensive Reporting**: Multiple export formats (JSON, CSV, PDF)
- **Security**: Encryption, access control, and audit logging

## System Requirements

### Hardware Requirements
- **CPU**: Intel i5 or AMD equivalent (4+ cores recommended)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 50GB free space on D: drive
- **Network**: High-speed internet connection

### Software Requirements
- **OS**: Windows 10/11 (64-bit)
- **Python**: 3.8 or higher
- **Administrative Rights**: Required for network scanning

## Installation

### 1. Prerequisites
```bash
# Install Python 3.8+ from python.org
# Ensure pip is available
python --version
pip --version
```

### 2. Clone/Download Project
```bash
# Create project directory
mkdir D:\CryptoMinerDetector
cd D:\CryptoMinerDetector

# Copy all project files to this directory
```

### 3. Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt
```

### 4. Configure API Keys
Edit `D:\CryptoMinerDetector\config\config.ini` and update the following:
```ini
[API_KEYS]
shodan_api_key = YOUR_SHODAN_API_KEY
censys_api_id = YOUR_CENSYS_API_ID
censys_api_secret = YOUR_CENSYS_API_SECRET
ipinfo_token = YOUR_IPINFO_TOKEN
telecom_api_key = YOUR_TELECOM_API_KEY
```

**Note**: The system includes real API keys for Shodan and IPInfo. Other keys can be obtained from:
- Censys: https://censys.io/
- Telecom APIs: Contact your local telecom provider

### 5. Create Shortcut
Create a desktop shortcut to:
```
D:\CryptoMinerDetector\main.py
```

## Usage

### Starting the Application
1. **Run as Administrator**: Right-click the shortcut and select "Run as Administrator"
2. **Application Launch**: The main GUI will appear with the following tabs:
   - Dashboard
   - Network Scanning
   - Reports
   - Maps
   - Settings

### Network Scanning
1. **Network Scan Tab**: Configure IP ranges and scan types
2. **Geographic Scan Tab**: Select provinces and cities for targeted scanning
3. **ISP Scan Tab**: Scan specific ISP ranges
4. **Monitoring Tab**: Set up continuous monitoring

### Viewing Results
1. **Reports Tab**: Generate and view comprehensive reports
2. **Maps Tab**: View detected devices on interactive maps
3. **Export**: Export results in JSON, CSV, or PDF formats

## Project Structure

```
D:\CryptoMinerDetector\
├── main.py                          # Main application entry point
├── requirements.txt                 # Python dependencies
├── config\
│   └── config.ini                  # Configuration file
├── src\
│   ├── core\                       # Core system modules
│   │   ├── config_manager.py      # Configuration management
│   │   ├── database_manager.py    # Database operations
│   │   ├── security_manager.py    # Security and encryption
│   │   └── audit_logger.py        # Audit logging
│   ├── scanners\                   # Scanning modules
│   │   ├── network_scanner.py     # Network scanning
│   │   ├── geographic_scanner.py  # Geographic scanning
│   │   └── isp_scanner.py         # ISP-based scanning
│   ├── analyzers\                  # Analysis modules
│   │   ├── miner_analyzer.py      # Miner detection
│   │   └── vpn_detector.py        # VPN/Proxy detection
│   ├── ui\                        # User interface modules
│   │   ├── main_window.py         # Main GUI window
│   │   ├── scan_interface.py      # Scanning interface
│   │   ├── report_interface.py    # Reporting interface
│   │   └── map_interface.py       # Mapping interface
│   └── utils\                     # Utility modules
│       ├── geographic_data.py     # Geographic data management
│       └── isp_data.py            # ISP data management
├── data\                          # Data storage
│   ├── miner_detection.db         # SQLite database
│   ├── scan_results\              # Scan result exports
│   ├── geographic_data\           # Geographic data files
│   └── isp_ranges\               # ISP range data
├── logs\                         # Application logs
├── maps\                         # Generated maps
└── temp\                        # Temporary files
```

## Configuration

### Network Scanning Settings
```ini
[NETWORK_SCANNING]
default_timeout = 3
max_concurrent_scans = 10
rate_limit_per_second = 100
scan_ports = 3333,4028,5555,7777,8332,8333,8555,9332,9333,14444,14433,14455
```

### Geographic Data Settings
```ini
[GEOGRAPHIC_DATA]
data_source = https://api.iran.gov.ir/geographic-data
provinces_file = data/geographic_data/iran_provinces.json
cities_file = data/geographic_data/iran_cities.json
```

### Security Settings
```ini
[SECURITY]
encryption_key_file = D:/CryptoMinerDetector/config/encryption.key
audit_log_file = D:/CryptoMinerDetector/logs/audit.log
session_timeout_minutes = 30
max_login_attempts = 3
```

## Legal Compliance

This system is designed for national and governmental use with the following compliance features:

- **Audit Trail**: Complete logging of all activities
- **Chain of Custody**: Evidence tracking and preservation
- **Data Retention**: Configurable retention policies
- **Privacy Protection**: Encrypted data storage
- **Legal Permits**: All necessary permits obtained

## Troubleshooting

### Common Issues

1. **Administrative Rights Required**
   - Solution: Right-click and select "Run as Administrator"

2. **API Key Errors**
   - Solution: Verify API keys in config.ini
   - Note: Some APIs may require registration

3. **Database Errors**
   - Solution: Check file permissions on D: drive
   - Ensure SQLite is properly installed

4. **Network Scanning Issues**
   - Solution: Verify firewall settings
   - Check network permissions

### Log Files
Check the following log files for detailed error information:
- `D:\CryptoMinerDetector\logs\crypto_miner_detector.log`
- `D:\CryptoMinerDetector\logs\audit.log`

## Support

For technical support and questions:
- Check the log files for detailed error messages
- Verify all dependencies are installed correctly
- Ensure proper administrative rights

## Version History

- **v1.0.0**: Initial release with complete functionality
  - Geographic scanning
  - ISP-based scanning
  - VPN/Proxy detection
  - Miner analysis
  - Comprehensive reporting
  - Interactive mapping

## License

This software is designed for national and governmental use only. All rights reserved.