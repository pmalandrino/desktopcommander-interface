#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path
from typing import Tuple

from core.models import CommandStatus
from core.security import is_command_safe, estimate_command_risk, is_command_in_safe_mode_whitelist


def execute_command(command: str, timeout: int, dry_run: bool = False, safe_mode: bool = False) -> Tuple[str, CommandStatus]:
    """Execute a shell command with optional dry-run mode and safe mode."""
    if not is_command_safe(command):
        return "Command blocked for safety", CommandStatus.WARNING
    
    # Check safe mode restrictions
    if safe_mode and not is_command_in_safe_mode_whitelist(command):
        return f"""Command blocked by SAFE MODE

The command '{command}' is not in the safe mode whitelist.

Safe mode only allows read-only commands that cannot modify the system.
To execute this command, disable safe mode.

Allowed command types in safe mode:
- File listing and reading (ls, cat, grep, etc.)
- System information (ps, df, uname, etc.)
- Network diagnostics (ping, dig, etc.)
- Package listings (pip list, npm list, etc.)
- Git read operations (git status, git log, etc.)""", CommandStatus.WARNING
    
    # Check for dry-run mode
    if dry_run:
        dry_run_output = f"""[DRY RUN MODE - Command NOT executed]

Command that would be executed:
$ {command}

Working directory: {Path.cwd()}
User permissions: {os.getlogin() if hasattr(os, 'getlogin') else 'current user'}
Shell: {os.environ.get('SHELL', 'default')}

Safety check: {'PASSED' if is_command_safe(command) else 'FAILED'}
Estimated risk: {estimate_command_risk(command)}

To actually execute this command, disable dry-run mode."""
        return dry_run_output, CommandStatus.SUCCESS
    
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            timeout=timeout, cwd=Path.cwd()
        )
        
        output = result.stdout or ""
        stderr = result.stderr or ""
        
        if stderr and result.returncode != 0:
            return f"Error:\n{stderr}\n\nOutput:\n{output}", CommandStatus.ERROR
        elif stderr:
            return f"Warnings:\n{stderr}\n\nOutput:\n{output}", CommandStatus.WARNING
        
        return output or "Command executed successfully (no output)", CommandStatus.SUCCESS
        
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout} seconds", CommandStatus.ERROR
    except Exception as e:
        return f"Execution failed: {str(e)}", CommandStatus.ERROR