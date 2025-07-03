import customtkinter as ctk
import tkinter as tk
from pathlib import Path

class ProgressFrame(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        title_label = ctk.CTkLabel(
            self,
            text="Generation Progress",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        progress_container = ctk.CTkFrame(self)
        progress_container.pack(fill="x", padx=15, pady=10)
        
        progress_row = ctk.CTkFrame(progress_container)
        progress_row.pack(fill="x", padx=10, pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(
            progress_row,
            height=25,
            corner_radius=12
        )
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.progress_bar.set(0)
        
        self.percentage_label = ctk.CTkLabel(
            progress_row,
            text="0%",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=50
        )
        self.percentage_label.pack(side="right")
        
        self.status_label = ctk.CTkLabel(
            progress_container,
            text="Ready to generate datasets",
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        self.status_label.pack(fill="x", padx=10, pady=(0, 10))
    
    def update_progress(self, value: float, message: str = "", info: str = "") -> None:
        def _update():
            self.progress_bar.set(max(0, min(1, value)))
            percentage = int(value * 100)
            self.percentage_label.configure(text=f"{percentage}%")
            if message:
                self.status_label.configure(text=message)
        
        self.after_idle(_update)
    
    def reset(self) -> None:
        def _reset():
            self.progress_bar.set(0)
            self.percentage_label.configure(text="0%")
            self.status_label.configure(text="Ready to generate datasets")
        
        self.after_idle(_reset)

class StatusBar(ctk.CTkFrame):
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
        def _update():
            self.status_label.configure(text=message)
        self.after_idle(_update)

class ResultsFrame(ctk.CTkScrollableFrame):
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
            text="No datasets generated yet.\nClick 'Start Generation' to get started!",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.no_results_label.pack(expand=True)
    
    def display_results(self, results):
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
Total Time: {results.get('total_time', 0):.1f}s"""
        
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
            
            open_button = ctk.CTkButton(
                file_frame,
                text="Open",
                width=80,
                command=lambda fp=file_path: self._open_file(fp)
            )
            open_button.pack(side="right", padx=15, pady=5)
    
    def _open_file(self, file_path: str) -> None:
        import os
        try:
            os.startfile(file_path)
        except:
            print(f"Cannot open file: {file_path}")

class LogViewer(ctk.CTkTextbox):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            font=ctk.CTkFont(family="Consolas", size=10),
            **kwargs
        )
        self.configure(state="disabled")
        self._load_existing_logs()
    
    def _load_existing_logs(self):
        try:
            log_file = Path("logs/dataforge.log")
            if log_file.exists():
                with open(log_file, 'r') as f:
                    logs = f.read()
                self.configure(state="normal")
                self.insert("1.0", logs)
                self.see("end")
                self.configure(state="disabled")
        except Exception:
            pass

class ConfigFrame(ctk.CTkFrame):
    def __init__(self, parent, config_manager, **kwargs):
        super().__init__(parent, **kwargs)
        
        title_label = ctk.CTkLabel(
            self,
            text="Configuration Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(anchor="w", padx=10, pady=(10, 20))
        
        info_label = ctk.CTkLabel(
            self,
            text="Configuration is managed through config.json file",
            font=ctk.CTkFont(size=12)
        )
        info_label.pack(anchor="w", padx=10, pady=10)
    
    def refresh(self):
        pass
