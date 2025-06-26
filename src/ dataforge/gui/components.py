import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List, Optional
import json
from pathlib import Path

class ModernFrame(ctk.CTkFrame):
    """Modern frame with title and content area."""
    
    def __init__(self, parent, title: str = "", **kwargs):
        super().__init__(parent, **kwargs)
        
        if title:
            self.title_label = ctk.CTkLabel(
                self,
                text=title,
                font=ctk.CTkFont(size=16, weight="bold")
            )
            self.title_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=10, pady=(0, 15))

class ProgressFrame(ctk.CTkFrame):
    """Progress display frame with progress bar and status."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.title_label = ctk.CTkLabel(
            self,
            text="Generation Progress",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Progress container
        progress_container = ctk.CTkFrame(self)
        progress_container.pack(fill="x", padx=15, pady=(0, 10))
        
        self.progress_bar = ctk.CTkProgressBar(
            progress_container,
            height=20,
            corner_radius=10
        )
        self.progress_bar.pack(fill="x", padx=10, pady=10)
        self.progress_bar.set(0)
        
        # Status and percentage container
        status_container = ctk.CTkFrame(self)
        status_container.pack(fill="x", padx=15, pady=(0, 15))
        
        self.status_label = ctk.CTkLabel(
            status_container,
            text="Ready to generate datasets",
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10, pady=10)
        
        self.percentage_label = ctk.CTkLabel(
            status_container,
            text="0%",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.percentage_label.pack(side="right", padx=10, pady=10)
    
    def update_progress(self, value: float, message: str = "") -> None:
        """Update progress bar and status - thread safe"""
        def _update():
            self.progress_bar.set(value)
            self.percentage_label.configure(text=f"{int(value * 100)}%")
            if message:
                self.status_label.configure(text=message)
        
        # Use after_idle for thread safety
        self.after_idle(_update)
    
    def reset(self) -> None:
        """Reset progress display"""
        def _reset():
            self.progress_bar.set(0)
            self.percentage_label.configure(text="0%")
            self.status_label.configure(text="Ready to generate datasets")
        
        self.after_idle(_reset)

class StatusBar(ctk.CTkFrame):
    """Application status bar."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, height=30, **kwargs)
        
        self.status_label = ctk.CTkLabel(
            self,
            text="Ready",
            font=ctk.CTkFont(size=10),
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10, pady=5, fill="x", expand=True)
        
    def set_status(self, message: str) -> None:
        """Set status message - thread safe"""
        def _update():
            self.status_label.configure(text=message)
        
        self.after_idle(_update)

class LogViewer(ctk.CTkTextbox):
    """Enhanced text widget for displaying logs with real-time updates."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            font=ctk.CTkFont(family="Consolas", size=10),
            **kwargs
        )
        
        self.configure(state="disabled")
        
        # Load existing log file if it exists
        self._load_existing_logs()
    
    def _load_existing_logs(self):
        """Load existing logs from file"""
        try:
            log_file = Path("logs/dataforge.log")
            if log_file.exists():
                with open(log_file, 'r') as f:
                    logs = f.read()
                self.configure(state="normal")
                self.insert("1.0", logs)
                self.see("end")
                self.configure(state="disabled")
        except Exception as e:
            self.configure(state="normal")
            self.insert("1.0", f"Error loading existing logs: {e}\n")
            self.configure(state="disabled")
    
    def append_log(self, message: str, level: str = "INFO") -> None:
        """Append log message - thread safe"""
        def _append():
            self.configure(state="normal")
            self.insert("end", f"{message}\n")
            self.see("end")
            self.configure(state="disabled")
        
        self.after_idle(_append)
    
    def clear(self) -> None:
        """Clear log content"""
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")

class ConfigFrame(ctk.CTkScrollableFrame):
    """Configuration management frame."""
    
    def __init__(self, parent, config_manager, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.config_manager = config_manager
        self.config_widgets = {}
        
        self._create_config_widgets()
    
    def _create_config_widgets(self) -> None:
        """Create configuration editing widgets."""
        title_label = ctk.CTkLabel(
            self,
            text="Application Configuration",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(anchor="w", padx=10, pady=(10, 20))
        
        # Kaggle section
        self._create_section("Kaggle Settings", "kaggle", {
            "max_download_size_mb": "Max Download Size (MB)",
            "min_rating": "Minimum Dataset Rating",
            "max_results": "Max Search Results"
        })
        
        # Mistral section
        self._create_section("Mistral Model Settings", "mistral", {
            "model_name": "Model Name",
            "max_tokens": "Max Tokens",
            "temperature": "Temperature"
        })
        
        # Generation section
        self._create_section("Generation Settings", "generation", {
            "default_rows": "Default Rows",
            "variations": "Default Variations"
        })
        
        save_button = ctk.CTkButton(
            self,
            text="Save Configuration",
            command=self._save_config
        )
        save_button.pack(pady=20)
    
    def _create_section(self, title: str, section_key: str, fields: Dict[str, str]) -> None:
        """Create a configuration section."""
        section_frame = ctk.CTkFrame(self)
        section_frame.pack(fill="x", padx=10, pady=10)
        
        section_title = ctk.CTkLabel(
            section_frame,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        section_title.pack(anchor="w", padx=15, pady=(15, 10))
        
        for field_key, field_label in fields.items():
            field_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
            field_frame.pack(fill="x", padx=15, pady=5)
            
            label = ctk.CTkLabel(
                field_frame,
                text=field_label,
                width=200,
                anchor="w"
            )
            label.pack(side="left", padx=(0, 10))
            
            current_value = self.config_manager.get(f"{section_key}.{field_key}", "")
            
            entry = ctk.CTkEntry(field_frame, width=200)
            entry.pack(side="right")
            entry.insert(0, str(current_value))
            
            self.config_widgets[f"{section_key}.{field_key}"] = entry
        
        ctk.CTkLabel(section_frame, text="", height=10).pack()
    
    def _save_config(self) -> None:
        """Save configuration changes."""
        try:
            for key, widget in self.config_widgets.items():
                value = widget.get()
                if value.isdigit():
                    value = int(value)
                elif value.replace('.', '').isdigit():
                    value = float(value)
                elif value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'
                
                self.config_manager.set(key, value)
            
            self.config_manager.save_config()
            
            from tkinter import messagebox
            messagebox.showinfo("Success", "Configuration saved successfully!")
            
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
    
    def refresh(self) -> None:
        """Refresh configuration display."""
        for key, widget in self.config_widgets.items():
            current_value = self.config_manager.get(key, "")
            widget.delete(0, "end")
            widget.insert(0, str(current_value))

class ResultsFrame(ctk.CTkScrollableFrame):
    """Frame for displaying generation results."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.title_label = ctk.CTkLabel(
            self,
            text="Generation Results",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.title_label.pack(anchor="w", padx=10, pady=(10, 20))
        
        self.results_container = ctk.CTkFrame(self, fg_color="transparent")
        self.results_container.pack(fill="both", expand=True, padx=10)
        
        self.no_results_label = ctk.CTkLabel(
            self.results_container,
            text="No datasets generated yet.\nClick 'Generate Datasets' to get started!",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.no_results_label.pack(expand=True)
    
    def display_results(self, results: Dict[str, Any]) -> None:
        """Display generation results."""
        for widget in self.results_container.winfo_children():
            widget.destroy()
        
        if not results.get('generated_files'):
            self.no_results_label = ctk.CTkLabel(
                self.results_container,
                text="No files were generated.",
                font=ctk.CTkFont(size=14),
                text_color="orange"
            )
            self.no_results_label.pack(expand=True)
            return
        
        # Summary
        summary_frame = ctk.CTkFrame(self.results_container)
        summary_frame.pack(fill="x", pady=(0, 20))
        
        summary_title = ctk.CTkLabel(
            summary_frame,
            text="Generation Summary",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        summary_title.pack(anchor="w", padx=15, pady=(15, 10))
        
        info_text = f"""Keyword: {results.get('keyword', 'N/A')}
Files Generated: {len(results.get('generated_files', []))}
Reference Dataset: {Path(results.get('reference_dataset', 'N/A')).name if results.get('reference_dataset') else 'N/A'}
Total Generation Time: {results.get('total_time', 'N/A'):.1f}s"""
        
        info_label = ctk.CTkLabel(
            summary_frame,
            text=info_text,
            anchor="w",
            justify="left"
        )
        info_label.pack(anchor="w", padx=15, pady=(0, 15))
        
        # File list
        files_frame = ctk.CTkFrame(self.results_container)
        files_frame.pack(fill="both", expand=True)
        
        files_title = ctk.CTkLabel(
            files_frame,
            text="Generated Files",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        files_title.pack(anchor="w", padx=15, pady=(15, 10))
        
        for i, file_path in enumerate(results.get('generated_files', [])):
            file_frame = ctk.CTkFrame(files_frame)
            file_frame.pack(fill="x", padx=15, pady=5)
            
            file_label = ctk.CTkLabel(
                file_frame,
                text=f"📄 {Path(file_path).name}",
                anchor="w"
            )
            file_label.pack(side="left", padx=15, pady=10)
            
            actions_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
            actions_frame.pack(side="right", padx=15, pady=5)
            
            open_button = ctk.CTkButton(
                actions_frame,
                text="Open",
                width=80,
                command=lambda fp=file_path: self._open_file(fp)
            )
            open_button.pack(side="right", padx=5)
            
            folder_button = ctk.CTkButton(
                actions_frame,
                text="Show in Folder",
                width=120,
                command=lambda fp=file_path: self._show_in_folder(fp)
            )
            folder_button.pack(side="right", padx=5)
    
    def _open_file(self, file_path: str) -> None:
        """Open file with default application."""
        import os
        try:
            os.startfile(file_path)
        except:
            try:
                os.system(f'open "{file_path}"')
            except:
                os.system(f'xdg-open "{file_path}"')
    
    def _show_in_folder(self, file_path: str) -> None:
        """Show file in folder."""
        import os
        folder_path = Path(file_path).parent
        try:
            os.startfile(str(folder_path))
        except:
            try:
                os.system(f'open "{folder_path}"')
            except:
                os.system(f'xdg-open "{folder_path}"')
