"""Configuration management using Pydantic settings."""
import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    """Database configuration."""
    
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=3306, description="Database port")
    username: str = Field(description="Database username")
    password: str = Field(description="Database password")
    database: str = Field(description="Database name")
    
    model_config = SettingsConfigDict(
        env_prefix="DB_",
        env_file=".env",
        case_sensitive=False
    )


class HoneypotConfig(BaseSettings):
    """Honeypot configuration."""
    
    hostname: str = Field(default="server", description="Honeypot hostname")
    listen_port: int = Field(default=2222, description="SSH listen port")
    log_path: Path = Field(default=Path("logs"), description="Log directory")
    data_path: Path = Field(default=Path("data"), description="Data directory")
    filesystem_file: Path = Field(
        default=Path("data/filesystem.pickle"), 
        description="Filesystem pickle file"
    )
    
    # Security settings
    max_sessions: int = Field(default=100, description="Maximum concurrent sessions")
    session_timeout: int = Field(default=3600, description="Session timeout in seconds")
    
    model_config = SettingsConfigDict(
        env_prefix="HONEYPOT_",
        env_file=".env",
        case_sensitive=False
    )


class RLConfig(BaseSettings):
    """Reinforcement Learning configuration."""
    
    learning_rate: float = Field(default=0.01, description="Learning rate")
    epsilon: float = Field(default=0.1, description="Exploration rate")
    gamma: float = Field(default=0.95, description="Discount factor")
    batch_size: int = Field(default=32, description="Training batch size")
    memory_size: int = Field(default=10000, description="Replay buffer size")
    
    model_config = SettingsConfigDict(
        env_prefix="RL_",
        env_file=".env",
        case_sensitive=False
    )


class AppConfig(BaseSettings):
    """Main application configuration."""
    
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Component configs
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    honeypot: HoneypotConfig = Field(default_factory=HoneypotConfig)
    rl: RLConfig = Field(default_factory=RLConfig)
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )


def get_config() -> AppConfig:
    """Get application configuration."""
    return AppConfig()