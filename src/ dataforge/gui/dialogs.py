# src/dataforge/gui/dialogs.py
import customtkinter as ctk
import tkinter as tk
from tkinter import simpledialog, messagebox
import threading
import time

class ProgressDialog(ctk.CTkToplevel):
    """Progress dialog for long-running operations"""
    
    def __init__(self, parent, title="Processing", message="Please wait..."):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x150")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Center on parent window
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        x = parent_x + (parent_width - 400) // 2
        y = parent_y + (parent_height - 150) // 2
        self.geometry(f"+{x}+{y}")
        
        # Message label
        self.message_label = ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(size=14)
        )
        self.message_label.pack(pady=(20, 10), padx=20, anchor="w")
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(
            self,
            mode="indeterminate",
            height=20,
            corner_radius=10
        )
        self.progress.pack(fill="x", padx=20, pady=10)
        self.progress.start()
        
        # Cancel button
        self.cancel_button = ctk.CTkButton(
            self,
            text="Cancel",
            command=self._on_cancel,
            fg_color="#d42c2c",
            hover_color="#8b1e1e"
        )
        self.cancel_button.pack(pady=(0, 20))
        
        self.cancelled = False
    
    def _on_cancel(self):
        self.cancelled = True
        self.destroy()
    
    def update_message(self, new_message):
        self.message_label.configure(text=new_message)
        self.update()

class SystemInfoDialog(ctk.CTkToplevel):
    """Dialog to display system information"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("System Information")
        self.geometry("500x400")
        self.resizable(False, False)
        self.transient(parent)
        
        # System info content
        info_frame = ctk.CTkFrame(self)
        info_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            info_frame,
            text="System Information",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Get system info
        info = self._get_system_info()
        
        # Display info in textbox
        self.info_text = ctk.CTkTextbox(
            info_frame,
            wrap="word",
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.info_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.info_text.insert("1.0", info)
        self.info_text.configure(state="disabled")
        
        # Close button
        close_button = ctk.CTkButton(
            info_frame,
            text="Close",
            command=self.destroy
        )
        close_button.pack(pady=(0, 10))
    
    def _get_system_info(self):
        """Collect system information"""
        import platform
        import psutil
        import torch
        
        info = []
        
        # System information
        info.append(f"System: {platform.system()} {platform.release()}")
        info.append(f"Processor: {platform.processor()}")
        info.append(f"Python: {platform.python_version()}")
        
        # Memory
        mem = psutil.virtual_memory()
        info.append(f"RAM: {mem.total / (1024**3):.2f} GB Total, {mem.used / (1024**3):.2f} GB Used")
        
        # GPU information
        info.append("\nGPU Information:")
        if torch.cuda.is_available():
            info.append(f"Device: {torch.cuda.get_device_name(0)}")
            info.append(f"CUDA Version: {torch.version.cuda}")
            info.append(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
        else:
            info.append("No GPU available - Using CPU")
        
        # Disk space
        try:
            disk = psutil.disk_usage('/')
            info.append(f"\nDisk: {disk.total / (1024**3):.2f} GB Total, {disk.free / (1024**3):.2f} GB Free")
        except:
            pass
        
        return "\n".join(info)

class AboutDialog(ctk.CTkToplevel):
    """About dialog for the application"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("About DataForge")
        self.geometry("400x300")
        self.resizable(False, False)
        self.transient(parent)
        
        # Content frame
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Application icon/logo
        try:
            # Placeholder for application logo
            logo_label = ctk.CTkLabel(
                content_frame,
                text="🔬",
                font=ctk.CTkFont(size=48)
            )
            logo_label.pack(pady=(20, 10))
        except:
            pass
        
        # Application information
        info_text = """
        DataForge v1.0.0
        Professional Synthetic Dataset Generator
        
        Powered by:
        - Ollama with Mistral 7B
        - Kaggle Datasets
        - Python 3.10+
        
        Features:
        - Automatic dataset discovery
        - Schema-aware generation
        - Multiple output variations
        - Modern GUI interface
        
        © 2025 DataForge Team
        MIT Licensed
        """
        
        info_label = ctk.CTkLabel(
            content_frame,
            text=info_text.strip(),
            justify="left"
        )
        info_label.pack(pady=10, padx=20)
        
        # Close button
        close_button = ctk.CTkButton(
            content_frame,
            text="Close",
            command=self.destroy
        )
        close_button.pack(pady=(10, 20))

# Utility function for showing busy dialog during operations
def show_busy_dialog(parent, title, message, operation, *args):
    """Show progress dialog while executing an operation"""
    result = None
    exception = None
    
    def worker():
        nonlocal result, exception
        try:
            result = operation(*args)
        except Exception as e:
            exception = e
    
    # Start the operation in a separate thread
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    
    # Show progress dialog
    dialog = ProgressDialog(parent, title, message)
    
    # Wait for operation to complete
    while thread.is_alive():
        parent.update()
        time.sleep(0.1)
    
    dialog.destroy()
    
    if exception:
        raise exception
    
    return result
