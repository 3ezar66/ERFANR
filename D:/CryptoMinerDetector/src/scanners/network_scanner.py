#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Network Scanner for CryptoMinerDetector
Handles network scanning operations for detecting cryptocurrency miners.
"""

import socket
import threading
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import ipaddress
from scapy.all import ARP, Ether, srp
import nmap
import requests
from datetime import datetime

class NetworkScanner:
    """
    Network scanner for detecting cryptocurrency mining devices.
    Supports various scanning methods and protocols.
    """
    
    def __init__(self, config, db_manager):
        """
        Initialize the network scanner.
        
        Args:
            config: Configuration manager instance
            db_manager: Database manager instance
        """
        self.config = config
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        
        # Scanner configuration
        self.timeout = config.getint('NETWORK_SCANNING', 'default_timeout', fallback=3)
        self.max_concurrent = config.getint('NETWORK_SCANNING', 'max_concurrent_scans', fallback=10)
        self.rate_limit = config.getint('NETWORK_SCANNING', 'rate_limit_per_second', fallback=100)
        self.scan_ports = config.get_scan_ports()
        self.miner_protocols = config.get_miner_protocols()
        
        # Initialize nmap scanner
        self.nmap_scanner = nmap.PortScanner()
        
        # Rate limiting
        self.last_scan_time = 0
        self.scan_lock = threading.Lock()
        
    def scan_network_range(self, ip_range: str, scan_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Scan a network range for cryptocurrency miners.
        
        Args:
            ip_range: IP range to scan (CIDR notation)
            scan_type: Type of scan (quick, comprehensive, stealth)
            
        Returns:
            Dictionary containing scan results
        """
        try:
            self.logger.info(f"Starting {scan_type} scan of network range: {ip_range}")
            
            scan_id = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{ip_range.replace('/', '_')}"
            start_time = datetime.now()
            
            # Initialize scan result
            scan_result = {
                'scan_id': scan_id,
                'scan_type': scan_type,
                'target_range': ip_range,
                'start_time': start_time,
                'devices_found': 0,
                'miners_detected': 0,
                'devices': [],
                'scan_status': 'running'
            }
            
            # Add scan to database
            self.db_manager.add_scan_result(scan_result)
            
            # Perform different types of scans
            if scan_type == "quick":
                devices = self._quick_scan(ip_range)
            elif scan_type == "comprehensive":
                devices = self._comprehensive_scan(ip_range)
            elif scan_type == "stealth":
                devices = self._stealth_scan(ip_range)
            else:
                devices = self._comprehensive_scan(ip_range)
                
            # Analyze devices for mining activity
            miners = []
            for device in devices:
                mining_analysis = self._analyze_mining_activity(device)
                if mining_analysis['is_miner']:
                    miners.append(mining_analysis)
                    device.update(mining_analysis)
                    
            # Update scan result
            scan_result.update({
                'devices_found': len(devices),
                'miners_detected': len(miners),
                'devices': devices,
                'end_time': datetime.now(),
                'scan_status': 'completed'
            })
            
            # Save devices to database
            for device in devices:
                self.db_manager.add_device(device)
                
            # Update scan result in database
            self.db_manager.update_scan_result(scan_id, scan_result)
            
            self.logger.info(f"Scan completed: {len(devices)} devices found, {len(miners)} miners detected")
            
            return scan_result
            
        except Exception as e:
            self.logger.error(f"Failed to scan network range {ip_range}: {e}")
            scan_result.update({
                'scan_status': 'failed',
                'error': str(e),
                'end_time': datetime.now()
            })
            return scan_result
            
    def _quick_scan(self, ip_range: str) -> List[Dict[str, Any]]:
        """
        Perform a quick network scan using ARP.
        
        Args:
            ip_range: IP range to scan
            
        Returns:
            List of discovered devices
        """
        devices = []
        
        try:
            # ARP scan
            arp = ARP(pdst=ip_range)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether/arp
            
            result = srp(packet, timeout=self.timeout, verbose=0)[0]
            
            for sent, received in result:
                device = {
                    'ip_address': received.psrc,
                    'mac_address': received.hwsrc,
                    'hostname': self._get_hostname(received.psrc),
                    'open_ports': [],
                    'miner_ports': [],
                    'miner_protocols': [],
                    'vpn_detected': False,
                    'confidence_score': 0.0,
                    'scan_time': datetime.now()
                }
                
                # Quick port scan for common miner ports
                device['open_ports'] = self._quick_port_scan(received.psrc)
                device['miner_ports'] = [port for port in device['open_ports'] if port in self.scan_ports]
                
                devices.append(device)
                
        except Exception as e:
            self.logger.error(f"Quick scan failed: {e}")
            
        return devices
        
    def _comprehensive_scan(self, ip_range: str) -> List[Dict[str, Any]]:
        """
        Perform a comprehensive network scan.
        
        Args:
            ip_range: IP range to scan
            
        Returns:
            List of discovered devices
        """
        devices = []
        
        try:
            # First, get all hosts using ARP
            arp_devices = self._quick_scan(ip_range)
            
            # Then perform detailed scans on each device
            with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
                future_to_device = {
                    executor.submit(self._detailed_device_scan, device): device 
                    for device in arp_devices
                }
                
                for future in as_completed(future_to_device):
                    device = future_to_device[future]
                    try:
                        detailed_device = future.result()
                        if detailed_device:
                            devices.append(detailed_device)
                    except Exception as e:
                        self.logger.error(f"Detailed scan failed for {device['ip_address']}: {e}")
                        devices.append(device)
                        
        except Exception as e:
            self.logger.error(f"Comprehensive scan failed: {e}")
            
        return devices
        
    def _stealth_scan(self, ip_range: str) -> List[Dict[str, Any]]:
        """
        Perform a stealth network scan.
        
        Args:
            ip_range: IP range to scan
            
        Returns:
            List of discovered devices
        """
        devices = []
        
        try:
            # Use nmap for stealth scanning
            self.nmap_scanner.scan(hosts=ip_range, arguments='-sn -n')
            
            for host in self.nmap_scanner.all_hosts():
                if self.nmap_scanner[host].state() == 'up':
                    device = {
                        'ip_address': host,
                        'mac_address': self.nmap_scanner[host]['addresses'].get('mac', ''),
                        'hostname': self._get_hostname(host),
                        'open_ports': [],
                        'miner_ports': [],
                        'miner_protocols': [],
                        'vpn_detected': False,
                        'confidence_score': 0.0,
                        'scan_time': datetime.now()
                    }
                    
                    # Stealth port scan
                    device['open_ports'] = self._stealth_port_scan(host)
                    device['miner_ports'] = [port for port in device['open_ports'] if port in self.scan_ports]
                    
                    devices.append(device)
                    
        except Exception as e:
            self.logger.error(f"Stealth scan failed: {e}")
            
        return devices
        
    def _detailed_device_scan(self, device: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Perform detailed scan of a single device.
        
        Args:
            device: Device information
            
        Returns:
            Updated device information
        """
        try:
            ip = device['ip_address']
            
            # Rate limiting
            with self.scan_lock:
                current_time = time.time()
                time_since_last = current_time - self.last_scan_time
                if time_since_last < (1.0 / self.rate_limit):
                    time.sleep((1.0 / self.rate_limit) - time_since_last)
                self.last_scan_time = time.time()
                
            # Port scan
            device['open_ports'] = self._comprehensive_port_scan(ip)
            device['miner_ports'] = [port for port in device['open_ports'] if port in self.scan_ports]
            
            # Service detection
            device['services'] = self._detect_services(ip, device['open_ports'])
            
            # VPN detection
            device['vpn_detected'] = self._detect_vpn(ip)
            
            # ISP information
            isp_info = self._get_isp_info(ip)
            if isp_info:
                device.update(isp_info)
                
            return device
            
        except Exception as e:
            self.logger.error(f"Detailed device scan failed for {device['ip_address']}: {e}")
            return device
            
    def _quick_port_scan(self, ip: str) -> List[int]:
        """
        Quick port scan for common ports.
        
        Args:
            ip: IP address to scan
            
        Returns:
            List of open ports
        """
        open_ports = []
        
        try:
            for port in self.scan_ports:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                if result == 0:
                    open_ports.append(port)
                sock.close()
                
        except Exception as e:
            self.logger.error(f"Quick port scan failed for {ip}: {e}")
            
        return open_ports
        
    def _comprehensive_port_scan(self, ip: str) -> List[int]:
        """
        Comprehensive port scan.
        
        Args:
            ip: IP address to scan
            
        Returns:
            List of open ports
        """
        open_ports = []
        
        try:
            # Use nmap for comprehensive port scanning
            self.nmap_scanner.scan(hosts=ip, arguments='-sS -sU -p- --min-rate=1000')
            
            if ip in self.nmap_scanner.all_hosts():
                for proto in self.nmap_scanner[ip].all_protocols():
                    ports = self.nmap_scanner[ip][proto].keys()
                    open_ports.extend(ports)
                    
        except Exception as e:
            self.logger.error(f"Comprehensive port scan failed for {ip}: {e}")
            
        return open_ports
        
    def _stealth_port_scan(self, ip: str) -> List[int]:
        """
        Stealth port scan.
        
        Args:
            ip: IP address to scan
            
        Returns:
            List of open ports
        """
        open_ports = []
        
        try:
            # Use nmap for stealth scanning
            self.nmap_scanner.scan(hosts=ip, arguments='-sS -p- --min-rate=500')
            
            if ip in self.nmap_scanner.all_hosts():
                for proto in self.nmap_scanner[ip].all_protocols():
                    ports = self.nmap_scanner[ip][proto].keys()
                    open_ports.extend(ports)
                    
        except Exception as e:
            self.logger.error(f"Stealth port scan failed for {ip}: {e}")
            
        return open_ports
        
    def _get_hostname(self, ip: str) -> str:
        """
        Get hostname for an IP address.
        
        Args:
            ip: IP address
            
        Returns:
            Hostname or empty string
        """
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except Exception:
            return ""
            
    def _detect_services(self, ip: str, ports: List[int]) -> Dict[str, Any]:
        """
        Detect services running on ports.
        
        Args:
            ip: IP address
            ports: List of open ports
            
        Returns:
            Dictionary of detected services
        """
        services = {}
        
        try:
            for port in ports:
                service_name = self._identify_service(ip, port)
                if service_name:
                    services[port] = service_name
                    
        except Exception as e:
            self.logger.error(f"Service detection failed for {ip}: {e}")
            
        return services
        
    def _identify_service(self, ip: str, port: int) -> Optional[str]:
        """
        Identify service running on a port.
        
        Args:
            ip: IP address
            port: Port number
            
        Returns:
            Service name or None
        """
        try:
            # Common service mappings
            common_services = {
                22: "SSH",
                23: "Telnet",
                25: "SMTP",
                53: "DNS",
                80: "HTTP",
                443: "HTTPS",
                1433: "MSSQL",
                3306: "MySQL",
                5432: "PostgreSQL",
                27017: "MongoDB",
                6379: "Redis",
                8080: "HTTP-Alt",
                8443: "HTTPS-Alt",
                9000: "HTTP-Alt",
                9200: "Elasticsearch",
                9300: "Elasticsearch-Transport",
                11211: "Memcached",
                15672: "RabbitMQ-Management",
                5672: "AMQP",
                2181: "Zookeeper",
                9092: "Kafka",
                9042: "Cassandra",
                9160: "Cassandra-Thrift",
                7000: "Cassandra-Inter-Node",
                7001: "Cassandra-SSL",
                7199: "Cassandra-JMX",
                9160: "Cassandra-Thrift",
                9042: "Cassandra-CQL",
                9160: "Cassandra-Thrift",
                7000: "Cassandra-Inter-Node",
                7001: "Cassandra-SSL",
                7199: "Cassandra-JMX"
            }
            
            # Check if it's a common service
            if port in common_services:
                return common_services[port]
                
            # Try to get service name from nmap
            if ip in self.nmap_scanner.all_hosts():
                for proto in self.nmap_scanner[ip].all_protocols():
                    if port in self.nmap_scanner[ip][proto]:
                        service_info = self.nmap_scanner[ip][proto][port]
                        if 'name' in service_info:
                            return service_info['name']
                            
            return None
            
        except Exception as e:
            self.logger.error(f"Service identification failed for {ip}:{port}: {e}")
            return None
            
    def _detect_vpn(self, ip: str) -> bool:
        """
        Detect if an IP is using VPN.
        
        Args:
            ip: IP address to check
            
        Returns:
            True if VPN is detected, False otherwise
        """
        try:
            # This is a simplified VPN detection
            # In a real implementation, you would use more sophisticated methods
            
            # Check against known VPN IP ranges
            vpn_ranges = [
                "10.0.0.0/8",
                "172.16.0.0/12",
                "192.168.0.0/16"
            ]
            
            ip_obj = ipaddress.IPv4Address(ip)
            for vpn_range in vpn_ranges:
                network = ipaddress.IPv4Network(vpn_range, strict=False)
                if ip_obj in network:
                    return True
                    
            # Check against VPN detection APIs (if available)
            # vpn_api_key = self.config.get_api_key('vpn_detection')
            # if vpn_api_key:
            #     response = requests.get(f"https://api.vpndetection.com/{ip}?key={vpn_api_key}")
            #     if response.status_code == 200:
            #         data = response.json()
            #         return data.get('vpn', False)
                    
            return False
            
        except Exception as e:
            self.logger.error(f"VPN detection failed for {ip}: {e}")
            return False
            
    def _get_isp_info(self, ip: str) -> Optional[Dict[str, Any]]:
        """
        Get ISP information for an IP address.
        
        Args:
            ip: IP address
            
        Returns:
            ISP information dictionary or None
        """
        try:
            # Use ipinfo.io API
            ipinfo_token = self.config.get_api_key('ipinfo')
            if ipinfo_token:
                response = requests.get(f"https://ipinfo.io/{ip}/json?token={ipinfo_token}")
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'isp_name': data.get('org', ''),
                        'isp_asn': data.get('asn', ''),
                        'province': data.get('region', ''),
                        'city': data.get('city', ''),
                        'latitude': float(data.get('loc', '0,0').split(',')[0]),
                        'longitude': float(data.get('loc', '0,0').split(',')[1])
                    }
                    
            return None
            
        except Exception as e:
            self.logger.error(f"ISP info retrieval failed for {ip}: {e}")
            return None
            
    def _analyze_mining_activity(self, device: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze device for cryptocurrency mining activity.
        
        Args:
            device: Device information
            
        Returns:
            Mining analysis results
        """
        analysis = {
            'is_miner': False,
            'miner_type': None,
            'mining_pools': [],
            'confidence_score': 0.0,
            'mining_indicators': []
        }
        
        try:
            # Check for mining ports
            if device.get('miner_ports'):
                analysis['is_miner'] = True
                analysis['confidence_score'] += 0.3
                analysis['mining_indicators'].append('mining_ports_open')
                
            # Check for mining services
            services = device.get('services', {})
            mining_services = ['stratum', 'bitcoin', 'ethereum', 'mining', 'pool']
            
            for port, service in services.items():
                if any(mining_service in service.lower() for mining_service in mining_services):
                    analysis['is_miner'] = True
                    analysis['confidence_score'] += 0.4
                    analysis['mining_indicators'].append(f'mining_service_{service}')
                    
            # Check for known mining pool connections
            mining_pools = self._detect_mining_pools(device['ip_address'])
            if mining_pools:
                analysis['is_miner'] = True
                analysis['confidence_score'] += 0.5
                analysis['mining_pools'] = mining_pools
                analysis['mining_indicators'].append('mining_pool_connections')
                
            # Determine miner type based on ports and services
            if analysis['is_miner']:
                analysis['miner_type'] = self._determine_miner_type(device)
                
            # Cap confidence score at 1.0
            analysis['confidence_score'] = min(analysis['confidence_score'], 1.0)
            
        except Exception as e:
            self.logger.error(f"Mining activity analysis failed for {device['ip_address']}: {e}")
            
        return analysis
        
    def _detect_mining_pools(self, ip: str) -> List[str]:
        """
        Detect connections to known mining pools.
        
        Args:
            ip: IP address
            
        Returns:
            List of detected mining pools
        """
        # This is a simplified implementation
        # In a real implementation, you would monitor network traffic
        # and check for connections to known mining pool domains/IPs
        
        known_pools = [
            "stratum+tcp://pool.example.com",
            "stratum+tcp://mining.example.com",
            "stratum+tcp://pool.bitcoin.com",
            "stratum+tcp://pool.ethereum.com"
        ]
        
        # For now, return empty list
        # In real implementation, you would check actual connections
        return []
        
    def _determine_miner_type(self, device: Dict[str, Any]) -> str:
        """
        Determine the type of cryptocurrency miner.
        
        Args:
            device: Device information
            
        Returns:
            Miner type
        """
        try:
            ports = device.get('miner_ports', [])
            services = device.get('services', {})
            
            # Bitcoin mining
            if 8332 in ports or 8333 in ports:
                return "bitcoin"
                
            # Ethereum mining
            if 8545 in ports or 8546 in ports:
                return "ethereum"
                
            # General mining
            if any('stratum' in str(service).lower() for service in services.values()):
                return "stratum_miner"
                
            # Unknown mining
            if ports:
                return "unknown_miner"
                
            return "unknown"
            
        except Exception as e:
            self.logger.error(f"Miner type determination failed: {e}")
            return "unknown"