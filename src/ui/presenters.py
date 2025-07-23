#!/usr/bin/env python3

import sys
from typing import Any, Dict, Tuple

import gradio as gr

from core.models import AppState, CommandStatus
from core.command_service import execute_command
from core.ollama_service import generate_command, check_ollama, get_available_models
from core.history import add_to_history
from core.config_manager import save_config, load_config, reset_config


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
    
    def get_available_models(self) -> Tuple[Any, Any]:
        """Get available Ollama models and return dropdown updates."""
        models, status = get_available_models()
        
        if status == CommandStatus.SUCCESS and models:
            # Return dropdown with models and current selection
            return (
                gr.update(choices=models, value=self.app_state.config.ollama_model),
                gr.update(value=f"Found {len(models)} models", visible=True)
            )
        elif status == CommandStatus.WARNING:
            return (
                gr.update(choices=[], value=None),
                gr.update(value="No models found. Run 'ollama pull <model>' to install models.", visible=True)
            )
        else:
            return (
                gr.update(choices=[], value=None),
                gr.update(value="Cannot connect to Ollama. Ensure it's running.", visible=True)
            )
    
    def update_model(self, selected_model: str) -> Any:
        """Update the selected Ollama model."""
        if selected_model:
            self.app_state.config.ollama_model = selected_model
            return self.refresh_status()
        return gr.update()
    
    def update_timeout(self, timeout_value: int) -> Any:
        """Update the command timeout setting."""
        if 5 <= timeout_value <= 300:  # Reasonable bounds
            self.app_state.config.command_timeout = timeout_value
            return gr.update(value=f"Timeout updated to {timeout_value}s")
        return gr.update(value="Timeout must be between 5 and 300 seconds")
    
    def update_ollama_url(self, url: str) -> Any:
        """Update the Ollama URL setting."""
        if url and url.startswith(('http://', 'https://')):
            self.app_state.config.ollama_url = url
            return gr.update(value="URL updated successfully")
        return gr.update(value="Invalid URL format")
    
    def save_configuration(self) -> Any:
        """Save current configuration to file."""
        message, status = save_config(self.app_state.config)
        if status == CommandStatus.SUCCESS:
            return gr.update(value=f"✅ {message}", visible=True)
        else:
            return gr.update(value=f"❌ {message}", visible=True)
    
    def reset_configuration(self) -> Tuple[Any, ...]:
        """Reset configuration to defaults."""
        config, status = reset_config()
        self.app_state.config = config
        
        # Return updates for all config components
        return (
            gr.update(value=config.ollama_model),  # model_dropdown
            gr.update(value=config.ollama_url),    # ollama_url_input  
            gr.update(value=config.command_timeout), # timeout_slider
            self.refresh_status(),                  # system_status
            gr.update(value="✅ Configuration reset to defaults", visible=True)  # status message
        )
    
    def load_saved_configuration(self) -> Tuple[Any, ...]:
        """Load configuration from file."""
        config, status = load_config()
        self.app_state.config = config
        
        message = "Configuration loaded from file" if status == CommandStatus.SUCCESS else "Using default configuration"
        
        # Return updates for all config components
        return (
            gr.update(value=config.ollama_model),   # model_dropdown
            gr.update(value=config.ollama_url),     # ollama_url_input
            gr.update(value=config.command_timeout), # timeout_slider
            self.refresh_status(),                   # system_status
            gr.update(value=f"✅ {message}", visible=True)  # status message
        )