#!/usr/bin/env python3

from typing import List


DANGEROUS_PATTERNS: List[str] = [
    "rm -rf /", "sudo rm", "format", "mkfs", "dd if=/dev/zero",
    "> /dev/", ":(){ :|:& };:", "chmod -r 777 /", "chown -r",
    "rm -rf /*", "sudo shutdown", "sudo reboot", "sudo halt",
    "wipefs", "shred", ">/dev/sd", "cat /dev/urandom >",
    "sudo passwd", "sudo userdel", "sudo usermod", "sudo groupdel",
    "iptables -F", "systemctl stop", "service stop", "kill -9",
    "truncate", ">/etc/", "| sh", "| bash", "curl | sh", "wget | sh", "curl | bash", "wget | bash",
    "bash <(", "eval $(", "$(curl", "$(wget", "base64 -d |", "| base64 -d"
]


# Safe read-only commands for safe mode
SAFE_COMMANDS: List[str] = [
    # File system exploration
    "ls", "ll", "la", "dir", "pwd", "find", "locate", "which", "whereis",
    "file", "stat", "du", "df", "mount", "lsblk", "tree",
    
    # File reading
    "cat", "head", "tail", "less", "more", "grep", "egrep", "fgrep",
    "awk", "sed -n", "cut", "sort", "uniq", "wc", "diff", "comm",
    
    # System information
    "ps", "top", "htop", "free", "vmstat", "iostat", "netstat", "ss",
    "lsof", "who", "w", "id", "groups", "uname", "hostname", "uptime",
    "date", "cal", "env", "printenv", "locale", "lscpu", "lspci", "lsusb",
    
    # Network information
    "ping", "traceroute", "nslookup", "dig", "host", "ifconfig", "ip addr",
    "ip route", "arp", "route",
    
    # Package information
    "dpkg -l", "rpm -qa", "yum list", "apt list", "brew list",
    "pip list", "pip freeze", "npm list", "gem list",
    
    # Help and documentation
    "man", "info", "help", "--help", "-h", "--version", "-v",
    
    # Git read operations
    "git status", "git log", "git diff", "git branch", "git remote",
    "git show", "git config --list",
    
    # Development tools (read-only)
    "echo", "printf", "test", "true", "false", "whoami", "basename",
    "dirname", "readlink", "type", "command",
]


def is_command_safe(command: str) -> bool:
    """Check if a command is safe to execute."""
    command_lower = command.lower()
    return not any(pattern in command_lower for pattern in DANGEROUS_PATTERNS)


def estimate_command_risk(command: str) -> str:
    """Estimate the risk level of a command."""
    high_risk_terms = ['rm', 'delete', 'sudo', 'chmod', 'chown', 'format', 'mkfs']
    command_lower = command.lower()
    
    if any(term in command_lower for term in high_risk_terms):
        return "HIGH"
    return "LOW"


def is_command_in_safe_mode_whitelist(command: str) -> bool:
    """Check if a command is whitelisted for safe mode execution."""
    command_lower = command.lower().strip()
    
    # Check exact matches first
    if command_lower in SAFE_COMMANDS:
        return True
    
    # Check if command starts with any safe command
    for safe_cmd in SAFE_COMMANDS:
        if command_lower.startswith(safe_cmd + " ") or command_lower == safe_cmd:
            # Additional check: ensure no pipes or redirects to dangerous operations
            if any(danger in command_lower for danger in ["|", ">", "<", "&&", ";", "`", "$("]):
                # Allow safe pipes like "| grep", "| less", etc.
                safe_pipes = ["| grep", "| egrep", "| fgrep", "| less", "| more", 
                             "| head", "| tail", "| sort", "| uniq", "| wc"]
                if not any(pipe in command_lower for pipe in safe_pipes):
                    return False
            return True
    
    return False