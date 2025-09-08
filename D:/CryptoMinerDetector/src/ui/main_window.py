#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Window for CryptoMinerDetector
Main GUI interface for the cryptocurrency miner detection system.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

class MainWindow:
    """
    Main window for the CryptoMinerDetector application.
    Provides the primary interface for all system operations.
    """
    
    def __init__(self, root, config, db_manager, security_manager, audit_logger, geo_manager, isp_manager):
        """
        Initialize the main window.
        
        Args:
            root: Tkinter root window
            config: Configuration manager
            db_manager: Database manager
            security_manager: Security manager
            audit_logger: Audit logger
            geo_manager: Geographic data manager
            isp_manager: ISP data manager
        """
        self.root = root
        self.config = config
        self.db_manager = db_manager
        self.security_manager = security_manager
        self.audit_logger = audit_logger
        self.geo_manager = geo_manager
        self.isp_manager = isp_manager
        self.logger = logging.getLogger(__name__)
        
        # Initialize UI components
        self._setup_ui()
        
        # Load initial data
        self._load_initial_data()
        
    def _setup_ui(self):
        """Setup the main UI components."""
        # Configure main window
        self.root.title("CryptoMinerDetector - National Security System")
        self.root.configure(bg='#2c3e50')
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self._create_dashboard_tab()
        self._create_scan_tab()
        self._create_reports_tab()
        self._create_maps_tab()
        self._create_settings_tab()
        
        # Create status bar
        self._create_status_bar()
        
        # Create menu bar
        self._create_menu_bar()
        
    def _create_dashboard_tab(self):
        """Create the dashboard tab."""
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        
        # Dashboard title
        title_label = ttk.Label(self.dashboard_frame, text="CryptoMinerDetector Dashboard", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(self.dashboard_frame, text="System Statistics")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Statistics labels
        self.total_devices_label = ttk.Label(stats_frame, text="Total Devices: 0")
        self.total_devices_label.pack(anchor=tk.W, padx=10, pady=2)
        
        self.miners_detected_label = ttk.Label(stats_frame, text="Miners Detected: 0")
        self.miners_detected_label.pack(anchor=tk.W, padx=10, pady=2)
        
        self.vpn_detected_label = ttk.Label(stats_frame, text="VPN Detected: 0")
        self.vpn_detected_label.pack(anchor=tk.W, padx=10, pady=2)
        
        self.scans_last_7_days_label = ttk.Label(stats_frame, text="Scans Last 7 Days: 0")
        self.scans_last_7_days_label.pack(anchor=tk.W, padx=10, pady=2)
        
        # Quick actions frame
        actions_frame = ttk.LabelFrame(self.dashboard_frame, text="Quick Actions")
        actions_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Quick action buttons
        ttk.Button(actions_frame, text="Start New Scan", 
                  command=self._start_new_scan).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(actions_frame, text="View Reports", 
                  command=self._view_reports).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(actions_frame, text="Open Maps", 
                  command=self._open_maps).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(actions_frame, text="Refresh Statistics", 
                  command=self._refresh_statistics).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Recent activity frame
        activity_frame = ttk.LabelFrame(self.dashboard_frame, text="Recent Activity")
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Activity listbox
        self.activity_listbox = tk.Listbox(activity_frame, height=10)
        self.activity_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def _create_scan_tab(self):
        """Create the scan tab."""
        self.scan_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.scan_frame, text="Network Scanning")
        
        # Scan configuration frame
        config_frame = ttk.LabelFrame(self.scan_frame, text="Scan Configuration")
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Geographic selection
        geo_frame = ttk.Frame(config_frame)
        geo_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(geo_frame, text="Province:").pack(side=tk.LEFT)
        self.province_var = tk.StringVar()
        self.province_combo = ttk.Combobox(geo_frame, textvariable=self.province_var, state="readonly")
        self.province_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(geo_frame, text="City:").pack(side=tk.LEFT, padx=(20, 0))
        self.city_var = tk.StringVar()
        self.city_combo = ttk.Combobox(geo_frame, textvariable=self.city_var, state="readonly")
        self.city_combo.pack(side=tk.LEFT, padx=5)
        
        # ISP selection
        isp_frame = ttk.Frame(config_frame)
        isp_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(isp_frame, text="ISP:").pack(side=tk.LEFT)
        self.isp_var = tk.StringVar()
        self.isp_combo = ttk.Combobox(isp_frame, textvariable=self.isp_var, state="readonly")
        self.isp_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(isp_frame, text="Load ISP Data", 
                  command=self._load_isp_data).pack(side=tk.LEFT, padx=5)
        
        # IP range selection
        range_frame = ttk.Frame(config_frame)
        range_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(range_frame, text="IP Range:").pack(side=tk.LEFT)
        self.ip_range_var = tk.StringVar()
        self.ip_range_entry = ttk.Entry(range_frame, textvariable=self.ip_range_var, width=30)
        self.ip_range_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(range_frame, text="Calculate Range", 
                  command=self._calculate_ip_range).pack(side=tk.LEFT, padx=5)
        
        # Scan type selection
        scan_type_frame = ttk.Frame(config_frame)
        scan_type_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(scan_type_frame, text="Scan Type:").pack(side=tk.LEFT)
        self.scan_type_var = tk.StringVar(value="comprehensive")
        scan_types = ["quick", "comprehensive", "stealth"]
        for scan_type in scan_types:
            ttk.Radiobutton(scan_type_frame, text=scan_type.title(), 
                           variable=self.scan_type_var, value=scan_type).pack(side=tk.LEFT, padx=5)
        
        # Scan control frame
        control_frame = ttk.LabelFrame(self.scan_frame, text="Scan Control")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Control buttons
        self.start_scan_button = ttk.Button(control_frame, text="Start Scan", 
                                           command=self._start_scan)
        self.start_scan_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.stop_scan_button = ttk.Button(control_frame, text="Stop Scan", 
                                         command=self._stop_scan, state=tk.DISABLED)
        self.stop_scan_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.pause_scan_button = ttk.Button(control_frame, text="Pause Scan", 
                                          command=self._pause_scan, state=tk.DISABLED)
        self.pause_scan_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(self.scan_frame, text="Scan Progress")
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)
        
        # Progress label
        self.progress_label = ttk.Label(progress_frame, text="Ready to scan")
        self.progress_label.pack(pady=5)
        
        # Results frame
        results_frame = ttk.LabelFrame(self.scan_frame, text="Scan Results")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Results treeview
        columns = ('IP', 'MAC', 'ISP', 'Province', 'Miner Ports', 'VPN', 'Status')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings')
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=100)
            
        self.results_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar for results
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, 
                                        command=self.results_tree.yview)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)
        
    def _create_reports_tab(self):
        """Create the reports tab."""
        self.reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_frame, text="Reports")
        
        # Reports title
        title_label = ttk.Label(self.reports_frame, text="Reports and Analytics", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Report generation frame
        gen_frame = ttk.LabelFrame(self.reports_frame, text="Generate Reports")
        gen_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Report type selection
        ttk.Label(gen_frame, text="Report Type:").pack(anchor=tk.W, padx=10, pady=2)
        self.report_type_var = tk.StringVar(value="summary")
        report_types = ["summary", "detailed", "geographic", "isp", "mining_activity"]
        for report_type in report_types:
            ttk.Radiobutton(gen_frame, text=report_type.replace('_', ' ').title(), 
                           variable=self.report_type_var, value=report_type).pack(anchor=tk.W, padx=20)
        
        # Date range selection
        date_frame = ttk.Frame(gen_frame)
        date_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(date_frame, text="Date Range:").pack(side=tk.LEFT)
        self.date_from_var = tk.StringVar()
        self.date_from_entry = ttk.Entry(date_frame, textvariable=self.date_from_var, width=15)
        self.date_from_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(date_frame, text="to").pack(side=tk.LEFT)
        self.date_to_var = tk.StringVar()
        self.date_to_entry = ttk.Entry(date_frame, textvariable=self.date_to_var, width=15)
        self.date_to_entry.pack(side=tk.LEFT, padx=5)
        
        # Generate button
        ttk.Button(gen_frame, text="Generate Report", 
                  command=self._generate_report).pack(pady=10)
        
        # Reports list frame
        list_frame = ttk.LabelFrame(self.reports_frame, text="Available Reports")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Reports listbox
        self.reports_listbox = tk.Listbox(list_frame, height=15)
        self.reports_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Report actions frame
        actions_frame = ttk.Frame(list_frame)
        actions_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(actions_frame, text="View Report", 
                  command=self._view_report).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(actions_frame, text="Export Report", 
                  command=self._export_report).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(actions_frame, text="Delete Report", 
                  command=self._delete_report).pack(side=tk.LEFT, padx=5)
        
    def _create_maps_tab(self):
        """Create the maps tab."""
        self.maps_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.maps_frame, text="Maps")
        
        # Maps title
        title_label = ttk.Label(self.maps_frame, text="Geographic Visualization", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Map controls frame
        controls_frame = ttk.LabelFrame(self.maps_frame, text="Map Controls")
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Map type selection
        ttk.Label(controls_frame, text="Map Type:").pack(side=tk.LEFT)
        self.map_type_var = tk.StringVar(value="devices")
        map_types = ["devices", "miners", "isp_coverage", "vpn_detection"]
        for map_type in map_types:
            ttk.Radiobutton(controls_frame, text=map_type.replace('_', ' ').title(), 
                           variable=self.map_type_var, value=map_type).pack(side=tk.LEFT, padx=5)
        
        # Generate map button
        ttk.Button(controls_frame, text="Generate Map", 
                  command=self._generate_map).pack(side=tk.RIGHT, padx=10)
        
        # Map display frame
        map_display_frame = ttk.LabelFrame(self.maps_frame, text="Map Display")
        map_display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Map canvas (placeholder for actual map display)
        self.map_canvas = tk.Canvas(map_display_frame, bg='white', height=400)
        self.map_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Map legend frame
        legend_frame = ttk.LabelFrame(self.maps_frame, text="Legend")
        legend_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Legend items
        legend_items = [
            ("Blue", "Your Location"),
            ("Red", "Mining Device"),
            ("Green", "Regular Device"),
            ("Orange", "VPN Detected"),
            ("Purple", "High Confidence Miner")
        ]
        
        for color, description in legend_items:
            item_frame = ttk.Frame(legend_frame)
            item_frame.pack(side=tk.LEFT, padx=10, pady=5)
            
            color_label = tk.Label(item_frame, text="■", fg=color, font=('Arial', 16))
            color_label.pack(side=tk.LEFT)
            
            desc_label = ttk.Label(item_frame, text=description)
            desc_label.pack(side=tk.LEFT, padx=5)
        
    def _create_settings_tab(self):
        """Create the settings tab."""
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        
        # Settings title
        title_label = ttk.Label(self.settings_frame, text="System Settings", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # API Keys frame
        api_frame = ttk.LabelFrame(self.settings_frame, text="API Configuration")
        api_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # API key entries
        api_keys = [
            ("Shodan API Key:", "shodan_api_key"),
            ("Censys API ID:", "censys_api_id"),
            ("Censys API Secret:", "censys_api_secret"),
            ("IPInfo Token:", "ipinfo_token"),
            ("Telecom API Key:", "telecom_api_key")
        ]
        
        self.api_vars = {}
        for label, key in api_keys:
            frame = ttk.Frame(api_frame)
            frame.pack(fill=tk.X, padx=10, pady=2)
            
            ttk.Label(frame, text=label).pack(side=tk.LEFT)
            var = tk.StringVar()
            entry = ttk.Entry(frame, textvariable=var, width=50, show="*")
            entry.pack(side=tk.LEFT, padx=5)
            
            self.api_vars[key] = var
        
        # Save API keys button
        ttk.Button(api_frame, text="Save API Keys", 
                  command=self._save_api_keys).pack(pady=10)
        
        # System settings frame
        sys_frame = ttk.LabelFrame(self.settings_frame, text="System Settings")
        sys_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # System settings
        settings = [
            ("Max Concurrent Scans:", "max_concurrent_scans", "int"),
            ("Rate Limit (per second):", "rate_limit_per_second", "int"),
            ("Scan Timeout (seconds):", "default_timeout", "int"),
            ("Session Timeout (minutes):", "session_timeout_minutes", "int"),
            ("Max Memory Usage (GB):", "max_memory_usage_gb", "int"),
            ("CPU Usage Limit (%):", "cpu_usage_limit_percent", "int")
        ]
        
        self.settings_vars = {}
        for label, key, var_type in settings:
            frame = ttk.Frame(sys_frame)
            frame.pack(fill=tk.X, padx=10, pady=2)
            
            ttk.Label(frame, text=label).pack(side=tk.LEFT)
            var = tk.StringVar()
            entry = ttk.Entry(frame, textvariable=var, width=20)
            entry.pack(side=tk.LEFT, padx=5)
            
            self.settings_vars[key] = (var, var_type)
        
        # Save settings button
        ttk.Button(sys_frame, text="Save Settings", 
                  command=self._save_settings).pack(pady=10)
        
        # Database management frame
        db_frame = ttk.LabelFrame(self.settings_frame, text="Database Management")
        db_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(db_frame, text="Backup Database", 
                  command=self._backup_database).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(db_frame, text="Restore Database", 
                  command=self._restore_database).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(db_frame, text="Cleanup Old Data", 
                  command=self._cleanup_database).pack(side=tk.LEFT, padx=5, pady=5)
        
    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.time_label = ttk.Label(self.status_bar, text="")
        self.time_label.pack(side=tk.RIGHT, padx=5)
        
        # Update time
        self._update_time()
        
    def _create_menu_bar(self):
        """Create the menu bar."""
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Scan", command=self._start_new_scan)
        file_menu.add_command(label="Open Report", command=self._open_report)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._exit_application)
        
        # Tools menu
        tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Network Scanner", command=self._open_scanner)
        tools_menu.add_command(label="Report Generator", command=self._open_reports)
        tools_menu.add_command(label="Map Viewer", command=self._open_maps)
        
        # Help menu
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Manual", command=self._show_manual)
        help_menu.add_command(label="About", command=self._show_about)
        
    def _load_initial_data(self):
        """Load initial data for the application."""
        try:
            # Load provinces
            provinces = self.geo_manager.get_provinces()
            province_names = [p['name'] for p in provinces]
            self.province_combo['values'] = province_names
            
            # Load ISPs
            isps = self.isp_manager.get_isps()
            isp_names = [isp['name'] for isp in isps]
            self.isp_combo['values'] = isp_names
            
            # Load statistics
            self._refresh_statistics()
            
            # Load recent activity
            self._load_recent_activity()
            
        except Exception as e:
            self.logger.error(f"Failed to load initial data: {e}")
            messagebox.showerror("Error", f"Failed to load initial data: {e}")
            
    def _refresh_statistics(self):
        """Refresh system statistics."""
        try:
            stats = self.db_manager.get_statistics()
            
            self.total_devices_label.config(text=f"Total Devices: {stats.get('total_devices', 0)}")
            self.miners_detected_label.config(text=f"Miners Detected: {stats.get('miners_detected', 0)}")
            self.vpn_detected_label.config(text=f"VPN Detected: {stats.get('vpn_detected', 0)}")
            self.scans_last_7_days_label.config(text=f"Scans Last 7 Days: {stats.get('scans_last_7_days', 0)}")
            
        except Exception as e:
            self.logger.error(f"Failed to refresh statistics: {e}")
            
    def _load_recent_activity(self):
        """Load recent activity into the listbox."""
        try:
            self.activity_listbox.delete(0, tk.END)
            
            # Add some sample activity (in real implementation, get from database)
            activities = [
                "System started successfully",
                "Database initialized",
                "Configuration loaded",
                "Ready for scanning operations"
            ]
            
            for activity in activities:
                self.activity_listbox.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {activity}")
                
        except Exception as e:
            self.logger.error(f"Failed to load recent activity: {e}")
            
    def _update_time(self):
        """Update the time display in status bar."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self._update_time)
        
    # Event handlers
    def _start_new_scan(self):
        """Start a new scan."""
        self.notebook.select(1)  # Switch to scan tab
        
    def _view_reports(self):
        """View reports."""
        self.notebook.select(2)  # Switch to reports tab
        
    def _open_maps(self):
        """Open maps."""
        self.notebook.select(3)  # Switch to maps tab
        
    def _load_isp_data(self):
        """Load ISP data for selected province."""
        try:
            province = self.province_var.get()
            if province:
                coverage = self.isp_manager.get_isp_coverage_by_province(province)
                isp_names = [c['isp']['name'] for c in coverage]
                self.isp_combo['values'] = isp_names
                
        except Exception as e:
            self.logger.error(f"Failed to load ISP data: {e}")
            messagebox.showerror("Error", f"Failed to load ISP data: {e}")
            
    def _calculate_ip_range(self):
        """Calculate IP range for selected ISP."""
        try:
            isp_name = self.isp_var.get()
            if isp_name:
                ip_ranges = self.isp_manager.get_ip_ranges_by_isp(isp_name)
                if ip_ranges:
                    # Use the first range as default
                    self.ip_range_var.set(ip_ranges[0]['range'])
                    
        except Exception as e:
            self.logger.error(f"Failed to calculate IP range: {e}")
            messagebox.showerror("Error", f"Failed to calculate IP range: {e}")
            
    def _start_scan(self):
        """Start the network scan."""
        try:
            ip_range = self.ip_range_var.get()
            scan_type = self.scan_type_var.get()
            
            if not ip_range:
                messagebox.showerror("Error", "Please enter an IP range to scan")
                return
                
            # Update UI
            self.start_scan_button.config(state=tk.DISABLED)
            self.stop_scan_button.config(state=tk.NORMAL)
            self.pause_scan_button.config(state=tk.NORMAL)
            self.progress_label.config(text="Starting scan...")
            
            # Start scan in background thread
            scan_thread = threading.Thread(target=self._run_scan, args=(ip_range, scan_type))
            scan_thread.daemon = True
            scan_thread.start()
            
        except Exception as e:
            self.logger.error(f"Failed to start scan: {e}")
            messagebox.showerror("Error", f"Failed to start scan: {e}")
            
    def _run_scan(self, ip_range, scan_type):
        """Run the network scan in background thread."""
        try:
            # Import here to avoid circular imports
            from scanners.network_scanner import NetworkScanner
            
            scanner = NetworkScanner(self.config, self.db_manager)
            result = scanner.scan_network_range(ip_range, scan_type)
            
            # Update UI in main thread
            self.root.after(0, self._scan_completed, result)
            
        except Exception as e:
            self.logger.error(f"Scan failed: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Scan failed: {e}"))
            
    def _scan_completed(self, result):
        """Handle scan completion."""
        try:
            # Update UI
            self.start_scan_button.config(state=tk.NORMAL)
            self.stop_scan_button.config(state=tk.DISABLED)
            self.pause_scan_button.config(state=tk.DISABLED)
            self.progress_label.config(text="Scan completed")
            self.progress_var.set(100)
            
            # Show results
            messagebox.showinfo("Scan Complete", 
                              f"Scan completed successfully!\n"
                              f"Devices found: {result['devices_found']}\n"
                              f"Miners detected: {result['miners_detected']}")
            
            # Refresh statistics
            self._refresh_statistics()
            
        except Exception as e:
            self.logger.error(f"Failed to handle scan completion: {e}")
            
    def _stop_scan(self):
        """Stop the current scan."""
        # Implementation for stopping scan
        pass
        
    def _pause_scan(self):
        """Pause the current scan."""
        # Implementation for pausing scan
        pass
        
    def _generate_report(self):
        """Generate a report."""
        # Implementation for report generation
        pass
        
    def _view_report(self):
        """View a selected report."""
        # Implementation for viewing reports
        pass
        
    def _export_report(self):
        """Export a report."""
        # Implementation for exporting reports
        pass
        
    def _delete_report(self):
        """Delete a report."""
        # Implementation for deleting reports
        pass
        
    def _generate_map(self):
        """Generate a map."""
        # Implementation for map generation
        pass
        
    def _save_api_keys(self):
        """Save API keys to configuration."""
        # Implementation for saving API keys
        pass
        
    def _save_settings(self):
        """Save system settings."""
        # Implementation for saving settings
        pass
        
    def _backup_database(self):
        """Backup the database."""
        # Implementation for database backup
        pass
        
    def _restore_database(self):
        """Restore the database."""
        # Implementation for database restore
        pass
        
    def _cleanup_database(self):
        """Cleanup old database data."""
        # Implementation for database cleanup
        pass
        
    def _open_scanner(self):
        """Open the network scanner."""
        self.notebook.select(1)
        
    def _open_reports(self):
        """Open the reports section."""
        self.notebook.select(2)
        
    def _exit_application(self):
        """Exit the application."""
        if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
            self.root.quit()
            
    def _show_manual(self):
        """Show the user manual."""
        messagebox.showinfo("User Manual", "User manual will be displayed here.")
        
    def _show_about(self):
        """Show about dialog."""
        messagebox.showinfo("About", 
                          "CryptoMinerDetector v1.0.0\n"
                          "National Security System\n"
                          "For Government Use Only")