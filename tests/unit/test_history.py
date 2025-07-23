#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from datetime import datetime
from unittest.mock import patch

import pytest

from core.history import add_to_history
from core.models import CommandEntry, CommandStatus


class TestAddToHistory:
    """Test command history management."""
    
    @patch('src.core.history.datetime')
    def test_add_to_history_success(self, mock_datetime):
        mock_datetime.now.return_value.strftime.return_value = "12:34:56"
        
        history = []
        entry = add_to_history(
            history,
            "list files",
            "ls -la",
            "file1.txt\nfile2.txt",
            CommandStatus.SUCCESS
        )
        
        assert len(history) == 1
        assert history[0] == entry
        assert entry.timestamp == "12:34:56"
        assert entry.prompt == "list files"
        assert entry.command == "ls -la"
        assert entry.output == "file1.txt\nfile2.txt"
        assert entry.status == CommandStatus.SUCCESS
    
    @patch('src.core.history.datetime')
    def test_add_to_history_multiple_entries(self, mock_datetime):
        mock_datetime.now.return_value.strftime.side_effect = ["12:00:00", "12:00:30", "12:01:00"]
        
        history = []
        
        # Add first entry
        add_to_history(history, "first", "echo 1", "1", CommandStatus.SUCCESS)
        
        # Add second entry
        add_to_history(history, "second", "echo 2", "2", CommandStatus.ERROR)
        
        # Add third entry
        add_to_history(history, "third", "echo 3", "3", CommandStatus.WARNING)
        
        assert len(history) == 3
        assert history[0].timestamp == "12:00:00"
        assert history[1].timestamp == "12:00:30"
        assert history[2].timestamp == "12:01:00"
        assert history[0].status == CommandStatus.SUCCESS
        assert history[1].status == CommandStatus.ERROR
        assert history[2].status == CommandStatus.WARNING
    
    @patch('src.core.history.datetime')
    def test_add_to_history_long_output(self, mock_datetime):
        mock_datetime.now.return_value.strftime.return_value = "12:34:56"
        
        history = []
        long_output = "x" * 600
        
        entry = add_to_history(
            history,
            "generate long output",
            "cat bigfile",
            long_output,
            CommandStatus.SUCCESS
        )
        
        assert len(entry.output) == 503  # 500 chars + "..."
        assert entry.output.endswith("...")
    
    def test_add_to_history_preserves_existing(self):
        # Create initial history
        existing_entry = CommandEntry(
            timestamp="11:00:00",
            prompt="existing",
            command="echo existing",
            output="existing",
            status=CommandStatus.SUCCESS
        )
        history = [existing_entry]
        
        # Add new entry
        with patch('src.core.history.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "12:00:00"
            
            add_to_history(
                history,
                "new",
                "echo new",
                "new",
                CommandStatus.SUCCESS
            )
        
        assert len(history) == 2
        assert history[0] == existing_entry  # Original entry preserved
        assert history[1].prompt == "new"    # New entry added