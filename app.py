#!/usr/bin/env python3

import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Tuple

import gradio as gr
import requests

class CommandStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"

@dataclass
class CommandEntry:
    timestamp: str
    prompt: str
    command: str
    output: str
    status: CommandStatus

    def __post_init__(self):
        if len(self.output) > 500:
            self.output = self.output[:500] + "..."

@dataclass
class Config:
    ollama_url: str = "http://localhost:11434/api/generate"
    ollama_model: str = "gemma3:4b"
    command_timeout: int = 30

    @classmethod
    def from_env(cls):
        return cls(
            ollama_url=os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate"),
            ollama_model=os.environ.get("OLLAMA_MODEL", "gemma3:4b"),
            command_timeout=int(os.environ.get("COMMAND_TIMEOUT", "30"))
        )

@dataclass
class AppState:
    command_history: List[CommandEntry] = field(default_factory=list)
    config: Config = field(default_factory=Config.from_env)

app_state = AppState()

DANGEROUS_PATTERNS = [
    "rm -rf /", "sudo rm", "format", "mkfs", "dd if=/dev/zero",
    "> /dev/", ":(){ :|:& };:", "chmod -R 777 /", "chown -R",
    "rm -rf /*", "sudo shutdown", "sudo reboot", "sudo halt",
    "wipefs", "shred", ">/dev/sd", "cat /dev/urandom >",
    "sudo passwd", "sudo userdel", "sudo usermod", "sudo groupdel",
    "iptables -F", "systemctl stop", "service stop", "kill -9",
    "truncate", ">/etc/", "curl | sh", "wget | sh", "bash <(",
    "eval $(", "$(curl", "$(wget", "base64 -d |", "| base64 -d"
]

def check_ollama():
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=2)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            if app_state.config.ollama_model in model_names:
                return f"Ollama ready ({app_state.config.ollama_model})", CommandStatus.SUCCESS
            return f"Model {app_state.config.ollama_model} not found", CommandStatus.ERROR
        return "Ollama not responding", CommandStatus.ERROR
    except requests.RequestException:
        return "Ollama offline", CommandStatus.ERROR

def generate_command(prompt: str) -> Tuple[str, CommandStatus]:
    enhanced_prompt = f"""You are a helpful shell command expert. Generate a single shell command.
User request: {prompt}
Operating system: {sys.platform}
Important: Respond with ONLY the command, no explanations or markdown."""
    
    payload = {
        "model": app_state.config.ollama_model,
        "prompt": enhanced_prompt,
        "stream": False,
        "temperature": 0.7,
        "options": {"num_predict": 100}
    }
    
    try:
        resp = requests.post(app_state.config.ollama_url, json=payload, 
                           timeout=app_state.config.command_timeout)
        resp.raise_for_status()
        
        response_data = resp.json()
        if "response" in response_data:
            command = response_data["response"].strip().replace("```", "").strip()
            return command, CommandStatus.SUCCESS
        return "", CommandStatus.ERROR
            
    except requests.exceptions.ConnectionError:
        return "Cannot connect to Ollama. Please run: ollama serve", CommandStatus.ERROR
    except requests.exceptions.Timeout:
        return "Request timed out. Try a simpler prompt.", CommandStatus.WARNING
    except Exception as e:
        return f"Error: {str(e)}", CommandStatus.ERROR

def is_command_safe(command: str) -> bool:
    command_lower = command.lower()
    return not any(pattern in command_lower for pattern in DANGEROUS_PATTERNS)

def execute_command(command: str) -> Tuple[str, CommandStatus]:
    if not is_command_safe(command):
        return "Command blocked for safety", CommandStatus.WARNING
    
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            timeout=app_state.config.command_timeout, cwd=Path.cwd()
        )
        
        output = result.stdout or ""
        stderr = result.stderr or ""
        
        if stderr and result.returncode != 0:
            return f"Error:\n{stderr}\n\nOutput:\n{output}", CommandStatus.ERROR
        elif stderr:
            return f"Warnings:\n{stderr}\n\nOutput:\n{output}", CommandStatus.WARNING
        
        return output or "Command executed successfully (no output)", CommandStatus.SUCCESS
        
    except subprocess.TimeoutExpired:
        return f"Command timed out after {app_state.config.command_timeout} seconds", CommandStatus.ERROR
    except Exception as e:
        return f"Execution failed: {str(e)}", CommandStatus.ERROR

def add_to_history(prompt: str, command: str, output: str, status: CommandStatus):
    entry = CommandEntry(
        timestamp=datetime.now().strftime("%H:%M:%S"),
        prompt=prompt,
        command=command,
        output=output,
        status=status
    )
    app_state.command_history.append(entry)

def process_prompt(prompt: str, execute_immediately: bool = False):
    if not prompt.strip():
        return (
            gr.update(value="", visible=False),
            gr.update(value="Please enter a command or description", visible=True),
            gr.update(visible=False),
            gr.update(value="Please enter a command request", visible=True)
        )
    
    command, cmd_status = generate_command(prompt)
    
    if cmd_status == CommandStatus.ERROR:
        return (
            gr.update(value="", visible=False),
            gr.update(value=command, visible=True),
            gr.update(visible=False),
            gr.update(value="Failed to generate command", visible=True)
        )
    
    if execute_immediately and cmd_status == CommandStatus.SUCCESS:
        output, exec_status = execute_command(command)
        add_to_history(prompt, command, output, exec_status)
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

def execute_displayed_command(command: str):
    if not command.strip():
        return (
            gr.update(value="No command to execute", visible=True),
            gr.update(value="Please generate a command first", visible=True)
        )
    
    output, status = execute_command(command)
    add_to_history("Manual execution", command, output, status)
    return (
        gr.update(value=output, visible=True),
        gr.update(value="Command executed", visible=True)
    )

def clear_interface():
    return (
        gr.update(value=""),
        gr.update(value="", visible=False),
        gr.update(value="", visible=False),
        gr.update(value="Ready for new command", visible=True)
    )

def refresh_status():
    status_text, _ = check_ollama()
    return gr.update(value=f"{status_text}\nReady ({sys.platform})")

def create_ui():
    with gr.Blocks(title="Desktop Commander") as app:
        gr.Markdown("# Desktop Commander")
        gr.Markdown("AI-powered command line interface")
        
        with gr.Row():
            with gr.Column(scale=4):
                system_status = gr.Markdown(value="Loading...")
            with gr.Column(scale=1):
                refresh_btn = gr.Button("🔄 Refresh", size="sm")
        
        with gr.Column():
            prompt_input = gr.Textbox(
                label="Command Request",
                placeholder="Describe what you want to do in natural language...",
                lines=3
            )
            
            with gr.Row():
                generate_btn = gr.Button("Generate Command")
                execute_btn = gr.Button("Generate & Execute", variant="primary")
                clear_btn = gr.Button("Clear", variant="stop")
            
            status_message = gr.Markdown("Ready to generate commands", visible=True)
            
            command_display = gr.Textbox(
                label="Generated Command",
                placeholder="Your generated command will appear here",
                lines=2,
                visible=False,
                interactive=True
            )
            
            manual_execute_btn = gr.Button(
                "Execute Command",
                variant="primary",
                visible=False
            )
            
            output_display = gr.Textbox(
                label="Output",
                lines=15,
                visible=False,
                interactive=False,
                show_copy_button=True
            )
            
            loading_indicator = gr.Markdown("Processing...", visible=False)

        gr.Markdown("Commands are filtered for safety")
        
        command_display.change(
            fn=lambda cmd: gr.update(visible=bool(cmd.strip())),
            inputs=command_display,
            outputs=manual_execute_btn
        )
        
        generate_btn.click(
            fn=lambda p: process_prompt(p, False),
            inputs=prompt_input,
            outputs=[command_display, output_display, loading_indicator, status_message]
        )
        
        execute_btn.click(
            fn=lambda p: process_prompt(p, True),
            inputs=prompt_input,
            outputs=[command_display, output_display, loading_indicator, status_message]
        )
        
        manual_execute_btn.click(
            fn=execute_displayed_command,
            inputs=command_display,
            outputs=[output_display, status_message]
        )
        
        clear_btn.click(
            fn=clear_interface,
            outputs=[prompt_input, command_display, output_display, status_message]
        )
        
        refresh_btn.click(fn=refresh_status, outputs=system_status)
        app.load(refresh_status, outputs=system_status)
    
    return app

if __name__ == "__main__":
    print("Desktop Commander")
    print(f"Working Directory: {os.getcwd()}")
    print(f"Ollama Model: {app_state.config.ollama_model}")
    
    status_text, status_type = check_ollama()
    print(status_text)
    
    if status_type == CommandStatus.ERROR:
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    print("Launching at http://127.0.0.1:7860")
    app = create_ui()
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        inbrowser=True,
        show_error=True
    )