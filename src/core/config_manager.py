#!/usr/bin/env python3

import json
import os
from pathlib import Path
from typing import Dict, Any, Tuple

from core.models import Config, CommandStatus


CONFIG_FILE = Path.home() / ".desktopcommander_config.json"


def save_config(config: Config) -> Tuple[str, CommandStatus]:
    """Save configuration to file."""
    try:
        config_data = {
            "ollama_url": config.ollama_url,
            "ollama_model": config.ollama_model,
            "command_timeout": config.command_timeout
        }
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        return f"Configuration saved to {CONFIG_FILE}", CommandStatus.SUCCESS
        
    except Exception as e:
        return f"Failed to save configuration: {str(e)}", CommandStatus.ERROR


def load_config() -> Tuple[Config, CommandStatus]:
    """Load configuration from file."""
    try:
        if not CONFIG_FILE.exists():
            # Return default config if file doesn't exist
            return Config.from_env(), CommandStatus.WARNING
        
        with open(CONFIG_FILE, 'r') as f:
            config_data = json.load(f)
        
        config = Config(
            ollama_url=config_data.get("ollama_url", "http://localhost:11434/api/generate"),
            ollama_model=config_data.get("ollama_model", "gemma3:4b"),
            command_timeout=config_data.get("command_timeout", 30)
        )
        
        return config, CommandStatus.SUCCESS
        
    except Exception as e:
        # Return default config on error
        return Config.from_env(), CommandStatus.ERROR


def reset_config() -> Tuple[Config, CommandStatus]:
    """Reset configuration to defaults."""
    try:
        # Remove config file if it exists
        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()
        
        config = Config.from_env()
        return config, CommandStatus.SUCCESS
        
    except Exception as e:
        return Config.from_env(), CommandStatus.ERROR


def get_config_info() -> Dict[str, Any]:
    """Get information about the configuration file."""
    return {
        "config_file": str(CONFIG_FILE),
        "exists": CONFIG_FILE.exists(),
        "size": CONFIG_FILE.stat().st_size if CONFIG_FILE.exists() else 0,
        "modified": CONFIG_FILE.stat().st_mtime if CONFIG_FILE.exists() else None
    }