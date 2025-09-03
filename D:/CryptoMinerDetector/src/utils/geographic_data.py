#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Geographic Data Manager for CryptoMinerDetector
Handles Iranian administrative divisions and geographic data.
"""

import json
import logging
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import sqlite3
from datetime import datetime

class GeographicDataManager:
    """
    Manages geographic data for Iranian provinces, cities, and administrative divisions.
    Provides data for geographic-based scanning and reporting.
    """
    
    def __init__(self, config):
        """
        Initialize the geographic data manager.
        
        Args:
            config: Configuration manager instance
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.data_dir = Path("D:/CryptoMinerDetector/data/geographic_data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.provinces_file = self.data_dir / "iran_provinces.json"
        self.cities_file = self.data_dir / "iran_cities.json"
        self.postal_codes_file = self.data_dir / "iran_postal_codes.json"
        
        # Load or initialize data
        self._load_geographic_data()
        
    def _load_geographic_data(self):
        """Load or initialize geographic data."""
        try:
            # Load provinces data
            if not self.provinces_file.exists():
                self._create_provinces_data()
            else:
                self.logger.info("Provinces data loaded from file")
                
            # Load cities data
            if not self.cities_file.exists():
                self._create_cities_data()
            else:
                self.logger.info("Cities data loaded from file")
                
            # Load postal codes data
            if not self.postal_codes_file.exists():
                self._create_postal_codes_data()
            else:
                self.logger.info("Postal codes data loaded from file")
                
        except Exception as e:
            self.logger.error(f"Failed to load geographic data: {e}")
            raise
            
    def _create_provinces_data(self):
        """Create Iranian provinces data."""
        provinces_data = {
            "provinces": [
                {
                    "code": "01",
                    "name": "آذربایجان شرقی",
                    "name_en": "East Azerbaijan",
                    "capital": "تبریز",
                    "capital_en": "Tabriz",
                    "latitude": 38.0962,
                    "longitude": 46.2738,
                    "area_km2": 45650,
                    "population": 3909652,
                    "cities_count": 21
                },
                {
                    "code": "02",
                    "name": "آذربایجان غربی",
                    "name_en": "West Azerbaijan",
                    "capital": "ارومیه",
                    "capital_en": "Urmia",
                    "latitude": 37.5527,
                    "longitude": 45.0761,
                    "area_km2": 37437,
                    "population": 3265219,
                    "cities_count": 17
                },
                {
                    "code": "03",
                    "name": "اردبیل",
                    "name_en": "Ardabil",
                    "capital": "اردبیل",
                    "capital_en": "Ardabil",
                    "latitude": 38.2498,
                    "longitude": 48.2933,
                    "area_km2": 17800,
                    "population": 1274180,
                    "cities_count": 12
                },
                {
                    "code": "04",
                    "name": "اصفهان",
                    "name_en": "Isfahan",
                    "capital": "اصفهان",
                    "capital_en": "Isfahan",
                    "latitude": 32.6546,
                    "longitude": 51.6680,
                    "area_km2": 107029,
                    "population": 5120850,
                    "cities_count": 24
                },
                {
                    "code": "05",
                    "name": "البرز",
                    "name_en": "Alborz",
                    "capital": "کرج",
                    "capital_en": "Karaj",
                    "latitude": 35.8400,
                    "longitude": 50.9391,
                    "area_km2": 5832,
                    "population": 2712400,
                    "cities_count": 6
                },
                {
                    "code": "06",
                    "name": "ایلام",
                    "name_en": "Ilam",
                    "capital": "ایلام",
                    "capital_en": "Ilam",
                    "latitude": 33.6374,
                    "longitude": 46.4227,
                    "area_km2": 20133,
                    "population": 580158,
                    "cities_count": 10
                },
                {
                    "code": "07",
                    "name": "بوشهر",
                    "name_en": "Bushehr",
                    "capital": "بوشهر",
                    "capital_en": "Bushehr",
                    "latitude": 28.9234,
                    "longitude": 50.8203,
                    "area_km2": 22743,
                    "population": 1163400,
                    "cities_count": 10
                },
                {
                    "code": "08",
                    "name": "تهران",
                    "name_en": "Tehran",
                    "capital": "تهران",
                    "capital_en": "Tehran",
                    "latitude": 35.6892,
                    "longitude": 51.3890,
                    "area_km2": 18814,
                    "population": 13267637,
                    "cities_count": 16
                },
                {
                    "code": "09",
                    "name": "چهارمحال و بختیاری",
                    "name_en": "Chaharmahal and Bakhtiari",
                    "capital": "شهرکرد",
                    "capital_en": "Shahrekord",
                    "latitude": 32.3256,
                    "longitude": 50.8644,
                    "area_km2": 16332,
                    "population": 947763,
                    "cities_count": 9
                },
                {
                    "code": "10",
                    "name": "خراسان جنوبی",
                    "name_en": "South Khorasan",
                    "capital": "بیرجند",
                    "capital_en": "Birjand",
                    "latitude": 32.8649,
                    "longitude": 59.2262,
                    "area_km2": 151913,
                    "population": 768898,
                    "cities_count": 11
                },
                {
                    "code": "11",
                    "name": "خراسان رضوی",
                    "name_en": "Razavi Khorasan",
                    "capital": "مشهد",
                    "capital_en": "Mashhad",
                    "latitude": 35.2216,
                    "longitude": 59.1042,
                    "area_km2": 118851,
                    "population": 6434501,
                    "cities_count": 28
                },
                {
                    "code": "12",
                    "name": "خراسان شمالی",
                    "name_en": "North Khorasan",
                    "capital": "بجنورد",
                    "capital_en": "Bojnord",
                    "latitude": 37.4761,
                    "longitude": 57.3317,
                    "area_km2": 28434,
                    "population": 863092,
                    "cities_count": 8
                },
                {
                    "code": "13",
                    "name": "خوزستان",
                    "name_en": "Khuzestan",
                    "capital": "اهواز",
                    "capital_en": "Ahvaz",
                    "latitude": 31.3183,
                    "longitude": 48.6706,
                    "area_km2": 64055,
                    "population": 4710509,
                    "cities_count": 27
                },
                {
                    "code": "14",
                    "name": "زنجان",
                    "name_en": "Zanjan",
                    "capital": "زنجان",
                    "capital_en": "Zanjan",
                    "latitude": 36.6736,
                    "longitude": 48.4787,
                    "area_km2": 21773,
                    "population": 1057461,
                    "cities_count": 8
                },
                {
                    "code": "15",
                    "name": "سمنان",
                    "name_en": "Semnan",
                    "capital": "سمنان",
                    "capital_en": "Semnan",
                    "latitude": 35.2256,
                    "longitude": 54.4342,
                    "area_km2": 97491,
                    "population": 702360,
                    "cities_count": 8
                },
                {
                    "code": "16",
                    "name": "سیستان و بلوچستان",
                    "name_en": "Sistan and Baluchestan",
                    "capital": "زاهدان",
                    "capital_en": "Zahedan",
                    "latitude": 29.4963,
                    "longitude": 60.8629,
                    "area_km2": 181785,
                    "population": 2775014,
                    "cities_count": 26
                },
                {
                    "code": "17",
                    "name": "فارس",
                    "name_en": "Fars",
                    "capital": "شیراز",
                    "capital_en": "Shiraz",
                    "latitude": 29.5917,
                    "longitude": 52.5836,
                    "area_km2": 122608,
                    "population": 4851274,
                    "cities_count": 29
                },
                {
                    "code": "18",
                    "name": "قزوین",
                    "name_en": "Qazvin",
                    "capital": "قزوین",
                    "capital_en": "Qazvin",
                    "latitude": 36.2797,
                    "longitude": 50.0049,
                    "area_km2": 15567,
                    "population": 1273761,
                    "cities_count": 6
                },
                {
                    "code": "19",
                    "name": "قم",
                    "name_en": "Qom",
                    "capital": "قم",
                    "capital_en": "Qom",
                    "latitude": 34.6416,
                    "longitude": 50.8746,
                    "area_km2": 11526,
                    "population": 1292283,
                    "cities_count": 1
                },
                {
                    "code": "20",
                    "name": "کردستان",
                    "name_en": "Kurdistan",
                    "capital": "سنندج",
                    "capital_en": "Sanandaj",
                    "latitude": 35.3219,
                    "longitude": 46.9862,
                    "area_km2": 29137,
                    "population": 1603011,
                    "cities_count": 10
                },
                {
                    "code": "21",
                    "name": "کرمان",
                    "name_en": "Kerman",
                    "capital": "کرمان",
                    "capital_en": "Kerman",
                    "latitude": 30.2839,
                    "longitude": 57.0834,
                    "area_km2": 180726,
                    "population": 3164718,
                    "cities_count": 23
                },
                {
                    "code": "22",
                    "name": "کرمانشاه",
                    "name_en": "Kermanshah",
                    "capital": "کرمانشاه",
                    "capital_en": "Kermanshah",
                    "latitude": 34.3277,
                    "longitude": 47.0778,
                    "area_km2": 24998,
                    "population": 1952434,
                    "cities_count": 14
                },
                {
                    "code": "23",
                    "name": "کهگیلویه و بویراحمد",
                    "name_en": "Kohgiluyeh and Boyer-Ahmad",
                    "capital": "یاسوج",
                    "capital_en": "Yasuj",
                    "latitude": 30.6682,
                    "longitude": 51.5880,
                    "area_km2": 15504,
                    "population": 713052,
                    "cities_count": 9
                },
                {
                    "code": "24",
                    "name": "گلستان",
                    "name_en": "Golestan",
                    "capital": "گرگان",
                    "capital_en": "Gorgan",
                    "latitude": 37.2898,
                    "longitude": 55.1376,
                    "area_km2": 20438,
                    "population": 1868819,
                    "cities_count": 14
                },
                {
                    "code": "25",
                    "name": "گیلان",
                    "name_en": "Gilan",
                    "capital": "رشت",
                    "capital_en": "Rasht",
                    "latitude": 37.2809,
                    "longitude": 49.5924,
                    "area_km2": 14042,
                    "population": 2530696,
                    "cities_count": 16
                },
                {
                    "code": "26",
                    "name": "لرستان",
                    "name_en": "Lorestan",
                    "capital": "خرم‌آباد",
                    "capital_en": "Khorramabad",
                    "latitude": 33.5818,
                    "longitude": 48.3988,
                    "area_km2": 28294,
                    "population": 1764649,
                    "cities_count": 11
                },
                {
                    "code": "27",
                    "name": "مازندران",
                    "name_en": "Mazandaran",
                    "capital": "ساری",
                    "capital_en": "Sari",
                    "latitude": 36.2262,
                    "longitude": 53.1880,
                    "area_km2": 23701,
                    "population": 3283582,
                    "cities_count": 22
                },
                {
                    "code": "28",
                    "name": "مرکزی",
                    "name_en": "Markazi",
                    "capital": "اراک",
                    "capital_en": "Arak",
                    "latitude": 34.0954,
                    "longitude": 49.7016,
                    "area_km2": 29127,
                    "population": 1429475,
                    "cities_count": 12
                },
                {
                    "code": "29",
                    "name": "هرمزگان",
                    "name_en": "Hormozgan",
                    "capital": "بندرعباس",
                    "capital_en": "Bandar Abbas",
                    "latitude": 27.1832,
                    "longitude": 56.2666,
                    "area_km2": 70697,
                    "population": 1776415,
                    "cities_count": 13
                },
                {
                    "code": "30",
                    "name": "همدان",
                    "name_en": "Hamadan",
                    "capital": "همدان",
                    "capital_en": "Hamadan",
                    "latitude": 34.7983,
                    "longitude": 48.5148,
                    "area_km2": 19368,
                    "population": 1758268,
                    "cities_count": 9
                },
                {
                    "code": "31",
                    "name": "یزد",
                    "name_en": "Yazd",
                    "capital": "یزد",
                    "capital_en": "Yazd",
                    "latitude": 31.8974,
                    "longitude": 54.3569,
                    "area_km2": 129285,
                    "population": 1138533,
                    "cities_count": 10
                }
            ]
        }
        
        with open(self.provinces_file, 'w', encoding='utf-8') as f:
            json.dump(provinces_data, f, ensure_ascii=False, indent=2)
            
        self.logger.info("Iranian provinces data created")
        
    def _create_cities_data(self):
        """Create sample cities data for major provinces."""
        # This is a simplified version. In a real implementation,
        # you would load comprehensive city data from official sources
        cities_data = {
            "cities": [
                {
                    "province_code": "08",
                    "province_name": "تهران",
                    "city_code": "0801",
                    "city_name": "تهران",
                    "city_name_en": "Tehran",
                    "latitude": 35.6892,
                    "longitude": 51.3890,
                    "population": 8693706,
                    "postal_code_prefix": "11"
                },
                {
                    "province_code": "04",
                    "province_name": "اصفهان",
                    "city_code": "0401",
                    "city_name": "اصفهان",
                    "city_name_en": "Isfahan",
                    "latitude": 32.6546,
                    "longitude": 51.6680,
                    "population": 1961260,
                    "postal_code_prefix": "81"
                },
                {
                    "province_code": "11",
                    "province_name": "خراسان رضوی",
                    "city_code": "1101",
                    "city_name": "مشهد",
                    "city_name_en": "Mashhad",
                    "latitude": 35.2216,
                    "longitude": 59.1042,
                    "population": 3001184,
                    "postal_code_prefix": "91"
                }
            ]
        }
        
        with open(self.cities_file, 'w', encoding='utf-8') as f:
            json.dump(cities_data, f, ensure_ascii=False, indent=2)
            
        self.logger.info("Iranian cities data created")
        
    def _create_postal_codes_data(self):
        """Create sample postal codes data."""
        postal_codes_data = {
            "postal_codes": [
                {
                    "prefix": "11",
                    "province": "تهران",
                    "city": "تهران",
                    "range_start": "1100000000",
                    "range_end": "1199999999"
                },
                {
                    "prefix": "81",
                    "province": "اصفهان",
                    "city": "اصفهان",
                    "range_start": "8100000000",
                    "range_end": "8199999999"
                },
                {
                    "prefix": "91",
                    "province": "خراسان رضوی",
                    "city": "مشهد",
                    "range_start": "9100000000",
                    "range_end": "9199999999"
                }
            ]
        }
        
        with open(self.postal_codes_file, 'w', encoding='utf-8') as f:
            json.dump(postal_codes_data, f, ensure_ascii=False, indent=2)
            
        self.logger.info("Iranian postal codes data created")
        
    def get_provinces(self) -> List[Dict[str, Any]]:
        """
        Get all Iranian provinces.
        
        Returns:
            List of province dictionaries
        """
        try:
            with open(self.provinces_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('provinces', [])
        except Exception as e:
            self.logger.error(f"Failed to load provinces: {e}")
            return []
            
    def get_province_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Get province by code.
        
        Args:
            code: Province code
            
        Returns:
            Province dictionary or None if not found
        """
        provinces = self.get_provinces()
        for province in provinces:
            if province['code'] == code:
                return province
        return None
        
    def get_province_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get province by name (Persian or English).
        
        Args:
            name: Province name
            
        Returns:
            Province dictionary or None if not found
        """
        provinces = self.get_provinces()
        for province in provinces:
            if (province['name'] == name or 
                province['name_en'] == name or
                province['name_en'].lower() == name.lower()):
                return province
        return None
        
    def get_cities_by_province(self, province_code: str) -> List[Dict[str, Any]]:
        """
        Get cities in a specific province.
        
        Args:
            province_code: Province code
            
        Returns:
            List of city dictionaries
        """
        try:
            with open(self.cities_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cities = data.get('cities', [])
                return [city for city in cities if city['province_code'] == province_code]
        except Exception as e:
            self.logger.error(f"Failed to load cities for province {province_code}: {e}")
            return []
            
    def get_city_by_code(self, city_code: str) -> Optional[Dict[str, Any]]:
        """
        Get city by code.
        
        Args:
            city_code: City code
            
        Returns:
            City dictionary or None if not found
        """
        try:
            with open(self.cities_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cities = data.get('cities', [])
                for city in cities:
                    if city['city_code'] == city_code:
                        return city
                return None
        except Exception as e:
            self.logger.error(f"Failed to get city by code {city_code}: {e}")
            return None
            
    def get_postal_codes_by_province(self, province: str) -> List[Dict[str, Any]]:
        """
        Get postal codes for a specific province.
        
        Args:
            province: Province name
            
        Returns:
            List of postal code dictionaries
        """
        try:
            with open(self.postal_codes_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                postal_codes = data.get('postal_codes', [])
                return [pc for pc in postal_codes if pc['province'] == province]
        except Exception as e:
            self.logger.error(f"Failed to load postal codes for province {province}: {e}")
            return []
            
    def search_location(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for locations by name.
        
        Args:
            query: Search query
            
        Returns:
            List of matching locations
        """
        results = []
        query_lower = query.lower()
        
        # Search in provinces
        provinces = self.get_provinces()
        for province in provinces:
            if (query_lower in province['name'].lower() or 
                query_lower in province['name_en'].lower() or
                query_lower in province['capital'].lower() or
                query_lower in province['capital_en'].lower()):
                results.append({
                    'type': 'province',
                    'data': province
                })
                
        # Search in cities
        try:
            with open(self.cities_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cities = data.get('cities', [])
                for city in cities:
                    if (query_lower in city['city_name'].lower() or
                        query_lower in city['city_name_en'].lower()):
                        results.append({
                            'type': 'city',
                            'data': city
                        })
        except Exception as e:
            self.logger.error(f"Failed to search cities: {e}")
            
        return results
        
    def get_province_coordinates(self, province_code: str) -> Optional[Tuple[float, float]]:
        """
        Get province center coordinates.
        
        Args:
            province_code: Province code
            
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        province = self.get_province_by_code(province_code)
        if province:
            return (province['latitude'], province['longitude'])
        return None
        
    def get_city_coordinates(self, city_code: str) -> Optional[Tuple[float, float]]:
        """
        Get city coordinates.
        
        Args:
            city_code: City code
            
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        city = self.get_city_by_code(city_code)
        if city:
            return (city['latitude'], city['longitude'])
        return None
        
    def update_geographic_data(self):
        """Update geographic data from external sources."""
        try:
            # In a real implementation, this would fetch data from official sources
            # For now, we'll just log that this would happen
            self.logger.info("Geographic data update requested")
            
            # Example of how to update from an API
            # api_url = self.config.get('GEOGRAPHIC_DATA', 'data_source')
            # response = requests.get(api_url)
            # if response.status_code == 200:
            #     data = response.json()
            #     # Process and save updated data
            #     self._save_updated_data(data)
            
        except Exception as e:
            self.logger.error(f"Failed to update geographic data: {e}")
            raise