# Desktop Commander Gradio UI

A beautiful, user-friendly interface for natural language desktop automation using Ollama LLM.

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- 🎨 **Modern UX Design** - Beautiful, intuitive interface with smooth animations
- 🤖 **Natural Language Processing** - Convert plain English to shell commands
- ⚡ **Smart Command Generation** - Uses Ollama LLM (gemma3:4b model)
- 🛡️ **Safety First** - Built-in command filtering and review before execution
- 📚 **Command Templates** - Quick access to common operations
- 📜 **Command History** - Track and learn from previous commands
- 🎯 **Contextual Help** - Smart error messages and suggestions
- 🌙 **Beautiful UI** - Gradient headers, smooth transitions, responsive design
- ⌨️ **Keyboard Shortcuts** - Power user features
- 📱 **Fully Responsive** - Works on desktop and mobile browsers

## 🖼️ UI Preview

The interface features:
- Clean, modern design with a gradient header
- Natural language input with smart suggestions
- Command preview and editing before execution
- Rich output display with syntax highlighting
- Organized command templates by category
- Visual feedback for all actions
- Real-time system status monitoring

## Prerequisites

1. **Python 3.8+** installed
2. **Desktop Commander** installed:
   ```bash
   npm install -g @wonderwhy-er/desktop-commander
   ```
3. **Ollama** running locally with `gemma3:4b` model:
   ```bash
   # Start Ollama service
   ollama serve
   
   # Pull the model (if not already installed)
   ollama pull gemma3:4b
   ```

## Installation

1. Clone or navigate to this directory:
   ```bash
   cd /Users/pjmalandrino/Documents/Pro/workspace/poc/desktopcommander-interface
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Make sure Ollama is running:
   ```bash
   ollama serve
   ```

2. Run the application:
   
   **🎨 UX-Enhanced Version (Recommended)**:
   ```bash
   python app_ux.py
   ```
   
   **Other versions**:
   ```bash
   python app.py          # Full Desktop Commander integration
   python app_simple.py   # Basic version with direct execution
   ```

3. The interface will open automatically at `http://127.0.0.1:7860`

### 🚀 Quick Start with UX Version

The UX-enhanced version (`app_ux.py`) provides the best experience with:
- Beautiful, intuitive interface
- Onboarding guide for new users
- Smart command suggestions
- Visual feedback for all operations
- Command templates organized by category
- Contextual error help

## Interface Overview

### 🎨 UX-Enhanced Version (`app_ux.py`)
- **Smart Input**: Natural language processing with autocomplete suggestions
- **Visual Feedback**: Color-coded status messages and smooth animations  
- **Command Templates**: Pre-built commands organized by category:
  - 📁 Files & Folders
  - 📊 System Information
  - 🔍 Search & Filter
  - 📝 Text Processing
- **Safety Features**: 
  - Command preview before execution
  - Dangerous command filtering
  - Clear error messages with solutions
- **Rich History**: Visual command history with status indicators
- **Responsive Design**: Works beautifully on all screen sizes

### Classic Versions
- **System Status**: Shows if Ollama and Desktop Commander are properly configured
- **Prompt Input**: Enter natural language commands
- **Command Display**: Shows and allows editing of generated commands
- **Output Display**: Shows command results
- **Command History**: Tracks last 10 commands with timestamps

## Security Notes

- All operations are local-only (no internet connection required)
- Desktop Commander restrictions apply (blocked commands, allowed directories)
- Commands can be reviewed and edited before execution
- No remote connections are accepted

## Troubleshooting

### Ollama not connecting
- Ensure Ollama is running: `ollama serve`
- Check if the model is installed: `ollama list`
- Verify the model name in `app.py` matches your installed model

### Desktop Commander errors
- Check if it's installed: `npx -y @wonderwhy-er/desktop-commander --version`
- Verify allowed directories in Desktop Commander configuration
- Some commands may be blocked by security settings

### Permission errors
- Ensure you have proper permissions for the directories you're accessing
- Desktop Commander may have directory restrictions configured

## Example Commands

Try these natural language prompts:
- "List all CSV files in the current directory"
- "Show me what's in the README file"
- "Create a new folder called projects"
- "Find Python files modified today"
- "Count lines in all JavaScript files"

## Architecture

```
User Input → Gradio UI → Ollama LLM → Shell Command
                ↓
          Desktop Commander (MCP/JSON-RPC)
                ↓
          Command Execution
                ↓
          Output Display
```

## Extending

The application can be extended with:
- Additional LLM models
- Custom command templates
- Advanced UI features
- Batch command execution
- Command scheduling
- Output parsing and visualization

## License

This project is for local use and demonstration purposes.