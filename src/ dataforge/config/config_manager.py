import json
import logging
from pathlib import Path
from typing import Any, Dict

class ConfigManager:
    DEFAULT_CONFIG = {
        "kaggle": {"max_download_size_mb": 50, "min_rating": 5.0, "max_results": 3},
        "mistral": {"model_name": "mistral", "max_tokens": 1000, "temperature": 0.7},
        "generation": {"default_rows": 500, "variations": 6, "max_rows": 1000},
        "logging": {"log_file": "logs/dataforge.log", "log_level": "INFO"},
        "paths": {"reference_datasets": "data/reference_datasets", "generated_datasets": "data/generated_datasets"}
    }
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return self.DEFAULT_CONFIG
        return self.DEFAULT_CONFIG
    
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        current = self.config
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        return current
    
    def save_config(self) -> None:
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
