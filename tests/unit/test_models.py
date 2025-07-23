#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from unittest.mock import patch

import pytest

from core.models import CommandEntry, CommandStatus, Config, AppState


class TestCommandEntry:
    """Test CommandEntry model."""
    
    def test_command_entry_creation(self):
        entry = CommandEntry(
            timestamp="12:34:56",
            prompt="list files",
            command="ls -la",
            output="file1.txt\nfile2.txt",
            status=CommandStatus.SUCCESS
        )
        assert entry.timestamp == "12:34:56"
        assert entry.prompt == "list files"
        assert entry.command == "ls -la"
        assert entry.output == "file1.txt\nfile2.txt"
        assert entry.status == CommandStatus.SUCCESS
    
    def test_command_entry_output_truncation(self):
        long_output = "x" * 600
        entry = CommandEntry(
            timestamp="12:34:56",
            prompt="test",
            command="test",
            output=long_output,
            status=CommandStatus.SUCCESS
        )
        assert len(entry.output) == 503  # 500 chars + "..."
        assert entry.output.endswith("...")


class TestConfig:
    """Test Config model."""
    
    def test_config_defaults(self):
        config = Config()
        assert config.ollama_url == "http://localhost:11434/api/generate"
        assert config.ollama_model == "gemma3:4b"
        assert config.command_timeout == 30
    
    def test_config_custom_values(self):
        config = Config(
            ollama_url="http://custom:8080/api",
            ollama_model="llama2",
            command_timeout=60
        )
        assert config.ollama_url == "http://custom:8080/api"
        assert config.ollama_model == "llama2"
        assert config.command_timeout == 60
    
    @patch.dict(os.environ, {
        "OLLAMA_URL": "http://env:9999/api",
        "OLLAMA_MODEL": "custom-model",
        "COMMAND_TIMEOUT": "45"
    })
    def test_config_from_env(self):
        config = Config.from_env()
        assert config.ollama_url == "http://env:9999/api"
        assert config.ollama_model == "custom-model"
        assert config.command_timeout == 45


class TestAppState:
    """Test AppState model."""
    
    def test_app_state_defaults(self):
        state = AppState()
        assert state.command_history == []
        assert isinstance(state.config, Config)
        assert state.dry_run_mode is False
    
    def test_app_state_with_history(self):
        entry = CommandEntry(
            timestamp="12:00:00",
            prompt="test",
            command="echo test",
            output="test",
            status=CommandStatus.SUCCESS
        )
        state = AppState(command_history=[entry])
        assert len(state.command_history) == 1
        assert state.command_history[0] == entry
    
    def test_app_state_dry_run_mode(self):
        state = AppState(dry_run_mode=True)
        assert state.dry_run_mode is True