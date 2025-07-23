#!/usr/bin/env python3

import sys
from typing import Any, Dict, Tuple

import gradio as gr

from core.models import AppState, CommandStatus
from core.command_service import execute_command
from core.ollama_service import generate_command, check_ollama
from core.history import add_to_history


class CommandPresenter:
    """Handles the presentation logic for command operations."""
    
    def __init__(self, app_state: AppState):
        self.app_state = app_state
    
    def process_prompt(self, prompt: str, execute_immediately: bool = False) -> Tuple[Any, ...]:
        """Process a command prompt and return UI updates."""
        if not prompt.strip():
            return (
                gr.update(value="", visible=False),
                gr.update(value="Please enter a command or description", visible=True),
                gr.update(visible=False),
                gr.update(value="Please enter a command request", visible=True)
            )
        
        command, cmd_status = generate_command(
            prompt,
            self.app_state.config.ollama_url,
            self.app_state.config.ollama_model,
            self.app_state.config.command_timeout
        )
        
        if cmd_status == CommandStatus.ERROR:
            return (
                gr.update(value="", visible=False),
                gr.update(value=command, visible=True),
                gr.update(visible=False),
                gr.update(value="Failed to generate command", visible=True)
            )
        
        if execute_immediately and cmd_status == CommandStatus.SUCCESS:
            output, exec_status = execute_command(
                command,
                self.app_state.config.command_timeout,
                self.app_state.dry_run_mode,
                self.app_state.safe_mode
            )
            add_to_history(
                self.app_state.command_history,
                prompt, command, output, exec_status
            )
            return (
                gr.update(value=command, visible=True),
                gr.update(value=output, visible=True),
                gr.update(visible=False),
                gr.update(value="Command executed", visible=True)
            )
        
        return (
            gr.update(value=command, visible=True),
            gr.update(value="", visible=False),
            gr.update(visible=False),
            gr.update(value="Command generated", visible=True)
        )
    
    def execute_displayed_command(self, command: str) -> Tuple[Any, ...]:
        """Execute a displayed command and return UI updates."""
        if not command.strip():
            return (
                gr.update(value="No command to execute", visible=True),
                gr.update(value="Please generate a command first", visible=True)
            )
        
        output, status = execute_command(
            command,
            self.app_state.config.command_timeout,
            self.app_state.dry_run_mode,
            self.app_state.safe_mode
        )
        add_to_history(
            self.app_state.command_history,
            "Manual execution", command, output, status
        )
        return (
            gr.update(value=output, visible=True),
            gr.update(value="Command executed", visible=True)
        )
    
    def clear_interface(self) -> Tuple[Any, ...]:
        """Clear the interface and return UI updates."""
        return (
            gr.update(value=""),
            gr.update(value="", visible=False),
            gr.update(value="", visible=False),
            gr.update(value="Ready for new command", visible=True)
        )
    
    def refresh_status(self) -> Any:
        """Refresh and return the system status."""
        status_text, _ = check_ollama(self.app_state.config.ollama_model)
        
        modes = []
        if self.app_state.dry_run_mode:
            modes.append("DRY RUN MODE ACTIVE")
        if self.app_state.safe_mode:
            modes.append("SAFE MODE ACTIVE")
        if not modes:
            modes.append("Live execution mode")
        
        mode_status = " | ".join(modes)
        return gr.update(value=f"{status_text}\nReady ({sys.platform})\n{mode_status}")
    
    def toggle_dry_run(self, is_enabled: bool) -> Any:
        """Toggle dry-run mode and return updated status."""
        self.app_state.dry_run_mode = is_enabled
        return self.refresh_status()
    
    def toggle_safe_mode(self, is_enabled: bool) -> Any:
        """Toggle safe mode and return updated status."""
        self.app_state.safe_mode = is_enabled
        return self.refresh_status()