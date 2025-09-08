#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CryptoMinerDetector - Comprehensive Cryptocurrency Miner Detection System
National and Governmental Use Only

This system is designed for legal detection and identification of cryptocurrency
mining devices within specified geographic regions of Iran.

Author: National Security Team
License: Government Use Only
Version: 1.0.0
"""

import os
import sys
import logging
import configparser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import multiprocessing
from datetime import datetime
import json
import sqlite3
from pathlib import Path

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.config_manager import ConfigManager
from core.database_manager import DatabaseManager
from core.security_manager import SecurityManager
from core.audit_logger import AuditLogger
from ui.main_window import MainWindow
from ui.scan_interface import ScanInterface
from ui.report_interface import ReportInterface
from ui.map_interface import MapInterface
from scanners.network_scanner import NetworkScanner
from scanners.geographic_scanner import GeographicScanner
from scanners.isp_scanner import ISPScanner
from analyzers.miner_analyzer import MinerAnalyzer
from analyzers.vpn_detector import VPNDetector
from utils.geographic_data import GeographicDataManager
from utils.isp_data import ISPDataManager

class CryptoMinerDetector:
    """
    Main application class for the CryptoMinerDetector system.
    """
    
    def __init__(self):
        """Initialize the main application."""
        self.config_manager = None
        self.database_manager = None
        self.security_manager = None
        self.audit_logger = None
        self.root = None
        self.main_window = None
        
        # Initialize logging
        self._setup_logging()
        
        # Load configuration
        self._load_configuration()
        
        # Initialize core components
        self._initialize_core_components()
        
        # Setup GUI
        self._setup_gui()
        
    def _setup_logging(self):
        """Setup application logging."""
        log_dir = Path("D:/CryptoMinerDetector/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "crypto_miner_detector.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("CryptoMinerDetector application starting...")
        
    def _load_configuration(self):
        """Load application configuration."""
        try:
            config_path = Path("D:/CryptoMinerDetector/config/config.ini")
            if not config_path.exists():
                self.logger.error(f"Configuration file not found: {config_path}")
                messagebox.showerror("Error", "Configuration file not found!")
                sys.exit(1)
                
            self.config_manager = ConfigManager(config_path)
            self.logger.info("Configuration loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            messagebox.showerror("Error", f"Failed to load configuration: {e}")
            sys.exit(1)
            
    def _initialize_core_components(self):
        """Initialize core system components."""
        try:
            # Initialize core managers
            self.config_manager = ConfigManager()
            self.database_manager = DatabaseManager(self.config_manager)
            self.security_manager = SecurityManager(self.config_manager)
            self.audit_logger = AuditLogger(self.config_manager, self.database_manager)
            
            # Initialize data managers
            self.geographic_data_manager = GeographicDataManager(self.config_manager)
            self.isp_data_manager = ISPDataManager(self.config_manager)
            
            # Initialize scanners
            self.network_scanner = NetworkScanner(self.config_manager, self.database_manager, self.audit_logger)
            self.geographic_scanner = GeographicScanner(self.config_manager, self.database_manager, 
                                                       self.network_scanner, self.geographic_data_manager, 
                                                       self.isp_data_manager, self.audit_logger)
            self.isp_scanner = ISPScanner(self.config_manager, self.database_manager, 
                                         self.network_scanner, self.isp_data_manager, self.audit_logger)
            
            # Initialize analyzers
            self.miner_analyzer = MinerAnalyzer(self.config_manager, self.database_manager, self.audit_logger)
            self.vpn_detector = VPNDetector(self.config_manager, self.database_manager, self.audit_logger)
            
            self.logger.info("Core components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize core components: {e}")
            messagebox.showerror("Error", f"Failed to initialize core components: {e}")
            sys.exit(1)
            
    def _setup_gui(self):
        """Setup the main GUI window."""
        try:
            self.root = tk.Tk()
            self.root.title("CryptoMinerDetector - National Security System")
            self.root.geometry("1400x900")
            self.root.configure(bg='#2c3e50')
            
            # Set window icon
            icon_path = Path("D:/CryptoMinerDetector/assets/icon.ico")
            if icon_path.exists():
                self.root.iconbitmap(icon_path)
                
            # Create main window
            self.main_window = MainWindow(
                self.root,
                self.config_manager,
                self.database_manager,
                self.security_manager,
                self.audit_logger,
                self.geographic_data_manager,
                self.isp_data_manager
            )
            
            # Setup window close handler
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
            
            self.logger.info("GUI setup completed successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to setup GUI: {e}")
            messagebox.showerror("Error", f"Failed to setup GUI: {e}")
            sys.exit(1)
            
    def _on_closing(self):
        """Handle application closing."""
        try:
            # Log the closing event
            self.audit_logger.log_system_event(
                event_type="application_close",
                description="Application closed by user",
                system_component="main"
            )
            
            # Cleanup resources
            if self.database_manager:
                self.database_manager.close()
                
            # Destroy the window
            if self.root:
                self.root.destroy()
                
            self.logger.info("Application closed successfully")
            
        except Exception as e:
            self.logger.error(f"Error during application closing: {e}")
            
    def run(self):
        """Run the main application."""
        try:
            self.logger.info("Starting CryptoMinerDetector application")
            
            # Log application start
            self.audit_logger.log_system_event(
                event_type="application_start",
                description="Application started successfully",
                system_component="main"
            )
            
            # Start the GUI main loop
            self.root.mainloop()
            
        except Exception as e:
            self.logger.error(f"Application runtime error: {e}")
            messagebox.showerror("Runtime Error", f"Application runtime error: {e}")
            
def main():
    """Main entry point for the application."""
    try:
        # Check if running with administrative privileges
        if os.name == 'nt':  # Windows
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                messagebox.showerror(
                    "Administrative Rights Required",
                    "This application requires administrative privileges to run properly.\n"
                    "Please run as Administrator."
                )
                sys.exit(1)
                
        # Create and run the application
        app = CryptoMinerDetector()
        app.run()
        
    except Exception as e:
        logging.error(f"Fatal error in main: {e}")
        messagebox.showerror("Fatal Error", f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()