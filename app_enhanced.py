# Enhanced version of app.py with additional features
# This is an example of how to extend the basic functionality

import os
import sys

# Try to import config if it exists
try:
    from config import *
except ImportError:
    # Use defaults from config_example.py
    from config_example import *

# Import the main app
from app import *

# Additional utility functions
def save_command_history(filename="command_history.json"):
    """Save command history to a JSON file."""
    try:
        with open(filename, 'w') as f:
            json.dump(command_history, f, indent=2)
        return f"History saved to {filename}"
    except Exception as e:
        return f"Error saving history: {str(e)}"

def load_command_history(filename="command_history.json"):
    """Load command history from a JSON file."""
    global command_history
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                command_history = json.load(f)
            return f"Loaded {len(command_history)} commands from history"
        return "No history file found"
    except Exception as e:
        return f"Error loading history: {str(e)}"

def execute_quick_action(action_name):
    """Execute a predefined quick action."""
    if action_name in QUICK_ACTIONS:
        command = QUICK_ACTIONS[action_name]
        return execute_command(command)
    return "Unknown quick action", format_history()

# Enhanced interface with additional features
def create_enhanced_interface():
    with gr.Blocks(title="Desktop Commander UI Pro", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🖥️ Desktop Commander UI Pro
        
        Enhanced interface with quick actions and history management.
        """)
        
        # Tabs for different sections
        with gr.Tabs():
            with gr.Tab("Main"):
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
                
                # Main interface (same as before)
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
            
            with gr.Tab("Quick Actions"):
                gr.Markdown("### Common Commands")
                quick_action_output = gr.Textbox(label="Output", lines=10)
                quick_history = gr.Textbox(label="History", lines=5)
                
                with gr.Row():
                    for action_name, command in list(QUICK_ACTIONS.items())[:4]:
                        btn = gr.Button(action_name.replace('_', ' ').title())
                        btn.click(
                            fn=lambda a=action_name: execute_quick_action(a),
                            outputs=[quick_action_output, quick_history]
                        )
                
                with gr.Row():
                    for action_name, command in list(QUICK_ACTIONS.items())[4:]:
                        btn = gr.Button(action_name.replace('_', ' ').title())
                        btn.click(
                            fn=lambda a=action_name: execute_quick_action(a),
                            outputs=[quick_action_output, quick_history]
                        )
            
            with gr.Tab("History Management"):
                gr.Markdown("### Command History Management")
                history_status = gr.Textbox(label="Status", lines=2)
                
                with gr.Row():
                    save_btn = gr.Button("💾 Save History")
                    load_btn = gr.Button("📂 Load History")
                    clear_btn = gr.Button("🗑️ Clear History")
                
                history_view = gr.Textbox(
                    label="Full History",
                    value=format_history(),
                    lines=20,
                    interactive=False
                )
                
                save_btn.click(
                    fn=save_command_history,
                    outputs=history_status
                )
                
                load_btn.click(
                    fn=load_command_history,
                    outputs=history_status
                )
                
                def clear_history():
                    global command_history
                    command_history = []
                    return "History cleared", format_history()
                
                clear_btn.click(
                    fn=clear_history,
                    outputs=[history_status, history_view]
                )
        
        # Event handlers for main tab
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

# If running this enhanced version directly
if __name__ == "__main__" and "app_enhanced" in sys.argv[0]:
    print("Starting Enhanced Desktop Commander UI...")
    print(f"Using Ollama model: {OLLAMA_MODEL}")
    
    # Try to load history
    load_result = load_command_history()
    print(f"\n{load_result}")
    
    print("\nChecking services...")
    print(check_services())
    print("\nLaunching enhanced Gradio interface...")
    
    demo = create_enhanced_interface()
    demo.launch(
        server_name=SERVER_HOST,
        server_port=SERVER_PORT,
        share=False,
        inbrowser=AUTO_OPEN_BROWSER
    )