# Desktop Commander Interface

> ⚠️ **SECURITY WARNING** ⚠️
> 
> This application executes system commands with the permissions of the user running it. 
> 
> **IMPORTANT SECURITY CONSIDERATIONS:**
> - Commands are executed directly on your system without sandboxing
> - Malicious or incorrect commands can cause permanent damage
> - Always review and understand commands before execution
> - Never run this application with elevated privileges unless absolutely necessary
> - This is an ALPHA version - use at your own risk
>
> **Recommended for development environments only. NOT for production use.**

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
# Using the new modular structure
python run.py

# With dry-run mode enabled
python run.py --dry-run

# With safe mode enabled (only read-only commands)
python run.py --safe-mode

# Both modes enabled for maximum safety
python run.py --dry-run --safe-mode

# Specify custom port
python run.py --port 8080

# Don't open browser automatically
python run.py --no-browser

# Or use the legacy single-file version
python app.py
```

The interface will open in your default browser at `http://localhost:7860`

### Command Line Options

- `--dry-run`: Enable dry-run mode (commands are previewed but not executed)
- `--safe-mode`: Enable safe mode (only read-only commands are allowed)
- `--port PORT`: Specify the port to run on (default: 7860)
- `--no-browser`: Don't open the browser automatically

### Safety Modes

1. **Dry Run Mode**: Preview commands without execution - see exactly what would run
2. **Safe Mode**: Only allows whitelisted read-only commands (ls, cat, ps, etc.)
3. **Combined**: Use both modes together for maximum safety during exploration

### Configuration Management

Desktop Commander now includes a comprehensive configuration panel accessible through the UI:

1. **Model Selection**: Choose from available Ollama models with live refresh
2. **Timeout Settings**: Adjust command execution timeout (5-300 seconds)
3. **Ollama URL**: Configure custom Ollama server endpoints
4. **Persistence**: Settings are automatically saved to `~/.desktopcommander_config.json`
5. **Reset Option**: Restore default settings at any time

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

5. **Configuration Panel**
   - Ollama model selection with live model list
   - Command timeout adjustment
   - Server URL configuration
   - Settings persistence and reset options

## Command Categories

- 📁 **Files & Folders**: List, find, count, and manage files
- 📊 **System Info**: Check disk, memory, CPU, and network status
- 🛠️ **Development**: Git operations, code searching, process management
- 🌐 **Network**: Ping, curl, port checking, and network diagnostics

## Security & Safety

### ⚠️ Critical Security Information

This application executes commands with full system privileges. Exercise extreme caution:

1. **Command Execution Risks**:
   - Commands run with your user permissions
   - No sandboxing or isolation is currently implemented
   - Destructive commands (rm, format, etc.) will execute without additional confirmation
   
2. **Best Practices**:
   - Always understand what a command does before executing
   - Test commands in a safe environment first
   - Never paste commands from untrusted sources
   - Avoid running with sudo/admin privileges
   - Use --dry-run or equivalent flags when available
   
3. **Known Limitations**:
   - Basic command validation only checks for obvious dangerous patterns
   - AI suggestions may occasionally be incorrect or unsafe
   - No rollback mechanism for executed commands
   - Command history is stored in plain text

4. **Recommended Usage**:
   - Development environments only
   - Non-critical systems
   - With regular backups in place
   - Under user supervision at all times

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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Development

### Running Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests with coverage
pytest

# Run only unit tests
pytest tests/unit

# Run only integration tests
pytest tests/integration

# Generate HTML coverage report
pytest --cov-report=html
# Open htmlcov/index.html in your browser
```

### Code Quality

```bash
# Format code with black
black src tests

# Check code style with flake8
flake8 src tests

# Type checking with mypy
mypy src
```

### Project Structure

```
desktopcommander-interface/
├── src/                      # Refactored modular code
│   ├── core/                 # Core business logic
│   │   ├── models.py         # Data models
│   │   ├── command_service.py # Command execution
│   │   ├── ollama_service.py  # AI integration
│   │   ├── security.py       # Safety checks
│   │   ├── history.py        # Command history
│   │   └── config_manager.py # Configuration persistence
│   ├── ui/                   # User interface
│   │   ├── gradio_app.py     # Gradio UI creation
│   │   └── presenters.py     # UI logic
│   └── app.py               # Main application
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests
│   └── integration/          # Integration tests
├── app.py                    # Legacy single-file version
├── run.py                    # New entry point
├── requirements.txt          # Runtime dependencies
├── requirements-dev.txt      # Development dependencies
├── LICENSE                   # MIT License
├── SECURITY.md              # Security policy
└── README.md                # This file
```

## Contributing

Feel free to submit issues and enhancement requests!

### Security Issues

Please see [SECURITY.md](SECURITY.md) for information on reporting security vulnerabilities.
