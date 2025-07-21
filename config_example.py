# Configuration for Desktop Commander UI
# Copy this file to config.py and modify as needed

# Ollama Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:4b"
OLLAMA_TEMPERATURE = 0.7
OLLAMA_MAX_TOKENS = 100

# Desktop Commander Configuration
DESKTOP_COMMANDER_CMD = ["npx", "-y", "@wonderwhy-er/desktop-commander"]
DESKTOP_COMMANDER_TIMEOUT = 60  # seconds

# UI Configuration
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 7860
AUTO_OPEN_BROWSER = True
HISTORY_SIZE = 10

# Prompt Templates
COMMAND_GENERATION_TEMPLATE = """You are a helpful assistant that generates shell commands.
User request: {prompt}
Generate a single shell command that accomplishes this task. 
Respond with ONLY the command, no explanation."""

# Security Settings
ALLOWED_COMMANDS = None  # None means all (Desktop Commander will filter)
BLOCKED_PATTERNS = [
    "rm -rf /",
    "sudo rm",
    "format",
    "mkfs"
]

# Example custom prompts for common tasks
QUICK_ACTIONS = {
    "list_files": "ls -la",
    "show_date": "date",
    "disk_usage": "df -h",
    "memory_info": "free -h",
    "process_list": "ps aux | head -20",
    "network_info": "ifconfig || ip addr",
    "current_directory": "pwd",
    "system_info": "uname -a"
}