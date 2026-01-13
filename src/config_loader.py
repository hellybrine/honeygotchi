"""Configuration loader for Honeygotchi."""
import os
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class Config:
    """Configuration manager for Honeygotchi."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration from file or defaults."""
        self.config_path = config_path or self._find_config_file()
        self._config = self._load_config()
    
    def _find_config_file(self) -> str:
        """Find configuration file in common locations."""
        possible_paths = [
            "config.yaml",
            "config.yml",
            os.path.join(os.path.dirname(__file__), "..", "config.yaml"),
            os.path.expanduser("~/.honeygotchi/config.yaml"),
            "/etc/honeygotchi/config.yaml"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Return default path if none found
        return "config.yaml"
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        default_config = {
            "ssh": {
                "port": 2222,
                "host": "0.0.0.0",
                "host_key": "ssh_host_key",
                "generate_key": False,
                "banner": True
            },
            "reinforcement_learning": {
                "epsilon": 0.3,
                "learning_rate": 0.1,
                "state_file": "rl_state.json",
                "save_interval": 100
            },
            "monitoring": {
                "metrics_port": 9090,
                "enable_health_check": True,
                "health_check_port": 8080
            },
            "logging": {
                "level": "INFO",
                "log_dir": "logs",
                "log_file": "honeygotchi.log",
                "json_format": True,
                "max_log_size_mb": 100,
                "backup_count": 5
            },
            "filesystem": {
                "hostname_prefix": "srv",
                "default_user": "user",
                "default_home": "/home/user"
            },
            "security": {
                "max_failed_attempts": 10,
                "session_timeout_seconds": 3600,
                "command_timeout_seconds": 30
            }
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    file_config = yaml.safe_load(f) or {}
                    # Deep merge with defaults
                    return self._deep_merge(default_config, file_config)
            except Exception as e:
                logger.warning(f"Failed to load config from {self.config_path}: {e}. Using defaults.")
                return default_config
        else:
            logger.info(f"Config file not found at {self.config_path}. Using defaults.")
            return default_config
    
    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """Deep merge two dictionaries."""
        result = base.copy()
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated key."""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section."""
        return self._config.get(section, {})
    
    def update(self, key: str, value: Any):
        """Update configuration value."""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def save(self, path: Optional[str] = None):
        """Save current configuration to file."""
        save_path = path or self.config_path
        os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
        with open(save_path, 'w') as f:
            yaml.dump(self._config, f, default_flow_style=False, sort_keys=False)
