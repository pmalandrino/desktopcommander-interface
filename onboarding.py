"""
Onboarding and help components for Desktop Commander UI
"""

def get_onboarding_html():
    """Get the onboarding HTML content"""
    return """
    <div style="max-width: 800px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #1f2937; margin-bottom: 1.5rem;">🎯 Quick Start Guide</h2>
        
        <div style="background: #f0f9ff; border-left: 4px solid #3b82f6; padding: 1rem; margin-bottom: 1.5rem; border-radius: 0 8px 8px 0;">
            <h3 style="margin-top: 0; color: #1e40af;">1. Natural Language Commands</h3>
            <p style="margin-bottom: 0.5rem;">Simply describe what you want to do in plain English:</p>
            <ul style="margin: 0.5rem 0;">
                <li>"Show me all images in this folder"</li>
                <li>"Find files larger than 10MB"</li>
                <li>"Count how many Python files I have"</li>
            </ul>
        </div>
        
        <div style="background: #f0fdf4; border-left: 4px solid #10b981; padding: 1rem; margin-bottom: 1.5rem; border-radius: 0 8px 8px 0;">
            <h3 style="margin-top: 0; color: #059669;">2. Review Before Running</h3>
            <p style="margin-bottom: 0;">Always review the generated command before executing it. You can edit it if needed!</p>
        </div>
        
        <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 1rem; margin-bottom: 1.5rem; border-radius: 0 8px 8px 0;">
            <h3 style="margin-top: 0; color: #d97706;">3. Use Templates</h3>
            <p style="margin-bottom: 0;">Check out the Quick Commands panel for common operations. Click any template to use it instantly.</p>
        </div>
        
        <div style="background: #fce7f3; border-left: 4px solid #ec4899; padding: 1rem; margin-bottom: 1.5rem; border-radius: 0 8px 8px 0;">
            <h3 style="margin-top: 0; color: #be185d;">4. Learn from History</h3>
            <p style="margin-bottom: 0;">Your command history shows what worked. You can learn from previous commands and outputs.</p>
        </div>
        
        <h3 style="color: #1f2937; margin-top: 2rem;">⌨️ Keyboard Shortcuts</h3>
        <table style="width: 100%; border-collapse: collapse; margin-top: 1rem;">
            <tr style="background: #f3f4f6;">
                <th style="padding: 0.75rem; text-align: left; border-bottom: 2px solid #e5e7eb;">Action</th>
                <th style="padding: 0.75rem; text-align: left; border-bottom: 2px solid #e5e7eb;">Shortcut</th>
            </tr>
            <tr>
                <td style="padding: 0.75rem; border-bottom: 1px solid #e5e7eb;">Generate Command</td>
                <td style="padding: 0.75rem; border-bottom: 1px solid #e5e7eb;"><code>Ctrl/Cmd + Enter</code></td>
            </tr>
            <tr>
                <td style="padding: 0.75rem; border-bottom: 1px solid #e5e7eb;">Execute Command</td>
                <td style="padding: 0.75rem; border-bottom: 1px solid #e5e7eb;"><code>Ctrl/Cmd + Shift + Enter</code></td>
            </tr>
            <tr>
                <td style="padding: 0.75rem; border-bottom: 1px solid #e5e7eb;">Clear All</td>
                <td style="padding: 0.75rem; border-bottom: 1px solid #e5e7eb;"><code>Ctrl/Cmd + K</code></td>
            </tr>
        </table>
        
        <div style="background: #f9fafb; padding: 1.5rem; margin-top: 2rem; border-radius: 12px; border: 1px solid #e5e7eb;">
            <h3 style="margin-top: 0; color: #1f2937;">🛡️ Safety First</h3>
            <p>Desktop Commander includes safety filters to prevent dangerous operations. However:</p>
            <ul>
                <li>Always review commands before executing</li>
                <li>Be careful with file deletion or modification commands</li>
                <li>Start with read-only operations to get familiar</li>
                <li>Use absolute paths when you need specific locations</li>
            </ul>
        </div>
    </div>
    """

def get_tips_carousel():
    """Get rotating tips for the UI"""
    tips = [
        "💡 Try natural language like 'organize my downloads folder'",
        "🚀 Press Tab to autocomplete file paths",
        "📊 Use '| head -20' to limit long outputs",
        "🔍 Combine commands with && for multiple operations",
        "📁 Drag and drop files to get their paths",
        "⚡ Double-click history items to reuse commands",
        "🎯 Be specific - 'find Python files' vs 'find .py files in src'",
        "🛡️ Test commands with 'echo' first to preview",
        "📝 Save useful commands to your personal templates",
        "🌟 Star frequently used commands for quick access"
    ]
    return tips

def get_error_help(error_message: str) -> str:
    """Get contextual help based on error message"""
    error_help = {
        "permission denied": {
            "icon": "🔐",
            "title": "Permission Issue",
            "help": "This file or directory requires higher permissions. Try:\n• Using a different location\n• Checking file ownership\n• Running with appropriate permissions"
        },
        "command not found": {
            "icon": "❓",
            "title": "Command Not Available",
            "help": "This command isn't installed or not in PATH. Try:\n• Installing the required tool\n• Using an alternative command\n• Checking your system's package manager"
        },
        "no such file": {
            "icon": "📁",
            "title": "File Not Found",
            "help": "The specified file or directory doesn't exist. Try:\n• Checking the path spelling\n• Using tab completion\n• Listing directory contents first"
        },
        "timeout": {
            "icon": "⏱️",
            "title": "Operation Timed Out",
            "help": "The command took too long to complete. Try:\n• Breaking it into smaller operations\n• Adding filters to reduce data\n• Using more efficient commands"
        }
    }
    
    for key, help_data in error_help.items():
        if key in error_message.lower():
            return f"""
            <div style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 1rem; margin-top: 1rem;">
                <h4 style="margin: 0 0 0.5rem 0; color: #991b1b;">
                    {help_data['icon']} {help_data['title']}
                </h4>
                <p style="margin: 0; color: #7f1d1d; white-space: pre-line;">
                    {help_data['help']}
                </p>
            </div>
            """
    
    return ""

def format_command_suggestion(user_input: str) -> list:
    """Get command suggestions based on user input"""
    suggestions = {
        "file": ["find . -name '*.txt'", "ls -la", "du -sh *"],
        "search": ["grep -r 'pattern' .", "find . -name '*keyword*'", "rg 'pattern'"],
        "count": ["wc -l filename", "find . -type f | wc -l", "ls -1 | wc -l"],
        "size": ["du -sh *", "df -h", "find . -size +100M"],
        "process": ["ps aux", "top -n 1", "pgrep processname"],
        "network": ["netstat -an", "lsof -i", "ping -c 4 google.com"],
        "system": ["uname -a", "uptime", "free -h"],
    }
    
    matched_suggestions = []
    for keyword, commands in suggestions.items():
        if keyword in user_input.lower():
            matched_suggestions.extend(commands)
    
    return matched_suggestions[:3]  # Return top 3 suggestions