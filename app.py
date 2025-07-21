#!/usr/bin/env python3
"""
Desktop Commander Gradio UI
A local Gradio-based interface for connecting Desktop Commander with Ollama LLM
"""

import gradio as gr
import requests
import subprocess
import json
import threading
import queue
import time
from datetime import datetime
import sys
import os

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:4b"  # Using your installed model
DESKTOP_COMMANDER_CMD = ["npx", "-y", "@wonderwhy-er/desktop-commander"]

# Global state for command history
command_history = []
output_queue = queue.Queue()


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


def desktop_commander_execute(command, method="execute_command"):
    """Execute command via Desktop Commander MCP protocol."""
    try:
        # Start Desktop Commander process
        proc = subprocess.Popen(
            DESKTOP_COMMANDER_CMD + ["--stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Initialize MCP connection
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "gradio-ui",
                    "version": "1.0.0"
                }
            }
        }
        
        # Send initialization
        proc.stdin.write(json.dumps(init_request) + "\n")
        proc.stdin.flush()
        
        # Wait for initialization response
        init_response = None
        start_time = time.time()
        while time.time() - start_time < 5:
            line = proc.stdout.readline()
            if line:
                try:
                    data = json.loads(line)
                    if data.get("id") == 1:
                        init_response = data
                        break
                except:
                    pass
        
        if not init_response:
            proc.terminate()
            return "Error: Failed to initialize Desktop Commander"
        
        # Now send the actual command
        command_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": method,
                "arguments": {"command": command}
            }
        }
        
        proc.stdin.write(json.dumps(command_request) + "\n")
        proc.stdin.flush()
        
        # Read the response
        output_lines = []
        start_time = time.time()
        while time.time() - start_time < 30:
            line = proc.stdout.readline()
            if line:
                try:
                    data = json.loads(line)
                    if data.get("id") == 2:
                        if "result" in data:
                            proc.terminate()
                            result = data["result"]
                            # Extract the actual output from the result
                            if isinstance(result, dict) and "output" in result:
                                return result["output"]
                            return str(result)
                        elif "error" in data:
                            proc.terminate()
                            return f"Error: {data['error']}"
                except:
                    output_lines.append(line.strip())
        
        # Terminate the process
        proc.terminate()
        
        # If we didn't get a proper response, return what we collected
        if output_lines:
            return "\n".join(output_lines)
        
        return "Error: No response received from Desktop Commander"
        
    except subprocess.TimeoutExpired:
        proc.kill()
        return "Error: Command execution timed out"
    except Exception as e:
        return f"Error: {str(e)}"


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
        output = desktop_commander_execute(ai_command)
        command_history[-1]["output"] = output
        return ai_command, output, format_history()
    
    return ai_command, "", format_history()

def execute_command(command):
    """Execute the command directly."""
    if not command.strip():
        return "Please enter a command", format_history()
    
    output = desktop_commander_execute(command)
    
    # Update history
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    command_history.append({
        "timestamp": timestamp,
        "prompt": "Manual execution",
        "command": command,
        "output": output,
        "auto_executed": False
    })
    
    return output, format_history()


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
    
    # Check Desktop Commander
    try:
        result = subprocess.run(["npx", "-y", "@wonderwhy-er/desktop-commander", "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            status.append("✅ Desktop Commander is available")
        else:
            status.append("❌ Desktop Commander check failed")
    except:
        status.append("❌ Desktop Commander not found. Install with: npm install -g @wonderwhy-er/desktop-commander")
    
    return "\n".join(status)


# Create Gradio interface
def create_interface():
    with gr.Blocks(title="Desktop Commander UI", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🖥️ Desktop Commander UI
        
        Connect your local LLM (Ollama) with Desktop Commander for natural language automation.
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
                "Show the contents of README.md",
                "Create a new directory called 'test'",
                "Count the number of lines in all .py files",
                "Find files modified in the last 24 hours",
                "Show system information",
            ],
            inputs=prompt_input
        )
        
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
            outputs=[output_display, history_display]
        )
    
    return demo


# Main entry point
if __name__ == "__main__":
    print("Starting Desktop Commander UI...")
    print(f"Using Ollama model: {OLLAMA_MODEL}")
    print("\nChecking services...")
    print(check_services())
    print("\nLaunching Gradio interface...")
    
    demo = create_interface()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        inbrowser=True
    )
