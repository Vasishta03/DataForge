import logging
import sys
import tkinter as tk
from pathlib import Path
from typing import Optional

class GUILogHandler(logging.Handler):
    """Custom logging handler that sends logs to GUI"""
    
    def __init__(self, log_widget=None):
        super().__init__()
        self.log_widget = log_widget
    
    def emit(self, record):
        """Send log record to GUI widget"""
        if self.log_widget:
            try:
                msg = self.format(record)
                # Use after_idle to ensure thread safety
                self.log_widget.after_idle(self._append_to_gui, msg)
            except Exception:
                self.handleError(record)
    
    def _append_to_gui(self, message):
        """Append message to GUI log widget"""
        if self.log_widget:
            self.log_widget.configure(state="normal")
            self.log_widget.insert("end", f"{message}\n")
            self.log_widget.see("end")
            self.log_widget.configure(state="disabled")

def setup_logging(config: dict, gui_log_widget: Optional[tk.Widget] = None) -> logging.Logger:
    """
    Configure logging for DataForge application with GUI support
    """
    log_config = config.get('logging', {})
    log_file = log_config.get('log_file', 'logs/dataforge.log')
    log_level = log_config.get('log_level', 'INFO').upper()
    
    # Create log directory if needed
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger('dataforge')
    logger.setLevel(log_level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Create GUI handler if widget provided
    if gui_log_widget:
        gui_handler = GUILogHandler(gui_log_widget)
        gui_handler.setFormatter(formatter)
        logger.addHandler(gui_handler)
    
    # Set library log levels
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("fsspec").setLevel(logging.WARNING)
    
    return logger
