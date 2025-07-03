import sys
import os
import threading
from pathlib import Path
import tkinter as tk

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Create required directories
for directory in ["data/generated_datasets", "data/reference_datasets", "config", "logs"]:
    Path(directory).mkdir(parents=True, exist_ok=True)

from dataforge.utils.logger import setup_logging
from dataforge.gui.main_window import DataForgeApp
from dataforge.config.config_manager import ConfigManager

def start_api_server():
    """Start the API server in a separate thread"""
    try:
        import subprocess
        subprocess.Popen([sys.executable, "api_server.py"], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Could not start API server: {e}")

def main():
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.config
        
        # Setup logging
        logger = setup_logging(config)
        logger.info("DataForge application starting")
        
        # Start API server in background
        api_thread = threading.Thread(target=start_api_server, daemon=True)
        api_thread.start()
        
        # Create and run GUI
        root = tk.Tk()
        app = DataForgeApp(root, config_manager, logger)
        root.mainloop()
        
    except Exception as e:
        print(f"Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
