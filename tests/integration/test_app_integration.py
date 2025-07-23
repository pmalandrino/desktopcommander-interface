#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from unittest.mock import patch

import pytest

from core.models import AppState, CommandStatus
from ui.presenters import CommandPresenter


class TestCommandPresenterIntegration:
    """Integration tests for CommandPresenter."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app_state = AppState()
        self.presenter = CommandPresenter(self.app_state)
    
    @patch('src.ui.presenters.generate_command')
    @patch('src.ui.presenters.execute_command')
    def test_process_prompt_generate_only(self, mock_execute, mock_generate):
        mock_generate.return_value = ("ls -la", CommandStatus.SUCCESS)
        
        result = self.presenter.process_prompt("list files", execute_immediately=False)
        
        # Check that command is displayed but not executed
        assert result[0].value == "ls -la"  # command_display
        assert result[0].visible is True
        assert result[1].value == ""        # output_display
        assert result[1].visible is False
        assert result[3].value == "Command generated"
        
        mock_generate.assert_called_once()
        mock_execute.assert_not_called()
    
    @patch('src.ui.presenters.generate_command')
    @patch('src.ui.presenters.execute_command')
    def test_process_prompt_generate_and_execute(self, mock_execute, mock_generate):
        mock_generate.return_value = ("echo test", CommandStatus.SUCCESS)
        mock_execute.return_value = ("test", CommandStatus.SUCCESS)
        
        result = self.presenter.process_prompt("print test", execute_immediately=True)
        
        # Check that command is displayed and executed
        assert result[0].value == "echo test"  # command_display
        assert result[0].visible is True
        assert result[1].value == "test"       # output_display
        assert result[1].visible is True
        assert result[3].value == "Command executed"
        
        mock_generate.assert_called_once()
        mock_execute.assert_called_once_with("echo test", 30, False, False)
        
        # Check history
        assert len(self.app_state.command_history) == 1
        assert self.app_state.command_history[0].command == "echo test"
    
    def test_process_prompt_empty(self):
        result = self.presenter.process_prompt("", execute_immediately=False)
        
        assert result[0].value == ""
        assert result[0].visible is False
        assert result[1].value == "Please enter a command or description"
        assert result[3].value == "Please enter a command request"
    
    @patch('src.ui.presenters.generate_command')
    def test_process_prompt_generation_error(self, mock_generate):
        mock_generate.return_value = ("Ollama offline", CommandStatus.ERROR)
        
        result = self.presenter.process_prompt("do something", execute_immediately=False)
        
        assert result[0].value == ""
        assert result[0].visible is False
        assert result[1].value == "Ollama offline"
        assert result[3].value == "Failed to generate command"
    
    def test_toggle_dry_run(self):
        # Initially dry run is off
        assert self.app_state.dry_run_mode is False
        
        # Enable dry run
        result = self.presenter.toggle_dry_run(True)
        assert self.app_state.dry_run_mode is True
        assert "DRY RUN MODE ACTIVE" in result.value
        
        # Disable dry run
        result = self.presenter.toggle_dry_run(False)
        assert self.app_state.dry_run_mode is False
        assert "Live execution mode" in result.value
    
    @patch('src.ui.presenters.execute_command')
    def test_execute_displayed_command_dry_run(self, mock_execute):
        mock_execute.return_value = ("[DRY RUN MODE - Command NOT executed]", CommandStatus.SUCCESS)
        
        self.app_state.dry_run_mode = True
        result = self.presenter.execute_displayed_command("rm important.txt")
        
        assert "[DRY RUN MODE" in result[0].value
        assert result[1].value == "Command executed"
        mock_execute.assert_called_once_with("rm important.txt", 30, True, False)
    
    def test_clear_interface(self):
        result = self.presenter.clear_interface()
        
        assert result[0].value == ""  # prompt_input
        assert result[1].value == ""  # command_display
        assert result[1].visible is False
        assert result[2].value == ""  # output_display
        assert result[2].visible is False
        assert result[3].value == "Ready for new command"