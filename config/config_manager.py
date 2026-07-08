"""
Configuration management module for enterprise competitor analysis system.

This module provides centralized configuration management with validation,
supporting environment variables, JSON files, and default values.
"""

import os
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from core.exceptions import ConfigurationException


@dataclass
class AppConfig:
    """
    Application configuration with typed fields.
    
    Attributes:
        api_key: Zhipu AI API key
        model_name: LLM model name
        cache_enabled: Whether caching is enabled
        cache_expiry_seconds: Cache TTL in seconds
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_concurrent_requests: Maximum concurrent LLM requests
        api_timeout_seconds: API request timeout in seconds
        max_retries: Maximum retry attempts for failed API calls
    """
    api_key: str = "5cc61335eb4e4ea0a3b6277741d915b8.I3mHKoh7woyJndIE"
    model_name: str = "GLM-4.7-Flash"
    cache_enabled: bool = True
    cache_expiry_seconds: int = 3600
    log_level: str = "INFO"
    max_concurrent_requests: int = 3
    api_timeout_seconds: int = 60
    max_retries: int = 3


@dataclass
class PathConfig:
    """
    Path configuration for directories and files.
    
    Attributes:
        base_dir: Base directory of the application
        cache_dir: Directory for cache storage
        logs_dir: Directory for log files
        reports_dir: Directory for generated reports
        history_dir: Directory for analysis history
        prompts_dir: Directory for prompt templates
    """
    base_dir: Path
    cache_dir: Path
    logs_dir: Path
    reports_dir: Path
    history_dir: Path
    prompts_dir: Path


class ConfigManager:
    """
    Centralized configuration manager with validation.
    
    Loads configuration from:
    1. Environment variables (highest priority)
    2. JSON configuration file (if specified)
    3. Hardcoded defaults (lowest priority)
    
    Validates all configuration values before use.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Optional path to JSON configuration file
        """
        self.config_path = config_path
        self._app_config: Optional[AppConfig] = None
        self._path_config: Optional[PathConfig] = None
    
    def load_config(self) -> AppConfig:
        """
        Load and validate application configuration.
        
        Returns:
            Validated AppConfig instance
            
        Raises:
            ConfigurationException: If required config is missing or invalid
        """
        # Load from sources in priority order
        config_dict = self._load_config_dict()
        
        # Create AppConfig
        try:
            app_config = AppConfig(
                api_key=config_dict.get("api_key", ""),
                model_name=config_dict.get("model_name", "GLM-4.7-Flash"),
                cache_enabled=config_dict.get("cache_enabled", True),
                cache_expiry_seconds=config_dict.get("cache_expiry_seconds", 3600),
                log_level=config_dict.get("log_level", "INFO"),
                max_concurrent_requests=config_dict.get("max_concurrent_requests", 3),
                api_timeout_seconds=config_dict.get("api_timeout_seconds", 60),
                max_retries=config_dict.get("max_retries", 3)
            )
        except Exception as e:
            raise ConfigurationException(
                f"Failed to create configuration: {str(e)}"
            )
        
        # Validate configuration
        self._validate_app_config(app_config)
        
        self._app_config = app_config
        return app_config
    
    def get_app_config(self) -> AppConfig:
        """
        Get loaded application configuration.
        
        Returns:
            AppConfig instance
            
        Raises:
            ConfigurationException: If config not loaded yet
        """
        if self._app_config is None:
            raise ConfigurationException("Configuration not loaded. Call load_config() first.")
        return self._app_config
    
    def load_path_config(self, base_dir: Optional[Path] = None) -> PathConfig:
        """
        Load and validate path configuration.
        
        Args:
            base_dir: Base directory (defaults to current directory)
            
        Returns:
            Validated PathConfig instance
            
        Raises:
            ConfigurationException: If paths are invalid
        """
        if base_dir is None:
            base_dir = Path.cwd()
        
        # Create path configuration
        path_config = PathConfig(
            base_dir=base_dir,
            cache_dir=base_dir / "cache",
            logs_dir=base_dir / "logs",
            reports_dir=base_dir / "reports",
            history_dir=base_dir / "history",
            prompts_dir=base_dir / "prompts"
        )
        
        # Validate paths
        self._validate_path_config(path_config)
        
        # Create directories if they don't exist
        self._create_directories(path_config)
        
        self._path_config = path_config
        return path_config
    
    def get_path_config(self) -> PathConfig:
        """
        Get loaded path configuration.
        
        Returns:
            PathConfig instance
            
        Raises:
            ConfigurationException: If config not loaded yet
        """
        if self._path_config is None:
            raise ConfigurationException("Path configuration not loaded. Call load_path_config() first.")
        return self._path_config
    
    def validate_config(self) -> bool:
        """
        Validate all loaded configuration.
        
        Returns:
            True if all validation passes
            
        Raises:
            ConfigurationException: If validation fails
        """
        if self._app_config is None:
            raise ConfigurationException("Configuration not loaded")
        
        self._validate_app_config(self._app_config)
        
        if self._path_config is not None:
            self._validate_path_config(self._path_config)
        
        return True
    
    def _load_config_dict(self) -> dict:
        """
        Load configuration from all sources.
        
        Returns:
            Merged configuration dictionary
        """
        config = {}
        
        # Load from .env file if it exists
        env_file = Path.cwd() / ".env"
        if env_file.exists():
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            # Map .env keys to config keys
                            if key == "ZHIPU_API_KEY":
                                config["api_key"] = value
                            elif key == "ZHIPU_MODEL":
                                config["model_name"] = value
                            elif key == "CACHE_ENABLED":
                                config["cache_enabled"] = value.lower() in ("true", "1", "yes")
                            elif key == "CACHE_EXPIRY_SECONDS":
                                config["cache_expiry_seconds"] = int(value)
                            elif key == "LOG_LEVEL":
                                config["log_level"] = value
                            elif key == "MAX_CONCURRENT_REQUESTS":
                                config["max_concurrent_requests"] = int(value)
                            elif key == "API_TIMEOUT_SECONDS":
                                config["api_timeout_seconds"] = int(value)
                            elif key == "MAX_RETRIES":
                                config["max_retries"] = int(value)
            except Exception as e:
                print(f"Warning: Failed to load .env file: {str(e)}")
        
        # Load from JSON file if specified
        if self.config_path and self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    config.update(file_config)
            except Exception as e:
                raise ConfigurationException(
                    f"Failed to load config file: {str(e)}",
                    field_name="config_file"
                )
        
        # Override with environment variables (highest priority)
        env_mappings = {
            "ZHIPU_API_KEY": "api_key",
            "ZHIPU_MODEL": "model_name",
            "CACHE_ENABLED": "cache_enabled",
            "CACHE_EXPIRY_SECONDS": "cache_expiry_seconds",
            "LOG_LEVEL": "log_level",
            "MAX_CONCURRENT_REQUESTS": "max_concurrent_requests",
            "API_TIMEOUT_SECONDS": "api_timeout_seconds",
            "MAX_RETRIES": "max_retries"
        }
        
        for env_key, config_key in env_mappings.items():
            env_value = os.getenv(env_key)
            if env_value is not None:
                # Convert types
                if config_key in ["cache_enabled"]:
                    config[config_key] = env_value.lower() in ("true", "1", "yes")
                elif config_key in ["cache_expiry_seconds", "max_concurrent_requests", 
                                   "api_timeout_seconds", "max_retries"]:
                    try:
                        config[config_key] = int(env_value)
                    except ValueError:
                        raise ConfigurationException(
                            f"Invalid integer value for {env_key}: {env_value}",
                            field_name=config_key
                        )
                else:
                    config[config_key] = env_value
        
        return config
    
    def _validate_app_config(self, config: AppConfig) -> None:
        """
        Validate application configuration values.
        
        Args:
            config: AppConfig to validate
            
        Raises:
            ConfigurationException: If validation fails
        """
        # Validate API key
        if not config.api_key:
            raise ConfigurationException(
                "Missing required configuration: api_key",
                field_name="api_key"
            )
        
        if not isinstance(config.api_key, str):
            raise ConfigurationException(
                "Invalid configuration for api_key: must be a string",
                field_name="api_key"
            )
        
        if not (32 <= len(config.api_key) <= 128):
            raise ConfigurationException(
                "Invalid configuration for api_key: length must be between 32 and 128 characters",
                field_name="api_key"
            )
        
        # Validate cache_expiry_seconds
        if not (1 <= config.cache_expiry_seconds <= 86400):
            raise ConfigurationException(
                "Invalid configuration for cache_expiry_seconds: must be between 1 and 86400",
                field_name="cache_expiry_seconds"
            )
        
        # Validate max_concurrent_requests
        if not (1 <= config.max_concurrent_requests <= 10):
            raise ConfigurationException(
                "Invalid configuration for max_concurrent_requests: must be between 1 and 10",
                field_name="max_concurrent_requests"
            )
        
        # Validate api_timeout_seconds
        if not (1 <= config.api_timeout_seconds <= 300):
            raise ConfigurationException(
                "Invalid configuration for api_timeout_seconds: must be between 1 and 300",
                field_name="api_timeout_seconds"
            )
        
        # Validate max_retries
        if not (0 <= config.max_retries <= 5):
            raise ConfigurationException(
                "Invalid configuration for max_retries: must be between 0 and 5",
                field_name="max_retries"
            )
        
        # Validate log_level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if config.log_level not in valid_log_levels:
            raise ConfigurationException(
                f"Invalid configuration for log_level: must be one of {valid_log_levels}",
                field_name="log_level"
            )
    
    def _validate_path_config(self, config: PathConfig) -> None:
        """
        Validate path configuration.
        
        Args:
            config: PathConfig to validate
            
        Raises:
            ConfigurationException: If paths are invalid
        """
        # Validate base_dir exists
        if not config.base_dir.exists():
            raise ConfigurationException(
                f"Base directory does not exist: {config.base_dir}",
                field_name="base_dir"
            )
        
        if not config.base_dir.is_dir():
            raise ConfigurationException(
                f"Base directory is not a directory: {config.base_dir}",
                field_name="base_dir"
            )
    
    def _create_directories(self, config: PathConfig) -> None:
        """
        Create directories if they don't exist.
        
        Args:
            config: PathConfig with directory paths
        """
        directories = [
            config.cache_dir,
            config.logs_dir,
            config.reports_dir,
            config.history_dir,
            config.prompts_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
