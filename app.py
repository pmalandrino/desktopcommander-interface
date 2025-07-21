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
        * {
            box-sizing: border-box;
        }
        .gradio-container {
            max-width: 1200px !important;
            margin: 0 auto !important;
            padding: 0 !important;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, system-ui, sans-serif !important;
            background: #ffffff !important;
        }
        .block {
            border: none !important;
            box-shadow: none !important;
            background: transparent !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        .main-header {
            background: #1e293b;
            color: white;
            padding: 2rem;
            margin: 0;
            text-align: center;
            border-bottom: 1px solid #334155;
        }
        .main-header h1 {
            font-size: 1.875rem !important;
            font-weight: 400 !important;
            margin: 0 0 0.5rem 0 !important;
        }
        .main-header p {
            margin: 0 !important;
            opacity: 0.8;
            font-size: 1rem !important;
        }
        .content-area {
            padding: 2rem;
            max-width: 800px;
            margin: 0 auto;
        }
        .form-group {
            margin-bottom: 1.5rem;
        }
        .form-group label {
            display: block;
            font-weight: 600;
            color: #374151;
            font-size: 0.875rem;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .command-input textarea, .command-input input {
            width: 100% !important;
            font-size: 1rem !important;
            border: 2px solid #e5e7eb !important;
            border-radius: 8px !important;
            padding: 0.875rem !important;
            transition: border-color 0.2s ease !important;
            background: #ffffff !important;
            font-family: inherit !important;
        }
        .command-input textarea:focus, .command-input input:focus {
            outline: none !important;
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        }
        .button-group {
            display: flex;
            gap: 0.75rem;
            margin: 1.5rem 0;
            flex-wrap: wrap;
        }
        .btn {
            padding: 0.75rem 1.5rem !important;
            font-size: 0.875rem !important;
            font-weight: 600 !important;
            border-radius: 6px !important;
            transition: all 0.2s ease !important;
            border: none !important;
            cursor: pointer !important;
        }
        .btn-primary {
            background: #3b82f6 !important;
            color: white !important;
        }
        .btn-primary:hover {
            background: #2563eb !important;
        }
        .btn-secondary {
            background: #f3f4f6 !important;
            color: #374151 !important;
            border: 1px solid #d1d5db !important;
        }
        .btn-secondary:hover {
            background: #e5e7eb !important;
        }
        .btn-danger {
            background: #ef4444 !important;
            color: white !important;
        }
        .btn-danger:hover {
            background: #dc2626 !important;
        }
        .status-message {
            padding: 0.75rem 1rem;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            font-size: 0.875rem;
            color: #64748b;
            margin: 1rem 0;
        }
        .code-output {
            background: #1e293b !important;
            color: #e2e8f0 !important;
            border: none !important;
            border-radius: 8px !important;
            font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace !important;
            font-size: 0.875rem !important;
            line-height: 1.6 !important;
            padding: 1.5rem !important;
        }
        .code-input {
            background: #f8fafc !important;
            border: 2px solid #e2e8f0 !important;
            border-radius: 6px !important;
            font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace !important;
            font-size: 0.875rem !important;
            padding: 1rem !important;
        }
        .code-input:focus {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        }
        .footer {
            text-align: center;
            padding: 2rem;
            border-top: 1px solid #e5e7eb;
            color: #6b7280;
            font-size: 0.875rem;
            background: #f9fafb;
        }
        """
    ) as app:
        # Header
        gr.HTML("""
        <div class="main-header">
            <h1>Desktop Commander</h1>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.8; font-size: 1.125rem; font-weight: 400;">AI-powered command line interface</p>
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
        with gr.Column(elem_classes=["content-area"]):
            # Input Section
            with gr.Group(elem_classes=["form-group"]):
                prompt_input = gr.Textbox(
                    label="Command Request",
                    placeholder="Describe what you want to do in natural language...",
                    lines=3,
                    elem_classes=["command-input"]
                )
            
            # Action Buttons
            with gr.Row(elem_classes=["button-group"]):
                generate_btn = gr.Button(
                    "Generate Command",
                    elem_classes=["btn", "btn-secondary"]
                )
                execute_btn = gr.Button(
                    "Generate & Execute",
                    elem_classes=["btn", "btn-primary"]
                )
                clear_btn = gr.Button(
                    "Clear",
                    elem_classes=["btn", "btn-danger"]
                )
            
            # Status Message
            status_message = gr.HTML(
                value='<div class="status-message">Ready to generate commands</div>',
                visible=True
            )
            
            # Generated Command Section
            with gr.Group(elem_classes=["form-group"]):
                command_display = gr.Textbox(
                    label="Generated Command",
                    placeholder="Your generated command will appear here",
                    lines=2,
                    visible=False,
                    interactive=True,
                    elem_classes=["code-input"]
                )
                
                manual_execute_btn = gr.Button(
                    "Execute Command",
                    elem_classes=["btn", "btn-primary"],
                    visible=False
                )
            
            # Output Section
            with gr.Group(elem_classes=["form-group"]):
                output_display = gr.Textbox(
                    label="Output",
                    lines=15,
                    visible=False,
                    interactive=False,
                    elem_classes=["code-output"],
                    show_copy_button=True
                )
            
            # Loading indicator
            loading_indicator = gr.HTML(
                value='<div class="status-message">Processing...</div>',
                visible=False
            )


        
        # Footer
        gr.HTML("""
        <div class="footer">
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