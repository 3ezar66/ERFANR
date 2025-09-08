#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VPN Detector for CryptoMinerDetector
Handles VPN, proxy, and DNS changer detection.
"""

import logging
import requests
import socket
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import ipaddress

class VPNDetector:
    """
    Detector for VPN, proxy, and DNS changer services.
    Uses non-malicious methods to detect IP changers.
    """
    
    def __init__(self, config, database_manager, audit_logger):
        """
        Initialize the VPN detector.
        
        Args:
            config: Configuration manager instance
            database_manager: Database manager instance
            audit_logger: Audit logger instance
        """
        self.config = config
        self.db_manager = database_manager
        self.audit_logger = audit_logger
        self.logger = logging.getLogger(__name__)
        
        # API keys
        self.shodan_api_key = config.get('API_KEYS', 'shodan_api_key')
        self.ipinfo_token = config.get('API_KEYS', 'ipinfo_token')
        
        # VPN detection patterns
        self.vpn_patterns = self._load_vpn_patterns()
        self.proxy_patterns = self._load_proxy_patterns()
        self.dns_changer_patterns = self._load_dns_changer_patterns()
        
    def _load_vpn_patterns(self) -> Dict[str, Any]:
        """
        Load VPN detection patterns.
        
        Returns:
            Dictionary of VPN patterns
        """
        return {
            'vpn_services': [
                'nordvpn', 'expressvpn', 'cyberghost', 'surfshark', 'protonvpn',
                'windscribe', 'private internet access', 'tunnelbear', 'hotspot shield',
                'ipvanish', 'purevpn', 'vpn unlimited', 'hide.me', 'mullvad',
                'ivpn', 'perfect privacy', 'airvpn', 'ovpn', 'vpn.ac'
            ],
            'vpn_ports': [443, 1194, 500, 1723, 8080, 3128, 1080],
            'vpn_protocols': ['openvpn', 'ikev2', 'l2tp', 'pptp', 'sstp', 'wireguard'],
            'vpn_indicators': [
                'vpn', 'virtual private network', 'tunnel', 'proxy', 'anonymizer',
                'privacy', 'security', 'encryption', 'bypass', 'geo'
            ]
        }
        
    def _load_proxy_patterns(self) -> Dict[str, Any]:
        """
        Load proxy detection patterns.
        
        Returns:
            Dictionary of proxy patterns
        """
        return {
            'proxy_services': [
                'tor', 'socks', 'http proxy', 'https proxy', 'transparent proxy',
                'anonymous proxy', 'elite proxy', 'distorting proxy'
            ],
            'proxy_ports': [1080, 3128, 8080, 8118, 9050, 9150],
            'proxy_indicators': [
                'proxy', 'socks', 'tor', 'relay', 'gateway', 'forwarder'
            ]
        }
        
    def _load_dns_changer_patterns(self) -> Dict[str, Any]:
        """
        Load DNS changer detection patterns.
        
        Returns:
            Dictionary of DNS changer patterns
        """
        return {
            'dns_services': [
                'cloudflare', 'google dns', 'opendns', 'quad9', '1.1.1.1',
                '8.8.8.8', '8.8.4.4', '208.67.222.222', '208.67.220.220'
            ],
            'dns_ports': [53, 853],
            'dns_indicators': [
                'dns', 'domain name system', 'resolver', 'nameserver'
            ]
        }
        
    def detect_ip_changer(self, ip_address: str, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect if an IP address is using IP changing services.
        
        Args:
            ip_address: IP address to check
            device_data: Device scan data
            
        Returns:
            Detection results
        """
        try:
            detection_result = {
                'ip_address': ip_address,
                'detection_time': datetime.now().isoformat(),
                'vpn_detected': False,
                'proxy_detected': False,
                'dns_changer_detected': False,
                'suspicious_score': 0,
                'detection_methods': [],
                'original_ip': None,
                'service_provider': None,
                'confidence': 0,
                'legal_compliance': True
            }
            
            # Method 1: Check against known VPN/Proxy databases
            database_check = self._check_against_databases(ip_address)
            if database_check['found']:
                detection_result['detection_methods'].append('database_check')
                detection_result['suspicious_score'] += 40
                detection_result['service_provider'] = database_check['provider']
                detection_result['confidence'] += 30
                
                if database_check['type'] == 'vpn':
                    detection_result['vpn_detected'] = True
                elif database_check['type'] == 'proxy':
                    detection_result['proxy_detected'] = True
                    
            # Method 2: Analyze network behavior patterns
            behavior_check = self._analyze_network_behavior(device_data)
            if behavior_check['suspicious']:
                detection_result['detection_methods'].append('behavior_analysis')
                detection_result['suspicious_score'] += 25
                detection_result['confidence'] += 20
                
            # Method 3: Check for VPN/Proxy ports and services
            service_check = self._check_services_and_ports(device_data)
            if service_check['vpn_indicators']:
                detection_result['detection_methods'].append('service_analysis')
                detection_result['suspicious_score'] += 20
                detection_result['confidence'] += 15
                detection_result['vpn_detected'] = True
                
            if service_check['proxy_indicators']:
                detection_result['detection_methods'].append('service_analysis')
                detection_result['suspicious_score'] += 20
                detection_result['confidence'] += 15
                detection_result['proxy_detected'] = True
                
            # Method 4: DNS analysis
            dns_check = self._analyze_dns_behavior(device_data)
            if dns_check['dns_changer_detected']:
                detection_result['detection_methods'].append('dns_analysis')
                detection_result['suspicious_score'] += 15
                detection_result['confidence'] += 10
                detection_result['dns_changer_detected'] = True
                
            # Method 5: Metadata analysis
            metadata_check = self._analyze_metadata(ip_address)
            if metadata_check['suspicious']:
                detection_result['detection_methods'].append('metadata_analysis')
                detection_result['suspicious_score'] += 20
                detection_result['confidence'] += 15
                
            # Determine overall suspicious score
            detection_result['suspicious_score'] = min(detection_result['suspicious_score'], 100)
            
            # Log detection activity
            self.audit_logger.log_data_access(
                user_id="SYSTEM",
                data_type="vpn_detection",
                access_method="detect",
                record_count=1
            )
            
            return detection_result
            
        except Exception as e:
            self.logger.error(f"Failed to detect IP changer for {ip_address}: {e}")
            return {
                'ip_address': ip_address,
                'detection_time': datetime.now().isoformat(),
                'error': str(e),
                'legal_compliance': True
            }
            
    def _check_against_databases(self, ip_address: str) -> Dict[str, Any]:
        """
        Check IP against known VPN/Proxy databases.
        
        Args:
            ip_address: IP address to check
            
        Returns:
            Database check results
        """
        try:
            # Check using IPInfo API
            if self.ipinfo_token and self.ipinfo_token != 'YOUR_IPINFO_TOKEN':
                try:
                    response = requests.get(
                        f"https://ipinfo.io/{ip_address}/json?token={self.ipinfo_token}",
                        timeout=5
                    )
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Check for VPN/Proxy indicators in hostname
                        hostname = data.get('hostname', '').lower()
                        for vpn_service in self.vpn_patterns['vpn_services']:
                            if vpn_service in hostname:
                                return {
                                    'found': True,
                                    'type': 'vpn',
                                    'provider': vpn_service,
                                    'confidence': 80
                                }
                                
                        # Check for proxy indicators
                        for proxy_service in self.proxy_patterns['proxy_services']:
                            if proxy_service in hostname:
                                return {
                                    'found': True,
                                    'type': 'proxy',
                                    'provider': proxy_service,
                                    'confidence': 80
                                }
                                
                except Exception as e:
                    self.logger.warning(f"IPInfo API check failed: {e}")
                    
            # Check using Shodan API
            if self.shodan_api_key and self.shodan_api_key != 'YOUR_SHODAN_API_KEY':
                try:
                    response = requests.get(
                        f"https://api.shodan.io/shodan/host/{ip_address}?key={self.shodan_api_key}",
                        timeout=5
                    )
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Check for VPN/Proxy services in Shodan data
                        if 'data' in data:
                            for item in data['data']:
                                product = item.get('product', '').lower()
                                for vpn_service in self.vpn_patterns['vpn_services']:
                                    if vpn_service in product:
                                        return {
                                            'found': True,
                                            'type': 'vpn',
                                            'provider': vpn_service,
                                            'confidence': 85
                                        }
                                        
                except Exception as e:
                    self.logger.warning(f"Shodan API check failed: {e}")
                    
            return {
                'found': False,
                'type': None,
                'provider': None,
                'confidence': 0
            }
            
        except Exception as e:
            self.logger.error(f"Failed to check against databases: {e}")
            return {
                'found': False,
                'type': None,
                'provider': None,
                'confidence': 0
            }
            
    def _analyze_network_behavior(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze network behavior patterns for VPN/Proxy indicators.
        
        Args:
            device_data: Device scan data
            
        Returns:
            Behavior analysis results
        """
        try:
            suspicious = False
            indicators = []
            
            # Check for multiple connections to different countries
            connections = device_data.get('connections', [])
            countries = set()
            for conn in connections:
                country = conn.get('country', 'Unknown')
                if country != 'Unknown':
                    countries.add(country)
                    
            if len(countries) > 3:
                suspicious = True
                indicators.append(f"Multiple country connections: {', '.join(countries)}")
                
            # Check for unusual port patterns
            open_ports = device_data.get('open_ports', [])
            vpn_ports = [port for port in open_ports if port in self.vpn_patterns['vpn_ports']]
            if vpn_ports:
                suspicious = True
                indicators.append(f"VPN-related ports open: {vpn_ports}")
                
            # Check for high connection churn
            connection_count = len(connections)
            if connection_count > 50:
                suspicious = True
                indicators.append(f"High connection count: {connection_count}")
                
            return {
                'suspicious': suspicious,
                'indicators': indicators,
                'total_indicators': len(indicators)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze network behavior: {e}")
            return {
                'suspicious': False,
                'indicators': [],
                'total_indicators': 0
            }
            
    def _check_services_and_ports(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check for VPN/Proxy services and ports.
        
        Args:
            device_data: Device scan data
            
        Returns:
            Service check results
        """
        try:
            vpn_indicators = []
            proxy_indicators = []
            
            # Check services
            services = device_data.get('services', [])
            for service in services:
                service_lower = service.lower()
                
                # Check for VPN indicators
                for indicator in self.vpn_patterns['vpn_indicators']:
                    if indicator in service_lower:
                        vpn_indicators.append(service)
                        
                # Check for proxy indicators
                for indicator in self.proxy_patterns['proxy_indicators']:
                    if indicator in service_lower:
                        proxy_indicators.append(service)
                        
            # Check ports
            open_ports = device_data.get('open_ports', [])
            for port in open_ports:
                if port in self.vpn_patterns['vpn_ports']:
                    vpn_indicators.append(f"Port {port}")
                if port in self.proxy_patterns['proxy_ports']:
                    proxy_indicators.append(f"Port {port}")
                    
            return {
                'vpn_indicators': vpn_indicators,
                'proxy_indicators': proxy_indicators,
                'total_vpn_indicators': len(vpn_indicators),
                'total_proxy_indicators': len(proxy_indicators)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to check services and ports: {e}")
            return {
                'vpn_indicators': [],
                'proxy_indicators': [],
                'total_vpn_indicators': 0,
                'total_proxy_indicators': 0
            }
            
    def _analyze_dns_behavior(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze DNS behavior for DNS changer detection.
        
        Args:
            device_data: Device scan data
            
        Returns:
            DNS analysis results
        """
        try:
            dns_changer_detected = False
            indicators = []
            
            # Check for DNS-related services
            services = device_data.get('services', [])
            for service in services:
                service_lower = service.lower()
                for indicator in self.dns_changer_patterns['dns_indicators']:
                    if indicator in service_lower:
                        dns_changer_detected = True
                        indicators.append(service)
                        
            # Check for DNS ports
            open_ports = device_data.get('open_ports', [])
            dns_ports = [port for port in open_ports if port in self.dns_changer_patterns['dns_ports']]
            if dns_ports:
                dns_changer_detected = True
                indicators.append(f"DNS ports open: {dns_ports}")
                
            return {
                'dns_changer_detected': dns_changer_detected,
                'indicators': indicators,
                'total_indicators': len(indicators)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze DNS behavior: {e}")
            return {
                'dns_changer_detected': False,
                'indicators': [],
                'total_indicators': 0
            }
            
    def _analyze_metadata(self, ip_address: str) -> Dict[str, Any]:
        """
        Analyze IP metadata for suspicious patterns.
        
        Args:
            ip_address: IP address to analyze
            
        Returns:
            Metadata analysis results
        """
        try:
            suspicious = False
            indicators = []
            
            # Check if IP is in private ranges but appears to be public
            try:
                ip_obj = ipaddress.ip_address(ip_address)
                if ip_obj.is_private:
                    suspicious = True
                    indicators.append("Private IP range")
            except ValueError:
                pass
                
            # Check for datacenter IP ranges (common for VPNs)
            datacenter_ranges = [
                '8.8.8.0/24', '8.8.4.0/24',  # Google DNS
                '1.1.1.0/24', '1.0.0.0/24',  # Cloudflare
                '208.67.222.0/24', '208.67.220.0/24'  # OpenDNS
            ]
            
            for range_str in datacenter_ranges:
                try:
                    network = ipaddress.ip_network(range_str)
                    if ipaddress.ip_address(ip_address) in network:
                        suspicious = True
                        indicators.append(f"Datacenter IP range: {range_str}")
                        break
                except ValueError:
                    continue
                    
            return {
                'suspicious': suspicious,
                'indicators': indicators,
                'total_indicators': len(indicators)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze metadata: {e}")
            return {
                'suspicious': False,
                'indicators': [],
                'total_indicators': 0
            }
            
    def get_original_ip_estimation(self, ip_address: str, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate the original IP address (non-malicious methods only).
        
        Args:
            ip_address: Current IP address
            device_data: Device scan data
            
        Returns:
            Original IP estimation results
        """
        try:
            estimation_result = {
                'current_ip': ip_address,
                'original_ip_estimated': False,
                'estimated_original_ip': None,
                'estimation_method': None,
                'confidence': 0,
                'legal_compliance': True,
                'notes': []
            }
            
            # Method 1: Check for X-Forwarded-For headers (if available)
            if 'headers' in device_data:
                headers = device_data['headers']
                x_forwarded_for = headers.get('X-Forwarded-For', '')
                if x_forwarded_for:
                    original_ip = x_forwarded_for.split(',')[0].strip()
                    if self._is_valid_ip(original_ip):
                        estimation_result['original_ip_estimated'] = True
                        estimation_result['estimated_original_ip'] = original_ip
                        estimation_result['estimation_method'] = 'X-Forwarded-For header'
                        estimation_result['confidence'] = 70
                        estimation_result['notes'].append('Original IP found in X-Forwarded-For header')
                        
            # Method 2: Check for Real-IP headers
            if 'headers' in device_data:
                headers = device_data['headers']
                real_ip = headers.get('X-Real-IP', '')
                if real_ip and self._is_valid_ip(real_ip):
                    estimation_result['original_ip_estimated'] = True
                    estimation_result['estimated_original_ip'] = real_ip
                    estimation_result['estimation_method'] = 'X-Real-IP header'
                    estimation_result['confidence'] = 75
                    estimation_result['notes'].append('Original IP found in X-Real-IP header')
                    
            # Method 3: Analyze connection patterns
            connections = device_data.get('connections', [])
            if connections:
                # Look for connections that might indicate the original network
                local_connections = [conn for conn in connections 
                                    if conn.get('destination_ip', '').startswith('192.168.') or
                                       conn.get('destination_ip', '').startswith('10.')]
                
                if local_connections:
                    estimation_result['notes'].append('Local network connections detected')
                    estimation_result['confidence'] += 10
                    
            # Method 4: Check for ISP consistency
            isp_info = device_data.get('isp', '')
            if isp_info:
                # This would require additional ISP database lookup
                estimation_result['notes'].append(f'ISP information available: {isp_info}')
                
            return estimation_result
            
        except Exception as e:
            self.logger.error(f"Failed to estimate original IP: {e}")
            return {
                'current_ip': ip_address,
                'original_ip_estimated': False,
                'error': str(e),
                'legal_compliance': True
            }
            
    def _is_valid_ip(self, ip_string: str) -> bool:
        """
        Check if a string is a valid IP address.
        
        Args:
            ip_string: String to check
            
        Returns:
            True if valid IP, False otherwise
        """
        try:
            ipaddress.ip_address(ip_string)
            return True
        except ValueError:
            return False
            
    def get_vpn_detection_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about VPN/Proxy detection.
        
        Returns:
            VPN detection statistics
        """
        try:
            # Get all scan results from database
            all_results = self.db_manager.get_all_scan_results()
            
            # Analyze each result
            total_devices = len(all_results)
            vpn_detected = 0
            proxy_detected = 0
            dns_changer_detected = 0
            suspicious_scores = []
            
            for result in all_results:
                if result.get('vpn_detected', False):
                    vpn_detected += 1
                if result.get('proxy_detected', False):
                    proxy_detected += 1
                if result.get('dns_changer_detected', False):
                    dns_changer_detected += 1
                    
                suspicious_score = result.get('suspicious_score', 0)
                suspicious_scores.append(suspicious_score)
                
            # Calculate averages
            avg_suspicious_score = sum(suspicious_scores) / len(suspicious_scores) if suspicious_scores else 0
            
            return {
                'total_devices': total_devices,
                'vpn_detected': vpn_detected,
                'proxy_detected': proxy_detected,
                'dns_changer_detected': dns_changer_detected,
                'vpn_percentage': (vpn_detected / total_devices * 100) if total_devices > 0 else 0,
                'proxy_percentage': (proxy_detected / total_devices * 100) if total_devices > 0 else 0,
                'dns_changer_percentage': (dns_changer_detected / total_devices * 100) if total_devices > 0 else 0,
                'average_suspicious_score': avg_suspicious_score,
                'high_suspicious_devices': len([s for s in suspicious_scores if s > 80]),
                'medium_suspicious_devices': len([s for s in suspicious_scores if 50 <= s <= 80]),
                'low_suspicious_devices': len([s for s in suspicious_scores if s < 50])
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get VPN detection statistics: {e}")
            return {}
            
    def export_vpn_detection_results(self, output_format: str = 'json') -> str:
        """
        Export VPN detection results.
        
        Args:
            output_format: Output format (json, csv)
            
        Returns:
            Path to exported file
        """
        try:
            # Get all scan results with VPN detection
            all_results = self.db_manager.get_all_scan_results()
            vpn_results = [r for r in all_results if r.get('vpn_detected') or r.get('proxy_detected')]
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"vpn_detection_results_{timestamp}.{output_format}"
            
            # Export path
            export_path = f"D:/CryptoMinerDetector/data/scan_results/{filename}"
            
            # Create directory if not exists
            import os
            os.makedirs(os.path.dirname(export_path), exist_ok=True)
            
            # Export based on format
            if output_format == 'json':
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(vpn_results, f, indent=2, ensure_ascii=False)
            elif output_format == 'csv':
                import csv
                with open(export_path, 'w', newline='', encoding='utf-8') as f:
                    if vpn_results:
                        writer = csv.DictWriter(f, fieldnames=vpn_results[0].keys())
                        writer.writeheader()
                        writer.writerows(vpn_results)
                        
            self.logger.info(f"VPN detection results exported to: {export_path}")
            return export_path
            
        except Exception as e:
            self.logger.error(f"Failed to export VPN detection results: {e}")
            raise