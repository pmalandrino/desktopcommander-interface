#!/usr/bin/env python3
"""
Desktop Commander Gradio UI - UX Enhanced Version
Modern, intuitive interface with excellent user experience
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import gradio as gr
import requests

class CommandStatus(Enum):
    """Enum for command statuses"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    LOADING = "loading"


@dataclass
class CommandEntry:
    """Data class for command history entries"""
    timestamp: str
    date: str
    prompt: str
    command: str
    output: str
    status: CommandStatus
    full_output: str = ""

    def __post_init__(self) -> None:
        if not self.full_output:
            self.full_output = self.output
        if len(self.output) > 500:
            self.output = self.output[:500] + "..."


@dataclass
class Config:
    """Configuration management"""
    ollama_url: str = "http://localhost:11434/api/generate"
    ollama_model: str = "gemma3:4b"
    max_history_entries: int = 50
    command_timeout: int = 30
    log_level: str = "INFO"
    log_file: str = "desktop_commander.log"
    safe_mode: bool = True

    @classmethod
    def from_env(cls) -> Config:
        """Load configuration from environment variables"""
        return cls(
            ollama_url=os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate"),
            ollama_model=os.environ.get("OLLAMA_MODEL", "gemma3:4b"),
            max_history_entries=int(os.environ.get("MAX_HISTORY_ENTRIES", "50")),
            command_timeout=int(os.environ.get("COMMAND_TIMEOUT", "30")),
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
            log_file=os.environ.get("LOG_FILE", "desktop_commander.log"),
            safe_mode=os.environ.get("SAFE_MODE", "true").lower() == "true"
        )


@dataclass
class AppState:
    """Application state management"""
    command_history: List[CommandEntry] = field(default_factory=list)
    is_executing: bool = False
    config: Config = field(default_factory=Config.from_env)

    def add_command(self, entry: CommandEntry) -> None:
        """Add command to history with size limit"""
        self.command_history.append(entry)
        if len(self.command_history) > self.config.max_history_entries:
            self.command_history = self.command_history[-self.config.max_history_entries:]


# Global state instance
app_state = AppState()

# Setup logging with config
logging.basicConfig(
    level=getattr(logging, app_state.config.log_level.upper()),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(app_state.config.log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Color scheme and styling
THEME_COLORS = {
    "primary": "#2563eb",      # Blue
    "success": "#10b981",      # Green
    "warning": "#f59e0b",      # Amber
    "danger": "#ef4444",       # Red
    "info": "#3b82f6",         # Light Blue
    "dark": "#1f2937",         # Dark Gray
    "light": "#f9fafb"         # Light Gray
}


def get_greeting() -> str:
    """Get time-appropriate greeting"""
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning! ☀️"
    elif hour < 17:
        return "Good afternoon! 🌤️"
    else:
        return "Good evening! 🌙"

def format_status_message(status: CommandStatus | str, message: str) -> str:
    """Format status messages"""
    return message

def check_system_status() -> Tuple[str, CommandStatus]:
    """Check system status and return formatted message and status type"""
    messages: List[str] = []
    has_error = False
    
    # Check Ollama
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=2)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            if app_state.config.ollama_model in model_names:
                messages.append(f"Ollama ready ({app_state.config.ollama_model})")
            else:
                messages.append(f"Model {app_state.config.ollama_model} not found")
                has_error = True
        else:
            messages.append("Ollama not responding")
            has_error = True
    except requests.RequestException as e:
        logger.error(f"Failed to check Ollama status: {e}")
        messages.append("Ollama offline")
        has_error = True
    
    # System info
    messages.append(f"Ready ({sys.platform})")
    
    status_text = "\n".join(messages)
    status_type = CommandStatus.ERROR if has_error else CommandStatus.SUCCESS
    
    return status_text, status_type

def ollama_generate(prompt: str, temperature: float = 0.7) -> Tuple[str, CommandStatus]:
    """Generate command using Ollama. Returns (command, status)"""
    try:
        enhanced_prompt = f"""You are a helpful shell command expert. Generate a single shell command.
User request: {prompt}
Operating system: {sys.platform}
Important: Respond with ONLY the command, no explanations or markdown."""
        
        payload = {
            "model": app_state.config.ollama_model,
            "prompt": enhanced_prompt,
            "stream": False,
            "temperature": temperature,
            "options": {"num_predict": 100}
        }
        
        logger.info(f"Generating command for prompt: {prompt[:50]}...")
        resp = requests.post(app_state.config.ollama_url, json=payload, timeout=app_state.config.command_timeout)
        resp.raise_for_status()
        
        response_data = resp.json()
        if "response" in response_data:
            command = response_data["response"].strip()
            # Clean up common LLM artifacts
            command = command.replace("```", "").strip()
            logger.info(f"Generated command: {command}")
            return command, CommandStatus.SUCCESS
        else:
            logger.error("No response field in Ollama response")
            return "", CommandStatus.ERROR
            
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Cannot connect to Ollama: {e}")
        return "Cannot connect to Ollama. Please run: ollama serve", CommandStatus.ERROR
    except requests.exceptions.Timeout as e:
        logger.warning(f"Ollama request timed out: {e}")
        return "Request timed out. Try a simpler prompt.", CommandStatus.WARNING
    except Exception as e:
        logger.error(f"Unexpected error in ollama_generate: {e}")
        return f"Error: {str(e)}", CommandStatus.ERROR

def execute_command_safely(command: str) -> Tuple[str, CommandStatus]:
    """Execute command with safety checks. Returns (output, status)"""
    # Enhanced safety checks with more comprehensive patterns
    dangerous_patterns = [
        "rm -rf /", "sudo rm", "format", "mkfs", "dd if=/dev/zero",
        "> /dev/", ":(){ :|:& };:", "chmod -R 777 /", "chown -R",
        "rm -rf /*", "sudo shutdown", "sudo reboot", "sudo halt",
        "wipefs", "shred", ">/dev/sd", "cat /dev/urandom >",
        "sudo passwd", "sudo userdel", "sudo usermod", "sudo groupdel",
        "iptables -F", "systemctl stop", "service stop", "kill -9",
        "truncate", ">/etc/", "curl | sh", "wget | sh", "bash <(",
        "eval $(", "$(curl", "$(wget", "base64 -d |", "| base64 -d"
    ]
    
    command_lower = command.lower()
    for pattern in dangerous_patterns:
        if pattern in command_lower:
            logger.warning(f"Blocked dangerous command: {command}")
            return f"Command blocked for safety: contains '{pattern}'", CommandStatus.WARNING
    
    try:
        logger.info(f"Executing command: {command}")
        # Execute with reasonable limits and security constraints
        secure_env = {
            "LANG": "en_US.UTF-8",
            "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
            "HOME": os.environ.get("HOME", "/tmp"),
            "USER": os.environ.get("USER", "nobody")
        }
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=app_state.config.command_timeout,
            env=secure_env,
            cwd=Path.cwd()
        )
        
        output = result.stdout or ""
        stderr = result.stderr or ""
        
        if stderr and result.returncode != 0:
            full_output = f"Error:\n{stderr}\n\nOutput:\n{output}"
            logger.error(f"Command failed with return code {result.returncode}: {stderr}")
            return full_output, CommandStatus.ERROR
        elif stderr:
            full_output = f"Warnings:\n{stderr}\n\nOutput:\n{output}"
            logger.warning(f"Command completed with warnings: {stderr}")
            return full_output, CommandStatus.WARNING
        
        success_output = output if output else "Command executed successfully (no output)"
        logger.info(f"Command executed successfully")
        return success_output, CommandStatus.SUCCESS
        
    except subprocess.TimeoutExpired as e:
        logger.error(f"Command timed out: {e}")
        return f"Command timed out after {app_state.config.command_timeout} seconds", CommandStatus.ERROR
    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        return f"Execution failed: {str(e)}", CommandStatus.ERROR
def add_to_history(prompt: str, command: str, output: str, status: CommandStatus) -> None:
    """Add command to history"""
    entry = CommandEntry(
        timestamp=datetime.now().strftime("%H:%M:%S"),
        date=datetime.now().strftime("%Y-%m-%d"),
        prompt=prompt,
        command=command,
        output=output,
        status=status,
        full_output=output
    )
    app_state.add_command(entry)
    logger.info(f"Added command to history: {command}")


def process_natural_language(prompt: str, execute_immediately: bool = False) -> Tuple[gr.update, gr.update, gr.update, gr.update]:
    """Process natural language prompt"""
    
    if not prompt.strip():
        return (
            gr.update(value="", visible=False),  # command_display
            gr.update(value="Please enter a command or description", visible=True),  # output_display
            gr.update(visible=False),  # loading_indicator
            gr.update(value="Please enter a command request", visible=True)  # status_message
        )
    
    app_state.is_executing = True
    
    # Generate command
    command, cmd_status = ollama_generate(prompt)
    
    if cmd_status == CommandStatus.ERROR:
        app_state.is_executing = False
        return (
            gr.update(value="", visible=False),
            gr.update(value=command, visible=True),
            gr.update(visible=False),
            gr.update(value="Failed to generate command", visible=True)
        )
    
    # Show generated command
    updates = [
        gr.update(value=command, visible=True),  # command_display
        gr.update(value="", visible=False),  # output_display
        gr.update(visible=False),  # loading_indicator
        gr.update(value="Command generated", visible=True)  # status_message
    ]
    
    if execute_immediately and cmd_status == CommandStatus.SUCCESS:
        output, exec_status = execute_command_safely(command)
        add_to_history(prompt, command, output, exec_status)
        
        updates = [
            gr.update(value=command, visible=True),
            gr.update(value=output, visible=True),
            gr.update(visible=False),
            gr.update(value="Command executed", visible=True)
        ]
    
    app_state.is_executing = False
    return tuple(updates)

def execute_command_click(command: str) -> Tuple[gr.update, gr.update]:
    """Execute command from button click"""
    if not command.strip():
        return (
            gr.update(value="No command to execute", visible=True),
            gr.update(value="Please generate a command first", visible=True)
        )
    
    output, status = execute_command_safely(command)
    add_to_history("Manual execution", command, output, status)
    
    return (
        gr.update(value=output, visible=True),
        gr.update(value="Command executed", visible=True)
    )


def clear_all() -> Tuple[gr.update, gr.update, gr.update, gr.update]:
    """Clear all fields"""
    return (
        gr.update(value=""),  # prompt_input
        gr.update(value="", visible=False),  # command_display
        gr.update(value="", visible=False),  # output_display
        gr.update(value="Ready for new command", visible=True)  # status_message
    )

# Create the enhanced UI
def create_ui() -> gr.Blocks:
    with gr.Blocks(
        title="Desktop Commander",
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="slate",
            neutral_hue="gray",
            font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"]
        ),
        css="""
        .gradio-container {
            max-width: 900px !important;
            margin: auto !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, system-ui, sans-serif !important;
            padding: 1rem;
        }
        .main-header {
            background: #f8fafc;
            color: #1e293b;
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            text-align: center;
            border: 1px solid #e2e8f0;
        }
        .command-input {
            font-size: 1rem !important;
            border-radius: 6px !important;
            border: 1px solid #d1d5db !important;
            transition: all 0.2s ease !important;
        }
        .command-input:focus {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.08) !important;
        }
        .status-bar {
            padding: 0.75rem 1rem;
            border-radius: 6px;
            margin: 1rem 0;
            font-weight: 500;
            border: 1px solid #e5e7eb;
            background: #f9fafb;
        }
        .status-message {
            font-size: 0.9rem !important;
            color: #6b7280 !important;
            text-align: center !important;
            margin: 0.5rem 0 !important;
        }
        .monospace {
            font-family: ui-monospace, 'SF Mono', Monaco, 'Cascadia Code', monospace !important;
            font-size: 0.875rem !important;
            line-height: 1.6 !important;
            background: #f8fafc !important;
        }
        button {
            font-weight: 500 !important;
            transition: all 0.15s ease !important;
        }
        button:hover {
            transform: translateY(-1px) !important;
        }
        """
    ) as app:
        # Header
        gr.HTML("""
        <div class="main-header">
            <h1 style="margin: 0; font-size: 1.75rem; font-weight: 500;">Desktop Commander</h1>
        </div>
        """)
        
        # System Status Bar
        with gr.Row():
            with gr.Column(scale=4):
                status_text, status_type = check_system_status()
                system_status = gr.Markdown(
                    value=status_text,
                    elem_classes=["status-bar"]
                )
            with gr.Column(scale=1):
                refresh_status_btn = gr.Button(
                    "🔄 Refresh",
                    size="sm",
                    variant="secondary"
                )
        
        # Main Content Area
        with gr.Column():
                # Natural Language Input
                prompt_input = gr.Textbox(
                    label="Command Request",
                    placeholder="Describe what you want to do...",
                    lines=2,
                    elem_classes=["command-input"]
                )
                
                # Action Buttons
                with gr.Row():
                    generate_btn = gr.Button(
                        "Generate",
                        variant="secondary",
                        size="lg"
                    )
                    execute_btn = gr.Button(
                        "Generate & Execute",
                        variant="primary",
                        size="lg"
                    )
                    clear_btn = gr.Button(
                        "Clear",
                        variant="stop",
                        size="lg"
                    )
                
                # Status Message
                status_message = gr.Markdown(
                    value="Ready",
                    visible=True,
                    elem_classes=["status-message"]
                )
                
                # Generated Command Display
                command_display = gr.Textbox(
                    label="Generated Command",
                    placeholder="Generated command will appear here",
                    lines=2,
                    visible=False,
                    interactive=True,
                    elem_classes=["monospace"]
                )
                
                # Execute Button for Manual Commands
                with gr.Row():
                    manual_execute_btn = gr.Button(
                        "Execute",
                        variant="primary",
                        visible=False
                    )
                
                # Output Display
                output_display = gr.Textbox(
                    label="Output",
                    lines=12,
                    visible=False,
                    interactive=False,
                    elem_classes=["monospace"],
                    show_copy_button=True
                )
                
                # Loading indicator
                loading_indicator = gr.HTML(
                    value='<div style="text-align: center; padding: 1rem; color: #6b7280;">Processing...</div>',
                    visible=False
                )


        
        # Footer
        gr.HTML("""
        <div style='text-align: center; color: #9ca3af; font-size: 0.75rem; margin-top: 1.5rem; padding: 0.5rem;'>
            Commands are filtered for safety
        </div>
        """)
        
        # Event Handlers
        def update_command_visibility(command: str) -> gr.update:
            return gr.update(visible=bool(command.strip()))
        
        command_display.change(
            fn=update_command_visibility,
            inputs=command_display,
            outputs=manual_execute_btn
        )
        
        generate_btn.click(
            fn=lambda p: process_natural_language(p, False),
            inputs=prompt_input,
            outputs=[command_display, output_display, loading_indicator, status_message]
        )
        
        execute_btn.click(
            fn=lambda p: process_natural_language(p, True),
            inputs=prompt_input,
            outputs=[command_display, output_display, loading_indicator, status_message]
        )
        
        manual_execute_btn.click(
            fn=execute_command_click,
            inputs=command_display,
            outputs=[output_display, status_message]
        )
        
        clear_btn.click(
            fn=clear_all,
            outputs=[prompt_input, command_display, output_display, status_message]
        )
        
        # Define refresh function
        def refresh_status() -> gr.update:
            status_text, _ = check_system_status()
            return gr.update(value=status_text)
        
        # Refresh status button
        refresh_status_btn.click(
            fn=refresh_status,
            outputs=system_status
        )
        
        # Initial load
        app.load(refresh_status, outputs=system_status)
    
    return app

# Main entry point
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 Desktop Commander - UX Enhanced")
    print("="*50)
    print(f"\n📍 Working Directory: {os.getcwd()}")
    print(f"🤖 Using Ollama Model: {app_state.config.ollama_model}")
    print(f"🌐 Ollama URL: {app_state.config.ollama_url}")
    print(f"🛡️ Safe Mode: {'Enabled' if app_state.config.safe_mode else 'Disabled'}")
    print(f"📝 Log Level: {app_state.config.log_level}")
    print(f"📁 Log File: {app_state.config.log_file}")
    
    # Check initial status
    print("\n🔍 Checking system status...")
    status_text, status_type = check_system_status()
    print(status_text)
    
    if status_type == CommandStatus.ERROR:
        print("\n⚠️  Some services are not available.")
        print("You can still use the app, but some features may not work.")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    print("\n🎨 Launching enhanced UI...")
    print("📱 Opening in browser: http://127.0.0.1:7860")
    print("\nPress Ctrl+C to stop the server")
    print("="*50 + "\n")
    
    # Create and launch the app
    app = create_ui()
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        inbrowser=True,
        show_error=True
    )