#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Report Interface for CryptoMinerDetector
GUI interface for generating and managing reports.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import os

class ReportInterface:
    """
    GUI interface for generating and managing reports.
    Provides report generation, export, and management capabilities.
    """
    
    def __init__(self, parent, config, database_manager, audit_logger):
        """
        Initialize the report interface.
        
        Args:
            parent: Parent window
            config: Configuration manager
            database_manager: Database manager
            audit_logger: Audit logger instance
        """
        self.parent = parent
        self.config = config
        self.db_manager = database_manager
        self.audit_logger = audit_logger
        self.logger = logging.getLogger(__name__)
        
        # Create the interface
        self._create_interface()
        
    def _create_interface(self):
        """Create the report interface components."""
        # Main frame
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Report configuration frame
        config_frame = ttk.LabelFrame(self.main_frame, text="Report Configuration", padding=10)
        config_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Report type selection
        ttk.Label(config_frame, text="Report Type:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.report_type_var = tk.StringVar(value="scan_summary")
        report_type_combo = ttk.Combobox(config_frame, textvariable=self.report_type_var,
                                       values=["scan_summary", "device_details", "audit_log", "compliance"],
                                       state="readonly", width=20)
        report_type_combo.grid(row=0, column=1, sticky=tk.W, pady=2, padx=5)
        
        # Date range selection
        ttk.Label(config_frame, text="Date Range:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.date_range_var = tk.StringVar(value="last_7_days")
        date_range_combo = ttk.Combobox(config_frame, textvariable=self.date_range_var,
                                      values=["last_24_hours", "last_7_days", "last_30_days", "custom"],
                                      state="readonly", width=20)
        date_range_combo.grid(row=1, column=1, sticky=tk.W, pady=2, padx=5)
        
        # Custom date inputs
        self.custom_date_frame = ttk.Frame(config_frame)
        self.custom_date_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        ttk.Label(self.custom_date_frame, text="From:").pack(side=tk.LEFT)
        self.start_date_var = tk.StringVar()
        self.start_date_entry = ttk.Entry(self.custom_date_frame, textvariable=self.start_date_var, width=12)
        self.start_date_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.custom_date_frame, text="To:").pack(side=tk.LEFT, padx=5)
        self.end_date_var = tk.StringVar()
        self.end_date_entry = ttk.Entry(self.custom_date_frame, textvariable=self.end_date_var, width=12)
        self.end_date_entry.pack(side=tk.LEFT, padx=5)
        
        # Initially hide custom date frame
        self.custom_date_frame.grid_remove()
        
        # Bind date range selection
        date_range_combo.bind('<<ComboboxSelected>>', self._on_date_range_selected)
        
        # Report controls frame
        controls_frame = ttk.Frame(self.main_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Generate and export buttons
        ttk.Button(controls_frame, text="Generate Report", 
                  command=self._generate_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Export Report", 
                  command=self._export_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="View Report", 
                  command=self._view_report).pack(side=tk.LEFT, padx=5)
        
        # Reports list frame
        reports_frame = ttk.LabelFrame(self.main_frame, text="Generated Reports", padding=10)
        reports_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Reports treeview
        columns = ("Name", "Type", "Date", "Size", "Status")
        self.reports_tree = ttk.Treeview(reports_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.reports_tree.heading(col, text=col)
            self.reports_tree.column(col, width=120)
            
        reports_scrollbar = ttk.Scrollbar(reports_frame, orient=tk.VERTICAL, 
                                        command=self.reports_tree.yview)
        self.reports_tree.configure(yscrollcommand=reports_scrollbar.set)
        
        self.reports_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        reports_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load existing reports
        self._load_reports()
        
    def _on_date_range_selected(self, event=None):
        """Handle date range selection."""
        selected_range = self.date_range_var.get()
        if selected_range == "custom":
            self.custom_date_frame.grid()
        else:
            self.custom_date_frame.grid_remove()
            
    def _generate_report(self):
        """Generate a new report."""
        try:
            report_type = self.report_type_var.get()
            date_range = self.date_range_var.get()
            
            # Get date range
            start_date, end_date = self._get_date_range(date_range)
            
            # Generate report based on type
            if report_type == "scan_summary":
                report_data = self._generate_scan_summary_report(start_date, end_date)
            elif report_type == "device_details":
                report_data = self._generate_device_details_report(start_date, end_date)
            elif report_type == "audit_log":
                report_data = self._generate_audit_log_report(start_date, end_date)
            elif report_type == "compliance":
                report_data = self._generate_compliance_report(start_date, end_date)
            else:
                messagebox.showerror("Error", "Invalid report type")
                return
                
            # Save report
            report_name = f"{report_type}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
            self._save_report(report_name, report_data)
            
            # Refresh reports list
            self._load_reports()
            
            messagebox.showinfo("Success", f"Report '{report_name}' generated successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            messagebox.showerror("Error", f"Failed to generate report: {e}")
            
    def _get_date_range(self, date_range: str) -> tuple:
        """Get start and end dates based on selection."""
        end_date = datetime.now()
        
        if date_range == "last_24_hours":
            start_date = end_date - timedelta(days=1)
        elif date_range == "last_7_days":
            start_date = end_date - timedelta(days=7)
        elif date_range == "last_30_days":
            start_date = end_date - timedelta(days=30)
        elif date_range == "custom":
            try:
                start_date = datetime.strptime(self.start_date_var.get(), "%Y-%m-%d")
                end_date = datetime.strptime(self.end_date_var.get(), "%Y-%m-%d")
            except ValueError:
                raise ValueError("Invalid date format. Use YYYY-MM-DD")
        else:
            start_date = end_date - timedelta(days=7)
            
        return start_date, end_date
        
    def _generate_scan_summary_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate scan summary report."""
        try:
            # Get scan statistics
            stats = self.db_manager.get_statistics()
            
            # Get recent scans
            recent_scans = self.db_manager.get_recent_scan_results(limit=100)
            
            report_data = {
                'report_type': 'scan_summary',
                'generated_at': datetime.now().isoformat(),
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'statistics': stats,
                'recent_scans': recent_scans,
                'summary': {
                    'total_devices': len(recent_scans),
                    'miners_detected': sum(1 for scan in recent_scans if scan.get('miner_type')),
                    'vpn_detected': sum(1 for scan in recent_scans if scan.get('vpn_detected')),
                    'high_confidence': sum(1 for scan in recent_scans if scan.get('confidence', 0) > 80)
                }
            }
            
            return report_data
            
        except Exception as e:
            self.logger.error(f"Failed to generate scan summary report: {e}")
            raise
            
    def _generate_device_details_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate device details report."""
        try:
            # Get all devices
            devices = self.db_manager.get_all_devices()
            
            report_data = {
                'report_type': 'device_details',
                'generated_at': datetime.now().isoformat(),
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'devices': devices,
                'summary': {
                    'total_devices': len(devices),
                    'by_province': {},
                    'by_isp': {},
                    'by_miner_type': {}
                }
            }
            
            # Generate summaries
            for device in devices:
                province = device.get('province', 'Unknown')
                isp = device.get('isp', 'Unknown')
                miner_type = device.get('miner_type', 'Unknown')
                
                report_data['summary']['by_province'][province] = report_data['summary']['by_province'].get(province, 0) + 1
                report_data['summary']['by_isp'][isp] = report_data['summary']['by_isp'].get(isp, 0) + 1
                report_data['summary']['by_miner_type'][miner_type] = report_data['summary']['by_miner_type'].get(miner_type, 0) + 1
                
            return report_data
            
        except Exception as e:
            self.logger.error(f"Failed to generate device details report: {e}")
            raise
            
    def _generate_audit_log_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate audit log report."""
        try:
            # Get audit logs
            audit_logs = self.audit_logger.get_audit_logs(start_date=start_date, end_date=end_date)
            
            # Get audit statistics
            audit_stats = self.audit_logger.get_audit_statistics(start_date=start_date, end_date=end_date)
            
            report_data = {
                'report_type': 'audit_log',
                'generated_at': datetime.now().isoformat(),
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'audit_logs': audit_logs,
                'statistics': audit_stats
            }
            
            return report_data
            
        except Exception as e:
            self.logger.error(f"Failed to generate audit log report: {e}")
            raise
            
    def _generate_compliance_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate compliance report."""
        try:
            # Get compliance data
            compliance_data = {
                'legal_requirements': {
                    'warrant_required': self.config.getboolean('LEGAL_COMPLIANCE', 'warrant_required', fallback=True),
                    'data_retention_days': self.config.getint('LEGAL_COMPLIANCE', 'data_retention_days', fallback=1095),
                    'privacy_protection': self.config.getboolean('LEGAL_COMPLIANCE', 'privacy_protection', fallback=True),
                    'audit_trail': self.config.getboolean('LEGAL_COMPLIANCE', 'audit_trail', fallback=True),
                    'chain_of_custody': self.config.getboolean('LEGAL_COMPLIANCE', 'chain_of_custody', fallback=True)
                },
                'compliance_status': {
                    'data_retention': 'COMPLIANT',
                    'audit_logging': 'COMPLIANT',
                    'privacy_protection': 'COMPLIANT',
                    'chain_of_custody': 'COMPLIANT'
                },
                'recommendations': [
                    "Maintain regular audit log reviews",
                    "Ensure data retention policies are followed",
                    "Conduct periodic compliance assessments"
                ]
            }
            
            report_data = {
                'report_type': 'compliance',
                'generated_at': datetime.now().isoformat(),
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'compliance_data': compliance_data
            }
            
            return report_data
            
        except Exception as e:
            self.logger.error(f"Failed to generate compliance report: {e}")
            raise
            
    def _save_report(self, report_name: str, report_data: Dict[str, Any]):
        """Save report to file."""
        try:
            # Create reports directory
            reports_dir = self.config.get('REPORTING', 'report_template_path')
            os.makedirs(reports_dir, exist_ok=True)
            
            # Save as JSON
            report_file = os.path.join(reports_dir, f"{report_name}.json")
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
                
            # Log report generation
            self.audit_logger.log_data_access(
                user_id="USER",  # Replace with actual user ID
                data_type="report",
                access_method="generate",
                record_count=1
            )
            
        except Exception as e:
            self.logger.error(f"Failed to save report: {e}")
            raise
            
    def _load_reports(self):
        """Load existing reports into the treeview."""
        try:
            # Clear existing items
            for item in self.reports_tree.get_children():
                self.reports_tree.delete(item)
                
            # Get reports directory
            reports_dir = self.config.get('REPORTING', 'report_template_path')
            
            if os.path.exists(reports_dir):
                for filename in os.listdir(reports_dir):
                    if filename.endswith('.json'):
                        file_path = os.path.join(reports_dir, filename)
                        file_stat = os.stat(file_path)
                        
                        # Parse report name
                        report_name = filename.replace('.json', '')
                        parts = report_name.split('_')
                        
                        if len(parts) >= 3:
                            report_type = parts[0]
                            date_str = f"{parts[1]}-{parts[2]}"
                        else:
                            report_type = "unknown"
                            date_str = "unknown"
                            
                        # Add to treeview
                        self.reports_tree.insert('', tk.END, values=(
                            filename,
                            report_type,
                            date_str,
                            f"{file_stat.st_size / 1024:.1f} KB",
                            "Available"
                        ))
                        
        except Exception as e:
            self.logger.error(f"Failed to load reports: {e}")
            
    def _export_report(self):
        """Export selected report."""
        try:
            selected_item = self.reports_tree.selection()
            if not selected_item:
                messagebox.showwarning("Warning", "Please select a report to export")
                return
                
            # Get report filename
            filename = self.reports_tree.item(selected_item[0])['values'][0]
            
            # Ask user for export location
            export_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            
            if export_path:
                # Copy report file
                reports_dir = self.config.get('REPORTING', 'report_template_path')
                source_file = os.path.join(reports_dir, filename)
                
                import shutil
                shutil.copy2(source_file, export_path)
                
                messagebox.showinfo("Success", f"Report exported to {export_path}")
                
                # Log export activity
                self.audit_logger.log_data_access(
                    user_id="USER",  # Replace with actual user ID
                    data_type="report",
                    access_method="export",
                    record_count=1
                )
                
        except Exception as e:
            self.logger.error(f"Failed to export report: {e}")
            messagebox.showerror("Error", f"Failed to export report: {e}")
            
    def _view_report(self):
        """View selected report."""
        try:
            selected_item = self.reports_tree.selection()
            if not selected_item:
                messagebox.showwarning("Warning", "Please select a report to view")
                return
                
            # Get report filename
            filename = self.reports_tree.item(selected_item[0])['values'][0]
            
            # Load and display report
            reports_dir = self.config.get('REPORTING', 'report_template_path')
            report_file = os.path.join(reports_dir, filename)
            
            with open(report_file, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
                
            # Show report in new window
            self._show_report_window(report_data, filename)
            
        except Exception as e:
            self.logger.error(f"Failed to view report: {e}")
            messagebox.showerror("Error", f"Failed to view report: {e}")
            
    def _show_report_window(self, report_data: Dict[str, Any], filename: str):
        """Show report in a new window."""
        try:
            # Create report window
            report_window = tk.Toplevel(self.parent)
            report_window.title(f"Report Viewer - {filename}")
            report_window.geometry("800x600")
            report_window.transient(self.parent)
            
            # Create text widget
            text_widget = tk.Text(report_window, wrap=tk.WORD, padx=10, pady=10)
            text_widget.pack(fill=tk.BOTH, expand=True)
            
            # Format report data
            report_text = json.dumps(report_data, indent=2, ensure_ascii=False)
            text_widget.insert(tk.END, report_text)
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            self.logger.error(f"Failed to show report window: {e}")
            
    def refresh_reports(self):
        """Refresh the reports list."""
        self._load_reports()