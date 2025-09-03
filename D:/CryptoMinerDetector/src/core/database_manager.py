#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Manager for CryptoMinerDetector
Handles all database operations including device storage, scan results,
audit logs, and geographic data.
"""

import sqlite3
import logging
import json
import hashlib
import hmac
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import threading

class DatabaseManager:
    """
    Manages SQLite database operations for the CryptoMinerDetector system.
    Handles device information, scan results, audit logs, and geographic data.
    """
    
    def __init__(self, config):
        """
        Initialize the database manager.
        
        Args:
            config: Configuration manager instance
        """
        self.config = config
        self.db_path = config.get_database_path()
        self.logger = logging.getLogger(__name__)
        self.lock = threading.Lock()
        
        # Ensure database directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._initialize_database()
        
    def _initialize_database(self):
        """Initialize database tables and indexes."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Create devices table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS devices (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ip_address TEXT NOT NULL,
                        mac_address TEXT,
                        hostname TEXT,
                        isp_name TEXT,
                        isp_asn TEXT,
                        province TEXT,
                        city TEXT,
                        latitude REAL,
                        longitude REAL,
                        open_ports TEXT,
                        miner_ports TEXT,
                        miner_protocols TEXT,
                        vpn_detected BOOLEAN DEFAULT FALSE,
                        vpn_type TEXT,
                        original_ip TEXT,
                        confidence_score REAL DEFAULT 0.0,
                        last_scan_time TIMESTAMP,
                        first_detected TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'active',
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create scan_results table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS scan_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        scan_id TEXT NOT NULL,
                        scan_type TEXT NOT NULL,
                        target_range TEXT NOT NULL,
                        province TEXT,
                        city TEXT,
                        isp_name TEXT,
                        start_time TIMESTAMP,
                        end_time TIMESTAMP,
                        devices_found INTEGER DEFAULT 0,
                        miners_detected INTEGER DEFAULT 0,
                        scan_status TEXT DEFAULT 'running',
                        scan_config TEXT,
                        results_summary TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create audit_logs table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS audit_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT,
                        action TEXT NOT NULL,
                        target TEXT,
                        details TEXT,
                        ip_address TEXT,
                        session_id TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        success BOOLEAN DEFAULT TRUE,
                        error_message TEXT
                    )
                """)
                
                # Create geographic_data table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS geographic_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        province_code TEXT NOT NULL,
                        province_name TEXT NOT NULL,
                        city_code TEXT,
                        city_name TEXT,
                        postal_code TEXT,
                        latitude REAL,
                        longitude REAL,
                        population INTEGER,
                        area_km2 REAL,
                        isp_coverage TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create isp_data table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS isp_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        isp_name TEXT NOT NULL,
                        isp_code TEXT,
                        asn TEXT,
                        ip_range_start TEXT,
                        ip_range_end TEXT,
                        cidr_notation TEXT,
                        province TEXT,
                        city TEXT,
                        coverage_area TEXT,
                        contact_info TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create warrants table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS warrants (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        warrant_number TEXT NOT NULL,
                        warrant_type TEXT NOT NULL,
                        issued_by TEXT NOT NULL,
                        issued_date DATE NOT NULL,
                        expiry_date DATE,
                        target_province TEXT,
                        target_city TEXT,
                        target_isp TEXT,
                        target_ip_range TEXT,
                        warrant_details TEXT,
                        status TEXT DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_devices_ip ON devices(ip_address)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_devices_province ON devices(province)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_devices_isp ON devices(isp_name)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_devices_status ON devices(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_scan_results_scan_id ON scan_results(scan_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_geographic_data_province ON geographic_data(province_code)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_isp_data_name ON isp_data(isp_name)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_warrants_number ON warrants(warrant_number)")
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
            
    def _get_connection(self):
        """Get database connection with proper configuration."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
        
    def add_device(self, device_data: Dict[str, Any]) -> int:
        """
        Add a new device to the database.
        
        Args:
            device_data: Dictionary containing device information
            
        Returns:
            Device ID
        """
        with self.lock:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Prepare data
                    device_data['open_ports'] = json.dumps(device_data.get('open_ports', []))
                    device_data['miner_ports'] = json.dumps(device_data.get('miner_ports', []))
                    device_data['miner_protocols'] = json.dumps(device_data.get('miner_protocols', []))
                    device_data['last_scan_time'] = datetime.now()
                    device_data['updated_at'] = datetime.now()
                    
                    cursor.execute("""
                        INSERT INTO devices (
                            ip_address, mac_address, hostname, isp_name, isp_asn,
                            province, city, latitude, longitude, open_ports,
                            miner_ports, miner_protocols, vpn_detected, vpn_type,
                            original_ip, confidence_score, last_scan_time, notes
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        device_data.get('ip_address'),
                        device_data.get('mac_address'),
                        device_data.get('hostname'),
                        device_data.get('isp_name'),
                        device_data.get('isp_asn'),
                        device_data.get('province'),
                        device_data.get('city'),
                        device_data.get('latitude'),
                        device_data.get('longitude'),
                        device_data.get('open_ports'),
                        device_data.get('miner_ports'),
                        device_data.get('miner_protocols'),
                        device_data.get('vpn_detected', False),
                        device_data.get('vpn_type'),
                        device_data.get('original_ip'),
                        device_data.get('confidence_score', 0.0),
                        device_data.get('last_scan_time'),
                        device_data.get('notes')
                    ))
                    
                    device_id = cursor.lastrowid
                    conn.commit()
                    
                    self.logger.info(f"Device added with ID: {device_id}")
                    return device_id
                    
            except Exception as e:
                self.logger.error(f"Failed to add device: {e}")
                raise
                
    def update_device(self, device_id: int, device_data: Dict[str, Any]) -> bool:
        """
        Update an existing device.
        
        Args:
            device_id: Device ID to update
            device_data: Updated device information
            
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Prepare data
                    if 'open_ports' in device_data:
                        device_data['open_ports'] = json.dumps(device_data['open_ports'])
                    if 'miner_ports' in device_data:
                        device_data['miner_ports'] = json.dumps(device_data['miner_ports'])
                    if 'miner_protocols' in device_data:
                        device_data['miner_protocols'] = json.dumps(device_data['miner_protocols'])
                    
                    device_data['updated_at'] = datetime.now()
                    
                    # Build update query dynamically
                    set_clause = ", ".join([f"{k} = ?" for k in device_data.keys()])
                    query = f"UPDATE devices SET {set_clause} WHERE id = ?"
                    
                    values = list(device_data.values()) + [device_id]
                    cursor.execute(query, values)
                    
                    conn.commit()
                    
                    if cursor.rowcount > 0:
                        self.logger.info(f"Device {device_id} updated successfully")
                        return True
                    else:
                        self.logger.warning(f"Device {device_id} not found for update")
                        return False
                        
            except Exception as e:
                self.logger.error(f"Failed to update device {device_id}: {e}")
                raise
                
    def get_device(self, device_id: int) -> Optional[Dict[str, Any]]:
        """
        Get device by ID.
        
        Args:
            device_id: Device ID
            
        Returns:
            Device data dictionary or None if not found
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
                row = cursor.fetchone()
                
                if row:
                    device_data = dict(row)
                    # Parse JSON fields
                    device_data['open_ports'] = json.loads(device_data['open_ports'] or '[]')
                    device_data['miner_ports'] = json.loads(device_data['miner_ports'] or '[]')
                    device_data['miner_protocols'] = json.loads(device_data['miner_protocols'] or '[]')
                    return device_data
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get device {device_id}: {e}")
            raise
            
    def get_devices_by_province(self, province: str) -> List[Dict[str, Any]]:
        """
        Get all devices in a specific province.
        
        Args:
            province: Province name
            
        Returns:
            List of device dictionaries
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM devices WHERE province = ? AND status = 'active'", (province,))
                rows = cursor.fetchall()
                
                devices = []
                for row in rows:
                    device_data = dict(row)
                    device_data['open_ports'] = json.loads(device_data['open_ports'] or '[]')
                    device_data['miner_ports'] = json.loads(device_data['miner_ports'] or '[]')
                    device_data['miner_protocols'] = json.loads(device_data['miner_protocols'] or '[]')
                    devices.append(device_data)
                    
                return devices
                
        except Exception as e:
            self.logger.error(f"Failed to get devices for province {province}: {e}")
            raise
            
    def get_devices_by_isp(self, isp_name: str) -> List[Dict[str, Any]]:
        """
        Get all devices from a specific ISP.
        
        Args:
            isp_name: ISP name
            
        Returns:
            List of device dictionaries
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM devices WHERE isp_name = ? AND status = 'active'", (isp_name,))
                rows = cursor.fetchall()
                
                devices = []
                for row in rows:
                    device_data = dict(row)
                    device_data['open_ports'] = json.loads(device_data['open_ports'] or '[]')
                    device_data['miner_ports'] = json.loads(device_data['miner_ports'] or '[]')
                    device_data['miner_protocols'] = json.loads(device_data['miner_protocols'] or '[]')
                    devices.append(device_data)
                    
                return devices
                
        except Exception as e:
            self.logger.error(f"Failed to get devices for ISP {isp_name}: {e}")
            raise
            
    def add_scan_result(self, scan_data: Dict[str, Any]) -> int:
        """
        Add a new scan result.
        
        Args:
            scan_data: Dictionary containing scan information
            
        Returns:
            Scan result ID
        """
        with self.lock:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Prepare data
                    scan_data['scan_config'] = json.dumps(scan_data.get('scan_config', {}))
                    scan_data['results_summary'] = json.dumps(scan_data.get('results_summary', {}))
                    
                    cursor.execute("""
                        INSERT INTO scan_results (
                            scan_id, scan_type, target_range, province, city,
                            isp_name, start_time, end_time, devices_found,
                            miners_detected, scan_status, scan_config, results_summary
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        scan_data.get('scan_id'),
                        scan_data.get('scan_type'),
                        scan_data.get('target_range'),
                        scan_data.get('province'),
                        scan_data.get('city'),
                        scan_data.get('isp_name'),
                        scan_data.get('start_time'),
                        scan_data.get('end_time'),
                        scan_data.get('devices_found', 0),
                        scan_data.get('miners_detected', 0),
                        scan_data.get('scan_status', 'running'),
                        scan_data.get('scan_config'),
                        scan_data.get('results_summary')
                    ))
                    
                    scan_id = cursor.lastrowid
                    conn.commit()
                    
                    self.logger.info(f"Scan result added with ID: {scan_id}")
                    return scan_id
                    
            except Exception as e:
                self.logger.error(f"Failed to add scan result: {e}")
                raise
                
    def add_audit_log(self, audit_data: Dict[str, Any]) -> int:
        """
        Add an audit log entry.
        
        Args:
            audit_data: Dictionary containing audit information
            
        Returns:
            Audit log ID
        """
        with self.lock:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        INSERT INTO audit_logs (
                            user_id, action, target, details, ip_address,
                            session_id, success, error_message
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        audit_data.get('user_id'),
                        audit_data.get('action'),
                        audit_data.get('target'),
                        audit_data.get('details'),
                        audit_data.get('ip_address'),
                        audit_data.get('session_id'),
                        audit_data.get('success', True),
                        audit_data.get('error_message')
                    ))
                    
                    log_id = cursor.lastrowid
                    conn.commit()
                    
                    return log_id
                    
            except Exception as e:
                self.logger.error(f"Failed to add audit log: {e}")
                raise
                
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get system statistics.
        
        Returns:
            Dictionary containing various statistics
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Total devices
                cursor.execute("SELECT COUNT(*) FROM devices WHERE status = 'active'")
                stats['total_devices'] = cursor.fetchone()[0]
                
                # Miners detected
                cursor.execute("SELECT COUNT(*) FROM devices WHERE status = 'active' AND miner_ports != '[]'")
                stats['miners_detected'] = cursor.fetchone()[0]
                
                # VPN detected
                cursor.execute("SELECT COUNT(*) FROM devices WHERE status = 'active' AND vpn_detected = 1")
                stats['vpn_detected'] = cursor.fetchone()[0]
                
                # Devices by province
                cursor.execute("""
                    SELECT province, COUNT(*) as count 
                    FROM devices 
                    WHERE status = 'active' 
                    GROUP BY province 
                    ORDER BY count DESC
                """)
                stats['devices_by_province'] = dict(cursor.fetchall())
                
                # Devices by ISP
                cursor.execute("""
                    SELECT isp_name, COUNT(*) as count 
                    FROM devices 
                    WHERE status = 'active' 
                    GROUP BY isp_name 
                    ORDER BY count DESC
                """)
                stats['devices_by_isp'] = dict(cursor.fetchall())
                
                # Recent scans
                cursor.execute("""
                    SELECT COUNT(*) FROM scan_results 
                    WHERE start_time >= datetime('now', '-7 days')
                """)
                stats['scans_last_7_days'] = cursor.fetchone()[0]
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            raise
            
    def cleanup_old_data(self, days: int = 30):
        """
        Clean up old data based on retention policy.
        
        Args:
            days: Number of days to keep data
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cutoff_date = datetime.now() - timedelta(days=days)
                
                # Clean up old audit logs
                cursor.execute("DELETE FROM audit_logs WHERE timestamp < ?", (cutoff_date,))
                audit_deleted = cursor.rowcount
                
                # Clean up old scan results
                cursor.execute("DELETE FROM scan_results WHERE created_at < ?", (cutoff_date,))
                scan_deleted = cursor.rowcount
                
                conn.commit()
                
                self.logger.info(f"Cleanup completed: {audit_deleted} audit logs, {scan_deleted} scan results deleted")
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")
            raise
            
    def backup_database(self, backup_path: Path):
        """
        Create a backup of the database.
        
        Args:
            backup_path: Path where backup should be saved
        """
        try:
            import shutil
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.db_path, backup_path)
            self.logger.info(f"Database backed up to {backup_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to backup database: {e}")
            raise
            
    def close(self):
        """Close database connections."""
        self.logger.info("Database manager closing")