#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scan Interface for CryptoMinerDetector
GUI interface for managing network scans and monitoring.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

class ScanInterface:
    """
    GUI interface for managing network scans and monitoring.
    Provides controls for different types of scans and real-time monitoring.
    """
    
    def __init__(self, parent, config, database_manager, network_scanner, 
                 geographic_data_manager, isp_data_manager, audit_logger):
        """
        Initialize the scan interface.
        
        Args:
            parent: Parent window
            config: Configuration manager
            database_manager: Database manager
            network_scanner: Network scanner instance
            geographic_data_manager: Geographic data manager
            isp_data_manager: ISP data manager
            audit_logger: Audit logger instance
        """
        self.parent = parent
        self.config = config
        self.db_manager = database_manager
        self.network_scanner = network_scanner
        self.geographic_data_manager = geographic_data_manager
        self.isp_data_manager = isp_data_manager
        self.audit_logger = audit_logger
        self.logger = logging.getLogger(__name__)
        
        # Scan state
        self.current_scan = None
        self.scan_thread = None
        self.scan_results = []
        
        # Create the interface
        self._create_interface()
        
    def _create_interface(self):
        """Create the scan interface components."""
        # Main frame
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for different scan types
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self._create_network_scan_tab()
        self._create_geographic_scan_tab()
        self._create_isp_scan_tab()
        self._create_monitoring_tab()
        
        # Create status bar
        self._create_status_bar()
        
    def _create_network_scan_tab(self):
        """Create the network scan tab."""
        self.network_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.network_frame, text="Network Scan")
        
        # Scan configuration frame
        config_frame = ttk.LabelFrame(self.network_frame, text="Scan Configuration", padding=10)
        config_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # IP Range input
        ttk.Label(config_frame, text="IP Range (CIDR):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.ip_range_var = tk.StringVar(value="192.168.1.0/24")
        self.ip_range_entry = ttk.Entry(config_frame, textvariable=self.ip_range_var, width=30)
        self.ip_range_entry.grid(row=0, column=1, sticky=tk.W, pady=2, padx=5)
        
        # Scan type selection
        ttk.Label(config_frame, text="Scan Type:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.scan_type_var = tk.StringVar(value="quick")
        scan_type_combo = ttk.Combobox(config_frame, textvariable=self.scan_type_var, 
                                      values=["quick", "comprehensive", "stealth"], 
                                      state="readonly", width=15)
        scan_type_combo.grid(row=1, column=1, sticky=tk.W, pady=2, padx=5)
        
        # Ports to scan
        ttk.Label(config_frame, text="Ports:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.ports_var = tk.StringVar(value="3333,4028,5555,7777,8332,8333,8555,9332,9333,14444,14433,14455")
        self.ports_entry = ttk.Entry(config_frame, textvariable=self.ports_var, width=30)
        self.ports_entry.grid(row=2, column=1, sticky=tk.W, pady=2, padx=5)
        
        # Scan controls frame
        controls_frame = ttk.Frame(self.network_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Scan buttons
        self.start_scan_btn = ttk.Button(controls_frame, text="Start Scan", 
                                        command=self._start_network_scan)
        self.start_scan_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_scan_btn = ttk.Button(controls_frame, text="Stop Scan", 
                                      command=self._stop_scan, state=tk.DISABLED)
        self.stop_scan_btn.pack(side=tk.LEFT, padx=5)
        
        self.pause_scan_btn = ttk.Button(controls_frame, text="Pause", 
                                        command=self._pause_scan, state=tk.DISABLED)
        self.pause_scan_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(self.network_frame, text="Scan Progress", padding=10)
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Status label
        self.status_label = ttk.Label(progress_frame, text="Ready to scan")
        self.status_label.pack(pady=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.network_frame, text="Scan Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Results treeview
        columns = ("IP", "Hostname", "Status", "Open Ports", "Services", "Miner Type", "Confidence")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=10)
        
        # Configure columns
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=100)
            
        # Scrollbar for results
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, 
                                         command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Results controls
        results_controls_frame = ttk.Frame(self.network_frame)
        results_controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(results_controls_frame, text="Export Results", 
                  command=self._export_scan_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(results_controls_frame, text="Clear Results", 
                  command=self._clear_scan_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(results_controls_frame, text="View Details", 
                  command=self._view_device_details).pack(side=tk.LEFT, padx=5)
        
    def _create_geographic_scan_tab(self):
        """Create the geographic scan tab."""
        self.geographic_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.geographic_frame, text="Geographic Scan")
        
        # Province selection frame
        province_frame = ttk.LabelFrame(self.geographic_frame, text="Province Selection", padding=10)
        province_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(province_frame, text="Province:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.province_var = tk.StringVar()
        self.province_combo = ttk.Combobox(province_frame, textvariable=self.province_var, 
                                         state="readonly", width=30)
        self.province_combo.grid(row=0, column=1, sticky=tk.W, pady=2, padx=5)
        
        # City selection frame
        city_frame = ttk.LabelFrame(self.geographic_frame, text="City Selection", padding=10)
        city_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(city_frame, text="Cities:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        # City listbox with scrollbar
        city_list_frame = ttk.Frame(city_frame)
        city_list_frame.grid(row=0, column=1, sticky=tk.W, pady=2, padx=5)
        
        self.city_listbox = tk.Listbox(city_list_frame, selectmode=tk.MULTIPLE, height=6, width=30)
        city_scrollbar = ttk.Scrollbar(city_list_frame, orient=tk.VERTICAL, 
                                      command=self.city_listbox.yview)
        self.city_listbox.configure(yscrollcommand=city_scrollbar.set)
        
        self.city_listbox.pack(side=tk.LEFT)
        city_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load provinces
        self._load_provinces()
        
        # Geographic scan controls
        geo_controls_frame = ttk.Frame(self.geographic_frame)
        geo_controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(geo_controls_frame, text="Load ISP Data", 
                  command=self._load_isp_data_for_province).pack(side=tk.LEFT, padx=5)
        ttk.Button(geo_controls_frame, text="Start Geographic Scan", 
                  command=self._start_geographic_scan).pack(side=tk.LEFT, padx=5)
        
        # ISP data frame
        isp_data_frame = ttk.LabelFrame(self.geographic_frame, text="ISP Data", padding=10)
        isp_data_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # ISP treeview
        isp_columns = ("ISP", "ASN", "IP Ranges", "Coverage", "Status")
        self.isp_tree = ttk.Treeview(isp_data_frame, columns=isp_columns, show="headings", height=8)
        
        for col in isp_columns:
            self.isp_tree.heading(col, text=col)
            self.isp_tree.column(col, width=120)
            
        isp_scrollbar = ttk.Scrollbar(isp_data_frame, orient=tk.VERTICAL, 
                                     command=self.isp_tree.yview)
        self.isp_tree.configure(yscrollcommand=isp_scrollbar.set)
        
        self.isp_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        isp_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def _create_isp_scan_tab(self):
        """Create the ISP scan tab."""
        self.isp_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.isp_frame, text="ISP Scan")
        
        # ISP selection frame
        isp_select_frame = ttk.LabelFrame(self.isp_frame, text="ISP Selection", padding=10)
        isp_select_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(isp_select_frame, text="ISP:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.isp_var = tk.StringVar()
        self.isp_combo = ttk.Combobox(isp_select_frame, textvariable=self.isp_var, 
                                    state="readonly", width=30)
        self.isp_combo.grid(row=0, column=1, sticky=tk.W, pady=2, padx=5)
        
        # Load ISPs
        self._load_isps()
        
        # IP ranges frame
        ranges_frame = ttk.LabelFrame(self.isp_frame, text="IP Ranges", padding=10)
        ranges_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # IP ranges treeview
        range_columns = ("IP Range", "ASN", "Location", "Status", "Device Count")
        self.ranges_tree = ttk.Treeview(ranges_frame, columns=range_columns, show="headings", height=10)
        
        for col in range_columns:
            self.ranges_tree.heading(col, text=col)
            self.ranges_tree.column(col, width=120)
            
        ranges_scrollbar = ttk.Scrollbar(ranges_frame, orient=tk.VERTICAL, 
                                        command=self.ranges_tree.yview)
        self.ranges_tree.configure(yscrollcommand=ranges_scrollbar.set)
        
        self.ranges_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ranges_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ISP scan controls
        isp_scan_controls = ttk.Frame(self.isp_frame)
        isp_scan_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(isp_scan_controls, text="Load IP Ranges", 
                  command=self._load_ip_ranges_for_isp).pack(side=tk.LEFT, padx=5)
        ttk.Button(isp_scan_controls, text="Start ISP Scan", 
                  command=self._start_isp_scan).pack(side=tk.LEFT, padx=5)
        ttk.Button(isp_scan_controls, text="Export ISP Data", 
                  command=self._export_isp_data).pack(side=tk.LEFT, padx=5)
        
    def _create_monitoring_tab(self):
        """Create the monitoring tab."""
        self.monitoring_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.monitoring_frame, text="Monitoring")
        
        # Monitoring controls frame
        monitor_controls_frame = ttk.LabelFrame(self.monitoring_frame, text="Monitoring Controls", padding=10)
        monitor_controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Monitoring status
        self.monitoring_var = tk.BooleanVar()
        self.monitoring_check = ttk.Checkbutton(monitor_controls_frame, text="Enable Continuous Monitoring", 
                                               variable=self.monitoring_var, 
                                               command=self._toggle_monitoring)
        self.monitoring_check.pack(anchor=tk.W, pady=5)
        
        # Monitoring interval
        ttk.Label(monitor_controls_frame, text="Scan Interval (minutes):").pack(anchor=tk.W, pady=2)
        self.monitor_interval_var = tk.StringVar(value="30")
        self.monitor_interval_entry = ttk.Entry(monitor_controls_frame, textvariable=self.monitor_interval_var, 
                                              width=10)
        self.monitor_interval_entry.pack(anchor=tk.W, pady=2)
        
        # Monitoring targets
        ttk.Label(monitor_controls_frame, text="Monitoring Targets:").pack(anchor=tk.W, pady=2)
        self.monitor_targets_text = tk.Text(monitor_controls_frame, height=4, width=50)
        self.monitor_targets_text.pack(anchor=tk.W, pady=2)
        
        # Monitoring results frame
        monitor_results_frame = ttk.LabelFrame(self.monitoring_frame, text="Monitoring Results", padding=10)
        monitor_results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Monitoring results treeview
        monitor_columns = ("Time", "Target", "Status", "Changes", "Alerts")
        self.monitor_tree = ttk.Treeview(monitor_results_frame, columns=monitor_columns, show="headings", height=10)
        
        for col in monitor_columns:
            self.monitor_tree.heading(col, text=col)
            self.monitor_tree.column(col, width=120)
            
        monitor_scrollbar = ttk.Scrollbar(monitor_results_frame, orient=tk.VERTICAL, 
                                         command=self.monitor_tree.yview)
        self.monitor_tree.configure(yscrollcommand=monitor_scrollbar.set)
        
        self.monitor_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        monitor_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = ttk.Frame(self.main_frame)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side=tk.LEFT)
        
        self.time_label = ttk.Label(self.status_bar, text="")
        self.time_label.pack(side=tk.RIGHT)
        
        # Update time
        self._update_time()
        
    def _update_time(self):
        """Update the time display."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.parent.after(1000, self._update_time)
        
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
                    
                    # Clear and populate city listbox
                    self.city_listbox.delete(0, tk.END)
                    for city_name in city_names:
                        self.city_listbox.insert(tk.END, city_name)
                        
        except Exception as e:
            self.logger.error(f"Failed to load cities for province: {e}")
            
    def _load_isps(self):
        """Load ISPs into the combo box."""
        try:
            isps = self.isp_data_manager.get_isps()
            isp_names = [isp['name'] for isp in isps]
            self.isp_combo['values'] = isp_names
            
            if isp_names:
                self.isp_combo.set(isp_names[0])
                
        except Exception as e:
            self.logger.error(f"Failed to load ISPs: {e}")
            messagebox.showerror("Error", f"Failed to load ISPs: {e}")
            
    def _start_network_scan(self):
        """Start a network scan."""
        try:
            # Validate inputs
            ip_range = self.ip_range_var.get().strip()
            if not ip_range:
                messagebox.showerror("Error", "Please enter an IP range")
                return
                
            scan_type = self.scan_type_var.get()
            ports = self.ports_var.get().strip()
            
            # Parse ports
            try:
                port_list = [int(p.strip()) for p in ports.split(',')]
            except ValueError:
                messagebox.showerror("Error", "Invalid port format")
                return
                
            # Start scan in background thread
            self.scan_thread = threading.Thread(
                target=self._run_network_scan,
                args=(ip_range, scan_type, port_list)
            )
            self.scan_thread.daemon = True
            self.scan_thread.start()
            
            # Update UI
            self.start_scan_btn.config(state=tk.DISABLED)
            self.stop_scan_btn.config(state=tk.NORMAL)
            self.pause_scan_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Scanning...")
            
            # Log scan activity
            self.audit_logger.log_scan_activity(
                user_id="USER",  # Replace with actual user ID
                scan_type="network",
                target_range=ip_range,
                scan_parameters={
                    'scan_type': scan_type,
                    'ports': port_list
                },
                results_count=0
            )
            
        except Exception as e:
            self.logger.error(f"Failed to start network scan: {e}")
            messagebox.showerror("Error", f"Failed to start scan: {e}")
            
    def _run_network_scan(self, ip_range: str, scan_type: str, ports: List[int]):
        """Run the network scan in background thread."""
        try:
            # Perform the scan
            results = self.network_scanner.scan_network_range(
                ip_range=ip_range,
                scan_type=scan_type,
                ports=ports
            )
            
            # Update UI with results
            self.parent.after(0, self._scan_completed, results)
            
        except Exception as e:
            self.logger.error(f"Scan failed: {e}")
            self.parent.after(0, self._scan_failed, str(e))
            
    def _scan_completed(self, results: List[Dict[str, Any]]):
        """Handle scan completion."""
        try:
            # Clear previous results
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
                
            # Add new results
            for result in results:
                self.results_tree.insert('', tk.END, values=(
                    result.get('ip', ''),
                    result.get('hostname', ''),
                    result.get('status', ''),
                    ', '.join(map(str, result.get('open_ports', []))),
                    ', '.join(result.get('services', [])),
                    result.get('miner_type', ''),
                    f"{result.get('confidence', 0)}%"
                ))
                
            # Update UI
            self.start_scan_btn.config(state=tk.NORMAL)
            self.stop_scan_btn.config(state=tk.DISABLED)
            self.pause_scan_btn.config(state=tk.DISABLED)
            self.status_label.config(text=f"Scan completed. Found {len(results)} devices.")
            self.progress_var.set(100)
            
            # Store results
            self.scan_results = results
            
        except Exception as e:
            self.logger.error(f"Failed to handle scan completion: {e}")
            
    def _scan_failed(self, error_message: str):
        """Handle scan failure."""
        try:
            # Update UI
            self.start_scan_btn.config(state=tk.NORMAL)
            self.stop_scan_btn.config(state=tk.DISABLED)
            self.pause_scan_btn.config(state=tk.DISABLED)
            self.status_label.config(text=f"Scan failed: {error_message}")
            
            messagebox.showerror("Scan Failed", f"Scan failed: {error_message}")
            
        except Exception as e:
            self.logger.error(f"Failed to handle scan failure: {e}")
            
    def _stop_scan(self):
        """Stop the current scan."""
        try:
            if self.scan_thread and self.scan_thread.is_alive():
                # Signal scan to stop
                self.current_scan = None
                
            # Update UI
            self.start_scan_btn.config(state=tk.NORMAL)
            self.stop_scan_btn.config(state=tk.DISABLED)
            self.pause_scan_btn.config(state=tk.DISABLED)
            self.status_label.config(text="Scan stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop scan: {e}")
            
    def _pause_scan(self):
        """Pause the current scan."""
        try:
            # Update UI
            self.pause_scan_btn.config(text="Resume", command=self._resume_scan)
            self.status_label.config(text="Scan paused")
            
        except Exception as e:
            self.logger.error(f"Failed to pause scan: {e}")
            
    def _resume_scan(self):
        """Resume the current scan."""
        try:
            # Update UI
            self.pause_scan_btn.config(text="Pause", command=self._pause_scan)
            self.status_label.config(text="Scanning...")
            
        except Exception as e:
            self.logger.error(f"Failed to resume scan: {e}")
            
    def _load_isp_data_for_province(self):
        """Load ISP data for the selected province."""
        try:
            selected_province = self.province_var.get()
            if not selected_province:
                messagebox.showwarning("Warning", "Please select a province first")
                return
                
            # Get province code
            province = self.geographic_data_manager.get_province_by_name(selected_province)
            if not province:
                messagebox.showerror("Error", "Province not found")
                return
                
            # Get ISP coverage for the province
            isp_coverage = self.isp_data_manager.get_isp_coverage_by_province(province['code'])
            
            # Clear previous data
            for item in self.isp_tree.get_children():
                self.isp_tree.delete(item)
                
            # Add ISP data
            for isp in isp_coverage:
                self.isp_tree.insert('', tk.END, values=(
                    isp.get('name', ''),
                    isp.get('asn', ''),
                    isp.get('ip_ranges_count', 0),
                    f"{isp.get('coverage_percentage', 0)}%",
                    isp.get('status', 'Active')
                ))
                
            self.status_label.config(text=f"Loaded ISP data for {selected_province}")
            
        except Exception as e:
            self.logger.error(f"Failed to load ISP data: {e}")
            messagebox.showerror("Error", f"Failed to load ISP data: {e}")
            
    def _start_geographic_scan(self):
        """Start a geographic scan."""
        try:
            selected_province = self.province_var.get()
            selected_cities = self.city_listbox.curselection()
            
            if not selected_province:
                messagebox.showwarning("Warning", "Please select a province")
                return
                
            if not selected_cities:
                messagebox.showwarning("Warning", "Please select at least one city")
                return
                
            # Get selected city names
            city_names = [self.city_listbox.get(i) for i in selected_cities]
            
            # Start geographic scan
            self.status_label.config(text=f"Starting geographic scan for {selected_province}")
            
            # Log scan activity
            self.audit_logger.log_scan_activity(
                user_id="USER",  # Replace with actual user ID
                scan_type="geographic",
                target_range=f"{selected_province}: {', '.join(city_names)}",
                scan_parameters={
                    'province': selected_province,
                    'cities': city_names
                },
                results_count=0
            )
            
        except Exception as e:
            self.logger.error(f"Failed to start geographic scan: {e}")
            messagebox.showerror("Error", f"Failed to start geographic scan: {e}")
            
    def _load_ip_ranges_for_isp(self):
        """Load IP ranges for the selected ISP."""
        try:
            selected_isp = self.isp_var.get()
            if not selected_isp:
                messagebox.showwarning("Warning", "Please select an ISP first")
                return
                
            # Get ISP code
            isp = self.isp_data_manager.get_isp_by_name(selected_isp)
            if not isp:
                messagebox.showerror("Error", "ISP not found")
                return
                
            # Get IP ranges for the ISP
            ip_ranges = self.isp_data_manager.get_ip_ranges_by_isp(isp['code'])
            
            # Clear previous data
            for item in self.ranges_tree.get_children():
                self.ranges_tree.delete(item)
                
            # Add IP range data
            for ip_range in ip_ranges:
                self.ranges_tree.insert('', tk.END, values=(
                    ip_range.get('range', ''),
                    ip_range.get('asn', ''),
                    ip_range.get('location', ''),
                    ip_range.get('status', 'Active'),
                    ip_range.get('device_count', 0)
                ))
                
            self.status_label.config(text=f"Loaded IP ranges for {selected_isp}")
            
        except Exception as e:
            self.logger.error(f"Failed to load IP ranges: {e}")
            messagebox.showerror("Error", f"Failed to load IP ranges: {e}")
            
    def _start_isp_scan(self):
        """Start an ISP scan."""
        try:
            selected_isp = self.isp_var.get()
            if not selected_isp:
                messagebox.showwarning("Warning", "Please select an ISP first")
                return
                
            # Get selected IP ranges
            selected_ranges = self.ranges_tree.selection()
            if not selected_ranges:
                messagebox.showwarning("Warning", "Please select IP ranges to scan")
                return
                
            # Get range data
            ranges_to_scan = []
            for item in selected_ranges:
                values = self.ranges_tree.item(item)['values']
                ranges_to_scan.append(values[0])  # IP range
                
            # Start ISP scan
            self.status_label.config(text=f"Starting ISP scan for {selected_isp}")
            
            # Log scan activity
            self.audit_logger.log_scan_activity(
                user_id="USER",  # Replace with actual user ID
                scan_type="isp",
                target_range=f"{selected_isp}: {', '.join(ranges_to_scan)}",
                scan_parameters={
                    'isp': selected_isp,
                    'ranges': ranges_to_scan
                },
                results_count=0
            )
            
        except Exception as e:
            self.logger.error(f"Failed to start ISP scan: {e}")
            messagebox.showerror("Error", f"Failed to start ISP scan: {e}")
            
    def _toggle_monitoring(self):
        """Toggle continuous monitoring."""
        try:
            if self.monitoring_var.get():
                # Start monitoring
                interval = int(self.monitor_interval_var.get())
                self.status_label.config(text=f"Monitoring enabled (interval: {interval} minutes)")
                
                # Log monitoring start
                self.audit_logger.log_system_event(
                    event_type="monitoring_started",
                    description="Continuous monitoring enabled",
                    system_component="scan_interface"
                )
            else:
                # Stop monitoring
                self.status_label.config(text="Monitoring disabled")
                
                # Log monitoring stop
                self.audit_logger.log_system_event(
                    event_type="monitoring_stopped",
                    description="Continuous monitoring disabled",
                    system_component="scan_interface"
                )
                
        except Exception as e:
            self.logger.error(f"Failed to toggle monitoring: {e}")
            
    def _export_scan_results(self):
        """Export scan results to file."""
        try:
            if not self.scan_results:
                messagebox.showwarning("Warning", "No scan results to export")
                return
                
            # Ask user for file location
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                if filename.endswith('.json'):
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(self.scan_results, f, indent=2, ensure_ascii=False)
                elif filename.endswith('.csv'):
                    import csv
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        if self.scan_results:
                            writer = csv.DictWriter(f, fieldnames=self.scan_results[0].keys())
                            writer.writeheader()
                            writer.writerows(self.scan_results)
                            
                messagebox.showinfo("Success", f"Results exported to {filename}")
                
                # Log export activity
                self.audit_logger.log_data_access(
                    user_id="USER",  # Replace with actual user ID
                    data_type="scan_results",
                    access_method="export",
                    record_count=len(self.scan_results)
                )
                
        except Exception as e:
            self.logger.error(f"Failed to export scan results: {e}")
            messagebox.showerror("Error", f"Failed to export results: {e}")
            
    def _clear_scan_results(self):
        """Clear scan results."""
        try:
            # Clear treeview
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
                
            # Clear stored results
            self.scan_results = []
            
            # Update status
            self.status_label.config(text="Scan results cleared")
            
        except Exception as e:
            self.logger.error(f"Failed to clear scan results: {e}")
            
    def _view_device_details(self):
        """View details of selected device."""
        try:
            selected_item = self.results_tree.selection()
            if not selected_item:
                messagebox.showwarning("Warning", "Please select a device to view details")
                return
                
            # Get device data
            values = self.results_tree.item(selected_item[0])['values']
            device_ip = values[0]
            
            # Find device in scan results
            device = None
            for result in self.scan_results:
                if result.get('ip') == device_ip:
                    device = result
                    break
                    
            if device:
                # Show device details dialog
                self._show_device_details_dialog(device)
            else:
                messagebox.showerror("Error", "Device details not found")
                
        except Exception as e:
            self.logger.error(f"Failed to view device details: {e}")
            messagebox.showerror("Error", f"Failed to view device details: {e}")
            
    def _show_device_details_dialog(self, device: Dict[str, Any]):
        """Show device details dialog."""
        try:
            # Create details window
            details_window = tk.Toplevel(self.parent)
            details_window.title(f"Device Details - {device.get('ip', 'Unknown')}")
            details_window.geometry("600x400")
            details_window.transient(self.parent)
            details_window.grab_set()
            
            # Create text widget for details
            text_widget = tk.Text(details_window, wrap=tk.WORD, padx=10, pady=10)
            text_widget.pack(fill=tk.BOTH, expand=True)
            
            # Format device details
            details_text = f"""
Device Details:
==============

IP Address: {device.get('ip', 'Unknown')}
Hostname: {device.get('hostname', 'Unknown')}
Status: {device.get('status', 'Unknown')}

Open Ports: {', '.join(map(str, device.get('open_ports', [])))}
Services: {', '.join(device.get('services', []))}

Miner Detection:
===============
Type: {device.get('miner_type', 'Unknown')}
Confidence: {device.get('confidence', 0)}%
Detection Method: {device.get('detection_method', 'Unknown')}

Network Information:
===================
ISP: {device.get('isp', 'Unknown')}
ASN: {device.get('asn', 'Unknown')}
Location: {device.get('location', 'Unknown')}

VPN/Proxy Detection:
===================
VPN Detected: {device.get('vpn_detected', False)}
Proxy Detected: {device.get('proxy_detected', False)}
Original IP: {device.get('original_ip', 'Unknown')}

Additional Information:
======================
Scan Time: {device.get('scan_time', 'Unknown')}
Last Seen: {device.get('last_seen', 'Unknown')}
Notes: {device.get('notes', 'None')}
"""
            
            text_widget.insert(tk.END, details_text)
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            self.logger.error(f"Failed to show device details dialog: {e}")
            
    def _export_isp_data(self):
        """Export ISP data to file."""
        try:
            # Get ISP data
            isps = self.isp_data_manager.get_isps()
            
            # Ask user for file location
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                if filename.endswith('.json'):
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(isps, f, indent=2, ensure_ascii=False)
                elif filename.endswith('.csv'):
                    import csv
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        if isps:
                            writer = csv.DictWriter(f, fieldnames=isps[0].keys())
                            writer.writeheader()
                            writer.writerows(isps)
                            
                messagebox.showinfo("Success", f"ISP data exported to {filename}")
                
        except Exception as e:
            self.logger.error(f"Failed to export ISP data: {e}")
            messagebox.showerror("Error", f"Failed to export ISP data: {e}")