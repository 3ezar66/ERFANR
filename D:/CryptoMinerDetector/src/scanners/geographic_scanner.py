#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Geographic Scanner for CryptoMinerDetector
Handles geographic-based scanning operations.
"""

import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import ipaddress

class GeographicScanner:
    """
    Geographic scanner for targeting specific geographic areas.
    Handles province and city-based scanning operations.
    """
    
    def __init__(self, config, database_manager, network_scanner, 
                 geographic_data_manager, isp_data_manager, audit_logger):
        """
        Initialize the geographic scanner.
        
        Args:
            config: Configuration manager instance
            database_manager: Database manager instance
            network_scanner: Network scanner instance
            geographic_data_manager: Geographic data manager instance
            isp_data_manager: ISP data manager instance
            audit_logger: Audit logger instance
        """
        self.config = config
        self.db_manager = database_manager
        self.network_scanner = network_scanner
        self.geographic_data_manager = geographic_data_manager
        self.isp_data_manager = isp_data_manager
        self.audit_logger = audit_logger
        self.logger = logging.getLogger(__name__)
        
        # Scanner settings
        self.max_concurrent_scans = config.getint('NETWORK_SCANNING', 'max_concurrent_scans', fallback=10)
        self.rate_limit_per_second = config.getint('NETWORK_SCANNING', 'rate_limit_per_second', fallback=100)
        
        # Scan state
        self.current_scan = None
        self.scan_results = []
        
    def scan_province(self, province_name: str, cities: Optional[List[str]] = None,
                     scan_type: str = "comprehensive", user_id: str = "SYSTEM") -> Dict[str, Any]:
        """
        Scan a specific province for cryptocurrency miners.
        
        Args:
            province_name: Name of the province to scan
            cities: List of cities to scan (if None, scans all cities)
            scan_type: Type of scan to perform
            user_id: User ID performing the scan
            
        Returns:
            Scan results dictionary
        """
        try:
            self.logger.info(f"Starting geographic scan for province: {province_name}")
            
            # Get province data
            province = self.geographic_data_manager.get_province_by_name(province_name)
            if not province:
                raise ValueError(f"Province not found: {province_name}")
                
            # Get cities for the province
            if cities:
                target_cities = cities
            else:
                all_cities = self.geographic_data_manager.get_cities_by_province(province['code'])
                target_cities = [city['name'] for city in all_cities]
                
            # Get ISP coverage for the province
            isp_coverage = self.isp_data_manager.get_isp_coverage_by_province(province['code'])
            
            # Collect IP ranges for scanning
            ip_ranges = []
            for isp in isp_coverage:
                isp_ranges = self.isp_data_manager.get_ip_ranges_by_isp(isp['code'])
                ip_ranges.extend(isp_ranges)
                
            # Remove duplicates and validate ranges
            unique_ranges = list(set([r['range'] for r in ip_ranges]))
            valid_ranges = []
            
            for ip_range in unique_ranges:
                try:
                    ipaddress.ip_network(ip_range, strict=False)
                    valid_ranges.append(ip_range)
                except ValueError:
                    self.logger.warning(f"Invalid IP range: {ip_range}")
                    
            # Log scan start
            self.audit_logger.log_scan_activity(
                user_id=user_id,
                scan_type="geographic",
                target_range=f"{province_name}: {', '.join(target_cities)}",
                scan_parameters={
                    'province': province_name,
                    'cities': target_cities,
                    'ip_ranges': valid_ranges,
                    'scan_type': scan_type
                },
                results_count=0
            )
            
            # Perform scanning
            scan_results = self._perform_geographic_scan(
                province, target_cities, valid_ranges, scan_type
            )
            
            # Store results in database
            for result in scan_results:
                self.db_manager.add_scan_result(result)
                
            # Log scan completion
            self.audit_logger.log_scan_activity(
                user_id=user_id,
                scan_type="geographic_completed",
                target_range=f"{province_name}: {', '.join(target_cities)}",
                scan_parameters={
                    'province': province_name,
                    'cities': target_cities,
                    'ip_ranges': valid_ranges,
                    'scan_type': scan_type
                },
                results_count=len(scan_results)
            )
            
            return {
                'province': province_name,
                'cities': target_cities,
                'ip_ranges_scanned': valid_ranges,
                'scan_type': scan_type,
                'results': scan_results,
                'total_devices': len(scan_results),
                'miners_detected': sum(1 for r in scan_results if r.get('miner_type')),
                'vpn_detected': sum(1 for r in scan_results if r.get('vpn_detected')),
                'scan_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to scan province {province_name}: {e}")
            raise
            
    def scan_city(self, province_name: str, city_name: str,
                  scan_type: str = "comprehensive", user_id: str = "SYSTEM") -> Dict[str, Any]:
        """
        Scan a specific city for cryptocurrency miners.
        
        Args:
            province_name: Name of the province
            city_name: Name of the city to scan
            scan_type: Type of scan to perform
            user_id: User ID performing the scan
            
        Returns:
            Scan results dictionary
        """
        try:
            self.logger.info(f"Starting city scan: {city_name}, {province_name}")
            
            # Get province and city data
            province = self.geographic_data_manager.get_province_by_name(province_name)
            if not province:
                raise ValueError(f"Province not found: {province_name}")
                
            city = self.geographic_data_manager.get_city_by_name(city_name, province['code'])
            if not city:
                raise ValueError(f"City not found: {city_name} in {province_name}")
                
            # Get ISP coverage for the city
            isp_coverage = self.isp_data_manager.get_isp_coverage_by_province(province['code'])
            
            # Filter IP ranges by city (if city-specific data available)
            ip_ranges = []
            for isp in isp_coverage:
                isp_ranges = self.isp_data_manager.get_ip_ranges_by_isp(isp['code'])
                # Filter by city if possible
                city_ranges = [r for r in isp_ranges if r.get('city') == city_name]
                if city_ranges:
                    ip_ranges.extend(city_ranges)
                else:
                    # Use all ranges for the ISP if city-specific data not available
                    ip_ranges.extend(isp_ranges)
                    
            # Remove duplicates and validate ranges
            unique_ranges = list(set([r['range'] for r in ip_ranges]))
            valid_ranges = []
            
            for ip_range in unique_ranges:
                try:
                    ipaddress.ip_network(ip_range, strict=False)
                    valid_ranges.append(ip_range)
                except ValueError:
                    self.logger.warning(f"Invalid IP range: {ip_range}")
                    
            # Log scan start
            self.audit_logger.log_scan_activity(
                user_id=user_id,
                scan_type="city_scan",
                target_range=f"{city_name}, {province_name}",
                scan_parameters={
                    'province': province_name,
                    'city': city_name,
                    'ip_ranges': valid_ranges,
                    'scan_type': scan_type
                },
                results_count=0
            )
            
            # Perform scanning
            scan_results = self._perform_city_scan(
                province, city, valid_ranges, scan_type
            )
            
            # Store results in database
            for result in scan_results:
                self.db_manager.add_scan_result(result)
                
            # Log scan completion
            self.audit_logger.log_scan_activity(
                user_id=user_id,
                scan_type="city_scan_completed",
                target_range=f"{city_name}, {province_name}",
                scan_parameters={
                    'province': province_name,
                    'city': city_name,
                    'ip_ranges': valid_ranges,
                    'scan_type': scan_type
                },
                results_count=len(scan_results)
            )
            
            return {
                'province': province_name,
                'city': city_name,
                'ip_ranges_scanned': valid_ranges,
                'scan_type': scan_type,
                'results': scan_results,
                'total_devices': len(scan_results),
                'miners_detected': sum(1 for r in scan_results if r.get('miner_type')),
                'vpn_detected': sum(1 for r in scan_results if r.get('vpn_detected')),
                'scan_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to scan city {city_name}: {e}")
            raise
            
    def _perform_geographic_scan(self, province: Dict[str, Any], cities: List[str],
                                ip_ranges: List[str], scan_type: str) -> List[Dict[str, Any]]:
        """
        Perform the actual geographic scanning.
        
        Args:
            province: Province data
            cities: List of cities to scan
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
                    executor.submit(self._scan_ip_range, ip_range, scan_type, province, cities): ip_range
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
            self.logger.error(f"Failed to perform geographic scan: {e}")
            raise
            
    def _perform_city_scan(self, province: Dict[str, Any], city: Dict[str, Any],
                          ip_ranges: List[str], scan_type: str) -> List[Dict[str, Any]]:
        """
        Perform city-specific scanning.
        
        Args:
            province: Province data
            city: City data
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
                    executor.submit(self._scan_ip_range, ip_range, scan_type, province, [city['name']]): ip_range
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
            self.logger.error(f"Failed to perform city scan: {e}")
            raise
            
    def _scan_ip_range(self, ip_range: str, scan_type: str, province: Dict[str, Any],
                      cities: List[str]) -> List[Dict[str, Any]]:
        """
        Scan a specific IP range.
        
        Args:
            ip_range: IP range to scan
            scan_type: Type of scan to perform
            province: Province data
            cities: List of cities
            
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
            
            # Add geographic information to results
            for result in results:
                result.update({
                    'province': province['name'],
                    'province_code': province['code'],
                    'cities': cities,
                    'ip_range': ip_range,
                    'scan_type': scan_type,
                    'scan_time': datetime.now().isoformat()
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
            
    def get_scan_statistics(self, province_name: Optional[str] = None,
                          city_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics for geographic scans.
        
        Args:
            province_name: Optional province filter
            city_name: Optional city filter
            
        Returns:
            Statistics dictionary
        """
        try:
            # Get scan results from database
            if province_name and city_name:
                results = self.db_manager.get_scan_results_by_location(province_name, city_name)
            elif province_name:
                results = self.db_manager.get_scan_results_by_province(province_name)
            else:
                results = self.db_manager.get_all_scan_results()
                
            # Calculate statistics
            total_devices = len(results)
            miners_detected = sum(1 for r in results if r.get('miner_type'))
            vpn_detected = sum(1 for r in results if r.get('vpn_detected'))
            high_confidence = sum(1 for r in results if r.get('confidence', 0) > 80)
            
            # Group by province
            by_province = {}
            for result in results:
                province = result.get('province', 'Unknown')
                if province not in by_province:
                    by_province[province] = 0
                by_province[province] += 1
                
            # Group by ISP
            by_isp = {}
            for result in results:
                isp = result.get('isp', 'Unknown')
                if isp not in by_isp:
                    by_isp[isp] = 0
                by_isp[isp] += 1
                
            return {
                'total_devices': total_devices,
                'miners_detected': miners_detected,
                'vpn_detected': vpn_detected,
                'high_confidence': high_confidence,
                'by_province': by_province,
                'by_isp': by_isp,
                'miner_percentage': (miners_detected / total_devices * 100) if total_devices > 0 else 0,
                'vpn_percentage': (vpn_detected / total_devices * 100) if total_devices > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get scan statistics: {e}")
            return {}
            
    def export_geographic_results(self, province_name: Optional[str] = None,
                                 city_name: Optional[str] = None,
                                 output_format: str = 'json') -> str:
        """
        Export geographic scan results.
        
        Args:
            province_name: Optional province filter
            city_name: Optional city filter
            output_format: Output format (json, csv)
            
        Returns:
            Path to exported file
        """
        try:
            # Get scan results
            if province_name and city_name:
                results = self.db_manager.get_scan_results_by_location(province_name, city_name)
            elif province_name:
                results = self.db_manager.get_scan_results_by_province(province_name)
            else:
                results = self.db_manager.get_all_scan_results()
                
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if province_name and city_name:
                filename = f"geographic_scan_{province_name}_{city_name}_{timestamp}.{output_format}"
            elif province_name:
                filename = f"geographic_scan_{province_name}_{timestamp}.{output_format}"
            else:
                filename = f"geographic_scan_all_{timestamp}.{output_format}"
                
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
                        
            self.logger.info(f"Geographic results exported to: {export_path}")
            return export_path
            
        except Exception as e:
            self.logger.error(f"Failed to export geographic results: {e}")
            raise