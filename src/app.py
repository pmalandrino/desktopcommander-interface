#!/usr/bin/env python3

import argparse
import os
import sys

from core.models import AppState, CommandStatus
from core.ollama_service import check_ollama
from core.config_manager import load_config
from ui.gradio_app import create_ui


def main():
    """Main entry point for Desktop Commander."""
    parser = argparse.ArgumentParser(description="Desktop Commander - AI-powered command line interface")
    parser.add_argument("--dry-run", action="store_true", help="Enable dry-run mode (commands are not executed)")
    parser.add_argument("--safe-mode", action="store_true", help="Enable safe mode (only read-only commands allowed)")
    parser.add_argument("--port", type=int, default=7860, help="Port to run the server on (default: 7860)")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browser automatically")
    args = parser.parse_args()
    
    # Initialize app state
    app_state = AppState()
    
    # Load saved configuration (fallback to env/defaults)
    config, config_status = load_config()
    app_state.config = config
    
    # Override with command line arguments
    app_state.dry_run_mode = args.dry_run
    app_state.safe_mode = args.safe_mode
    
    print("Desktop Commander")
    print(f"Working Directory: {os.getcwd()}")
    print(f"Ollama Model: {app_state.config.ollama_model}")
    if args.dry_run:
        print("🔒 DRY RUN MODE ENABLED - Commands will NOT be executed")
    if args.safe_mode:
        print("🛡️  SAFE MODE ENABLED - Only read-only commands allowed")
    
    status_text, status_type = check_ollama(app_state.config.ollama_model)
    print(status_text)
    
    if status_type == CommandStatus.ERROR:
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    print(f"Launching at http://127.0.0.1:{args.port}")
    app = create_ui(app_state)
    app.launch(
        server_name="127.0.0.1",
        server_port=args.port,
        share=False,
        inbrowser=not args.no_browser,
        show_error=True
    )


if __name__ == "__main__":
    main()