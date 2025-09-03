# CryptoMinerDetector - Comprehensive Cryptocurrency Miner Detection System

## Overview

CryptoMinerDetector is a comprehensive, dynamic, and intelligent cryptocurrency miner detection system designed for national and governmental use in Windows environments. The system is embedded as an operating system application with a shortcut to its executable, and all source code, data, and files are stored on the `D:` drive.

## System Architecture

The system follows a layered architecture with the following components:

### Core Layers
1. **Legal & Governance Layer**: Handles legal compliance, warrants, audit trails, and access control
2. **Orchestration Layer**: Manages scan scheduling, coordination, and resource allocation
3. **Passive Collection Layer**: Collects network data, logs, and metadata
4. **Active Scanners Layer**: Performs targeted network scans and port analysis
5. **Analysis Layer**: Detects patterns, analyzes behavior, and scores confidence
6. **Validation & Triage Layer**: Validates findings and manages follow-up actions
7. **UI/Map/Reporting Layer**: Provides user interface, mapping, and reporting capabilities
8. **DB & Audit Layer**: Manages data persistence and audit trails

### Key Features

#### Geographic Scanning
- Comprehensive scanning of specific geographic areas (provinces, cities in Iran)
- Automatic retrieval and preparation of IPv4 ranges based on selected ISPs
- Integration with Iranian administrative divisions database

#### Network Scanning
- Multiple scan types: Quick, Comprehensive, and Stealth
- Port scanning for blockchain and cryptocurrency pool ports
- Service identification and fingerprinting
- Integration with Nmap and Wireshark

#### VPN/Proxy/DNS Changer Detection
- Detection of IP changers (VPNs, proxies, DNS changers)
- Non-malicious deanonymization using reference lists and metadata matching
- Judicial/ISP cooperation for suspicious activity reporting
- Original IP assessment for mining activity

#### Precise Location and Mapping
- Interactive, real-time mapping with Folium
- Precise location identification and routing guidance
- Geographic visualization of detected devices
- Multiple map types: device locations, ISP coverage, miner density, VPN detection

#### Internal Database
- Robust SQLite database for all events, actions, and data
- Chain of custody tracking
- Permanent review, search, and retrieval capabilities
- Audit logging and compliance reporting

#### Legal Compliance
- National and governmental use compliance
- All necessary legal, security, and judicial permits
- 100% realistic implementation for real-world environments
- Data retention and privacy protection

## Installation and Setup

### Prerequisites
- Windows operating system
- Python 3.8 or higher
- Administrative privileges
- D: drive available for data storage

### Dependencies
Install required packages using:
```bash
pip install -r requirements.txt
```

### Configuration
1. Copy the project to `D:/CryptoMinerDetector/`
2. Update `config/config.ini` with your API keys and settings
3. Ensure all paths point to the D: drive
4. Run the application as Administrator

## Usage

### Starting the Application
```bash
python main.py
```

### Main Interface
The application provides a tabbed interface with:

1. **Dashboard**: System overview, statistics, and recent activity
2. **Network Scanning**: Configure and run network scans
3. **Reports**: Generate and manage reports
4. **Maps**: Geographic visualization and location analysis
5. **Settings**: Configuration and system management

### Network Scanning
1. Select scan type (Quick, Comprehensive, Stealth)
2. Enter IP range in CIDR notation
3. Configure ports to scan
4. Start the scan and monitor progress
5. Review results and export data

### Geographic Scanning
1. Select province and cities
2. Load ISP data for the selected area
3. Configure scan parameters
4. Execute geographic scan
5. Analyze results by location

### Report Generation
1. Select report type (Scan Summary, Device Details, Audit Log, Compliance)
2. Choose date range
3. Generate report
4. Export in multiple formats (JSON, CSV, PDF)

### Map Visualization
1. Select map type (Device Locations, ISP Coverage, Miner Density, VPN Detection)
2. Choose geographic area
3. Generate interactive map
4. Open in browser or export

## File Structure

```
D:/CryptoMinerDetector/
├── main.py                          # Main application entry point
├── requirements.txt                 # Python dependencies
├── config/
│   └── config.ini                   # Configuration file
├── src/
│   ├── core/                        # Core system components
│   │   ├── config_manager.py       # Configuration management
│   │   ├── database_manager.py     # Database operations
│   │   ├── security_manager.py     # Security and encryption
│   │   └── audit_logger.py         # Audit logging
│   ├── scanners/                    # Scanning modules
│   │   ├── network_scanner.py      # Network scanning
│   │   ├── geographic_scanner.py   # Geographic scanning
│   │   └── isp_scanner.py          # ISP-based scanning
│   ├── analyzers/                   # Analysis modules
│   │   ├── miner_analyzer.py       # Miner detection
│   │   └── vpn_detector.py         # VPN detection
│   ├── ui/                         # User interface
│   │   ├── main_window.py          # Main GUI window
│   │   ├── scan_interface.py       # Scan interface
│   │   ├── report_interface.py     # Report interface
│   │   └── map_interface.py        # Map interface
│   └── utils/                      # Utility modules
│       ├── geographic_data.py      # Geographic data management
│       └── isp_data.py             # ISP data management
├── data/                           # Data storage
│   ├── isp_ranges/                 # ISP IP ranges
│   ├── geographic_data/            # Geographic data
│   └── scan_results/               # Scan results
├── logs/                           # Log files
├── reports/                        # Generated reports
├── maps/                           # Generated maps
└── docs/                           # Documentation
```

## Configuration

### API Keys
Configure the following API keys in `config/config.ini`:
- Shodan API key
- Censys API credentials
- IPInfo token
- Telecom API key

### Network Settings
- Default timeout: 3 seconds
- Maximum concurrent scans: 10
- Rate limit: 100 requests per second
- Default ports: 3333, 4028, 5555, 7777, 8332, 8333, 8555, 9332, 9333, 14444, 14433, 14455

### Security Settings
- Session timeout: 30 minutes
- Maximum login attempts: 3
- Encryption key file location
- Audit log file location

## Legal and Compliance

### Usage Restrictions
- **National and Governmental Use Only**
- Requires legal permits and judicial authorization
- All operations must comply with local laws and regulations
- Data retention policies must be followed

### Privacy Protection
- All sensitive data is encrypted
- Audit trails are maintained for all operations
- Chain of custody is preserved for evidence
- Access control is role-based

### VPN Detection Limitations
- No malicious deanonymization attempts
- Uses reference lists and metadata matching only
- Reports suspicious activity scores rather than definitive deanonymization
- Requires judicial cooperation for detailed investigation

## Troubleshooting

### Common Issues
1. **Administrative Rights Required**: Run the application as Administrator
2. **D: Drive Not Available**: Ensure D: drive is accessible and has sufficient space
3. **API Key Errors**: Verify API keys are correctly configured in config.ini
4. **Network Scanning Issues**: Check firewall settings and network permissions

### Log Files
Check the following log files for detailed error information:
- `logs/application.log`: General application logs
- `logs/audit.log`: Audit trail logs
- `logs/scan.log`: Network scanning logs

## Support

For technical support and legal compliance questions, contact the system administrator or legal department.

## Version History

- **v1.0.0**: Initial release with core functionality
  - Network scanning capabilities
  - Geographic data integration
  - VPN detection framework
  - Interactive mapping
  - Comprehensive reporting
  - Audit logging system

## License

This software is proprietary and confidential. Use is restricted to authorized governmental and national security organizations with proper legal authorization.

---

**Important**: This system is designed for legitimate law enforcement and national security purposes only. All usage must comply with applicable laws and regulations. Unauthorized use is strictly prohibited.