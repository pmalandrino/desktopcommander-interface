# Desktop Commander Interface

A modern, intuitive Gradio-based interface for executing system commands with AI assistance powered by Ollama.

## Features

- 🎨 **Modern UX Design**: Clean, intuitive interface with a professional color scheme
- 🤖 **AI-Powered Commands**: Get command suggestions and explanations using Ollama (Gemma 3 4B model)
- 📁 **Command Templates**: Pre-built templates for common tasks (file operations, system info, development, network)
- ⚡ **Real-time Execution**: Execute commands directly from the interface with live output
- 📜 **Command History**: Keep track of executed commands with timestamps
- 🛡️ **Safety Features**: Command validation and execution status indicators
- 🎯 **Smart Suggestions**: Context-aware command recommendations

## Requirements

- Python 3.7+
- Ollama running locally with Gemma 3 4B model
- gradio >= 3.0.0
- requests >= 2.31.0

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd desktopcommander-interface
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure Ollama is running with Gemma 3 model:
```bash
ollama pull gemma3:4b
ollama serve
```

## Usage

Run the application:
```bash
python app_ux.py
```

The interface will open in your default browser at `http://localhost:7860`

## Interface Overview

### Main Components:

1. **Command Input Area**
   - AI Assistant prompt field for natural language requests
   - Command input field with syntax highlighting
   - Execute button with status indicators

2. **Command Templates**
   - Quick access to common commands organized by category
   - Click any template to auto-fill the command field

3. **Output Display**
   - Real-time command output with proper formatting
   - Error handling and status messages
   - Execution time tracking

4. **Command History**
   - Chronological list of executed commands
   - Timestamps and execution status
   - Click to re-run previous commands

## Command Categories

- 📁 **Files & Folders**: List, find, count, and manage files
- 📊 **System Info**: Check disk, memory, CPU, and network status
- 🛠️ **Development**: Git operations, code searching, process management
- 🌐 **Network**: Ping, curl, port checking, and network diagnostics

## Safety Notes

- Always review commands before executing
- The interface includes basic command validation
- Use with caution on production systems
- Some commands may require appropriate permissions

## Customization

The app uses a modern color scheme defined in `THEME_COLORS`. You can modify these values to match your preferences:

```python
THEME_COLORS = {
    "primary": "#2563eb",      # Blue
    "success": "#10b981",      # Green
    "warning": "#f59e0b",      # Amber
    "danger": "#ef4444",       # Red
    "info": "#3b82f6",         # Light Blue
    "dark": "#1f2937",         # Dark Gray
    "light": "#f9fafb"         # Light Gray
}
```

## Troubleshooting

- **Ollama Connection Error**: Ensure Ollama is running on `http://localhost:11434`
- **Command Not Found**: Some commands may be OS-specific (Linux/macOS/Windows)
- **Permission Denied**: Run with appropriate permissions or use sudo when necessary

## License

[Your License Here]

## Contributing

Feel free to submit issues and enhancement requests!
