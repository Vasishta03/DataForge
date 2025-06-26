import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

class ConfigManager:
    DEFAULT_CONFIG = {
        "kaggle": {
            "max_download_size_mb": 100,
            "min_rating": 7.0,
            "max_results": 5
        },
        "mistral": {
            "model_name": "mistral",
            "max_tokens": 2000,
            "temperature": 0.7
        },
        "generation": {
            "default_rows": 500,
            "variations": 6,
            "max_rows": 2000
        },
        "logging": {
            "log_file": "logs/dataforge.log",
            "log_level": "INFO"
        },
        "paths": {
            "reference_datasets": "data/reference_datasets",
            "generated_datasets": "data/generated_datasets"
        }
    }
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
                return self.DEFAULT_CONFIG
        return self.DEFAULT_CONFIG
    
    def save_config(self) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation"""
        keys = key.split('.')
        current = self.config
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        return current
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value using dot notation"""
        keys = key.split('.')
        current = self.config
        for i, k in enumerate(keys[:-1]):
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
