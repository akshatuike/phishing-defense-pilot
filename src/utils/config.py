"""
Configuration management for the Gamification-Based Phishing Defense System
"""

import os
import json
from typing import Dict, Any
from pathlib import Path

class Config:
    """Configuration manager for the application"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "config/config.json"
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            "database": {
                "url": "sqlite:///phishing_defense.db",
                "echo": False
            },
            "models": {
                "bert_model": "bert-base-uncased",
                "resnet_model": "resnet50",
                "densenet_model": "densenet121",
                "model_cache_dir": "models/"
            },
            "gamification": {
                "max_daily_games": 10,
                "points_per_correct_answer": 10,
                "bonus_points": 5,
                "achievement_thresholds": {
                    "beginner": 50,
                    "intermediate": 150,
                    "expert": 300,
                    "master": 500
                }
            },
            "detection": {
                "confidence_threshold": 0.8,
                "max_response_time_ms": 100,
                "enable_real_time": True
            },
            "security": {
                "session_timeout": 3600,
                "max_login_attempts": 5,
                "password_min_length": 8
            },
            "logging": {
                "level": "INFO",
                "file": "logs/app.log",
                "max_size_mb": 10,
                "backup_count": 5
            }
        }
        
        # Try to load from file
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    file_config = json.load(f)
                    # Merge with defaults
                    self._merge_configs(default_config, file_config)
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
            
        return default_config
    
    def _merge_configs(self, default: Dict, override: Dict):
        """Recursively merge configuration dictionaries"""
        for key, value in override.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_configs(default[key], value)
            else:
                default[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation (e.g., 'database.url')"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Set configuration value by dot notation"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self):
        """Save configuration to file"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_model_path(self, model_name: str) -> str:
        """Get the path for a specific model"""
        cache_dir = self.get("models.model_cache_dir", "models/")
        return os.path.join(cache_dir, model_name)
    
    def get_database_url(self) -> str:
        """Get database URL with environment variable override"""
        return os.environ.get('DATABASE_URL', self.get('database.url'))
    
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled"""
        return os.environ.get('DEBUG', 'False').lower() == 'true'
