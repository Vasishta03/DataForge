import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import os
from pathlib import Path
import logging
import time
import webbrowser
from typing import Dict, Any

from dataforge.core.dataset_generator import DatasetGenerator
from dataforge.gui.components import ProgressFrame, StatusBar, ResultsFrame, LogViewer

class DataForgeApp:
    
    def __init__(self, root: tk.Tk, config_manager, app_logger):
        self.root = root
        self.config_manager = config_manager
        self.logger = app_logger
        
        self.generator = None
        self.current_keyword = ""
        self.generation_thread = None
        self.is_generating = False
        self.generation_start_time = None
        
        # Create StringVars
        self.rows_var = tk.StringVar(value="500")
        self.variations_var = tk.StringVar(value="6")
        
        # Setup GUI
        self._setup_window()
        self._create_widgets()
        self._setup_layout()
        self._setup_bindings()
        
        # Initialize generator
        self._initialize_generator()
        
        self.logger.info("DataForge GUI initialized successfully")
    
    def _setup_window(self) -> None:
        self.root.title("DataForge - Synthetic Dataset Generator")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
    
    def _create_widgets(self) -> None:
        self.main_frame = ctk.CTkFrame(self.root)
        
        # Header
        self.header_frame = ctk.CTkFrame(self.main_frame)
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="🔬 DataForge ",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Synthetic Dataset Generator",
            font=ctk.CTkFont(size=16)
        )
        
        # Create tabview (without configuration tab)
        self.tabview = ctk.CTkTabview(self.main_frame)
        
        # Add tabs
        self.generation_tab = self.tabview.add("Generation")
        self.results_tab = self.tabview.add("Results")  
        self.api_tab = self.tabview.add("API Access")
        self.logs_tab = self.tabview.add("Logs")
        
        # Set default tab
        self.tabview.set("Generation")
        
        # Create content
        self._create_generation_content()
        self._create_results_content()
        self._create_api_content()
        self._create_logs_content()
        
        # Status bar
        self.status_bar = StatusBar(self.main_frame)
    
    def _create_generation_content(self):
        container = ctk.CTkFrame(self.generation_tab)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title with API indicator
        title_frame = ctk.CTkFrame(container)
        title_frame.pack(fill="x", padx=20, pady=(20, 15))
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="Synthetic Dataset Generation",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", pady=15)
        
        api_indicator = ctk.CTkLabel(
            title_frame,
            text=" API Ready",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="green"
        )
        api_indicator.pack(side="right", pady=15)
        
        # Input section
        input_frame = ctk.CTkFrame(container)
        input_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        keyword_label = ctk.CTkLabel(
            input_frame,
            text="Domain Keyword:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        keyword_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        self.keyword_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="e.g., healthcare, finance, education, retail",
            font=ctk.CTkFont(size=14),
            height=40
        )
        self.keyword_entry.pack(fill="x", padx=20, pady=(0, 20))
        
        # Enhanced settings
        settings_frame = ctk.CTkFrame(input_frame)
        settings_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        settings_label = ctk.CTkLabel(
            settings_frame,
            text=" Generation Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        settings_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        settings_grid = ctk.CTkFrame(settings_frame)
        settings_grid.pack(padx=15, pady=(0, 15))
        
        # Rows setting
        rows_label = ctk.CTkLabel(settings_grid, text="Rows per dataset:")
        rows_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        self.rows_entry = ctk.CTkEntry(settings_grid, textvariable=self.rows_var, width=120)
        self.rows_entry.grid(row=0, column=1, padx=15, pady=10)
        
        # Variations setting
        variations_label = ctk.CTkLabel(settings_grid, text="🔄 Variations:")
        variations_label.grid(row=0, column=2, padx=15, pady=10, sticky="w")
        
        self.variations_entry = ctk.CTkEntry(settings_grid, textvariable=self.variations_var, width=120)
        self.variations_entry.grid(row=0, column=3, padx=15, pady=10)
        
        # Control buttons
        button_frame = ctk.CTkFrame(container)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        control_label = ctk.CTkLabel(
            button_frame,
            text="🎮 Generation Control",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        control_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        btn_container = ctk.CTkFrame(button_frame)
        btn_container.pack(pady=(0, 20))
        
        # START BUTTON
        self.start_btn = ctk.CTkButton(
            btn_container,
            text="START ENHANCED GENERATION",
            command=self._start_generation,
            height=50,
            width=280,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.start_btn.pack(side="left", padx=15, pady=15)
        
        # STOP BUTTON
        self.stop_btn = ctk.CTkButton(
            btn_container,
            text="⏹ STOP GENERATION",
            command=self._stop_generation,
            height=50,
            width=200,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#dc3545",
            hover_color="#c82333",
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=15, pady=15)
        
        # Progress section
        progress_container = ctk.CTkFrame(container)
        progress_container.pack(fill="x", padx=20, pady=(0, 20))
        
        self.progress_frame = ProgressFrame(progress_container)
        self.progress_frame.pack(fill="x", padx=20, pady=20)
    
    def _create_results_content(self):
        self.results_frame = ResultsFrame(self.results_tab)
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    def _create_api_content(self):
        container = ctk.CTkFrame(self.api_tab)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            container,
            text="API Access & Documentation",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 15))
        
        # API Status
        status_frame = ctk.CTkFrame(container)
        status_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        status_label = ctk.CTkLabel(
            status_frame,
            text="API Server Status",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        status_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        self.api_status_label = ctk.CTkLabel(
            status_frame,
            text="API Server Running on http://localhost:5000",
            font=ctk.CTkFont(size=12),
            text_color="green"
        )
        self.api_status_label.pack(anchor="w", padx=15, pady=(0, 10))
        
        # API Key
        key_frame = ctk.CTkFrame(status_frame)
        key_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        key_label = ctk.CTkLabel(key_frame, text=" API Key:", font=ctk.CTkFont(weight="bold"))
        key_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        key_text = ctk.CTkTextbox(key_frame, height=40, font=ctk.CTkFont(family="Consolas", size=12))
        key_text.pack(fill="x", padx=10, pady=(0, 10))
        key_text.insert("1.0", "algonomy")
        key_text.configure(state="disabled")
        
        # Quick Actions
        actions_frame = ctk.CTkFrame(container)
        actions_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        actions_label = ctk.CTkLabel(
            actions_frame,
            text="Quick Actions",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        actions_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        actions_buttons = ctk.CTkFrame(actions_frame)
        actions_buttons.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkButton(
            actions_buttons,
            text="Open API Docs",
            command=lambda: webbrowser.open("http://localhost:5000/api/health"),
            width=150
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            actions_buttons,
            text="Copy API Key",
            command=self._copy_api_key,
            width=150
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            actions_buttons,
            text="View Datasets",
            command=lambda: webbrowser.open("http://localhost:5000/api/datasets"),
            width=150
        ).pack(side="left", padx=10, pady=10)
        
        # Documentation
        docs_frame = ctk.CTkFrame(container)
        docs_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        docs_label = ctk.CTkLabel(
            docs_frame,
            text="API Endpoints",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        docs_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        docs_text = """
GET /api/health
   Health check and server status

GET /api/datasets  
   List all generated datasets with download links
   
GET /api/download/<keyword>/<filename>
   Download individual CSV files
   
GET /api/download-zip/<keyword>
   Download all files for a keyword as ZIP
   
POST /api/generate
   Trigger dataset generation programmatically

Example Usage:
curl -H "Authorization: Bearer algonomy" \\
     http://localhost:5000/api/datasets
        """
        
        docs_textbox = ctk.CTkTextbox(
            docs_frame,
            font=ctk.CTkFont(family="Consolas", size=11)
        )
        docs_textbox.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        docs_textbox.insert("1.0", docs_text.strip())
        docs_textbox.configure(state="disabled")
    
    def _create_logs_content(self):
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
            
            # Set callbacks
            self.generator.set_progress_callback(self._progress_callback)
            self.generator.set_status_callback(self._status_callback)
            
            self.status_bar.set_status("DataForge initialized with API access")
            self.logger.info("Dataset generator initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize generator: {e}")
            self.status_bar.set_status(f"❌ Initialization failed: {e}")
            messagebox.showerror("Initialization Error", f"Failed to initialize DataForge:\n{e}")

    def _progress_callback(self, value: float, message: str) -> None:
        if self.is_generating and self.generation_start_time:
            elapsed = time.time() - self.generation_start_time
            info = f"Elapsed: {elapsed:.1f}s"
        else:
            info = ""
        
        self.progress_frame.update_progress(value, message, info)

    def _status_callback(self, message: str) -> None:
        self.status_bar.set_status(message)
    
    def _start_generation(self):
        if self.is_generating:
            return
        
        keyword = self.keyword_entry.get().strip()
        if not keyword:
            messagebox.showwarning("Input Required", "Please enter a keyword")
            return
        
        try:
            rows = int(self.rows_var.get())
            variations = int(self.variations_var.get())
            
            if rows < 10 or rows > 2000:
                raise ValueError("Rows must be between 10 and 2000")
            if variations < 1 or variations > 15:
                raise ValueError("Variations must be between 1 and 15")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
            return
        
        self.start_btn.configure(state="disabled", fg_color="#666666")
        self.stop_btn.configure(state="normal", fg_color="#dc3545")
        
        self.progress_frame.reset()
        
        # Set state
        self.is_generating = True
        self.current_keyword = keyword
        self.generation_start_time = time.time()
        
        # Start generation thread
        self.generation_thread = threading.Thread(
            target=self._run_generation,
            args=(keyword, rows, variations),
            daemon=True
        )
        self.generation_thread.start()
        
        self.logger.info(f" Started enhanced generation: {keyword}")

    def _stop_generation(self):
        if not self.is_generating:
            return
        
        if self.generator:
            self.generator.should_stop = True
        
        # Reset button states
        self.start_btn.configure(state="normal", fg_color="#28a745")
        self.stop_btn.configure(state="disabled", fg_color="#666666")
        
        # Update progress
        self.progress_frame.update_progress(0, "⏹ Generation stopped by user")
        
        # Reset state
        self.is_generating = False
        
        self.logger.info("⏹ Generation stopped by user")

    def _run_generation(self, keyword, rows, variations):
        try:
            results = self.generator.generate_datasets(
                keyword=keyword,
                num_rows=rows,
                num_variations=variations
            )
            
            self.root.after(0, lambda: self._on_generation_complete(results))
            
        except Exception as e:
            self.root.after(0, lambda: self._on_generation_error(e))

    def _on_generation_complete(self, results):
        # Reset button states
        self.start_btn.configure(state="normal", fg_color="#28a745")
        self.stop_btn.configure(state="disabled", fg_color="#666666")
        
        # Update progress
        self.progress_frame.update_progress(1.0, " Generation completed successfully!")
        
        # Display results with API info
        self.results_frame.display_results(results)
        self.tabview.set("Results")
        
        # Reset state
        self.is_generating = False
        
        files_created = len(results.get('generated_files', []))
        if files_created > 0:
            api_info = results.get('api_info', {})
            message = f"Generated {files_created} datasets for '{self.current_keyword}'\n\n"
            message += f" API Access:\n"
            message += f"Base URL: {api_info.get('base_url', 'http://localhost:5000')}\n"
            message += f"Download ZIP: {api_info.get('endpoints', {}).get('download_zip', 'N/A')}\n"
            message += f"API Key: {api_info.get('api_key', 'algonomy')}"
            
            messagebox.showinfo("Generation Complete", message)
        else:
            messagebox.showwarning(" Warning", "No files were generated. Check logs for details.")

    def _on_generation_error(self, error):
        # Reset button states
        self.start_btn.configure(state="normal", fg_color="#28a745")
        self.stop_btn.configure(state="disabled", fg_color="#666666")
        
        # Update progress
        self.progress_frame.update_progress(0, f"❌ Error: {str(error)}")
        
        # Reset state
        self.is_generating = False
        
        messagebox.showerror("❌ Generation Error", f"Generation failed: {str(error)}")
    
    def _copy_api_key(self):
        """Copy API key to clipboard"""
        api_key = "algonomy"
        self.root.clipboard_clear()
        self.root.clipboard_append(api_key)
        messagebox.showinfo("Copied", "API key copied to clipboard!")
    
    def _on_closing(self) -> None:
        if self.is_generating:
            if messagebox.askyesno("Confirm Exit", "Generation in progress. Are you sure you want to exit?"):
                if self.generator:
                    self.generator.should_stop = True
                self.root.quit()
        else:
            self.root.quit()
