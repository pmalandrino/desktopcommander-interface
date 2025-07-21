#!/usr/bin/env python3
"""
Desktop Commander Gradio UI - Simple Version
Uses direct shell execution as fallback if Desktop Commander has issues
"""

import gradio as gr
import requests
import subprocess
import json
import time
from datetime import datetime
import os
import sys

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:4b"  # Using your installed model
USE_DESKTOP_COMMANDER = True  # Set to False to use direct shell execution

# Global state for command history
command_history = []


def ollama_generate(prompt, temperature=0.7):
    """Send prompt to Ollama and get response."""
    try:
        # Enhance prompt for better command generation
        enhanced_prompt = f"""You are a helpful assistant that generates shell commands.
User request: {prompt}
Generate a single shell command that accomplishes this task. 
Respond with ONLY the command, no explanation."""
        
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": enhanced_prompt,
            "stream": False,
            "temperature": temperature,
            "options": {
                "num_predict": 100  # Limit response length
            }
        }
        
        resp = requests.post(OLLAMA_URL, json=payload, timeout=30)
        resp.raise_for_status()
        
        response_data = resp.json()
        if "response" in response_data:
            return response_data["response"].strip()
        else:
            return "Error: No response from Ollama"
            
    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to Ollama. Make sure it's running (ollama serve)"
    except requests.exceptions.Timeout:
        return "Error: Ollama request timed out"
    except Exception as e:
        return f"Error: {str(e)}"


def execute_command_directly(command):
    """Execute command directly using subprocess (fallback method)."""
    try:
        # Security check - basic filtering of dangerous commands
        dangerous_patterns = ["rm -rf /", "sudo rm", "format", "mkfs", "dd if="]
        for pattern in dangerous_patterns:
            if pattern in command.lower():
                return f"Error: Command blocked for security reasons: {pattern}"
        
        # Execute the command
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\nError output:\n{result.stderr}"
        
        return output if output else "Command executed successfully (no output)"
        
    except subprocess.TimeoutExpired:
        return "Error: Command execution timed out (30 seconds)"
    except Exception as e:
        return f"Error: {str(e)}"
def execute_command(command):
    """Execute the command using configured method."""
    if not command.strip():
        return "Please enter a command"
    
    if USE_DESKTOP_COMMANDER:
        output = "Desktop Commander integration temporarily disabled. Using direct execution."
        output += "\n\n"
        output += execute_command_directly(command)
    else:
        output = execute_command_directly(command)
    
    # Update history
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    command_history.append({
        "timestamp": timestamp,
        "prompt": "Manual execution",
        "command": command,
        "output": output,
        "method": "direct" if not USE_DESKTOP_COMMANDER else "desktop-commander"
    })
    
    return output


def process_llm_and_execute(prompt, auto_execute=False):
    """Process prompt through LLM and optionally execute."""
    if not prompt.strip():
        return "", "", "Please enter a prompt"
    
    # Generate command with LLM
    ai_command = ollama_generate(prompt)
    
    if ai_command.startswith("Error:"):
        return "", ai_command, "LLM generation failed"
    
    # Add to history
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    command_history.append({
        "timestamp": timestamp,
        "prompt": prompt,
        "command": ai_command,
        "auto_executed": auto_execute
    })
    
    # Auto-execute if requested
    if auto_execute and not ai_command.startswith("Error:"):
        output = execute_command(ai_command)
        command_history[-1]["output"] = output
        return ai_command, output, format_history()
    
    return ai_command, "", format_history()


def format_history():
    """Format command history for display."""
    if not command_history:
        return "No commands executed yet"
    
    history_text = []
    for i, entry in enumerate(reversed(command_history[-10:]), 1):  # Show last 10
        history_text.append(f"[{entry['timestamp']}]")
        history_text.append(f"Prompt: {entry['prompt']}")
        history_text.append(f"Command: {entry['command']}")
        if 'output' in entry:
            output_preview = entry['output'][:200] + "..." if len(entry['output']) > 200 else entry['output']
            history_text.append(f"Output: {output_preview}")
        history_text.append("-" * 50)
    
    return "\n".join(history_text)


def check_services():
    """Check if required services are running."""
    status = []
    
    # Check Ollama
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=2)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            if OLLAMA_MODEL in model_names:
                status.append(f"✅ Ollama is running with {OLLAMA_MODEL}")
            else:
                status.append(f"⚠️ Ollama is running but {OLLAMA_MODEL} not found. Available: {', '.join(model_names)}")
        else:
            status.append("❌ Ollama is not responding properly")
    except:
        status.append("❌ Ollama is not running. Start with: ollama serve")
    
    # Execution method status
    if USE_DESKTOP_COMMANDER:
        status.append("⚠️ Desktop Commander mode (currently using direct fallback)")
    else:
        status.append("✅ Direct shell execution mode")
    
    return "\n".join(status)


# Create Gradio interface
def create_interface():
    with gr.Blocks(title="Desktop Commander UI - Simple", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🖥️ Desktop Commander UI (Simple Version)
        
        Connect your local LLM (Ollama) for natural language command generation.
        
        ⚠️ **Note**: This version uses direct shell execution. Be careful with generated commands!
        """)
        
        # Service status
        with gr.Row():
            with gr.Column():
                status_display = gr.Textbox(
                    label="System Status",
                    value=check_services(),
                    interactive=False,
                    lines=3
                )
                refresh_btn = gr.Button("🔄 Refresh Status", size="sm")
        
        gr.Markdown("---")
        
        # Main interface
        with gr.Row():
            with gr.Column(scale=2):
                prompt_input = gr.Textbox(
                    label="What would you like to do?",
                    placeholder="Example: List all CSV files in the current directory",
                    lines=2
                )
                
                with gr.Row():
                    generate_btn = gr.Button("🤖 Generate Command", variant="secondary")
                    generate_execute_btn = gr.Button("⚡ Generate & Execute", variant="primary")
                
                command_display = gr.Textbox(
                    label="Generated/Manual Command",
                    placeholder="Command will appear here. You can edit before executing.",
                    lines=2,
                    interactive=True
                )
                
                execute_btn = gr.Button("▶️ Execute Command", variant="primary")
                
                output_display = gr.Textbox(
                    label="Output",
                    lines=10,
                    interactive=False,
                    show_copy_button=True
                )
            
            with gr.Column(scale=1):
                history_display = gr.Textbox(
                    label="Command History (Last 10)",
                    value=format_history(),
                    lines=20,
                    interactive=False,
                    show_copy_button=True
                )
        
        # Examples
        gr.Examples(
            examples=[
                "List all Python files in the current directory",
                "Show the current directory path",
                "Count the number of files in this folder",
                "Show system information",
                "Display current date and time",
                "List running processes (first 10)",
            ],
            inputs=prompt_input
        )
        
        # Safety warning
        gr.Markdown("""
        ---
        ⚠️ **Safety Note**: Always review commands before executing them. 
        This tool uses direct shell execution, so be cautious with file operations and system commands.
        """)
        
        # Event handlers
        refresh_btn.click(
            fn=lambda: check_services(),
            outputs=status_display
        )
        
        generate_btn.click(
            fn=lambda p: process_llm_and_execute(p, False),
            inputs=prompt_input,
            outputs=[command_display, output_display, history_display]
        )
        
        generate_execute_btn.click(
            fn=lambda p: process_llm_and_execute(p, True),
            inputs=prompt_input,
            outputs=[command_display, output_display, history_display]
        )
        
        execute_btn.click(
            fn=execute_command,
            inputs=command_display,
            outputs=output_display
        )
        
        # Auto-update history after execution
        output_display.change(
            fn=lambda: format_history(),
            outputs=history_display
        )
    
    return demo


# Main entry point
if __name__ == "__main__":
    print("Starting Desktop Commander UI (Simple Version)...")
    print(f"Using Ollama model: {OLLAMA_MODEL}")
    print("\n⚠️  Note: This version uses direct shell execution")
    print("Be careful with the commands you execute!\n")
    
    print("Checking services...")
    print(check_services())
    print("\nLaunching Gradio interface...")
    
    demo = create_interface()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        inbrowser=True
    )