#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit Logger for CryptoMinerDetector
Handles comprehensive logging and chain of custody tracking.
"""

import logging
import json
import hashlib
import hmac
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import sqlite3
import threading

class AuditLogger:
    """
    Comprehensive audit logging system for CryptoMinerDetector.
    Handles chain of custody, security events, and compliance logging.
    """
    
    def __init__(self, config, database_manager):
        """
        Initialize the audit logger.
        
        Args:
            config: Configuration manager instance
            database_manager: Database manager instance
        """
        self.config = config
        self.db_manager = database_manager
        self.logger = logging.getLogger(__name__)
        
        # Audit settings
        self.audit_log_file = config.get('SECURITY', 'audit_log_file')
        self.data_retention_days = config.getint('LEGAL_COMPLIANCE', 'data_retention_days', fallback=1095)
        self.audit_trail = config.getboolean('LEGAL_COMPLIANCE', 'audit_trail', fallback=True)
        self.chain_of_custody = config.getboolean('LEGAL_COMPLIANCE', 'chain_of_custody', fallback=True)
        
        # Initialize audit logging
        self._setup_audit_logging()
        
        # Thread lock for thread-safe logging
        self._lock = threading.Lock()
        
    def _setup_audit_logging(self):
        """Setup audit logging configuration."""
        try:
            # Create audit log directory
            audit_log_dir = os.path.dirname(self.audit_log_file)
            os.makedirs(audit_log_dir, exist_ok=True)
            
            # Setup file handler for audit logs
            audit_handler = logging.FileHandler(self.audit_log_file)
            audit_handler.setLevel(logging.INFO)
            
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            audit_handler.setFormatter(formatter)
            
            # Add handler to logger
            self.logger.addHandler(audit_handler)
            
            self.logger.info("Audit logging initialized successfully")
            
        except Exception as e:
            print(f"Failed to setup audit logging: {e}")
            raise
            
    def log_event(self, event_type: str, user_id: str, action: str, 
                  details: Dict[str, Any], severity: str = 'INFO',
                  ip_address: Optional[str] = None, session_id: Optional[str] = None):
        """
        Log an audit event.
        
        Args:
            event_type: Type of event (login, scan, data_access, etc.)
            user_id: User ID performing the action
            action: Description of the action
            details: Additional details about the event
            severity: Event severity (INFO, WARNING, ERROR, CRITICAL)
            ip_address: IP address of the user
            session_id: Session ID if applicable
        """
        try:
            with self._lock:
                # Create audit record
                audit_record = {
                    'timestamp': datetime.now().isoformat(),
                    'event_type': event_type,
                    'user_id': user_id,
                    'action': action,
                    'details': details,
                    'severity': severity,
                    'ip_address': ip_address,
                    'session_id': session_id,
                    'hash': self._generate_event_hash(event_type, user_id, action, details)
                }
                
                # Log to file
                self.logger.log(
                    getattr(logging, severity.upper()),
                    f"EVENT: {event_type} | USER: {user_id} | ACTION: {action} | DETAILS: {json.dumps(details)}"
                )
                
                # Store in database
                self.db_manager.add_audit_log(audit_record)
                
        except Exception as e:
            print(f"Failed to log audit event: {e}")
            
    def log_scan_activity(self, user_id: str, scan_type: str, target_range: str,
                          scan_parameters: Dict[str, Any], results_count: int,
                          ip_address: Optional[str] = None, session_id: Optional[str] = None):
        """
        Log scan activity.
        
        Args:
            user_id: User ID performing the scan
            scan_type: Type of scan (network, geographic, ISP, etc.)
            target_range: Target range being scanned
            scan_parameters: Parameters used for the scan
            results_count: Number of results found
            ip_address: IP address of the user
            session_id: Session ID if applicable
        """
        try:
            details = {
                'scan_type': scan_type,
                'target_range': target_range,
                'scan_parameters': scan_parameters,
                'results_count': results_count,
                'scan_id': self._generate_scan_id(user_id, scan_type, target_range)
            }
            
            self.log_event(
                event_type='scan_activity',
                user_id=user_id,
                action=f"Performed {scan_type} scan on {target_range}",
                details=details,
                severity='INFO',
                ip_address=ip_address,
                session_id=session_id
            )
            
        except Exception as e:
            print(f"Failed to log scan activity: {e}")
            
    def log_data_access(self, user_id: str, data_type: str, access_method: str,
                       record_count: int, ip_address: Optional[str] = None,
                       session_id: Optional[str] = None):
        """
        Log data access events.
        
        Args:
            user_id: User ID accessing data
            data_type: Type of data being accessed
            access_method: Method of access (view, export, search, etc.)
            record_count: Number of records accessed
            ip_address: IP address of the user
            session_id: Session ID if applicable
        """
        try:
            details = {
                'data_type': data_type,
                'access_method': access_method,
                'record_count': record_count,
                'access_id': self._generate_access_id(user_id, data_type, access_method)
            }
            
            self.log_event(
                event_type='data_access',
                user_id=user_id,
                action=f"Accessed {data_type} data via {access_method}",
                details=details,
                severity='INFO',
                ip_address=ip_address,
                session_id=session_id
            )
            
        except Exception as e:
            print(f"Failed to log data access: {e}")
            
    def log_security_event(self, user_id: str, event_type: str, description: str,
                          severity: str = 'WARNING', ip_address: Optional[str] = None,
                          session_id: Optional[str] = None):
        """
        Log security-related events.
        
        Args:
            user_id: User ID involved in the event
            event_type: Type of security event
            description: Description of the event
            severity: Event severity
            ip_address: IP address of the user
            session_id: Session ID if applicable
        """
        try:
            details = {
                'security_event_type': event_type,
                'description': description,
                'event_id': self._generate_security_event_id(user_id, event_type)
            }
            
            self.log_event(
                event_type='security_event',
                user_id=user_id,
                action=description,
                details=details,
                severity=severity,
                ip_address=ip_address,
                session_id=session_id
            )
            
        except Exception as e:
            print(f"Failed to log security event: {e}")
            
    def log_system_event(self, event_type: str, description: str, 
                        system_component: str, severity: str = 'INFO'):
        """
        Log system-level events.
        
        Args:
            event_type: Type of system event
            description: Description of the event
            system_component: Component involved
            severity: Event severity
        """
        try:
            details = {
                'system_event_type': event_type,
                'system_component': system_component,
                'description': description,
                'event_id': self._generate_system_event_id(event_type, system_component)
            }
            
            self.log_event(
                event_type='system_event',
                user_id='SYSTEM',
                action=description,
                details=details,
                severity=severity
            )
            
        except Exception as e:
            print(f"Failed to log system event: {e}")
            
    def log_compliance_event(self, event_type: str, compliance_requirement: str,
                           status: str, details: Dict[str, Any], user_id: str = 'SYSTEM'):
        """
        Log compliance-related events.
        
        Args:
            event_type: Type of compliance event
            compliance_requirement: Compliance requirement being checked
            status: Status of compliance (PASS, FAIL, WARNING)
            details: Additional compliance details
            user_id: User ID if applicable
        """
        try:
            details.update({
                'compliance_event_type': event_type,
                'compliance_requirement': compliance_requirement,
                'status': status,
                'event_id': self._generate_compliance_event_id(event_type, compliance_requirement)
            })
            
            severity = 'ERROR' if status == 'FAIL' else 'WARNING' if status == 'WARNING' else 'INFO'
            
            self.log_event(
                event_type='compliance_event',
                user_id=user_id,
                action=f"Compliance check: {compliance_requirement} - {status}",
                details=details,
                severity=severity
            )
            
        except Exception as e:
            print(f"Failed to log compliance event: {e}")
            
    def log_chain_of_custody(self, evidence_id: str, action: str, user_id: str,
                            location: str, description: str, 
                            evidence_hash: Optional[str] = None):
        """
        Log chain of custody events for evidence tracking.
        
        Args:
            evidence_id: Unique identifier for the evidence
            action: Action being performed (created, accessed, modified, transferred)
            user_id: User ID performing the action
            location: Location where the action occurred
            description: Description of the action
            evidence_hash: Hash of the evidence if applicable
        """
        try:
            details = {
                'evidence_id': evidence_id,
                'action': action,
                'location': location,
                'description': description,
                'evidence_hash': evidence_hash,
                'chain_id': self._generate_chain_id(evidence_id, action)
            }
            
            self.log_event(
                event_type='chain_of_custody',
                user_id=user_id,
                action=f"Chain of custody: {action} for evidence {evidence_id}",
                details=details,
                severity='INFO'
            )
            
        except Exception as e:
            print(f"Failed to log chain of custody event: {e}")
            
    def _generate_event_hash(self, event_type: str, user_id: str, 
                           action: str, details: Dict[str, Any]) -> str:
        """
        Generate a hash for an audit event.
        
        Args:
            event_type: Type of event
            user_id: User ID
            action: Action description
            details: Event details
            
        Returns:
            Hash of the event
        """
        try:
            event_string = f"{event_type}:{user_id}:{action}:{json.dumps(details, sort_keys=True)}"
            return hashlib.sha256(event_string.encode('utf-8')).hexdigest()
            
        except Exception as e:
            print(f"Failed to generate event hash: {e}")
            return ""
            
    def _generate_scan_id(self, user_id: str, scan_type: str, target_range: str) -> str:
        """Generate a unique scan ID."""
        try:
            scan_string = f"{user_id}:{scan_type}:{target_range}:{datetime.now().isoformat()}"
            return hashlib.sha256(scan_string.encode('utf-8')).hexdigest()[:16]
            
        except Exception as e:
            print(f"Failed to generate scan ID: {e}")
            return ""
            
    def _generate_access_id(self, user_id: str, data_type: str, access_method: str) -> str:
        """Generate a unique access ID."""
        try:
            access_string = f"{user_id}:{data_type}:{access_method}:{datetime.now().isoformat()}"
            return hashlib.sha256(access_string.encode('utf-8')).hexdigest()[:16]
            
        except Exception as e:
            print(f"Failed to generate access ID: {e}")
            return ""
            
    def _generate_security_event_id(self, user_id: str, event_type: str) -> str:
        """Generate a unique security event ID."""
        try:
            security_string = f"{user_id}:{event_type}:{datetime.now().isoformat()}"
            return hashlib.sha256(security_string.encode('utf-8')).hexdigest()[:16]
            
        except Exception as e:
            print(f"Failed to generate security event ID: {e}")
            return ""
            
    def _generate_system_event_id(self, event_type: str, system_component: str) -> str:
        """Generate a unique system event ID."""
        try:
            system_string = f"{event_type}:{system_component}:{datetime.now().isoformat()}"
            return hashlib.sha256(system_string.encode('utf-8')).hexdigest()[:16]
            
        except Exception as e:
            print(f"Failed to generate system event ID: {e}")
            return ""
            
    def _generate_compliance_event_id(self, event_type: str, compliance_requirement: str) -> str:
        """Generate a unique compliance event ID."""
        try:
            compliance_string = f"{event_type}:{compliance_requirement}:{datetime.now().isoformat()}"
            return hashlib.sha256(compliance_string.encode('utf-8')).hexdigest()[:16]
            
        except Exception as e:
            print(f"Failed to generate compliance event ID: {e}")
            return ""
            
    def _generate_chain_id(self, evidence_id: str, action: str) -> str:
        """Generate a unique chain of custody ID."""
        try:
            chain_string = f"{evidence_id}:{action}:{datetime.now().isoformat()}"
            return hashlib.sha256(chain_string.encode('utf-8')).hexdigest()[:16]
            
        except Exception as e:
            print(f"Failed to generate chain ID: {e}")
            return ""
            
    def get_audit_logs(self, start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None,
                      event_type: Optional[str] = None,
                      user_id: Optional[str] = None,
                      severity: Optional[str] = None,
                      limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Retrieve audit logs with filtering.
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            event_type: Event type filter
            user_id: User ID filter
            severity: Severity filter
            limit: Maximum number of records to return
            
        Returns:
            List of audit log records
        """
        try:
            return self.db_manager.get_audit_logs(
                start_date=start_date,
                end_date=end_date,
                event_type=event_type,
                user_id=user_id,
                severity=severity,
                limit=limit
            )
            
        except Exception as e:
            print(f"Failed to get audit logs: {e}")
            return []
            
    def export_audit_report(self, start_date: datetime, end_date: datetime,
                           output_format: str = 'json') -> str:
        """
        Export audit report for a date range.
        
        Args:
            start_date: Start date for report
            end_date: End date for report
            output_format: Output format (json, csv, pdf)
            
        Returns:
            Path to the exported report file
        """
        try:
            # Get audit logs for the date range
            audit_logs = self.get_audit_logs(start_date=start_date, end_date=end_date)
            
            # Generate report filename
            report_filename = f"audit_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.{output_format}"
            report_path = os.path.join(self.config.get('REPORTING', 'report_template_path'), report_filename)
            
            # Create report directory
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            
            if output_format == 'json':
                with open(report_path, 'w', encoding='utf-8') as f:
                    json.dump(audit_logs, f, indent=2, ensure_ascii=False)
            elif output_format == 'csv':
                import csv
                with open(report_path, 'w', newline='', encoding='utf-8') as f:
                    if audit_logs:
                        writer = csv.DictWriter(f, fieldnames=audit_logs[0].keys())
                        writer.writeheader()
                        writer.writerows(audit_logs)
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
                
            self.log_system_event(
                event_type='audit_report_exported',
                description=f"Audit report exported: {report_path}",
                system_component='audit_logger'
            )
            
            return report_path
            
        except Exception as e:
            print(f"Failed to export audit report: {e}")
            return ""
            
    def cleanup_old_audit_logs(self):
        """Clean up audit logs older than retention period."""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.data_retention_days)
            
            # Clean up database records
            self.db_manager.cleanup_old_audit_logs(cutoff_date)
            
            # Clean up file logs (keep last 30 days in file)
            file_cutoff_date = datetime.now() - timedelta(days=30)
            
            self.log_system_event(
                event_type='audit_logs_cleaned',
                description=f"Cleaned audit logs older than {self.data_retention_days} days",
                system_component='audit_logger'
            )
            
        except Exception as e:
            print(f"Failed to cleanup old audit logs: {e}")
            
    def get_audit_statistics(self, start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get audit statistics for a date range.
        
        Args:
            start_date: Start date for statistics
            end_date: End date for statistics
            
        Returns:
            Dictionary containing audit statistics
        """
        try:
            audit_logs = self.get_audit_logs(start_date=start_date, end_date=end_date)
            
            statistics = {
                'total_events': len(audit_logs),
                'events_by_type': {},
                'events_by_severity': {},
                'events_by_user': {},
                'most_active_hours': {},
                'security_events': 0,
                'compliance_events': 0,
                'scan_activities': 0,
                'data_access_events': 0
            }
            
            for log in audit_logs:
                # Count by event type
                event_type = log.get('event_type', 'unknown')
                statistics['events_by_type'][event_type] = statistics['events_by_type'].get(event_type, 0) + 1
                
                # Count by severity
                severity = log.get('severity', 'INFO')
                statistics['events_by_severity'][severity] = statistics['events_by_severity'].get(severity, 0) + 1
                
                # Count by user
                user_id = log.get('user_id', 'unknown')
                statistics['events_by_user'][user_id] = statistics['events_by_user'].get(user_id, 0) + 1
                
                # Count by hour
                try:
                    timestamp = datetime.fromisoformat(log.get('timestamp', ''))
                    hour = timestamp.hour
                    statistics['most_active_hours'][hour] = statistics['most_active_hours'].get(hour, 0) + 1
                except:
                    pass
                
                # Count specific event types
                if event_type == 'security_event':
                    statistics['security_events'] += 1
                elif event_type == 'compliance_event':
                    statistics['compliance_events'] += 1
                elif event_type == 'scan_activity':
                    statistics['scan_activities'] += 1
                elif event_type == 'data_access':
                    statistics['data_access_events'] += 1
                    
            return statistics
            
        except Exception as e:
            print(f"Failed to get audit statistics: {e}")
            return {}