#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Manager for CryptoMinerDetector
Handles all configuration loading, validation, and management.
"""

import configparser
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import json

class ConfigManager:
    """
    Manages application configuration including API keys, network settings,
    database paths, and security parameters.
    """
    
    def __init__(self, config_path: Path):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self._load_config()
        
        # Validate configuration
        self._validate_config()
        
    def _load_config(self):
        """Load configuration from file."""
        try:
            if not self.config_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
                
            self.config.read(self.config_path, encoding='utf-8')
            self.logger.info(f"Configuration loaded from {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise
            
    def _validate_config(self):
        """Validate configuration parameters."""
        required_sections = [
            'API_KEYS', 'NETWORK_SCANNING', 'GEOGRAPHIC_DATA',
            'ISP_DATA', 'DATABASE', 'SECURITY', 'REPORTING',
            'LEGAL_COMPLIANCE', 'SYSTEM'
        ]
        
        for section in required_sections:
            if not self.config.has_section(section):
                raise ValueError(f"Missing required configuration section: {section}")
                
        # Validate critical paths
        self._validate_paths()
        
        # Validate API keys
        self._validate_api_keys()
        
        self.logger.info("Configuration validation completed successfully")
        
    def _validate_paths(self):
        """Validate file and directory paths in configuration."""
        paths_to_check = [
            ('DATABASE', 'db_path'),
            ('DATABASE', 'backup_path'),
            ('DATABASE', 'log_path'),
            ('SECURITY', 'encryption_key_file'),
            ('SECURITY', 'audit_log_file'),
            ('REPORTING', 'report_template_path'),
            ('REPORTING', 'map_output_path'),
            ('SYSTEM', 'temp_directory')
        ]
        
        for section, key in paths_to_check:
            if self.config.has_option(section, key):
                path_value = self.config.get(section, key)
                path = Path(path_value)
                
                # Create directory if it doesn't exist
                if key.endswith('_path') or key.endswith('_directory'):
                    path.mkdir(parents=True, exist_ok=True)
                    self.logger.info(f"Created directory: {path}")
                    
    def _validate_api_keys(self):
        """Validate API key configuration."""
        api_keys = [
            ('API_KEYS', 'shodan_api_key'),
            ('API_KEYS', 'censys_api_id'),
            ('API_KEYS', 'censys_api_secret'),
            ('API_KEYS', 'ipinfo_token'),
            ('API_KEYS', 'telecom_api_key')
        ]
        
        for section, key in api_keys:
            if self.config.has_option(section, key):
                value = self.config.get(section, key)
                if value == f'YOUR_{key.upper()}' or not value:
                    self.logger.warning(f"API key not configured: {key}")
                    
    def get(self, section: str, key: str, fallback: Any = None) -> str:
        """
        Get a configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            fallback: Fallback value if key doesn't exist
            
        Returns:
            Configuration value
        """
        return self.config.get(section, key, fallback=fallback)
        
    def getint(self, section: str, key: str, fallback: int = None) -> int:
        """
        Get an integer configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            fallback: Fallback value if key doesn't exist
            
        Returns:
            Integer configuration value
        """
        return self.config.getint(section, key, fallback=fallback)
        
    def getfloat(self, section: str, key: str, fallback: float = None) -> float:
        """
        Get a float configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            fallback: Fallback value if key doesn't exist
            
        Returns:
            Float configuration value
        """
        return self.config.getfloat(section, key, fallback=fallback)
        
    def getboolean(self, section: str, key: str, fallback: bool = None) -> bool:
        """
        Get a boolean configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            fallback: Fallback value if key doesn't exist
            
        Returns:
            Boolean configuration value
        """
        return self.config.getboolean(section, key, fallback=fallback)
        
    def getlist(self, section: str, key: str, fallback: list = None) -> list:
        """
        Get a list configuration value (comma-separated string).
        
        Args:
            section: Configuration section
            key: Configuration key
            fallback: Fallback value if key doesn't exist
            
        Returns:
            List configuration value
        """
        value = self.config.get(section, key, fallback=fallback)
        if value and isinstance(value, str):
            return [item.strip() for item in value.split(',')]
        return fallback or []
        
    def has_option(self, section: str, key: str) -> bool:
        """
        Check if a configuration option exists.
        
        Args:
            section: Configuration section
            key: Configuration key
            
        Returns:
            True if option exists, False otherwise
        """
        return self.config.has_option(section, key)
        
    def set(self, section: str, key: str, value: str):
        """
        Set a configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            value: Configuration value
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
            
        self.config.set(section, key, value)
        
    def save(self):
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as config_file:
                self.config.write(config_file)
            self.logger.info(f"Configuration saved to {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            raise
            
    def get_scan_ports(self) -> list:
        """Get list of ports to scan for miners."""
        return self.getlist('NETWORK_SCANNING', 'scan_ports')
        
    def get_miner_protocols(self) -> list:
        """Get list of mining protocols to detect."""
        return self.getlist('NETWORK_SCANNING', 'miner_protocols')
        
    def get_api_key(self, service: str) -> Optional[str]:
        """
        Get API key for a specific service.
        
        Args:
            service: Service name (shodan, censys, ipinfo, telecom)
            
        Returns:
            API key or None if not configured
        """
        key_mapping = {
            'shodan': 'shodan_api_key',
            'censys_id': 'censys_api_id',
            'censys_secret': 'censys_api_secret',
            'ipinfo': 'ipinfo_token',
            'telecom': 'telecom_api_key'
        }
        
        if service in key_mapping:
            return self.get('API_KEYS', key_mapping[service])
        return None
        
    def get_database_path(self) -> Path:
        """Get database file path."""
        return Path(self.get('DATABASE', 'db_path'))
        
    def get_log_path(self) -> Path:
        """Get log directory path."""
        return Path(self.get('DATABASE', 'log_path'))
        
    def get_backup_path(self) -> Path:
        """Get backup directory path."""
        return Path(self.get('DATABASE', 'backup_path'))
        
    def get_temp_directory(self) -> Path:
        """Get temporary directory path."""
        return Path(self.get('SYSTEM', 'temp_directory'))
        
    def get_map_output_path(self) -> Path:
        """Get map output directory path."""
        return Path(self.get('REPORTING', 'map_output_path'))
        
    def is_warrant_required(self) -> bool:
        """Check if warrant is required for operations."""
        return self.getboolean('LEGAL_COMPLIANCE', 'warrant_required', fallback=True)
        
    def get_data_retention_days(self) -> int:
        """Get data retention period in days."""
        return self.getint('LEGAL_COMPLIANCE', 'data_retention_days', fallback=1095)
        
    def get_max_concurrent_scans(self) -> int:
        """Get maximum number of concurrent scans."""
        return self.getint('NETWORK_SCANNING', 'max_concurrent_scans', fallback=10)
        
    def get_rate_limit_per_second(self) -> int:
        """Get rate limit for network scans per second."""
        return self.getint('NETWORK_SCANNING', 'rate_limit_per_second', fallback=100)
        
    def get_session_timeout_minutes(self) -> int:
        """Get session timeout in minutes."""
        return self.getint('SECURITY', 'session_timeout_minutes', fallback=30)
        
    def get_max_memory_usage_gb(self) -> int:
        """Get maximum memory usage in GB."""
        return self.getint('SYSTEM', 'max_memory_usage_gb', fallback=8)
        
    def get_cpu_usage_limit_percent(self) -> int:
        """Get CPU usage limit percentage."""
        return self.getint('SYSTEM', 'cpu_usage_limit_percent', fallback=80)