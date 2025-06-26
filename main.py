import sys
from pathlib import Path
import tkinter as tk

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dataforge.utils.logger import setup_logging
from dataforge.gui.main_window import DataForgeApp
from dataforge.config.config_manager import ConfigManager

def main():
    # Load configuration first
    config_manager = ConfigManager()
    config = config_manager.config
    
    # Setup logging using config
    logger = setup_logging(config)
    logger.info("DataForge application starting")
    
    # Create GUI
    root = tk.Tk()
    app = DataForgeApp(root, config_manager, logger)
    root.mainloop()

if __name__ == "__main__":
    main()
