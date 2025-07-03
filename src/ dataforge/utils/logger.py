import logging
import sys
from pathlib import Path

def setup_logging(config: dict) -> logging.Logger:
    log_config = config.get('logging', {})
    log_file = log_config.get('log_file', 'logs/dataforge.log')
    log_level = log_config.get('log_level', 'INFO').upper()
    
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger('dataforge')
    logger.setLevel(log_level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger
