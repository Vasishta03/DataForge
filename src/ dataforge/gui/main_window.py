import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
from pathlib import Path
import json
import logging
from typing import Dict, Any

from dataforge.core.dataset_generator import DatasetGenerator
from dataforge.gui.components import (
    ModernFrame, StatusBar, LogViewer, 
    ProgressFrame, ConfigFrame, ResultsFrame
)
from dataforge.gui.dialogs import ProgressDialog, SystemInfoDialog, AboutDialog

class DataForgeApp:
    def __init__(self, root: tk.Tk, config_manager, app_logger):
        self.root = root
        self.config_manager = config_manager
        self.logger = app_logger
        
        # Application state
        self.generator = None
        self.current_keyword = ""
        self.generation_thread = None
        self.is_generating = False
        
        # Create StringVars
        self.rows_var = tk.StringVar(value="500")
        self.variations_var = tk.StringVar(value="6")
        
        # Setup the GUI
        self._setup_window()
        self._create_widgets()
        self._setup_layout()
        self._setup_bindings()
        
        # Initialize generator
        self._initialize_generator()
        
        self.logger.info("GUI initialized successfully")
    
    def _setup_window(self) -> None:
        self.root.title("DataForge - Synthetic Dataset Generator")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
    
    def _create_widgets(self) -> None:
        self.main_frame = ctk.CTkFrame(self.root)
        
        # Header frame
        self.header_frame = ctk.CTkFrame(self.main_frame)
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="🔬 DataForge",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Synthetic Dataset Generator",
            font=ctk.CTkFont(size=16)
        )
        
        # Create main tabview
        self.tabview = ctk.CTkTabview(self.main_frame)
        
        # Add tabs and get references
        self.generation_tab = self.tabview.add("Generation")
        self.config_tab = self.tabview.add("Configuration") 
        self.results_tab = self.tabview.add("Results")
        self.logs_tab = self.tabview.add("Logs")
        
        # Set default tab
        self.tabview.set("Generation")
        
        # Create content for each tab
        self._create_generation_content()
        self._create_config_content()
        self._create_results_content()
        self._create_logs_content()
        
        # Status bar
        self.status_bar = StatusBar(self.main_frame)
        
        # Menu bar
        self._create_menu()
    
    def _create_generation_content(self):
        """Create content for Generation tab"""
        # Input frame
        input_frame = ctk.CTkFrame(self.generation_tab)
        input_frame.pack(fill="x", padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            input_frame,
            text="Dataset Generation",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        # Keyword input
        keyword_label = ctk.CTkLabel(
            input_frame,
            text="Domain Keyword:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        keyword_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.keyword_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="e.g., healthcare, finance, education",
            font=ctk.CTkFont(size=14),
            height=40
        )
        self.keyword_entry.pack(fill="x", padx=20, pady=(0, 15))
        
        # Settings frame
        settings_frame = ctk.CTkFrame(input_frame)
        settings_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        settings_title = ctk.CTkLabel(
            settings_frame,
            text="Generation Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        settings_title.pack(pady=(15, 10))
        
        # Settings grid
        settings_grid = ctk.CTkFrame(settings_frame)
        settings_grid.pack(pady=(0, 15))
        
        # Rows setting
        rows_label = ctk.CTkLabel(settings_grid, text="Rows per dataset:")
        rows_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        rows_entry = ctk.CTkEntry(settings_grid, textvariable=self.rows_var, width=100)
        rows_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Variations setting
        variations_label = ctk.CTkLabel(settings_grid, text="Variations:")
        variations_label.grid(row=0, column=2, padx=10, pady=5, sticky="w")
        
        variations_entry = ctk.CTkEntry(settings_grid, textvariable=self.variations_var, width=100)
        variations_entry.grid(row=0, column=3, padx=10, pady=5)
        
        # Buttons
        button_frame = ctk.CTkFrame(input_frame)
        button_frame.pack(pady=(0, 20))
        
        self.generate_button = ctk.CTkButton(
            button_frame,
            text="🚀 Generate Datasets",
            command=self._start_generation,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#1f538d", "#14375e")
        )
        self.generate_button.pack(side="left", padx=10, pady=15)
        
        self.stop_button = ctk.CTkButton(
            button_frame,
            text="⏹ Stop Generation",
            command=self._stop_generation,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#d42c2c", "#8b1e1e"),
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=10, pady=15)
        
        # Progress frame
        self.progress_frame = ProgressFrame(self.generation_tab)
        self.progress_frame.pack(fill="x", padx=20, pady=(0, 20))
    
    def _create_config_content(self):
        """Create content for Configuration tab"""
        self.config_frame = ConfigFrame(self.config_tab, self.config_manager)
        self.config_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    def _create_results_content(self):
        """Create content for Results tab"""
        self.results_frame = ResultsFrame(self.results_tab)
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    def _create_logs_content(self):
        """Create content for Logs tab with real-time updates"""
        logs_frame = ctk.CTkFrame(self.logs_tab)
        logs_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        logs_title = ctk.CTkLabel(
            logs_frame,
            text="System Logs",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        logs_title.pack(pady=(20, 10))
        
        self.log_viewer = LogViewer(logs_frame)
        self.log_viewer.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Connect GUI logging handler
        from dataforge.utils.logger import setup_logging
        setup_logging(self.config_manager.config, self.log_viewer)

    def _progress_callback(self, value: float, message: str) -> None:
        """Handle progress updates from generator - thread safe"""
        self.progress_frame.update_progress(value, message)

    def _status_callback(self, message: str) -> None:
        """Handle status updates from generator - thread safe"""
        self.status_bar.set_status(message)
    
    def _create_menu(self) -> None:
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Config", command=self._open_config)
        file_menu.add_command(label="Save Config", command=self._save_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Clear Logs", command=self._clear_logs)
        tools_menu.add_command(label="Open Output Folder", command=self._open_output_folder)
        tools_menu.add_command(label="System Info", command=self._show_system_info)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _setup_layout(self) -> None:
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.header_frame.pack(fill="x", pady=(0, 20))
        self.title_label.pack(pady=(10, 0))
        self.subtitle_label.pack(pady=(0, 10))
        
        self.tabview.pack(fill="both", expand=True, pady=(0, 10))
        self.status_bar.pack(fill="x", side="bottom")
    
    def _setup_bindings(self) -> None:
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.keyword_entry.bind("<Return>", lambda e: self._start_generation())
    
    def _initialize_generator(self) -> None:
            try:
                config_dict = self.config_manager.config
                self.generator = DatasetGenerator(config_dict)
                
                # Set up progress callbacks
                self.generator.set_progress_callback(self._progress_callback)
                self.generator.set_status_callback(self._status_callback)
                
                self.status_bar.set_status("DataForge initialized successfully")
                self.logger.info("Dataset generator initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize generator: {e}")
                self.status_bar.set_status(f"Initialization failed: {e}")
                messagebox.showerror("Initialization Error", f"Failed to initialize DataForge:\n{e}")
    
    def _start_generation(self) -> None:
        if self.is_generating:
            return
        
        keyword = self.keyword_entry.get().strip()
        if not keyword:
            messagebox.showwarning("Input Required", "Please enter a domain keyword")
            return
        
        try:
            rows = int(self.rows_var.get())
            variations = int(self.variations_var.get())
            
            if rows < 100 or rows > 2000:
                raise ValueError("Rows must be between 100 and 2000")
            if variations < 1 or variations > 10:
                raise ValueError("Variations must be between 1 and 10")
                
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Invalid settings: {e}")
            return
        
        self.is_generating = True
        self.current_keyword = keyword
        self.generate_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.progress_frame.reset()
        
        self.generation_thread = threading.Thread(
            target=self._run_generation,
            args=(keyword, rows, variations),
            daemon=True
        )
        self.generation_thread.start()
        
        self.logger.info(f"Started generation: keyword='{keyword}', rows={rows}, variations={variations}")
    
    def _run_generation(self, keyword: str, rows: int, variations: int) -> None:
        try:
            results = self.generator.generate_datasets(
                keyword=keyword,
                num_rows=rows,
                num_variations=variations
            )
            
            self.root.after(0, lambda: self._on_generation_complete(results))
            
        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            self.root.after(0, lambda: self._on_generation_error(e))
    
    def _stop_generation(self) -> None:
        if self.generator:
            self.generator.should_stop = True
        
        self._reset_ui_state()
        self.status_bar.set_status("Generation stopped by user")
        self.logger.info("Stopped generation")
    
    def _on_generation_complete(self, results: Dict[str, Any]) -> None:
        self._reset_ui_state()
        
        self.results_frame.display_results(results)
        self.tabview.set("Results")
        
        files_created = len(results.get('generated_files', []))
        message = f"Successfully generated {files_created} synthetic datasets for '{self.current_keyword}'"
        self.status_bar.set_status(message)
        messagebox.showinfo("Generation Complete", message)
        
        self.logger.info(f"Generation complete: {files_created} files created")
    
    def _on_generation_error(self, error: Exception) -> None:
        self._reset_ui_state()
        
        error_message = f"Generation failed: {str(error)}"
        self.status_bar.set_status(error_message)
        messagebox.showerror("Generation Error", error_message)
        
        self.logger.error(f"Generation error: {error}")
    
    def _reset_ui_state(self) -> None:
        self.is_generating = False
        self.generate_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.progress_frame.reset()
    
    def _open_config(self) -> None:
        filename = filedialog.askopenfilename(
            title="Open Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.config_manager.config_file = filename
                self.config_manager._load_config()
                self.config_frame.refresh()
                messagebox.showinfo("Success", "Configuration loaded successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load configuration: {e}")
    
    def _save_config(self) -> None:
        self.config_manager.save_config()
        messagebox.showinfo("Success", "Configuration saved successfully")
    
    def _clear_logs(self) -> None:
        self.log_viewer.delete("1.0", "end")
    
    def _open_output_folder(self) -> None:
        output_path = Path(self.config_manager.get('paths.generated_datasets', 'data/generated_datasets'))
        if output_path.exists():
            os.startfile(str(output_path))
        else:
            messagebox.showwarning("Folder Not Found", f"Output folder does not exist: {output_path}")
    
    def _show_system_info(self) -> None:
        SystemInfoDialog(self.root)
    
    def _show_about(self) -> None:
        AboutDialog(self.root)
    
    def _on_closing(self) -> None:
        if self.is_generating:
            if messagebox.askyesno("Confirm Exit", "Generation in progress. Are you sure you want to exit?"):
                if self.generator:
                    self.generator.should_stop = True
                self.root.quit()
        else:
            self.root.quit()
