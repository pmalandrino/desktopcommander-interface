#!/usr/bin/env python3

import gradio as gr

from core.models import AppState
from ui.presenters import CommandPresenter


def create_ui(app_state: AppState) -> gr.Blocks:
    """Create the Gradio UI for Desktop Commander."""
    presenter = CommandPresenter(app_state)
    
    with gr.Blocks(title="Desktop Commander") as app:
        gr.Markdown("# Desktop Commander")
        gr.Markdown("AI-powered command line interface")
        
        # Security disclaimer
        gr.Markdown("""
        <div style="background-color: #fee; border: 2px solid #c00; border-radius: 5px; padding: 10px; margin: 10px 0;">
            <h3 style="color: #c00; margin: 0;">⚠️ SECURITY WARNING</h3>
            <p style="margin: 5px 0;"><strong>This application executes system commands with your user permissions.</strong></p>
            <ul style="margin: 5px 0;">
                <li>Commands run WITHOUT sandboxing - they can modify or delete files</li>
                <li>Always review commands before execution</li>
                <li>AI suggestions may be incorrect or unsafe</li>
                <li>For development use only - NOT for production</li>
            </ul>
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                system_status = gr.Markdown(value="Loading...")
            with gr.Column(scale=1):
                dry_run_toggle = gr.Checkbox(
                    label="Dry Run Mode",
                    value=app_state.dry_run_mode,
                    info="Preview commands without executing"
                )
            with gr.Column(scale=1):
                safe_mode_toggle = gr.Checkbox(
                    label="Safe Mode",
                    value=app_state.safe_mode,
                    info="Only allow read-only commands"
                )
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
        
        # Event handlers
        command_display.change(
            fn=lambda cmd: gr.update(visible=bool(cmd.strip())),
            inputs=command_display,
            outputs=manual_execute_btn
        )
        
        generate_btn.click(
            fn=lambda p: presenter.process_prompt(p, False),
            inputs=prompt_input,
            outputs=[command_display, output_display, loading_indicator, status_message]
        )
        
        execute_btn.click(
            fn=lambda p: presenter.process_prompt(p, True),
            inputs=prompt_input,
            outputs=[command_display, output_display, loading_indicator, status_message]
        )
        
        manual_execute_btn.click(
            fn=presenter.execute_displayed_command,
            inputs=command_display,
            outputs=[output_display, status_message]
        )
        
        clear_btn.click(
            fn=presenter.clear_interface,
            outputs=[prompt_input, command_display, output_display, status_message]
        )
        
        refresh_btn.click(fn=presenter.refresh_status, outputs=system_status)
        dry_run_toggle.change(fn=presenter.toggle_dry_run, inputs=dry_run_toggle, outputs=system_status)
        safe_mode_toggle.change(fn=presenter.toggle_safe_mode, inputs=safe_mode_toggle, outputs=system_status)
        app.load(presenter.refresh_status, outputs=system_status)
    
    return app