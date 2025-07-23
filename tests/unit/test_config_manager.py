#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from core.config_manager import save_config, load_config, reset_config, get_config_info
from core.models import Config, CommandStatus


class TestConfigManager:
    """Test configuration management."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.test_config = Config(
            ollama_url="http://test:8080/api",
            ollama_model="test-model",
            command_timeout=60
        )
    
    @patch('core.config_manager.CONFIG_FILE')
    def test_save_config_success(self, mock_config_file):
        """Test successful configuration saving."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            mock_config_file.__str__ = lambda: temp_file.name
            mock_config_file.open = lambda mode: open(temp_file.name, mode)
            
            message, status = save_config(self.test_config)
            
            assert status == CommandStatus.SUCCESS
            assert "Configuration saved" in message
            
            # Verify file contents
            with open(temp_file.name, 'r') as f:
                data = json.load(f)
            
            assert data["ollama_url"] == "http://test:8080/api"
            assert data["ollama_model"] == "test-model"
            assert data["command_timeout"] == 60
            
            # Cleanup
            os.unlink(temp_file.name)
    
    @patch('core.config_manager.CONFIG_FILE')
    def test_load_config_success(self, mock_config_file):
        """Test successful configuration loading."""
        config_data = {
            "ollama_url": "http://loaded:9000/api",
            "ollama_model": "loaded-model",
            "command_timeout": 90
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            json.dump(config_data, temp_file)
            temp_file.flush()
            
            mock_config_file.exists.return_value = True
            mock_config_file.open = lambda mode: open(temp_file.name, mode)
            
            config, status = load_config()
            
            assert status == CommandStatus.SUCCESS
            assert config.ollama_url == "http://loaded:9000/api"
            assert config.ollama_model == "loaded-model"
            assert config.command_timeout == 90
            
            # Cleanup
            os.unlink(temp_file.name)
    
    @patch('core.config_manager.CONFIG_FILE')
    def test_load_config_file_not_exists(self, mock_config_file):
        """Test loading config when file doesn't exist."""
        mock_config_file.exists.return_value = False
        
        config, status = load_config()
        
        assert status == CommandStatus.WARNING
        assert isinstance(config, Config)
        # Should return default config
        assert config.ollama_url == "http://localhost:11434/api/generate"
    
    @patch('core.config_manager.CONFIG_FILE')
    def test_reset_config(self, mock_config_file):
        """Test configuration reset."""
        mock_config_file.exists.return_value = True
        mock_config_file.unlink = MagicMock()
        
        config, status = reset_config()
        
        assert status == CommandStatus.SUCCESS
        assert isinstance(config, Config)
        mock_config_file.unlink.assert_called_once()
    
    @patch('core.config_manager.CONFIG_FILE')
    def test_get_config_info(self, mock_config_file):
        """Test getting configuration info."""
        mock_stat = MagicMock()
        mock_stat.st_size = 1024
        mock_stat.st_mtime = 1609459200
        
        mock_config_file.exists.return_value = True
        mock_config_file.stat.return_value = mock_stat
        mock_config_file.__str__ = lambda: "/test/config.json"
        
        info = get_config_info()
        
        assert info["config_file"] == "/test/config.json"
        assert info["exists"] is True
        assert info["size"] == 1024
        assert info["modified"] == 1609459200