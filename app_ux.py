#!/usr/bin/env python3
"""
Desktop Commander Gradio UI - UX Enhanced Version
Modern, intuitive interface with excellent user experience
"""

import gradio as gr
import requests
import subprocess
import json
import time
from datetime import datetime
import os
import sys
from typing import List, Tuple, Dict

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:4b"

# Global state
command_history = []
is_executing = False

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

# Common command templates
COMMAND_TEMPLATES = {
    "📁 Files & Folders": {
        "List files": "ls -la",
        "Find large files": "find . -type f -size +10M -exec ls -lh {} \\;",
        "Count files": "find . -type f | wc -l",
        "Show tree structure": "tree -L 2 || ls -R",
        "Recent files": "find . -type f -mtime -1",
    },
    "📊 System Info": {
        "Disk usage": "df -h",
        "Memory info": "free -h || vm_stat",
        "CPU info": "lscpu || sysctl -a | grep cpu",
        "Network info": "ifconfig || ip addr",
        "Running processes": "ps aux | head -20",
    },
    "🔍 Search & Filter": {
        "Find Python files": "find . -name '*.py'",
        "Search in files": "grep -r 'TODO' .",
        "Find by extension": "find . -name '*.csv'",
        "List directories only": "find . -type d -maxdepth 1",
    },
    "📝 Text Processing": {
        "Count lines": "wc -l *.txt",
        "Show first lines": "head -n 10",
        "Show last lines": "tail -n 10",
        "Sort files by size": "ls -lhS",
    }
}

def get_greeting():
    """Get time-appropriate greeting"""
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning! ☀️"
    elif hour < 17:
        return "Good afternoon! 🌤️"
    else:
        return "Good evening! 🌙"

def format_status_message(status: str, message: str) -> str:
    """Format status messages with icons"""
    icons = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️",
        "loading": "⏳"
    }
    return f"{icons.get(status, '•')} {message}"

def check_system_status() -> Tuple[str, str]:
    """Check system status and return formatted message and status type"""
    messages = []
    has_error = False
    
    # Check Ollama
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=2)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            if OLLAMA_MODEL in model_names:
                messages.append(format_status_message("success", f"Ollama ready with {OLLAMA_MODEL}"))
            else:
                messages.append(format_status_message("warning", f"Model {OLLAMA_MODEL} not found"))
                has_error = True
        else:
            messages.append(format_status_message("error", "Ollama not responding"))
            has_error = True
    except:
        messages.append(format_status_message("error", "Ollama offline - run 'ollama serve'"))
        has_error = True
    
    # System info
    messages.append(format_status_message("info", f"Ready for commands on {sys.platform}"))
    
    status_text = "\n".join(messages)
    status_type = "error" if has_error else "success"
    
    return status_text, status_type

def ollama_generate(prompt: str, temperature: float = 0.7) -> Tuple[str, str]:
    """Generate command using Ollama. Returns (command, status)"""
    try:
        enhanced_prompt = f"""You are a helpful shell command expert. Generate a single shell command.
User request: {prompt}
Operating system: {sys.platform}
Important: Respond with ONLY the command, no explanations or markdown."""
        
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": enhanced_prompt,
            "stream": False,
            "temperature": temperature,
            "options": {"num_predict": 100}
        }
        
        resp = requests.post(OLLAMA_URL, json=payload, timeout=30)
        resp.raise_for_status()
        
        response_data = resp.json()
        if "response" in response_data:
            command = response_data["response"].strip()
            # Clean up common LLM artifacts
            command = command.replace("```", "").strip()
            return command, "success"
        else:
            return "", "error"
            
    except requests.exceptions.ConnectionError:
        return "Cannot connect to Ollama. Please run: ollama serve", "error"
    except requests.exceptions.Timeout:
        return "Request timed out. Try a simpler prompt.", "warning"
    except Exception as e:
        return f"Error: {str(e)}", "error"

def execute_command_safely(command: str) -> Tuple[str, str]:
    """Execute command with safety checks. Returns (output, status)"""
    # Safety checks
    dangerous_patterns = [
        "rm -rf /", "sudo rm", "format", "mkfs", "dd if=/dev/zero",
        "> /dev/", ":(){ :|:& };:", "chmod -R 777 /", "chown -R"
    ]
    
    for pattern in dangerous_patterns:
        if pattern in command.lower():
            return f"🛡️ Command blocked for safety: contains '{pattern}'", "warning"
    
    try:
        # Execute with reasonable limits
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            env={**os.environ, "LANG": "en_US.UTF-8"}
        )
        
        output = result.stdout
        if result.stderr and result.returncode != 0:
            output = f"❌ Error:\n{result.stderr}\n\n📋 Output:\n{output}"
            return output, "error"
        elif result.stderr:
            output = f"⚠️ Warnings:\n{result.stderr}\n\n📋 Output:\n{output}"
            return output, "warning"
        
        return output if output else "✅ Command executed successfully (no output)", "success"
        
    except subprocess.TimeoutExpired:
        return "⏱️ Command timed out after 30 seconds", "error"
    except Exception as e:
        return f"❌ Execution failed: {str(e)}", "error"
def add_to_history(prompt: str, command: str, output: str, status: str = "success"):
    """Add command to history"""
    command_history.append({
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "prompt": prompt,
        "command": command,
        "output": output[:500] + "..." if len(output) > 500 else output,
        "status": status,
        "full_output": output
    })

def format_history_html() -> str:
    """Format history as HTML for better display"""
    if not command_history:
        return """
        <div style='text-align: center; color: #6b7280; padding: 20px;'>
            <p>No commands yet</p>
            <p style='font-size: 0.9em;'>Your command history will appear here</p>
        </div>
        """
    
    html_items = []
    for entry in reversed(command_history[-10:]):
        status_color = {
            "success": "#10b981",
            "error": "#ef4444",
            "warning": "#f59e0b",
            "info": "#3b82f6"
        }.get(entry["status"], "#6b7280")
        
        html_items.append(f"""
        <div style='border-left: 3px solid {status_color}; padding: 10px; margin: 10px 0; background: #f9fafb; border-radius: 0 8px 8px 0;'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;'>
                <span style='font-weight: 600; color: #1f2937;'>{entry['timestamp']}</span>
                <span style='font-size: 0.8em; color: #6b7280;'>{entry.get('prompt', 'Manual')[:30]}...</span>
            </div>
            <code style='display: block; background: #e5e7eb; padding: 8px; border-radius: 4px; font-family: monospace; color: #1f2937; margin: 5px 0;'>
                {entry['command']}
            </code>
            <div style='font-size: 0.9em; color: #6b7280; margin-top: 5px;'>
                {entry['output'][:100]}...
            </div>
        </div>
        """)
    
    return "\n".join(html_items)

def process_natural_language(prompt: str, execute_immediately: bool = False):
    """Process natural language prompt"""
    global is_executing
    
    if not prompt.strip():
        return (
            gr.update(value="", visible=False),  # command_display
            gr.update(value="Please enter a command or description", visible=True),  # output_display
            gr.update(value=format_history_html()),  # history_display
            gr.update(visible=False),  # loading_indicator
            gr.update(value="💡 Tip: Try something like 'show all Python files'", visible=True)  # status_message
        )
    
    is_executing = True
    
    # Generate command
    command, cmd_status = ollama_generate(prompt)
    
    if cmd_status == "error":
        is_executing = False
        return (
            gr.update(value="", visible=False),
            gr.update(value=command, visible=True),
            gr.update(value=format_history_html()),
            gr.update(visible=False),
            gr.update(value=format_status_message("error", "Failed to generate command"), visible=True)
        )
    
    # Show generated command
    updates = [
        gr.update(value=command, visible=True),  # command_display
        gr.update(value="", visible=False),  # output_display
        gr.update(value=format_history_html()),  # history_display
        gr.update(visible=False),  # loading_indicator
        gr.update(value=format_status_message("success", "Command generated! Review before executing."), visible=True)  # status_message
    ]
    
    if execute_immediately and cmd_status == "success":
        output, exec_status = execute_command_safely(command)
        add_to_history(prompt, command, output, exec_status)
        
        updates = [
            gr.update(value=command, visible=True),
            gr.update(value=output, visible=True),
            gr.update(value=format_history_html()),
            gr.update(visible=False),
            gr.update(value=format_status_message(exec_status, "Command executed"), visible=True)
        ]
    
    is_executing = False
    return tuple(updates)

def execute_command_click(command: str):
    """Execute command from button click"""
    if not command.strip():
        return (
            gr.update(value="No command to execute", visible=True),
            gr.update(value=format_history_html()),
            gr.update(value=format_status_message("warning", "Please generate or enter a command first"), visible=True)
        )
    
    output, status = execute_command_safely(command)
    add_to_history("Manual execution", command, output, status)
    
    return (
        gr.update(value=output, visible=True),
        gr.update(value=format_history_html()),
        gr.update(value=format_status_message(status, "Command executed"), visible=True)
    )

def use_template(template_command: str):
    """Use a command template"""
    return gr.update(value=template_command)

def clear_all():
    """Clear all fields"""
    return (
        gr.update(value=""),  # prompt_input
        gr.update(value="", visible=False),  # command_display
        gr.update(value="", visible=False),  # output_display
        gr.update(value="Ready for new command", visible=True)  # status_message
    )

# Create the enhanced UI
def create_ui():
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
            max-width: 1200px !important;
            margin: auto !important;
        }
        .main-header {
            background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
            color: white;
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            text-align: center;
        }
        .command-input {
            font-size: 1.1rem !important;
        }
        .template-button {
            font-size: 0.9rem !important;
            padding: 0.5rem !important;
            border-radius: 6px !important;
            transition: all 0.2s ease !important;
        }
        .template-button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        }
        .status-bar {
            padding: 0.75rem 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            font-weight: 500;
        }
        .monospace {
            font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace !important;
        }
        """
    ) as app:
        # Header
        gr.HTML(f"""
        <div class="main-header">
            <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">🚀 Desktop Commander</h1>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 1.1rem;">
                {get_greeting()} Let's automate your tasks with natural language.
            </p>
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
        with gr.Row():
            # Left Column - Input and Output
            with gr.Column(scale=2):
                # Natural Language Input
                prompt_input = gr.Textbox(
                    label="What would you like to do?",
                    placeholder="e.g., 'Show all images in this folder' or 'Count Python files'",
                    lines=2,
                    elem_classes=["command-input"]
                )
                
                # Action Buttons
                with gr.Row():
                    generate_btn = gr.Button(
                        "✨ Generate Command",
                        variant="secondary",
                        size="lg"
                    )
                    execute_btn = gr.Button(
                        "🚀 Generate & Run",
                        variant="primary",
                        size="lg"
                    )
                    clear_btn = gr.Button(
                        "🗑️ Clear",
                        variant="stop",
                        size="lg"
                    )
                
                # Status Message
                status_message = gr.Markdown(
                    value="💡 Tip: Describe what you want to do in plain English",
                    visible=True
                )
                
                # Generated Command Display
                command_display = gr.Textbox(
                    label="📝 Generated Command",
                    placeholder="Your command will appear here",
                    lines=2,
                    visible=False,
                    interactive=True,
                    elem_classes=["monospace"]
                )
                
                # Execute Button for Manual Commands
                with gr.Row():
                    manual_execute_btn = gr.Button(
                        "▶️ Execute Command",
                        variant="primary",
                        visible=False
                    )
                
                # Output Display
                output_display = gr.Textbox(
                    label="📤 Output",
                    lines=12,
                    visible=False,
                    interactive=False,
                    elem_classes=["monospace"],
                    show_copy_button=True
                )
                
                # Loading indicator
                loading_indicator = gr.HTML(
                    value='<div style="text-align: center; padding: 20px;"><div class="loader"></div>Processing...</div>',
                    visible=False
                )
            
            # Right Column - Templates and History
            with gr.Column(scale=1):
                # Command Templates
                gr.Markdown("### 📚 Quick Commands")
                
                for category, commands in COMMAND_TEMPLATES.items():
                    with gr.Accordion(category, open=True):
                        for desc, cmd in commands.items():
                            template_btn = gr.Button(
                                desc,
                                variant="secondary",
                                size="sm",
                                elem_classes=["template-button"]
                            )
                            template_btn.click(
                                fn=lambda c=cmd: use_template(c),
                                outputs=command_display
                            )
                
                # History
                gr.Markdown("### 📜 Recent Commands")
                history_display = gr.HTML(
                    value=format_history_html(),
                    elem_classes=["history-panel"]
                )
        
        # Examples Section
        gr.Markdown("### 💡 Example Prompts")
        gr.Examples(
            examples=[
                "List all files modified in the last 24 hours",
                "Show me the largest files in this directory",
                "Create a backup folder with today's date",
                "Find all TODO comments in Python files",
                "Display system resource usage",
                "Count lines of code in all JavaScript files",
            ],
            inputs=prompt_input,
            cache_examples=False
        )
        
        # Footer
        gr.Markdown("""
        ---
        <div style='text-align: center; color: #6b7280; font-size: 0.9rem;'>
            <p>🛡️ Commands are filtered for safety • 📍 Working directory: <code>{}</code></p>
            <p>Built with ❤️ using Gradio and Ollama</p>
        </div>
        """.format(os.getcwd()))
        
        # Event Handlers
        def update_command_visibility(command):
            return gr.update(visible=bool(command.strip()))
        
        command_display.change(
            fn=update_command_visibility,
            inputs=command_display,
            outputs=manual_execute_btn
        )
        
        generate_btn.click(
            fn=lambda p: process_natural_language(p, False),
            inputs=prompt_input,
            outputs=[command_display, output_display, history_display, loading_indicator, status_message]
        )
        
        execute_btn.click(
            fn=lambda p: process_natural_language(p, True),
            inputs=prompt_input,
            outputs=[command_display, output_display, history_display, loading_indicator, status_message]
        )
        
        manual_execute_btn.click(
            fn=execute_command_click,
            inputs=command_display,
            outputs=[output_display, history_display, status_message]
        )
        
        clear_btn.click(
            fn=clear_all,
            outputs=[prompt_input, command_display, output_display, status_message]
        )
        
        # Define refresh function
        def refresh_status():
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
    print(f"🤖 Using Ollama Model: {OLLAMA_MODEL}")
    print(f"🌐 Ollama URL: {OLLAMA_URL}")
    
    # Check initial status
    print("\n🔍 Checking system status...")
    status_text, status_type = check_system_status()
    print(status_text)
    
    if status_type == "error":
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