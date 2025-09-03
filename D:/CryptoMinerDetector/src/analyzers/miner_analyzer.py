#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Miner Analyzer for CryptoMinerDetector
Handles cryptocurrency miner detection and analysis.
"""

import logging
import re
import socket
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import json

class MinerAnalyzer:
    """
    Analyzer for detecting and classifying cryptocurrency miners.
    Handles pattern matching, behavior analysis, and miner classification.
    """
    
    def __init__(self, config, database_manager, audit_logger):
        """
        Initialize the miner analyzer.
        
        Args:
            config: Configuration manager instance
            database_manager: Database manager instance
            audit_logger: Audit logger instance
        """
        self.config = config
        self.db_manager = database_manager
        self.audit_logger = audit_logger
        self.logger = logging.getLogger(__name__)
        
        # Mining patterns and signatures
        self.mining_patterns = self._load_mining_patterns()
        self.mining_pools = self._load_mining_pools()
        self.miner_signatures = self._load_miner_signatures()
        
    def _load_mining_patterns(self) -> Dict[str, Any]:
        """
        Load mining detection patterns.
        
        Returns:
            Dictionary of mining patterns
        """
        return {
            'ports': {
                'stratum': [3333, 3334, 3335, 3336, 3337, 3338, 3339],
                'getwork': [8332, 8333, 8334],
                'p2pool': [9332, 9333],
                'other': [4028, 5555, 7777, 8555, 14444, 14433, 14455]
            },
            'services': {
                'stratum': ['stratum', 'mining', 'pool'],
                'getwork': ['getwork', 'bitcoin', 'rpc'],
                'p2pool': ['p2pool', 'peer-to-peer'],
                'other': ['mining', 'crypto', 'blockchain']
            },
            'user_agents': [
                'cgminer', 'bfgminer', 'sgminer', 'xmr-stak', 'xmrig',
                'phoenixminer', 'teamredminer', 'nbminer', 't-rex',
                'lolminer', 'gminer', 'nanominer', 'srbminer'
            ],
            'protocols': [
                'stratum+tcp', 'stratum+ssl', 'getwork', 'getblocktemplate',
                'submitblock', 'submitwork'
            ]
        }
        
    def _load_mining_pools(self) -> Dict[str, List[str]]:
        """
        Load known mining pool domains and IPs.
        
        Returns:
            Dictionary of mining pools
        """
        return {
            'bitcoin': [
                'pool.bitcoin.com', 'slushpool.com', 'antpool.com',
                'f2pool.com', 'btc.com', 'viabtc.com', 'poolin.com'
            ],
            'ethereum': [
                'ethermine.org', 'nanopool.org', 'dwarfpool.com',
                'f2pool.com', 'sparkpool.com', '2miners.com'
            ],
            'monero': [
                'supportxmr.com', 'nanopool.org', 'dwarfpool.com',
                'xmrpool.eu', 'minexmr.com', 'cryptonight.net'
            ],
            'other': [
                'hashvault.pro', 'cryptonight.net', 'xmrpool.net',
                'moneroocean.stream', 'hashvault.pro'
            ]
        }
        
    def _load_miner_signatures(self) -> Dict[str, Dict[str, Any]]:
        """
        Load miner software signatures.
        
        Returns:
            Dictionary of miner signatures
        """
        return {
            'cgminer': {
                'name': 'CGMiner',
                'type': 'GPU/ASIC',
                'signatures': ['cgminer', 'cgminer.exe'],
                'ports': [4028],
                'confidence': 90
            },
            'bfgminer': {
                'name': 'BFGMiner',
                'type': 'GPU/ASIC',
                'signatures': ['bfgminer', 'bfgminer.exe'],
                'ports': [4028],
                'confidence': 90
            },
            'sgminer': {
                'name': 'SGMiner',
                'type': 'GPU',
                'signatures': ['sgminer', 'sgminer.exe'],
                'ports': [4028],
                'confidence': 90
            },
            'xmr-stak': {
                'name': 'XMR-Stak',
                'type': 'CPU/GPU',
                'signatures': ['xmr-stak', 'xmr-stak.exe'],
                'ports': [3333],
                'confidence': 85
            },
            'xmrig': {
                'name': 'XMRig',
                'type': 'CPU',
                'signatures': ['xmrig', 'xmrig.exe'],
                'ports': [3333],
                'confidence': 85
            },
            'phoenixminer': {
                'name': 'PhoenixMiner',
                'type': 'GPU',
                'signatures': ['phoenixminer', 'phoenixminer.exe'],
                'ports': [3333],
                'confidence': 90
            },
            'teamredminer': {
                'name': 'TeamRedMiner',
                'type': 'GPU',
                'signatures': ['teamredminer', 'teamredminer.exe'],
                'ports': [3333],
                'confidence': 90
            },
            'nbminer': {
                'name': 'NBMiner',
                'type': 'GPU',
                'signatures': ['nbminer', 'nbminer.exe'],
                'ports': [3333],
                'confidence': 90
            },
            't-rex': {
                'name': 'T-Rex Miner',
                'type': 'GPU',
                'signatures': ['t-rex', 't-rex.exe'],
                'ports': [3333],
                'confidence': 90
            },
            'lolminer': {
                'name': 'LolMiner',
                'type': 'GPU',
                'signatures': ['lolminer', 'lolminer.exe'],
                'ports': [3333],
                'confidence': 90
            },
            'gminer': {
                'name': 'GMiner',
                'type': 'GPU',
                'signatures': ['gminer', 'gminer.exe'],
                'ports': [3333],
                'confidence': 90
            }
        }
        
    def analyze_device(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a device for cryptocurrency mining activity.
        
        Args:
            device_data: Device scan data
            
        Returns:
            Analysis results with miner detection information
        """
        try:
            analysis_result = {
                'device_ip': device_data.get('ip', ''),
                'analysis_time': datetime.now().isoformat(),
                'miner_detected': False,
                'miner_type': None,
                'miner_name': None,
                'confidence': 0,
                'detection_methods': [],
                'mining_pools': [],
                'behavior_indicators': [],
                'risk_score': 0
            }
            
            # Check for mining ports
            port_analysis = self._analyze_ports(device_data)
            if port_analysis['mining_ports']:
                analysis_result['detection_methods'].append('mining_ports')
                analysis_result['confidence'] += 30
                
            # Check for mining services
            service_analysis = self._analyze_services(device_data)
            if service_analysis['mining_services']:
                analysis_result['detection_methods'].append('mining_services')
                analysis_result['confidence'] += 25
                
            # Check for miner signatures
            signature_analysis = self._analyze_signatures(device_data)
            if signature_analysis['miner_found']:
                analysis_result['detection_methods'].append('miner_signatures')
                analysis_result['confidence'] += 40
                analysis_result['miner_type'] = signature_analysis['miner_type']
                analysis_result['miner_name'] = signature_analysis['miner_name']
                
            # Check for mining pool connections
            pool_analysis = self._analyze_pool_connections(device_data)
            if pool_analysis['pool_connections']:
                analysis_result['detection_methods'].append('pool_connections')
                analysis_result['confidence'] += 35
                analysis_result['mining_pools'] = pool_analysis['pools']
                
            # Check for mining behavior patterns
            behavior_analysis = self._analyze_behavior_patterns(device_data)
            if behavior_analysis['suspicious_behavior']:
                analysis_result['detection_methods'].append('behavior_patterns')
                analysis_result['confidence'] += 20
                analysis_result['behavior_indicators'] = behavior_analysis['indicators']
                
            # Determine if miner is detected
            if analysis_result['confidence'] >= 50:
                analysis_result['miner_detected'] = True
                
            # Calculate risk score
            analysis_result['risk_score'] = self._calculate_risk_score(analysis_result)
            
            # Log analysis
            self.audit_logger.log_data_access(
                user_id="SYSTEM",
                data_type="miner_analysis",
                access_method="analyze",
                record_count=1
            )
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Failed to analyze device: {e}")
            return {
                'device_ip': device_data.get('ip', ''),
                'analysis_time': datetime.now().isoformat(),
                'miner_detected': False,
                'error': str(e)
            }
            
    def _analyze_ports(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze open ports for mining activity.
        
        Args:
            device_data: Device scan data
            
        Returns:
            Port analysis results
        """
        try:
            open_ports = device_data.get('open_ports', [])
            mining_ports = []
            
            for port in open_ports:
                if port in self.mining_patterns['ports']['stratum']:
                    mining_ports.append({'port': port, 'type': 'stratum'})
                elif port in self.mining_patterns['ports']['getwork']:
                    mining_ports.append({'port': port, 'type': 'getwork'})
                elif port in self.mining_patterns['ports']['p2pool']:
                    mining_ports.append({'port': port, 'type': 'p2pool'})
                elif port in self.mining_patterns['ports']['other']:
                    mining_ports.append({'port': port, 'type': 'other'})
                    
            return {
                'mining_ports': mining_ports,
                'total_mining_ports': len(mining_ports)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze ports: {e}")
            return {'mining_ports': [], 'total_mining_ports': 0}
            
    def _analyze_services(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze running services for mining activity.
        
        Args:
            device_data: Device scan data
            
        Returns:
            Service analysis results
        """
        try:
            services = device_data.get('services', [])
            mining_services = []
            
            for service in services:
                service_lower = service.lower()
                
                # Check for mining-related keywords
                for category, keywords in self.mining_patterns['services'].items():
                    for keyword in keywords:
                        if keyword.lower() in service_lower:
                            mining_services.append({
                                'service': service,
                                'category': category,
                                'keyword': keyword
                            })
                            
            return {
                'mining_services': mining_services,
                'total_mining_services': len(mining_services)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze services: {e}")
            return {'mining_services': [], 'total_mining_services': 0}
            
    def _analyze_signatures(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze for miner software signatures.
        
        Args:
            device_data: Device scan data
            
        Returns:
            Signature analysis results
        """
        try:
            services = device_data.get('services', [])
            processes = device_data.get('processes', [])
            miner_found = False
            miner_type = None
            miner_name = None
            confidence = 0
            
            # Check services and processes for miner signatures
            all_text = ' '.join(services + processes).lower()
            
            for miner_id, signature_data in self.miner_signatures.items():
                for signature in signature_data['signatures']:
                    if signature.lower() in all_text:
                        miner_found = True
                        miner_type = signature_data['type']
                        miner_name = signature_data['name']
                        confidence = signature_data['confidence']
                        break
                if miner_found:
                    break
                    
            return {
                'miner_found': miner_found,
                'miner_type': miner_type,
                'miner_name': miner_name,
                'confidence': confidence
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze signatures: {e}")
            return {
                'miner_found': False,
                'miner_type': None,
                'miner_name': None,
                'confidence': 0
            }
            
    def _analyze_pool_connections(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze for mining pool connections.
        
        Args:
            device_data: Device scan data
            
        Returns:
            Pool connection analysis results
        """
        try:
            connections = device_data.get('connections', [])
            pool_connections = []
            pools = []
            
            for connection in connections:
                dest_ip = connection.get('destination_ip', '')
                dest_port = connection.get('destination_port', '')
                dest_hostname = connection.get('destination_hostname', '')
                
                # Check if connection is to a known mining pool
                for pool_category, pool_domains in self.mining_pools.items():
                    for pool_domain in pool_domains:
                        if pool_domain in dest_hostname.lower():
                            pool_connections.append({
                                'pool_category': pool_category,
                                'pool_domain': pool_domain,
                                'destination_ip': dest_ip,
                                'destination_port': dest_port
                            })
                            pools.append(pool_domain)
                            
            return {
                'pool_connections': pool_connections,
                'pools': list(set(pools)),
                'total_pool_connections': len(pool_connections)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze pool connections: {e}")
            return {
                'pool_connections': [],
                'pools': [],
                'total_pool_connections': 0
            }
            
    def _analyze_behavior_patterns(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze device behavior patterns for mining indicators.
        
        Args:
            device_data: Device scan data
            
        Returns:
            Behavior analysis results
        """
        try:
            indicators = []
            suspicious_behavior = False
            
            # Check for high CPU usage patterns
            cpu_usage = device_data.get('cpu_usage', 0)
            if cpu_usage > 80:
                indicators.append(f"High CPU usage: {cpu_usage}%")
                suspicious_behavior = True
                
            # Check for high memory usage patterns
            memory_usage = device_data.get('memory_usage', 0)
            if memory_usage > 80:
                indicators.append(f"High memory usage: {memory_usage}%")
                suspicious_behavior = True
                
            # Check for network traffic patterns
            network_traffic = device_data.get('network_traffic', {})
            if network_traffic.get('outgoing', 0) > 1000000:  # 1MB/s
                indicators.append("High outgoing network traffic")
                suspicious_behavior = True
                
            # Check for specific port patterns
            open_ports = device_data.get('open_ports', [])
            if len(open_ports) >= 3 and any(port in open_ports for port in [3333, 4028, 5555]):
                indicators.append("Multiple mining ports open")
                suspicious_behavior = True
                
            # Check for process patterns
            processes = device_data.get('processes', [])
            mining_processes = [p for p in processes if any(keyword in p.lower() 
                                                         for keyword in ['miner', 'mining', 'cgminer', 'xmrig'])]
            if mining_processes:
                indicators.append(f"Mining processes detected: {', '.join(mining_processes)}")
                suspicious_behavior = True
                
            return {
                'suspicious_behavior': suspicious_behavior,
                'indicators': indicators,
                'total_indicators': len(indicators)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze behavior patterns: {e}")
            return {
                'suspicious_behavior': False,
                'indicators': [],
                'total_indicators': 0
            }
            
    def _calculate_risk_score(self, analysis_result: Dict[str, Any]) -> int:
        """
        Calculate risk score based on analysis results.
        
        Args:
            analysis_result: Analysis results
            
        Returns:
            Risk score (0-100)
        """
        try:
            risk_score = 0
            
            # Base score from confidence
            risk_score += analysis_result.get('confidence', 0) * 0.5
            
            # Additional risk factors
            if analysis_result.get('miner_detected', False):
                risk_score += 20
                
            if analysis_result.get('mining_pools'):
                risk_score += 15
                
            if len(analysis_result.get('behavior_indicators', [])) > 2:
                risk_score += 10
                
            if len(analysis_result.get('detection_methods', [])) > 3:
                risk_score += 10
                
            # Cap at 100
            return min(risk_score, 100)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate risk score: {e}")
            return 0
            
    def classify_miner(self, miner_name: str) -> Dict[str, Any]:
        """
        Classify a detected miner.
        
        Args:
            miner_name: Name of the detected miner
            
        Returns:
            Miner classification
        """
        try:
            if miner_name in self.miner_signatures:
                signature_data = self.miner_signatures[miner_name]
                return {
                    'name': signature_data['name'],
                    'type': signature_data['type'],
                    'category': self._get_miner_category(signature_data['type']),
                    'capabilities': self._get_miner_capabilities(signature_data['type']),
                    'common_coins': self._get_common_coins(signature_data['type'])
                }
            else:
                return {
                    'name': miner_name,
                    'type': 'Unknown',
                    'category': 'Unknown',
                    'capabilities': [],
                    'common_coins': []
                }
                
        except Exception as e:
            self.logger.error(f"Failed to classify miner: {e}")
            return {
                'name': miner_name,
                'type': 'Unknown',
                'category': 'Unknown',
                'capabilities': [],
                'common_coins': []
            }
            
    def _get_miner_category(self, miner_type: str) -> str:
        """
        Get miner category based on type.
        
        Args:
            miner_type: Type of miner
            
        Returns:
            Miner category
        """
        if 'GPU' in miner_type:
            return 'GPU Miner'
        elif 'CPU' in miner_type:
            return 'CPU Miner'
        elif 'ASIC' in miner_type:
            return 'ASIC Miner'
        else:
            return 'Unknown'
            
    def _get_miner_capabilities(self, miner_type: str) -> List[str]:
        """
        Get miner capabilities based on type.
        
        Args:
            miner_type: Type of miner
            
        Returns:
            List of capabilities
        """
        capabilities = []
        
        if 'GPU' in miner_type:
            capabilities.extend(['GPU Mining', 'Multiple Algorithms', 'High Performance'])
        if 'CPU' in miner_type:
            capabilities.extend(['CPU Mining', 'Low Power', 'Wide Compatibility'])
        if 'ASIC' in miner_type:
            capabilities.extend(['ASIC Mining', 'Maximum Efficiency', 'Specialized'])
            
        return capabilities
        
    def _get_common_coins(self, miner_type: str) -> List[str]:
        """
        Get common coins for miner type.
        
        Args:
            miner_type: Type of miner
            
        Returns:
            List of common coins
        """
        if 'GPU' in miner_type:
            return ['Ethereum', 'Monero', 'Ravencoin', 'Ethereum Classic', 'Zcash']
        elif 'CPU' in miner_type:
            return ['Monero', 'RandomX', 'CPU-friendly coins']
        elif 'ASIC' in miner_type:
            return ['Bitcoin', 'Litecoin', 'Bitcoin Cash', 'SHA256 coins']
        else:
            return []
            
    def get_mining_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about detected miners.
        
        Returns:
            Mining statistics
        """
        try:
            # Get all scan results from database
            all_results = self.db_manager.get_all_scan_results()
            
            # Analyze each result
            total_devices = len(all_results)
            miners_detected = 0
            miner_types = {}
            mining_pools = {}
            risk_scores = []
            
            for result in all_results:
                if result.get('miner_detected', False):
                    miners_detected += 1
                    
                    # Count miner types
                    miner_type = result.get('miner_type', 'Unknown')
                    miner_types[miner_type] = miner_types.get(miner_type, 0) + 1
                    
                    # Count mining pools
                    pools = result.get('mining_pools', [])
                    for pool in pools:
                        mining_pools[pool] = mining_pools.get(pool, 0) + 1
                        
                    # Collect risk scores
                    risk_score = result.get('risk_score', 0)
                    risk_scores.append(risk_score)
                    
            # Calculate averages
            avg_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0
            
            return {
                'total_devices': total_devices,
                'miners_detected': miners_detected,
                'miner_percentage': (miners_detected / total_devices * 100) if total_devices > 0 else 0,
                'miner_types': miner_types,
                'mining_pools': mining_pools,
                'average_risk_score': avg_risk_score,
                'high_risk_devices': len([r for r in risk_scores if r > 80]),
                'medium_risk_devices': len([r for r in risk_scores if 50 <= r <= 80]),
                'low_risk_devices': len([r for r in risk_scores if r < 50])
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get mining statistics: {e}")
            return {}