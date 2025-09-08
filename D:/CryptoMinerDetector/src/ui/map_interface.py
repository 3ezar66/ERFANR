#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Map Interface for CryptoMinerDetector
GUI interface for displaying geographic data and device locations.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import os
import webbrowser
from pathlib import Path

class MapInterface:
    """
    GUI interface for displaying geographic data and device locations.
    Provides map visualization and location-based analysis.
    """
    
    def __init__(self, parent, config, database_manager, geographic_data_manager, audit_logger):
        """
        Initialize the map interface.
        
        Args:
            parent: Parent window
            config: Configuration manager
            database_manager: Database manager
            geographic_data_manager: Geographic data manager
            audit_logger: Audit logger instance
        """
        self.parent = parent
        self.config = config
        self.db_manager = database_manager
        self.geographic_data_manager = geographic_data_manager
        self.audit_logger = audit_logger
        self.logger = logging.getLogger(__name__)
        
        # Map data
        self.current_map_data = {}
        self.device_locations = []
        
        # Create the interface
        self._create_interface()
        
    def _create_interface(self):
        """Create the map interface components."""
        # Main frame
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Map controls frame
        controls_frame = ttk.LabelFrame(self.main_frame, text="Map Controls", padding=10)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Province selection
        ttk.Label(controls_frame, text="Province:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.province_var = tk.StringVar()
        self.province_combo = ttk.Combobox(controls_frame, textvariable=self.province_var,
                                         state="readonly", width=20)
        self.province_combo.grid(row=0, column=1, sticky=tk.W, pady=2, padx=5)
        
        # City selection
        ttk.Label(controls_frame, text="City:").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.city_var = tk.StringVar()
        self.city_combo = ttk.Combobox(controls_frame, textvariable=self.city_var,
                                     state="readonly", width=20)
        self.city_combo.grid(row=0, column=3, sticky=tk.W, pady=2, padx=5)
        
        # Load provinces
        self._load_provinces()
        
        # Map type selection
        ttk.Label(controls_frame, text="Map Type:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.map_type_var = tk.StringVar(value="device_locations")
        map_type_combo = ttk.Combobox(controls_frame, textvariable=self.map_type_var,
                                    values=["device_locations", "isp_coverage", "miner_density", "vpn_detection"],
                                    state="readonly", width=20)
        map_type_combo.grid(row=1, column=1, sticky=tk.W, pady=2, padx=5)
        
        # Map controls
        map_controls_frame = ttk.Frame(controls_frame)
        map_controls_frame.grid(row=1, column=2, columnspan=2, sticky=tk.W, pady=2)
        
        ttk.Button(map_controls_frame, text="Generate Map", 
                  command=self._generate_map).pack(side=tk.LEFT, padx=5)
        ttk.Button(map_controls_frame, text="Open Map", 
                  command=self._open_map).pack(side=tk.LEFT, padx=5)
        ttk.Button(map_controls_frame, text="Export Map", 
                  command=self._export_map).pack(side=tk.LEFT, padx=5)
        
        # Map display frame
        map_display_frame = ttk.LabelFrame(self.main_frame, text="Map Display", padding=10)
        map_display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Map info
        self.map_info_label = ttk.Label(map_display_frame, text="No map generated yet")
        self.map_info_label.pack(pady=10)
        
        # Device locations frame
        locations_frame = ttk.LabelFrame(self.main_frame, text="Device Locations", padding=10)
        locations_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Device locations treeview
        columns = ("IP", "Location", "Province", "City", "ISP", "Miner Type", "Confidence")
        self.locations_tree = ttk.Treeview(locations_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.locations_tree.heading(col, text=col)
            self.locations_tree.column(col, width=100)
            
        locations_scrollbar = ttk.Scrollbar(locations_frame, orient=tk.VERTICAL,
                                          command=self.locations_tree.yview)
        self.locations_tree.configure(yscrollcommand=locations_scrollbar.set)
        
        self.locations_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        locations_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Location controls
        location_controls_frame = ttk.Frame(self.main_frame)
        location_controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(location_controls_frame, text="Load Locations", 
                  command=self._load_device_locations).pack(side=tk.LEFT, padx=5)
        ttk.Button(location_controls_frame, text="Filter by Province", 
                  command=self._filter_by_province).pack(side=tk.LEFT, padx=5)
        ttk.Button(location_controls_frame, text="Filter by ISP", 
                  command=self._filter_by_isp).pack(side=tk.LEFT, padx=5)
        ttk.Button(location_controls_frame, text="Clear Filters", 
                  command=self._clear_filters).pack(side=tk.LEFT, padx=5)
        
    def _load_provinces(self):
        """Load provinces into the combo box."""
        try:
            provinces = self.geographic_data_manager.get_provinces()
            province_names = [province['name'] for province in provinces]
            self.province_combo['values'] = province_names
            
            if province_names:
                self.province_combo.set(province_names[0])
                
            # Bind province selection to load cities
            self.province_combo.bind('<<ComboboxSelected>>', self._on_province_selected)
            
        except Exception as e:
            self.logger.error(f"Failed to load provinces: {e}")
            messagebox.showerror("Error", f"Failed to load provinces: {e}")
            
    def _on_province_selected(self, event=None):
        """Handle province selection."""
        try:
            selected_province = self.province_var.get()
            if selected_province:
                # Get province code
                province = self.geographic_data_manager.get_province_by_name(selected_province)
                if province:
                    # Load cities for the selected province
                    cities = self.geographic_data_manager.get_cities_by_province(province['code'])
                    city_names = [city['name'] for city in cities]
                    
                    # Update city combo box
                    self.city_combo['values'] = city_names
                    if city_names:
                        self.city_combo.set(city_names[0])
                    else:
                        self.city_combo.set('')
                        
        except Exception as e:
            self.logger.error(f"Failed to load cities for province: {e}")
            
    def _generate_map(self):
        """Generate a map based on current settings."""
        try:
            map_type = self.map_type_var.get()
            province = self.province_var.get()
            city = self.city_var.get()
            
            # Get map data based on type
            if map_type == "device_locations":
                map_data = self._generate_device_locations_map(province, city)
            elif map_type == "isp_coverage":
                map_data = self._generate_isp_coverage_map(province, city)
            elif map_type == "miner_density":
                map_data = self._generate_miner_density_map(province, city)
            elif map_type == "vpn_detection":
                map_data = self._generate_vpn_detection_map(province, city)
            else:
                messagebox.showerror("Error", "Invalid map type")
                return
                
            # Save map data
            self.current_map_data = map_data
            
            # Generate HTML map
            map_html = self._create_html_map(map_data)
            
            # Save HTML file
            map_output_path = self.config.get('REPORTING', 'map_output_path')
            os.makedirs(map_output_path, exist_ok=True)
            
            map_filename = f"map_{map_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            map_file_path = os.path.join(map_output_path, map_filename)
            
            with open(map_file_path, 'w', encoding='utf-8') as f:
                f.write(map_html)
                
            # Update map info
            self.map_info_label.config(text=f"Map generated: {map_filename}")
            
            # Log map generation
            self.audit_logger.log_data_access(
                user_id="USER",  # Replace with actual user ID
                data_type="map",
                access_method="generate",
                record_count=len(map_data.get('devices', []))
            )
            
            messagebox.showinfo("Success", f"Map generated successfully: {map_filename}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate map: {e}")
            messagebox.showerror("Error", f"Failed to generate map: {e}")
            
    def _generate_device_locations_map(self, province: str, city: str) -> Dict[str, Any]:
        """Generate device locations map data."""
        try:
            # Get devices from database
            if province and city:
                devices = self.db_manager.get_devices_by_province(province)
                # Filter by city if specified
                devices = [d for d in devices if d.get('city') == city]
            elif province:
                devices = self.db_manager.get_devices_by_province(province)
            else:
                devices = self.db_manager.get_all_devices()
                
            map_data = {
                'map_type': 'device_locations',
                'province': province,
                'city': city,
                'devices': devices,
                'center': self._get_map_center(province, city),
                'zoom': 10 if city else 8
            }
            
            return map_data
            
        except Exception as e:
            self.logger.error(f"Failed to generate device locations map: {e}")
            raise
            
    def _generate_isp_coverage_map(self, province: str, city: str) -> Dict[str, Any]:
        """Generate ISP coverage map data."""
        try:
            # Get ISP coverage data
            if province:
                isp_coverage = self.geographic_data_manager.get_isp_coverage_by_province(province)
            else:
                isp_coverage = self.geographic_data_manager.get_all_isp_coverage()
                
            map_data = {
                'map_type': 'isp_coverage',
                'province': province,
                'city': city,
                'isp_coverage': isp_coverage,
                'center': self._get_map_center(province, city),
                'zoom': 10 if city else 8
            }
            
            return map_data
            
        except Exception as e:
            self.logger.error(f"Failed to generate ISP coverage map: {e}")
            raise
            
    def _generate_miner_density_map(self, province: str, city: str) -> Dict[str, Any]:
        """Generate miner density map data."""
        try:
            # Get miner density data
            if province and city:
                devices = self.db_manager.get_devices_by_province(province)
                devices = [d for d in devices if d.get('city') == city and d.get('miner_type')]
            elif province:
                devices = self.db_manager.get_devices_by_province(province)
                devices = [d for d in devices if d.get('miner_type')]
            else:
                devices = self.db_manager.get_all_devices()
                devices = [d for d in devices if d.get('miner_type')]
                
            # Calculate density by location
            density_data = {}
            for device in devices:
                location = f"{device.get('province', 'Unknown')}-{device.get('city', 'Unknown')}"
                if location not in density_data:
                    density_data[location] = {
                        'province': device.get('province', 'Unknown'),
                        'city': device.get('city', 'Unknown'),
                        'count': 0,
                        'miner_types': set()
                    }
                density_data[location]['count'] += 1
                density_data[location]['miner_types'].add(device.get('miner_type', 'Unknown'))
                
            # Convert sets to lists for JSON serialization
            for location_data in density_data.values():
                location_data['miner_types'] = list(location_data['miner_types'])
                
            map_data = {
                'map_type': 'miner_density',
                'province': province,
                'city': city,
                'density_data': list(density_data.values()),
                'center': self._get_map_center(province, city),
                'zoom': 10 if city else 8
            }
            
            return map_data
            
        except Exception as e:
            self.logger.error(f"Failed to generate miner density map: {e}")
            raise
            
    def _generate_vpn_detection_map(self, province: str, city: str) -> Dict[str, Any]:
        """Generate VPN detection map data."""
        try:
            # Get VPN detection data
            if province and city:
                devices = self.db_manager.get_devices_by_province(province)
                devices = [d for d in devices if d.get('city') == city and d.get('vpn_detected')]
            elif province:
                devices = self.db_manager.get_devices_by_province(province)
                devices = [d for d in devices if d.get('vpn_detected')]
            else:
                devices = self.db_manager.get_all_devices()
                devices = [d for d in devices if d.get('vpn_detected')]
                
            map_data = {
                'map_type': 'vpn_detection',
                'province': province,
                'city': city,
                'vpn_devices': devices,
                'center': self._get_map_center(province, city),
                'zoom': 10 if city else 8
            }
            
            return map_data
            
        except Exception as e:
            self.logger.error(f"Failed to generate VPN detection map: {e}")
            raise
            
    def _get_map_center(self, province: str, city: str) -> Dict[str, float]:
        """Get map center coordinates."""
        try:
            if province:
                province_data = self.geographic_data_manager.get_province_by_name(province)
                if province_data and province_data.get('coordinates'):
                    return province_data['coordinates']
                    
            # Default to Iran center
            return {'lat': 32.4279, 'lng': 53.6880}
            
        except Exception as e:
            self.logger.error(f"Failed to get map center: {e}")
            return {'lat': 32.4279, 'lng': 53.6880}
            
    def _create_html_map(self, map_data: Dict[str, Any]) -> str:
        """Create HTML map using Folium."""
        try:
            import folium
            
            # Create base map
            center = map_data.get('center', {'lat': 32.4279, 'lng': 53.6880})
            zoom = map_data.get('zoom', 8)
            
            m = folium.Map(
                location=[center['lat'], center['lng']],
                zoom_start=zoom,
                tiles='OpenStreetMap'
            )
            
            # Add data based on map type
            map_type = map_data.get('map_type', 'device_locations')
            
            if map_type == 'device_locations':
                self._add_device_markers(m, map_data.get('devices', []))
            elif map_type == 'isp_coverage':
                self._add_isp_coverage(m, map_data.get('isp_coverage', []))
            elif map_type == 'miner_density':
                self._add_miner_density(m, map_data.get('density_data', []))
            elif map_type == 'vpn_detection':
                self._add_vpn_markers(m, map_data.get('vpn_devices', []))
                
            # Add legend
            self._add_legend(m, map_type)
            
            # Generate HTML
            return m._repr_html_()
            
        except ImportError:
            # Fallback to simple HTML if Folium is not available
            return self._create_simple_html_map(map_data)
        except Exception as e:
            self.logger.error(f"Failed to create HTML map: {e}")
            return self._create_simple_html_map(map_data)
            
    def _add_device_markers(self, map_obj, devices: List[Dict[str, Any]]):
        """Add device markers to map."""
        try:
            import folium
            
            for device in devices:
                if device.get('latitude') and device.get('longitude'):
                    # Create popup content
                    popup_content = f"""
                    <b>Device Details</b><br>
                    IP: {device.get('ip', 'Unknown')}<br>
                    Hostname: {device.get('hostname', 'Unknown')}<br>
                    Miner Type: {device.get('miner_type', 'Unknown')}<br>
                    Confidence: {device.get('confidence', 0)}%<br>
                    ISP: {device.get('isp', 'Unknown')}<br>
                    Location: {device.get('province', 'Unknown')}, {device.get('city', 'Unknown')}
                    """
                    
                    # Choose marker color based on miner type
                    if device.get('miner_type'):
                        color = 'red'
                    elif device.get('vpn_detected'):
                        color = 'orange'
                    else:
                        color = 'blue'
                        
                    folium.Marker(
                        location=[device['latitude'], device['longitude']],
                        popup=folium.Popup(popup_content, max_width=300),
                        icon=folium.Icon(color=color, icon='info-sign')
                    ).add_to(map_obj)
                    
        except Exception as e:
            self.logger.error(f"Failed to add device markers: {e}")
            
    def _add_isp_coverage(self, map_obj, isp_coverage: List[Dict[str, Any]]):
        """Add ISP coverage to map."""
        try:
            import folium
            
            for isp in isp_coverage:
                if isp.get('coordinates'):
                    popup_content = f"""
                    <b>ISP Coverage</b><br>
                    ISP: {isp.get('name', 'Unknown')}<br>
                    ASN: {isp.get('asn', 'Unknown')}<br>
                    Coverage: {isp.get('coverage_percentage', 0)}%<br>
                    IP Ranges: {isp.get('ip_ranges_count', 0)}
                    """
                    
                    folium.Marker(
                        location=[isp['coordinates']['lat'], isp['coordinates']['lng']],
                        popup=folium.Popup(popup_content, max_width=300),
                        icon=folium.Icon(color='green', icon='tower')
                    ).add_to(map_obj)
                    
        except Exception as e:
            self.logger.error(f"Failed to add ISP coverage: {e}")
            
    def _add_miner_density(self, map_obj, density_data: List[Dict[str, Any]]):
        """Add miner density to map."""
        try:
            import folium
            
            for location in density_data:
                if location.get('coordinates'):
                    # Create popup content
                    miner_types = ', '.join(location.get('miner_types', []))
                    popup_content = f"""
                    <b>Miner Density</b><br>
                    Location: {location.get('province', 'Unknown')}, {location.get('city', 'Unknown')}<br>
                    Count: {location.get('count', 0)}<br>
                    Miner Types: {miner_types}
                    """
                    
                    # Choose color based on density
                    count = location.get('count', 0)
                    if count > 10:
                        color = 'red'
                    elif count > 5:
                        color = 'orange'
                    elif count > 1:
                        color = 'yellow'
                    else:
                        color = 'green'
                        
                    folium.CircleMarker(
                        location=[location['coordinates']['lat'], location['coordinates']['lng']],
                        radius=min(count * 2, 20),
                        popup=folium.Popup(popup_content, max_width=300),
                        color=color,
                        fill=True,
                        fillOpacity=0.7
                    ).add_to(map_obj)
                    
        except Exception as e:
            self.logger.error(f"Failed to add miner density: {e}")
            
    def _add_vpn_markers(self, map_obj, vpn_devices: List[Dict[str, Any]]):
        """Add VPN detection markers to map."""
        try:
            import folium
            
            for device in vpn_devices:
                if device.get('latitude') and device.get('longitude'):
                    popup_content = f"""
                    <b>VPN Detection</b><br>
                    IP: {device.get('ip', 'Unknown')}<br>
                    Original IP: {device.get('original_ip', 'Unknown')}<br>
                    VPN Type: {device.get('vpn_type', 'Unknown')}<br>
                    Detection Method: {device.get('detection_method', 'Unknown')}<br>
                    Location: {device.get('province', 'Unknown')}, {device.get('city', 'Unknown')}
                    """
                    
                    folium.Marker(
                        location=[device['latitude'], device['longitude']],
                        popup=folium.Popup(popup_content, max_width=300),
                        icon=folium.Icon(color='purple', icon='shield')
                    ).add_to(map_obj)
                    
        except Exception as e:
            self.logger.error(f"Failed to add VPN markers: {e}")
            
    def _add_legend(self, map_obj, map_type: str):
        """Add legend to map."""
        try:
            import folium
            
            legend_html = f"""
            <div style="position: fixed; 
                        bottom: 50px; left: 50px; width: 200px; height: 120px; 
                        background-color: white; border:2px solid grey; z-index:9999; 
                        font-size:14px; padding: 10px">
            <p><b>{map_type.replace('_', ' ').title()}</b></p>
            """
            
            if map_type == 'device_locations':
                legend_html += """
                <p><i class="fa fa-circle" style="color:red"></i> Miner Detected<br>
                <i class="fa fa-circle" style="color:orange"></i> VPN Detected<br>
                <i class="fa fa-circle" style="color:blue"></i> Regular Device</p>
                """
            elif map_type == 'miner_density':
                legend_html += """
                <p><i class="fa fa-circle" style="color:red"></i> High Density (>10)<br>
                <i class="fa fa-circle" style="color:orange"></i> Medium Density (5-10)<br>
                <i class="fa fa-circle" style="color:yellow"></i> Low Density (2-5)<br>
                <i class="fa fa-circle" style="color:green"></i> Single Device</p>
                """
            elif map_type == 'vpn_detection':
                legend_html += """
                <p><i class="fa fa-shield" style="color:purple"></i> VPN Detected</p>
                """
                
            legend_html += "</div>"
            
            map_obj.get_root().html.add_child(folium.Element(legend_html))
            
        except Exception as e:
            self.logger.error(f"Failed to add legend: {e}")
            
    def _create_simple_html_map(self, map_data: Dict[str, Any]) -> str:
        """Create a simple HTML map without Folium."""
        try:
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>CryptoMinerDetector Map</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .map-container { border: 1px solid #ccc; padding: 20px; margin: 20px 0; }
                    .device-list { max-height: 400px; overflow-y: auto; }
                    .device-item { border: 1px solid #ddd; padding: 10px; margin: 5px 0; }
                    .miner { background-color: #ffebee; }
                    .vpn { background-color: #fff3e0; }
                    .regular { background-color: #f3e5f5; }
                </style>
            </head>
            <body>
                <h1>CryptoMinerDetector - {map_type}</h1>
                <div class="map-container">
                    <h2>Map Data</h2>
                    <p><strong>Province:</strong> {province}</p>
                    <p><strong>City:</strong> {city}</p>
                    <p><strong>Total Devices:</strong> {device_count}</p>
                </div>
                <div class="device-list">
                    <h2>Device List</h2>
                    {device_items}
                </div>
            </body>
            </html>
            """
            
            map_type = map_data.get('map_type', 'Unknown')
            province = map_data.get('province', 'All')
            city = map_data.get('city', 'All')
            
            devices = map_data.get('devices', [])
            device_count = len(devices)
            
            device_items = ""
            for device in devices:
                device_class = "regular"
                if device.get('miner_type'):
                    device_class = "miner"
                elif device.get('vpn_detected'):
                    device_class = "vpn"
                    
                device_items += f"""
                <div class="device-item {device_class}">
                    <strong>IP:</strong> {device.get('ip', 'Unknown')}<br>
                    <strong>Location:</strong> {device.get('province', 'Unknown')}, {device.get('city', 'Unknown')}<br>
                    <strong>Miner Type:</strong> {device.get('miner_type', 'None')}<br>
                    <strong>Confidence:</strong> {device.get('confidence', 0)}%
                </div>
                """
                
            return html_template.format(
                map_type=map_type,
                province=province,
                city=city,
                device_count=device_count,
                device_items=device_items
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create simple HTML map: {e}")
            return f"<html><body><h1>Error generating map</h1><p>{str(e)}</p></body></html>"
            
    def _open_map(self):
        """Open the generated map in browser."""
        try:
            if not self.current_map_data:
                messagebox.showwarning("Warning", "No map generated yet")
                return
                
            map_output_path = self.config.get('REPORTING', 'map_output_path')
            map_files = [f for f in os.listdir(map_output_path) if f.endswith('.html')]
            
            if map_files:
                # Open the most recent map file
                latest_map = max(map_files, key=lambda x: os.path.getctime(os.path.join(map_output_path, x)))
                map_file_path = os.path.join(map_output_path, latest_map)
                
                # Open in default browser
                webbrowser.open(f'file://{os.path.abspath(map_file_path)}')
                
                messagebox.showinfo("Success", f"Map opened in browser: {latest_map}")
            else:
                messagebox.showwarning("Warning", "No map files found")
                
        except Exception as e:
            self.logger.error(f"Failed to open map: {e}")
            messagebox.showerror("Error", f"Failed to open map: {e}")
            
    def _export_map(self):
        """Export the current map."""
        try:
            if not self.current_map_data:
                messagebox.showwarning("Warning", "No map data to export")
                return
                
            # Ask user for export location
            export_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("HTML files", "*.html"), ("All files", "*.*")]
            )
            
            if export_path:
                if export_path.endswith('.json'):
                    with open(export_path, 'w', encoding='utf-8') as f:
                        json.dump(self.current_map_data, f, indent=2, ensure_ascii=False)
                elif export_path.endswith('.html'):
                    html_content = self._create_html_map(self.current_map_data)
                    with open(export_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                        
                messagebox.showinfo("Success", f"Map exported to {export_path}")
                
                # Log export activity
                self.audit_logger.log_data_access(
                    user_id="USER",  # Replace with actual user ID
                    data_type="map",
                    access_method="export",
                    record_count=1
                )
                
        except Exception as e:
            self.logger.error(f"Failed to export map: {e}")
            messagebox.showerror("Error", f"Failed to export map: {e}")
            
    def _load_device_locations(self):
        """Load device locations into the treeview."""
        try:
            # Clear existing items
            for item in self.locations_tree.get_children():
                self.locations_tree.delete(item)
                
            # Get all devices with location data
            devices = self.db_manager.get_all_devices()
            
            for device in devices:
                if device.get('latitude') and device.get('longitude'):
                    self.locations_tree.insert('', tk.END, values=(
                        device.get('ip', ''),
                        f"{device.get('latitude', '')}, {device.get('longitude', '')}",
                        device.get('province', ''),
                        device.get('city', ''),
                        device.get('isp', ''),
                        device.get('miner_type', ''),
                        f"{device.get('confidence', 0)}%"
                    ))
                    
            self.device_locations = devices
            
            messagebox.showinfo("Success", f"Loaded {len(devices)} device locations")
            
        except Exception as e:
            self.logger.error(f"Failed to load device locations: {e}")
            messagebox.showerror("Error", f"Failed to load device locations: {e}")
            
    def _filter_by_province(self):
        """Filter device locations by province."""
        try:
            province = self.province_var.get()
            if not province:
                messagebox.showwarning("Warning", "Please select a province")
                return
                
            # Clear existing items
            for item in self.locations_tree.get_children():
                self.locations_tree.delete(item)
                
            # Filter devices
            filtered_devices = [d for d in self.device_locations if d.get('province') == province]
            
            for device in filtered_devices:
                if device.get('latitude') and device.get('longitude'):
                    self.locations_tree.insert('', tk.END, values=(
                        device.get('ip', ''),
                        f"{device.get('latitude', '')}, {device.get('longitude', '')}",
                        device.get('province', ''),
                        device.get('city', ''),
                        device.get('isp', ''),
                        device.get('miner_type', ''),
                        f"{device.get('confidence', 0)}%"
                    ))
                    
            messagebox.showinfo("Success", f"Filtered to {len(filtered_devices)} devices in {province}")
            
        except Exception as e:
            self.logger.error(f"Failed to filter by province: {e}")
            messagebox.showerror("Error", f"Failed to filter by province: {e}")
            
    def _filter_by_isp(self):
        """Filter device locations by ISP."""
        try:
            # Get unique ISPs
            isps = list(set(d.get('isp', '') for d in self.device_locations if d.get('isp')))
            
            if not isps:
                messagebox.showwarning("Warning", "No ISP data available")
                return
                
            # Create ISP selection dialog
            isp_dialog = tk.Toplevel(self.parent)
            isp_dialog.title("Select ISP")
            isp_dialog.geometry("300x200")
            isp_dialog.transient(self.parent)
            isp_dialog.grab_set()
            
            ttk.Label(isp_dialog, text="Select ISP to filter:").pack(pady=10)
            
            isp_var = tk.StringVar()
            isp_combo = ttk.Combobox(isp_dialog, textvariable=isp_var, values=isps, state="readonly")
            isp_combo.pack(pady=10)
            
            def apply_filter():
                selected_isp = isp_var.get()
                if selected_isp:
                    # Clear existing items
                    for item in self.locations_tree.get_children():
                        self.locations_tree.delete(item)
                        
                    # Filter devices
                    filtered_devices = [d for d in self.device_locations if d.get('isp') == selected_isp]
                    
                    for device in filtered_devices:
                        if device.get('latitude') and device.get('longitude'):
                            self.locations_tree.insert('', tk.END, values=(
                                device.get('ip', ''),
                                f"{device.get('latitude', '')}, {device.get('longitude', '')}",
                                device.get('province', ''),
                                device.get('city', ''),
                                device.get('isp', ''),
                                device.get('miner_type', ''),
                                f"{device.get('confidence', 0)}%"
                            ))
                            
                    messagebox.showinfo("Success", f"Filtered to {len(filtered_devices)} devices from {selected_isp}")
                    isp_dialog.destroy()
                    
            ttk.Button(isp_dialog, text="Apply Filter", command=apply_filter).pack(pady=10)
            
        except Exception as e:
            self.logger.error(f"Failed to filter by ISP: {e}")
            messagebox.showerror("Error", f"Failed to filter by ISP: {e}")
            
    def _clear_filters(self):
        """Clear all filters and show all devices."""
        try:
            self._load_device_locations()
            messagebox.showinfo("Success", "Filters cleared")
            
        except Exception as e:
            self.logger.error(f"Failed to clear filters: {e}")
            messagebox.showerror("Error", f"Failed to clear filters: {e}")