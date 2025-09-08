#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Test Script for CryptoMinerDetector
Tests all major components to ensure they work correctly.
"""

import sys
import os
import logging
from pathlib import Path

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test if all modules can be imported."""
    print("Testing module imports...")
    
    try:
        from core.config_manager import ConfigManager
        print("✓ ConfigManager imported successfully")
    except Exception as e:
        print(f"✗ ConfigManager import failed: {e}")
        return False
        
    try:
        from core.database_manager import DatabaseManager
        print("✓ DatabaseManager imported successfully")
    except Exception as e:
        print(f"✗ DatabaseManager import failed: {e}")
        return False
        
    try:
        from core.security_manager import SecurityManager
        print("✓ SecurityManager imported successfully")
    except Exception as e:
        print(f"✗ SecurityManager import failed: {e}")
        return False
        
    try:
        from core.audit_logger import AuditLogger
        print("✓ AuditLogger imported successfully")
    except Exception as e:
        print(f"✗ AuditLogger import failed: {e}")
        return False
        
    try:
        from scanners.network_scanner import NetworkScanner
        print("✓ NetworkScanner imported successfully")
    except Exception as e:
        print(f"✗ NetworkScanner import failed: {e}")
        return False
        
    try:
        from scanners.geographic_scanner import GeographicScanner
        print("✓ GeographicScanner imported successfully")
    except Exception as e:
        print(f"✗ GeographicScanner import failed: {e}")
        return False
        
    try:
        from scanners.isp_scanner import ISPScanner
        print("✓ ISPScanner imported successfully")
    except Exception as e:
        print(f"✗ ISPScanner import failed: {e}")
        return False
        
    try:
        from analyzers.miner_analyzer import MinerAnalyzer
        print("✓ MinerAnalyzer imported successfully")
    except Exception as e:
        print(f"✗ MinerAnalyzer import failed: {e}")
        return False
        
    try:
        from analyzers.vpn_detector import VPNDetector
        print("✓ VPNDetector imported successfully")
    except Exception as e:
        print(f"✗ VPNDetector import failed: {e}")
        return False
        
    try:
        from utils.geographic_data import GeographicDataManager
        print("✓ GeographicDataManager imported successfully")
    except Exception as e:
        print(f"✗ GeographicDataManager import failed: {e}")
        return False
        
    try:
        from utils.isp_data import ISPDataManager
        print("✓ ISPDataManager imported successfully")
    except Exception as e:
        print(f"✗ ISPDataManager import failed: {e}")
        return False
        
    return True

def test_configuration():
    """Test configuration loading."""
    print("\nTesting configuration...")
    
    try:
        from core.config_manager import ConfigManager
        config = ConfigManager()
        print("✓ Configuration loaded successfully")
        
        # Test some config values
        shodan_key = config.get('API_KEYS', 'shodan_api_key')
        if shodan_key and shodan_key != 'YOUR_SHODAN_API_KEY':
            print("✓ Shodan API key configured")
        else:
            print("⚠ Shodan API key not configured")
            
        ipinfo_token = config.get('API_KEYS', 'ipinfo_token')
        if ipinfo_token and ipinfo_token != 'YOUR_IPINFO_TOKEN':
            print("✓ IPInfo token configured")
        else:
            print("⚠ IPInfo token not configured")
            
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_database():
    """Test database initialization."""
    print("\nTesting database...")
    
    try:
        from core.config_manager import ConfigManager
        from core.database_manager import DatabaseManager
        
        config = ConfigManager()
        db = DatabaseManager(config)
        print("✓ Database initialized successfully")
        
        # Test basic operations
        stats = db.get_statistics()
        print(f"✓ Database statistics retrieved: {stats}")
        
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_geographic_data():
    """Test geographic data loading."""
    print("\nTesting geographic data...")
    
    try:
        from core.config_manager import ConfigManager
        from utils.geographic_data import GeographicDataManager
        
        config = ConfigManager()
        geo_manager = GeographicDataManager(config)
        
        provinces = geo_manager.get_provinces()
        print(f"✓ Loaded {len(provinces)} provinces")
        
        if provinces:
            first_province = provinces[0]
            cities = geo_manager.get_cities_by_province(first_province['code'])
            print(f"✓ Loaded {len(cities)} cities for {first_province['name']}")
            
        return True
        
    except Exception as e:
        print(f"✗ Geographic data test failed: {e}")
        return False

def test_isp_data():
    """Test ISP data loading."""
    print("\nTesting ISP data...")
    
    try:
        from core.config_manager import ConfigManager
        from utils.isp_data import ISPDataManager
        
        config = ConfigManager()
        isp_manager = ISPDataManager(config)
        
        isps = isp_manager.get_isps()
        print(f"✓ Loaded {len(isps)} ISPs")
        
        if isps:
            first_isp = isps[0]
            ip_ranges = isp_manager.get_ip_ranges_by_isp(first_isp['code'])
            print(f"✓ Loaded {len(ip_ranges)} IP ranges for {first_isp['name']}")
            
        return True
        
    except Exception as e:
        print(f"✗ ISP data test failed: {e}")
        return False

def test_security():
    """Test security features."""
    print("\nTesting security features...")
    
    try:
        from core.config_manager import ConfigManager
        from core.security_manager import SecurityManager
        
        config = ConfigManager()
        security = SecurityManager(config)
        
        # Test encryption
        test_data = "test_secret_data"
        encrypted = security.encrypt_data(test_data)
        decrypted = security.decrypt_data(encrypted)
        
        if decrypted == test_data:
            print("✓ Encryption/decryption working correctly")
        else:
            print("✗ Encryption/decryption failed")
            return False
            
        # Test password hashing
        password = "test_password"
        hash_result = security.hash_password(password)
        if security.verify_password(password, hash_result['hash'], hash_result['salt']):
            print("✓ Password hashing working correctly")
        else:
            print("✗ Password hashing failed")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Security test failed: {e}")
        return False

def test_audit_logging():
    """Test audit logging."""
    print("\nTesting audit logging...")
    
    try:
        from core.config_manager import ConfigManager
        from core.database_manager import DatabaseManager
        from core.audit_logger import AuditLogger
        
        config = ConfigManager()
        db = DatabaseManager(config)
        audit = AuditLogger(config, db)
        
        # Test logging
        audit.log_system_event(
            event_type="test_event",
            description="System test event",
            system_component="test_system"
        )
        print("✓ Audit logging working correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ Audit logging test failed: {e}")
        return False

def test_analyzers():
    """Test analyzer components."""
    print("\nTesting analyzers...")
    
    try:
        from core.config_manager import ConfigManager
        from core.database_manager import DatabaseManager
        from core.audit_logger import AuditLogger
        from analyzers.miner_analyzer import MinerAnalyzer
        from analyzers.vpn_detector import VPNDetector
        
        config = ConfigManager()
        db = DatabaseManager(config)
        audit = AuditLogger(config, db)
        
        # Test miner analyzer
        miner_analyzer = MinerAnalyzer(config, db, audit)
        print("✓ MinerAnalyzer initialized successfully")
        
        # Test VPN detector
        vpn_detector = VPNDetector(config, db, audit)
        print("✓ VPNDetector initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Analyzers test failed: {e}")
        return False

def test_scanners():
    """Test scanner components."""
    print("\nTesting scanners...")
    
    try:
        from core.config_manager import ConfigManager
        from core.database_manager import DatabaseManager
        from core.audit_logger import AuditLogger
        from scanners.network_scanner import NetworkScanner
        from scanners.geographic_scanner import GeographicScanner
        from scanners.isp_scanner import ISPScanner
        from utils.geographic_data import GeographicDataManager
        from utils.isp_data import ISPDataManager
        
        config = ConfigManager()
        db = DatabaseManager(config)
        audit = AuditLogger(config, db)
        geo_manager = GeographicDataManager(config)
        isp_manager = ISPDataManager(config)
        
        # Test network scanner
        network_scanner = NetworkScanner(config, db, audit)
        print("✓ NetworkScanner initialized successfully")
        
        # Test geographic scanner
        geo_scanner = GeographicScanner(config, db, network_scanner, geo_manager, isp_manager, audit)
        print("✓ GeographicScanner initialized successfully")
        
        # Test ISP scanner
        isp_scanner = ISPScanner(config, db, network_scanner, isp_manager, audit)
        print("✓ ISPScanner initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Scanners test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("CryptoMinerDetector - System Test")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("Database", test_database),
        ("Geographic Data", test_geographic_data),
        ("ISP Data", test_isp_data),
        ("Security", test_security),
        ("Audit Logging", test_audit_logging),
        ("Analyzers", test_analyzers),
        ("Scanners", test_scanners),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        return 0
    else:
        print("⚠ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())