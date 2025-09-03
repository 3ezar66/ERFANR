#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISP Scanner for CryptoMinerDetector
Handles ISP-based scanning operations.
"""

import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import ipaddress

class ISPScanner:
    """
    ISP scanner for targeting specific Internet Service Providers.
    Handles ISP-based scanning operations and IP range management.
    """
    
    def __init__(self, config, database_manager, network_scanner, 
                 isp_data_manager, audit_logger):
        """
        Initialize the ISP scanner.
        
        Args:
            config: Configuration manager instance
            database_manager: Database manager instance
            network_scanner: Network scanner instance
            isp_data_manager: ISP data manager instance
            audit_logger: Audit logger instance
        """
        self.config = config
        self.db_manager = database_manager
        self.network_scanner = network_scanner
        self.isp_data_manager = isp_data_manager
        self.audit_logger = audit_logger
        self.logger = logging.getLogger(__name__)
        
        # Scanner settings
        self.max_concurrent_scans = config.getint('NETWORK_SCANNING', 'max_concurrent_scans', fallback=10)
        self.rate_limit_per_second = config.getint('NETWORK_SCANNING', 'rate_limit_per_second', fallback=100)
        
        # Scan state
        self.current_scan = None
        self.scan_results = []
        
    def scan_isp(self, isp_name: str, ip_ranges: Optional[List[str]] = None,
                 scan_type: str = "comprehensive", user_id: str = "SYSTEM") -> Dict[str, Any]:
        """
        Scan a specific ISP for cryptocurrency miners.
        
        Args:
            isp_name: Name of the ISP to scan
            ip_ranges: List of IP ranges to scan (if None, scans all ranges for the ISP)
            scan_type: Type of scan to perform
            user_id: User ID performing the scan
            
        Returns:
            Scan results dictionary
        """
        try:
            self.logger.info(f"Starting ISP scan for: {isp_name}")
            
            # Get ISP data
            isp = self.isp_data_manager.get_isp_by_name(isp_name)
            if not isp:
                raise ValueError(f"ISP not found: {isp_name}")
                
            # Get IP ranges for the ISP
            if ip_ranges:
                target_ranges = ip_ranges
            else:
                all_ranges = self.isp_data_manager.get_ip_ranges_by_isp(isp['code'])
                target_ranges = [r['range'] for r in all_ranges]
                
            # Validate IP ranges
            valid_ranges = []
            for ip_range in target_ranges:
                try:
                    ipaddress.ip_network(ip_range, strict=False)
                    valid_ranges.append(ip_range)
                except ValueError:
                    self.logger.warning(f"Invalid IP range: {ip_range}")
                    
            # Log scan start
            self.audit_logger.log_scan_activity(
                user_id=user_id,
                scan_type="isp_scan",
                target_range=f"{isp_name}: {len(valid_ranges)} ranges",
                scan_parameters={
                    'isp': isp_name,
                    'isp_code': isp['code'],
                    'ip_ranges': valid_ranges,
                    'scan_type': scan_type
                },
                results_count=0
            )
            
            # Perform scanning
            scan_results = self._perform_isp_scan(
                isp, valid_ranges, scan_type
            )
            
            # Store results in database
            for result in scan_results:
                self.db_manager.add_scan_result(result)
                
            # Log scan completion
            self.audit_logger.log_scan_activity(
                user_id=user_id,
                scan_type="isp_scan_completed",
                target_range=f"{isp_name}: {len(valid_ranges)} ranges",
                scan_parameters={
                    'isp': isp_name,
                    'isp_code': isp['code'],
                    'ip_ranges': valid_ranges,
                    'scan_type': scan_type
                },
                results_count=len(scan_results)
            )
            
            return {
                'isp': isp_name,
                'isp_code': isp['code'],
                'ip_ranges_scanned': valid_ranges,
                'scan_type': scan_type,
                'results': scan_results,
                'total_devices': len(scan_results),
                'miners_detected': sum(1 for r in scan_results if r.get('miner_type')),
                'vpn_detected': sum(1 for r in scan_results if r.get('vpn_detected')),
                'scan_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to scan ISP {isp_name}: {e}")
            raise
            
    def scan_asn(self, asn_number: str, scan_type: str = "comprehensive",
                 user_id: str = "SYSTEM") -> Dict[str, Any]:
        """
        Scan a specific ASN for cryptocurrency miners.
        
        Args:
            asn_number: ASN number to scan
            scan_type: Type of scan to perform
            user_id: User ID performing the scan
            
        Returns:
            Scan results dictionary
        """
        try:
            self.logger.info(f"Starting ASN scan for: {asn_number}")
            
            # Get ASN data
            asn_data = self.isp_data_manager.get_asn_by_number(asn_number)
            if not asn_data:
                raise ValueError(f"ASN not found: {asn_number}")
                
            # Get IP ranges for the ASN
            ip_ranges = self.isp_data_manager.get_ip_ranges_by_asn(asn_number)
            target_ranges = [r['range'] for r in ip_ranges]
            
            # Validate IP ranges
            valid_ranges = []
            for ip_range in target_ranges:
                try:
                    ipaddress.ip_network(ip_range, strict=False)
                    valid_ranges.append(ip_range)
                except ValueError:
                    self.logger.warning(f"Invalid IP range: {ip_range}")
                    
            # Log scan start
            self.audit_logger.log_scan_activity(
                user_id=user_id,
                scan_type="asn_scan",
                target_range=f"ASN {asn_number}: {len(valid_ranges)} ranges",
                scan_parameters={
                    'asn': asn_number,
                    'ip_ranges': valid_ranges,
                    'scan_type': scan_type
                },
                results_count=0
            )
            
            # Perform scanning
            scan_results = self._perform_asn_scan(
                asn_data, valid_ranges, scan_type
            )
            
            # Store results in database
            for result in scan_results:
                self.db_manager.add_scan_result(result)
                
            # Log scan completion
            self.audit_logger.log_scan_activity(
                user_id=user_id,
                scan_type="asn_scan_completed",
                target_range=f"ASN {asn_number}: {len(valid_ranges)} ranges",
                scan_parameters={
                    'asn': asn_number,
                    'ip_ranges': valid_ranges,
                    'scan_type': scan_type
                },
                results_count=len(scan_results)
            )
            
            return {
                'asn': asn_number,
                'asn_name': asn_data.get('name', 'Unknown'),
                'ip_ranges_scanned': valid_ranges,
                'scan_type': scan_type,
                'results': scan_results,
                'total_devices': len(scan_results),
                'miners_detected': sum(1 for r in scan_results if r.get('miner_type')),
                'vpn_detected': sum(1 for r in scan_results if r.get('vpn_detected')),
                'scan_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to scan ASN {asn_number}: {e}")
            raise
            
    def scan_ip_ranges(self, ip_ranges: List[str], scan_type: str = "comprehensive",
                       user_id: str = "SYSTEM") -> Dict[str, Any]:
        """
        Scan specific IP ranges for cryptocurrency miners.
        
        Args:
            ip_ranges: List of IP ranges to scan
            scan_type: Type of scan to perform
            user_id: User ID performing the scan
            
        Returns:
            Scan results dictionary
        """
        try:
            self.logger.info(f"Starting IP ranges scan: {len(ip_ranges)} ranges")
            
            # Validate IP ranges
            valid_ranges = []
            for ip_range in ip_ranges:
                try:
                    ipaddress.ip_network(ip_range, strict=False)
                    valid_ranges.append(ip_range)
                except ValueError:
                    self.logger.warning(f"Invalid IP range: {ip_range}")
                    
            # Log scan start
            self.audit_logger.log_scan_activity(
                user_id=user_id,
                scan_type="ip_ranges_scan",
                target_range=f"{len(valid_ranges)} IP ranges",
                scan_parameters={
                    'ip_ranges': valid_ranges,
                    'scan_type': scan_type
                },
                results_count=0
            )
            
            # Perform scanning
            scan_results = self._perform_ip_ranges_scan(
                valid_ranges, scan_type
            )
            
            # Store results in database
            for result in scan_results:
                self.db_manager.add_scan_result(result)
                
            # Log scan completion
            self.audit_logger.log_scan_activity(
                user_id=user_id,
                scan_type="ip_ranges_scan_completed",
                target_range=f"{len(valid_ranges)} IP ranges",
                scan_parameters={
                    'ip_ranges': valid_ranges,
                    'scan_type': scan_type
                },
                results_count=len(scan_results)
            )
            
            return {
                'ip_ranges_scanned': valid_ranges,
                'scan_type': scan_type,
                'results': scan_results,
                'total_devices': len(scan_results),
                'miners_detected': sum(1 for r in scan_results if r.get('miner_type')),
                'vpn_detected': sum(1 for r in scan_results if r.get('vpn_detected')),
                'scan_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to scan IP ranges: {e}")
            raise
            
    def _perform_isp_scan(self, isp: Dict[str, Any], ip_ranges: List[str],
                          scan_type: str) -> List[Dict[str, Any]]:
        """
        Perform ISP-specific scanning.
        
        Args:
            isp: ISP data
            ip_ranges: List of IP ranges to scan
            scan_type: Type of scan to perform
            
        Returns:
            List of scan results
        """
        try:
            all_results = []
            
            # Use ThreadPoolExecutor for concurrent scanning
            with ThreadPoolExecutor(max_workers=self.max_concurrent_scans) as executor:
                # Submit scan tasks for each IP range
                future_to_range = {
                    executor.submit(self._scan_ip_range, ip_range, scan_type, isp): ip_range
                    for ip_range in ip_ranges
                }
                
                # Collect results
                for future in as_completed(future_to_range):
                    ip_range = future_to_range[future]
                    try:
                        results = future.result()
                        all_results.extend(results)
                        
                        # Rate limiting
                        time.sleep(1.0 / self.rate_limit_per_second)
                        
                    except Exception as e:
                        self.logger.error(f"Failed to scan IP range {ip_range}: {e}")
                        
            return all_results
            
        except Exception as e:
            self.logger.error(f"Failed to perform ISP scan: {e}")
            raise
            
    def _perform_asn_scan(self, asn_data: Dict[str, Any], ip_ranges: List[str],
                          scan_type: str) -> List[Dict[str, Any]]:
        """
        Perform ASN-specific scanning.
        
        Args:
            asn_data: ASN data
            ip_ranges: List of IP ranges to scan
            scan_type: Type of scan to perform
            
        Returns:
            List of scan results
        """
        try:
            all_results = []
            
            # Use ThreadPoolExecutor for concurrent scanning
            with ThreadPoolExecutor(max_workers=self.max_concurrent_scans) as executor:
                # Submit scan tasks for each IP range
                future_to_range = {
                    executor.submit(self._scan_ip_range, ip_range, scan_type, asn_data): ip_range
                    for ip_range in ip_ranges
                }
                
                # Collect results
                for future in as_completed(future_to_range):
                    ip_range = future_to_range[future]
                    try:
                        results = future.result()
                        all_results.extend(results)
                        
                        # Rate limiting
                        time.sleep(1.0 / self.rate_limit_per_second)
                        
                    except Exception as e:
                        self.logger.error(f"Failed to scan IP range {ip_range}: {e}")
                        
            return all_results
            
        except Exception as e:
            self.logger.error(f"Failed to perform ASN scan: {e}")
            raise
            
    def _perform_ip_ranges_scan(self, ip_ranges: List[str],
                                scan_type: str) -> List[Dict[str, Any]]:
        """
        Perform IP ranges scanning.
        
        Args:
            ip_ranges: List of IP ranges to scan
            scan_type: Type of scan to perform
            
        Returns:
            List of scan results
        """
        try:
            all_results = []
            
            # Use ThreadPoolExecutor for concurrent scanning
            with ThreadPoolExecutor(max_workers=self.max_concurrent_scans) as executor:
                # Submit scan tasks for each IP range
                future_to_range = {
                    executor.submit(self._scan_ip_range, ip_range, scan_type, None): ip_range
                    for ip_range in ip_ranges
                }
                
                # Collect results
                for future in as_completed(future_to_range):
                    ip_range = future_to_range[future]
                    try:
                        results = future.result()
                        all_results.extend(results)
                        
                        # Rate limiting
                        time.sleep(1.0 / self.rate_limit_per_second)
                        
                    except Exception as e:
                        self.logger.error(f"Failed to scan IP range {ip_range}: {e}")
                        
            return all_results
            
        except Exception as e:
            self.logger.error(f"Failed to perform IP ranges scan: {e}")
            raise
            
    def _scan_ip_range(self, ip_range: str, scan_type: str,
                      entity_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Scan a specific IP range.
        
        Args:
            ip_range: IP range to scan
            scan_type: Type of scan to perform
            entity_data: ISP or ASN data
            
        Returns:
            List of scan results for this IP range
        """
        try:
            # Use network scanner to scan the IP range
            results = self.network_scanner.scan_network_range(
                ip_range=ip_range,
                scan_type=scan_type,
                ports=self._get_mining_ports()
            )
            
            # Add entity information to results
            for result in results:
                result.update({
                    'ip_range': ip_range,
                    'scan_type': scan_type,
                    'scan_time': datetime.now().isoformat()
                })
                
                # Add ISP or ASN information
                if entity_data:
                    if 'isp' in entity_data:
                        result.update({
                            'isp': entity_data['name'],
                            'isp_code': entity_data['code'],
                            'asn': entity_data.get('asn', 'Unknown')
                        })
                    elif 'asn' in entity_data:
                        result.update({
                            'asn': entity_data['asn'],
                            'asn_name': entity_data.get('name', 'Unknown')
                        })
                        
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to scan IP range {ip_range}: {e}")
            return []
            
    def _get_mining_ports(self) -> List[int]:
        """
        Get list of ports commonly used for cryptocurrency mining.
        
        Returns:
            List of port numbers
        """
        try:
            ports_str = self.config.get('NETWORK_SCANNING', 'scan_ports')
            return [int(p.strip()) for p in ports_str.split(',')]
        except Exception as e:
            self.logger.error(f"Failed to get mining ports: {e}")
            # Default mining ports
            return [3333, 4028, 5555, 7777, 8332, 8333, 8555, 9332, 9333, 14444, 14433, 14455]
            
    def get_isp_scan_statistics(self, isp_name: Optional[str] = None,
                               asn_number: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics for ISP scans.
        
        Args:
            isp_name: Optional ISP filter
            asn_number: Optional ASN filter
            
        Returns:
            Statistics dictionary
        """
        try:
            # Get scan results from database
            if isp_name:
                results = self.db_manager.get_scan_results_by_isp(isp_name)
            elif asn_number:
                results = self.db_manager.get_scan_results_by_asn(asn_number)
            else:
                results = self.db_manager.get_all_scan_results()
                
            # Calculate statistics
            total_devices = len(results)
            miners_detected = sum(1 for r in results if r.get('miner_type'))
            vpn_detected = sum(1 for r in results if r.get('vpn_detected'))
            high_confidence = sum(1 for r in results if r.get('confidence', 0) > 80)
            
            # Group by ISP
            by_isp = {}
            for result in results:
                isp = result.get('isp', 'Unknown')
                if isp not in by_isp:
                    by_isp[isp] = 0
                by_isp[isp] += 1
                
            # Group by ASN
            by_asn = {}
            for result in results:
                asn = result.get('asn', 'Unknown')
                if asn not in by_asn:
                    by_asn[asn] = 0
                by_asn[asn] += 1
                
            # Group by IP range
            by_ip_range = {}
            for result in results:
                ip_range = result.get('ip_range', 'Unknown')
                if ip_range not in by_ip_range:
                    by_ip_range[ip_range] = 0
                by_ip_range[ip_range] += 1
                
            return {
                'total_devices': total_devices,
                'miners_detected': miners_detected,
                'vpn_detected': vpn_detected,
                'high_confidence': high_confidence,
                'by_isp': by_isp,
                'by_asn': by_asn,
                'by_ip_range': by_ip_range,
                'miner_percentage': (miners_detected / total_devices * 100) if total_devices > 0 else 0,
                'vpn_percentage': (vpn_detected / total_devices * 100) if total_devices > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get ISP scan statistics: {e}")
            return {}
            
    def export_isp_results(self, isp_name: Optional[str] = None,
                          asn_number: Optional[str] = None,
                          output_format: str = 'json') -> str:
        """
        Export ISP scan results.
        
        Args:
            isp_name: Optional ISP filter
            asn_number: Optional ASN filter
            output_format: Output format (json, csv)
            
        Returns:
            Path to exported file
        """
        try:
            # Get scan results
            if isp_name:
                results = self.db_manager.get_scan_results_by_isp(isp_name)
            elif asn_number:
                results = self.db_manager.get_scan_results_by_asn(asn_number)
            else:
                results = self.db_manager.get_all_scan_results()
                
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if isp_name:
                filename = f"isp_scan_{isp_name}_{timestamp}.{output_format}"
            elif asn_number:
                filename = f"asn_scan_{asn_number}_{timestamp}.{output_format}"
            else:
                filename = f"isp_scan_all_{timestamp}.{output_format}"
                
            # Export path
            export_path = f"D:/CryptoMinerDetector/data/scan_results/{filename}"
            
            # Create directory if not exists
            import os
            os.makedirs(os.path.dirname(export_path), exist_ok=True)
            
            # Export based on format
            if output_format == 'json':
                import json
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
            elif output_format == 'csv':
                import csv
                with open(export_path, 'w', newline='', encoding='utf-8') as f:
                    if results:
                        writer = csv.DictWriter(f, fieldnames=results[0].keys())
                        writer.writeheader()
                        writer.writerows(results)
                        
            self.logger.info(f"ISP results exported to: {export_path}")
            return export_path
            
        except Exception as e:
            self.logger.error(f"Failed to export ISP results: {e}")
            raise