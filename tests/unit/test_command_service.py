#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import subprocess
from unittest.mock import patch, MagicMock

import pytest

from core.command_service import execute_command
from core.models import CommandStatus


class TestExecuteCommand:
    """Test command execution service."""
    
    @patch('src.core.command_service.subprocess.run')
    def test_execute_command_success(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = "Success output"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        output, status = execute_command("echo test", timeout=30, dry_run=False)
        
        assert output == "Success output"
        assert status == CommandStatus.SUCCESS
        mock_run.assert_called_once()
    
    @patch('src.core.command_service.subprocess.run')
    def test_execute_command_error(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.stderr = "Error occurred"
        mock_result.returncode = 1
        mock_run.return_value = mock_result
        
        output, status = execute_command("bad-command", timeout=30, dry_run=False)
        
        assert "Error occurred" in output
        assert status == CommandStatus.ERROR
    
    @patch('src.core.command_service.subprocess.run')
    def test_execute_command_warning(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = "Output with warnings"
        mock_result.stderr = "Warning message"
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        output, status = execute_command("command-with-warnings", timeout=30, dry_run=False)
        
        assert "Warning message" in output
        assert "Output with warnings" in output
        assert status == CommandStatus.WARNING
    
    @patch('src.core.command_service.subprocess.run')
    def test_execute_command_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired('cmd', 30)
        
        output, status = execute_command("slow-command", timeout=30, dry_run=False)
        
        assert "timed out after 30 seconds" in output
        assert status == CommandStatus.ERROR
    
    def test_execute_command_unsafe(self):
        output, status = execute_command("rm -rf /", timeout=30, dry_run=False)
        
        assert output == "Command blocked for safety"
        assert status == CommandStatus.WARNING
    
    def test_execute_command_dry_run(self):
        output, status = execute_command("echo test", timeout=30, dry_run=True)
        
        assert "[DRY RUN MODE - Command NOT executed]" in output
        assert "echo test" in output
        assert "Safety check: PASSED" in output
        assert "Estimated risk: LOW" in output
        assert status == CommandStatus.SUCCESS
    
    def test_execute_command_dry_run_high_risk(self):
        output, status = execute_command("rm important.txt", timeout=30, dry_run=True)
        
        assert "[DRY RUN MODE - Command NOT executed]" in output
        assert "rm important.txt" in output
        assert "Estimated risk: HIGH" in output
        assert status == CommandStatus.SUCCESS
    
    @patch('src.core.command_service.subprocess.run')
    def test_execute_command_no_output(self, mock_run):
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        output, status = execute_command("silent-command", timeout=30, dry_run=False)
        
        assert output == "Command executed successfully (no output)"
        assert status == CommandStatus.SUCCESS