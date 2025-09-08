#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISP Data Manager for CryptoMinerDetector
Handles Iranian ISP information and IP range data.
"""

import json
import logging
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import ipaddress
from datetime import datetime

class ISPDataManager:
    """
    Manages ISP data for Iranian internet service providers.
    Provides data for ISP-based scanning and IP range management.
    """
    
    def __init__(self, config):
        """
        Initialize the ISP data manager.
        
        Args:
            config: Configuration manager instance
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.data_dir = Path("D:/CryptoMinerDetector/data/isp_ranges")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.isps_file = self.data_dir / "iran_isps.json"
        self.ip_ranges_file = self.data_dir / "iran_ip_ranges.json"
        self.asn_data_file = self.data_dir / "iran_asn_data.json"
        
        # Load or initialize data
        self._load_isp_data()
        
    def _load_isp_data(self):
        """Load or initialize ISP data."""
        try:
            # Load ISP data
            if not self.isps_file.exists():
                self._create_isps_data()
            else:
                self.logger.info("ISP data loaded from file")
                
            # Load IP ranges data
            if not self.ip_ranges_file.exists():
                self._create_ip_ranges_data()
            else:
                self.logger.info("IP ranges data loaded from file")
                
            # Load ASN data
            if not self.asn_data_file.exists():
                self._create_asn_data()
            else:
                self.logger.info("ASN data loaded from file")
                
        except Exception as e:
            self.logger.error(f"Failed to load ISP data: {e}")
            raise
            
    def _create_isps_data(self):
        """Create Iranian ISP data."""
        isps_data = {
            "isps": [
                {
                    "name": "شبکه ملی اطلاعات",
                    "name_en": "National Information Network",
                    "code": "NIN",
                    "asn": "AS58224",
                    "type": "government",
                    "coverage": "nationwide",
                    "contact_info": {
                        "phone": "+98-21-12345678",
                        "email": "info@nin.ir",
                        "website": "https://www.nin.ir"
                    },
                    "ip_ranges": [
                        "5.52.0.0/14",
                        "5.56.0.0/14",
                        "5.60.0.0/14"
                    ]
                },
                {
                    "name": "مخابرات ایران",
                    "name_en": "Iran Telecommunication Company",
                    "code": "TCI",
                    "asn": "AS12880",
                    "type": "government",
                    "coverage": "nationwide",
                    "contact_info": {
                        "phone": "+98-21-12345678",
                        "email": "info@tci.ir",
                        "website": "https://www.tci.ir"
                    },
                    "ip_ranges": [
                        "2.144.0.0/14",
                        "2.148.0.0/14",
                        "2.152.0.0/14",
                        "2.156.0.0/14",
                        "2.160.0.0/14",
                        "2.164.0.0/14",
                        "2.168.0.0/14",
                        "2.172.0.0/14",
                        "2.176.0.0/14",
                        "2.180.0.0/14",
                        "2.184.0.0/14",
                        "2.188.0.0/14",
                        "2.192.0.0/14",
                        "2.196.0.0/14",
                        "2.200.0.0/14",
                        "2.204.0.0/14",
                        "2.208.0.0/14",
                        "2.212.0.0/14",
                        "2.216.0.0/14",
                        "2.220.0.0/14",
                        "2.224.0.0/14",
                        "2.228.0.0/14",
                        "2.232.0.0/14",
                        "2.236.0.0/14",
                        "2.240.0.0/14",
                        "2.244.0.0/14",
                        "2.248.0.0/14",
                        "2.252.0.0/14"
                    ]
                },
                {
                    "name": "شبکه داده‌ای شاتل",
                    "name_en": "Shatel Data Network",
                    "code": "SHATEL",
                    "asn": "AS31549",
                    "type": "private",
                    "coverage": "major_cities",
                    "contact_info": {
                        "phone": "+98-21-12345678",
                        "email": "info@shatel.ir",
                        "website": "https://www.shatel.ir"
                    },
                    "ip_ranges": [
                        "37.156.0.0/16",
                        "37.157.0.0/16",
                        "37.158.0.0/16",
                        "37.159.0.0/16"
                    ]
                },
                {
                    "name": "پارس آنلاین",
                    "name_en": "Pars Online",
                    "code": "PARS",
                    "asn": "AS16322",
                    "type": "private",
                    "coverage": "major_cities",
                    "contact_info": {
                        "phone": "+98-21-12345678",
                        "email": "info@parsonline.ir",
                        "website": "https://www.parsonline.ir"
                    },
                    "ip_ranges": [
                        "78.38.0.0/16",
                        "78.39.0.0/16",
                        "78.40.0.0/16",
                        "78.41.0.0/16"
                    ]
                },
                {
                    "name": "آسیاتک",
                    "name_en": "Asiatech",
                    "code": "ASIATECH",
                    "asn": "AS43754",
                    "type": "private",
                    "coverage": "major_cities",
                    "contact_info": {
                        "phone": "+98-21-12345678",
                        "email": "info@asiatech.ir",
                        "website": "https://www.asiatech.ir"
                    },
                    "ip_ranges": [
                        "185.4.0.0/16",
                        "185.5.0.0/16",
                        "185.6.0.0/16",
                        "185.7.0.0/16"
                    ]
                },
                {
                    "name": "ایرانسل",
                    "name_en": "Irancell",
                    "code": "IRANCELL",
                    "asn": "AS44244",
                    "type": "mobile",
                    "coverage": "nationwide",
                    "contact_info": {
                        "phone": "+98-21-12345678",
                        "email": "info@irancell.ir",
                        "website": "https://www.irancell.ir"
                    },
                    "ip_ranges": [
                        "10.0.0.0/8",
                        "172.16.0.0/12",
                        "192.168.0.0/16"
                    ]
                },
                {
                    "name": "همراه اول",
                    "name_en": "MCCI",
                    "code": "MCCI",
                    "asn": "AS31549",
                    "type": "mobile",
                    "coverage": "nationwide",
                    "contact_info": {
                        "phone": "+98-21-12345678",
                        "email": "info@mci.ir",
                        "website": "https://www.mci.ir"
                    },
                    "ip_ranges": [
                        "10.0.0.0/8",
                        "172.16.0.0/12",
                        "192.168.0.0/16"
                    ]
                },
                {
                    "name": "رایتل",
                    "name_en": "RighTel",
                    "code": "RIGHTEL",
                    "asn": "AS43754",
                    "type": "mobile",
                    "coverage": "nationwide",
                    "contact_info": {
                        "phone": "+98-21-12345678",
                        "email": "info@rightel.ir",
                        "website": "https://www.rightel.ir"
                    },
                    "ip_ranges": [
                        "10.0.0.0/8",
                        "172.16.0.0/12",
                        "192.168.0.0/16"
                    ]
                }
            ]
        }
        
        with open(self.isps_file, 'w', encoding='utf-8') as f:
            json.dump(isps_data, f, ensure_ascii=False, indent=2)
            
        self.logger.info("Iranian ISP data created")
        
    def _create_ip_ranges_data(self):
        """Create IP ranges data."""
        ip_ranges_data = {
            "ip_ranges": [
                {
                    "range": "2.144.0.0/14",
                    "isp": "مخابرات ایران",
                    "isp_en": "Iran Telecommunication Company",
                    "asn": "AS12880",
                    "province": "تهران",
                    "city": "تهران",
                    "total_ips": 262144,
                    "allocated_ips": 200000,
                    "status": "active"
                },
                {
                    "range": "2.148.0.0/14",
                    "isp": "مخابرات ایران",
                    "isp_en": "Iran Telecommunication Company",
                    "asn": "AS12880",
                    "province": "اصفهان",
                    "city": "اصفهان",
                    "total_ips": 262144,
                    "allocated_ips": 180000,
                    "status": "active"
                },
                {
                    "range": "2.152.0.0/14",
                    "isp": "مخابرات ایران",
                    "isp_en": "Iran Telecommunication Company",
                    "asn": "AS12880",
                    "province": "خراسان رضوی",
                    "city": "مشهد",
                    "total_ips": 262144,
                    "allocated_ips": 220000,
                    "status": "active"
                },
                {
                    "range": "37.156.0.0/16",
                    "isp": "شبکه داده‌ای شاتل",
                    "isp_en": "Shatel Data Network",
                    "asn": "AS31549",
                    "province": "تهران",
                    "city": "تهران",
                    "total_ips": 65536,
                    "allocated_ips": 50000,
                    "status": "active"
                },
                {
                    "range": "78.38.0.0/16",
                    "isp": "پارس آنلاین",
                    "isp_en": "Pars Online",
                    "asn": "AS16322",
                    "province": "تهران",
                    "city": "تهران",
                    "total_ips": 65536,
                    "allocated_ips": 45000,
                    "status": "active"
                },
                {
                    "range": "185.4.0.0/16",
                    "isp": "آسیاتک",
                    "isp_en": "Asiatech",
                    "asn": "AS43754",
                    "province": "تهران",
                    "city": "تهران",
                    "total_ips": 65536,
                    "allocated_ips": 40000,
                    "status": "active"
                }
            ]
        }
        
        with open(self.ip_ranges_file, 'w', encoding='utf-8') as f:
            json.dump(ip_ranges_data, f, ensure_ascii=False, indent=2)
            
        self.logger.info("Iranian IP ranges data created")
        
    def _create_asn_data(self):
        """Create ASN data."""
        asn_data = {
            "asns": [
                {
                    "asn": "AS12880",
                    "name": "مخابرات ایران",
                    "name_en": "Iran Telecommunication Company",
                    "country": "IR",
                    "type": "ISP",
                    "ipv4_prefixes": 100,
                    "ipv6_prefixes": 50,
                    "description": "National telecommunications provider"
                },
                {
                    "asn": "AS31549",
                    "name": "شبکه داده‌ای شاتل",
                    "name_en": "Shatel Data Network",
                    "country": "IR",
                    "type": "ISP",
                    "ipv4_prefixes": 20,
                    "ipv6_prefixes": 10,
                    "description": "Private internet service provider"
                },
                {
                    "asn": "AS16322",
                    "name": "پارس آنلاین",
                    "name_en": "Pars Online",
                    "country": "IR",
                    "type": "ISP",
                    "ipv4_prefixes": 15,
                    "ipv6_prefixes": 8,
                    "description": "Private internet service provider"
                },
                {
                    "asn": "AS43754",
                    "name": "آسیاتک",
                    "name_en": "Asiatech",
                    "country": "IR",
                    "type": "ISP",
                    "ipv4_prefixes": 12,
                    "ipv6_prefixes": 6,
                    "description": "Private internet service provider"
                },
                {
                    "asn": "AS44244",
                    "name": "ایرانسل",
                    "name_en": "Irancell",
                    "country": "IR",
                    "type": "Mobile",
                    "ipv4_prefixes": 8,
                    "ipv6_prefixes": 4,
                    "description": "Mobile network operator"
                },
                {
                    "asn": "AS58224",
                    "name": "شبکه ملی اطلاعات",
                    "name_en": "National Information Network",
                    "country": "IR",
                    "type": "Government",
                    "ipv4_prefixes": 30,
                    "ipv6_prefixes": 15,
                    "description": "National information network"
                }
            ]
        }
        
        with open(self.asn_data_file, 'w', encoding='utf-8') as f:
            json.dump(asn_data, f, ensure_ascii=False, indent=2)
            
        self.logger.info("Iranian ASN data created")
        
    def get_isps(self) -> List[Dict[str, Any]]:
        """
        Get all Iranian ISPs.
        
        Returns:
            List of ISP dictionaries
        """
        try:
            with open(self.isps_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('isps', [])
        except Exception as e:
            self.logger.error(f"Failed to load ISPs: {e}")
            return []
            
    def get_isp_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Get ISP by code.
        
        Args:
            code: ISP code
            
        Returns:
            ISP dictionary or None if not found
        """
        isps = self.get_isps()
        for isp in isps:
            if isp['code'] == code:
                return isp
        return None
        
    def get_isp_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get ISP by name (Persian or English).
        
        Args:
            name: ISP name
            
        Returns:
            ISP dictionary or None if not found
        """
        isps = self.get_isps()
        for isp in isps:
            if (isp['name'] == name or 
                isp['name_en'] == name or
                isp['name_en'].lower() == name.lower()):
                return isp
        return None
        
    def get_isp_by_asn(self, asn: str) -> Optional[Dict[str, Any]]:
        """
        Get ISP by ASN.
        
        Args:
            asn: ASN number
            
        Returns:
            ISP dictionary or None if not found
        """
        isps = self.get_isps()
        for isp in isps:
            if isp['asn'] == asn:
                return isp
        return None
        
    def get_ip_ranges(self) -> List[Dict[str, Any]]:
        """
        Get all IP ranges.
        
        Returns:
            List of IP range dictionaries
        """
        try:
            with open(self.ip_ranges_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('ip_ranges', [])
        except Exception as e:
            self.logger.error(f"Failed to load IP ranges: {e}")
            return []
            
    def get_ip_ranges_by_isp(self, isp_name: str) -> List[Dict[str, Any]]:
        """
        Get IP ranges for a specific ISP.
        
        Args:
            isp_name: ISP name
            
        Returns:
            List of IP range dictionaries
        """
        ip_ranges = self.get_ip_ranges()
        return [ip_range for ip_range in ip_ranges if ip_range['isp'] == isp_name]
        
    def get_ip_ranges_by_province(self, province: str) -> List[Dict[str, Any]]:
        """
        Get IP ranges for a specific province.
        
        Args:
            province: Province name
            
        Returns:
            List of IP range dictionaries
        """
        ip_ranges = self.get_ip_ranges()
        return [ip_range for ip_range in ip_ranges if ip_range['province'] == province]
        
    def get_asn_data(self) -> List[Dict[str, Any]]:
        """
        Get all ASN data.
        
        Returns:
            List of ASN dictionaries
        """
        try:
            with open(self.asn_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('asns', [])
        except Exception as e:
            self.logger.error(f"Failed to load ASN data: {e}")
            return []
            
    def get_asn_by_number(self, asn_number: str) -> Optional[Dict[str, Any]]:
        """
        Get ASN by number.
        
        Args:
            asn_number: ASN number
            
        Returns:
            ASN dictionary or None if not found
        """
        asns = self.get_asn_data()
        for asn in asns:
            if asn['asn'] == asn_number:
                return asn
        return None
        
    def find_isp_by_ip(self, ip_address: str) -> Optional[Dict[str, Any]]:
        """
        Find ISP for a given IP address.
        
        Args:
            ip_address: IP address to check
            
        Returns:
            ISP dictionary or None if not found
        """
        try:
            ip_obj = ipaddress.IPv4Address(ip_address)
            ip_ranges = self.get_ip_ranges()
            
            for ip_range in ip_ranges:
                network = ipaddress.IPv4Network(ip_range['range'], strict=False)
                if ip_obj in network:
                    isp = self.get_isp_by_name(ip_range['isp'])
                    if isp:
                        return {
                            'isp': isp,
                            'ip_range': ip_range,
                            'matched_network': str(network)
                        }
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to find ISP for IP {ip_address}: {e}")
            return None
            
    def get_isp_coverage_by_province(self, province: str) -> List[Dict[str, Any]]:
        """
        Get ISP coverage for a specific province.
        
        Args:
            province: Province name
            
        Returns:
            List of ISP coverage dictionaries
        """
        ip_ranges = self.get_ip_ranges_by_province(province)
        coverage = {}
        
        for ip_range in ip_ranges:
            isp_name = ip_range['isp']
            if isp_name not in coverage:
                isp = self.get_isp_by_name(isp_name)
                coverage[isp_name] = {
                    'isp': isp,
                    'ip_ranges': [],
                    'total_ips': 0,
                    'allocated_ips': 0
                }
            
            coverage[isp_name]['ip_ranges'].append(ip_range)
            coverage[isp_name]['total_ips'] += ip_range['total_ips']
            coverage[isp_name]['allocated_ips'] += ip_range['allocated_ips']
            
        return list(coverage.values())
        
    def search_isp(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for ISPs by name or code.
        
        Args:
            query: Search query
            
        Returns:
            List of matching ISP dictionaries
        """
        results = []
        query_lower = query.lower()
        
        isps = self.get_isps()
        for isp in isps:
            if (query_lower in isp['name'].lower() or 
                query_lower in isp['name_en'].lower() or
                query_lower in isp['code'].lower() or
                query_lower in isp['asn'].lower()):
                results.append(isp)
                
        return results
        
    def get_isp_statistics(self) -> Dict[str, Any]:
        """
        Get ISP statistics.
        
        Returns:
            Dictionary containing ISP statistics
        """
        isps = self.get_isps()
        ip_ranges = self.get_ip_ranges()
        
        stats = {
            'total_isps': len(isps),
            'total_ip_ranges': len(ip_ranges),
            'total_ips': sum(ip_range['total_ips'] for ip_range in ip_ranges),
            'allocated_ips': sum(ip_range['allocated_ips'] for ip_range in ip_ranges),
            'by_type': {},
            'by_coverage': {}
        }
        
        # Statistics by type
        for isp in isps:
            isp_type = isp['type']
            if isp_type not in stats['by_type']:
                stats['by_type'][isp_type] = 0
            stats['by_type'][isp_type] += 1
            
        # Statistics by coverage
        for isp in isps:
            coverage = isp['coverage']
            if coverage not in stats['by_coverage']:
                stats['by_coverage'][coverage] = 0
            stats['by_coverage'][coverage] += 1
            
        return stats
        
    def update_isp_data(self):
        """Update ISP data from external sources."""
        try:
            # In a real implementation, this would fetch data from official sources
            # For now, we'll just log that this would happen
            self.logger.info("ISP data update requested")
            
            # Example of how to update from an API
            # api_url = "https://api.iran.gov.ir/isp-data"
            # response = requests.get(api_url)
            # if response.status_code == 200:
            #     data = response.json()
            #     # Process and save updated data
            #     self._save_updated_isp_data(data)
            
        except Exception as e:
            self.logger.error(f"Failed to update ISP data: {e}")
            raise