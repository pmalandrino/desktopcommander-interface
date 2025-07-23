# Security Policy

## Overview

Desktop Commander is an **ALPHA** version application that executes system commands with the permissions of the user running it. This document outlines the security considerations, known risks, and best practices for using this application.

## Security Warning

⚠️ **CRITICAL**: This application can execute ANY system command with your user permissions. Improper use can result in:
- Permanent data loss
- System corruption
- Security breaches
- Unauthorized access

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| Alpha   | :white_check_mark: |

## Known Security Risks

### 1. Command Execution
- Commands are executed directly through the system shell
- No sandboxing or containerization is implemented
- Commands run with full user permissions

### 2. AI-Generated Commands
- AI suggestions may be incorrect or potentially harmful
- The AI model can generate destructive commands if prompted
- Basic pattern matching is used to block obvious dangerous commands

### 3. Limited Safety Checks
The application blocks commands containing these patterns:
- System-wide deletions (`rm -rf /`, `rm -rf /*`)
- Permission changes (`chmod -R 777 /`)
- System shutdown/reboot commands
- Disk formatting commands
- Fork bombs and malicious scripts
- Piped curl/wget executions

However, many dangerous commands may still pass these checks.

### 4. Data Storage
- Command history is stored in memory (not persisted)
- No encryption is used for command storage
- Sensitive information in commands may be visible

## Security Features

### 1. Dry-Run Mode
- Use `--dry-run` flag to preview commands without execution
- Available as a toggle in the UI
- Shows command details and estimated risk level

### 2. Command Filtering
- Basic pattern matching for known dangerous commands
- Commands are rejected if they match dangerous patterns

### 3. User Confirmation
- Commands must be explicitly executed
- AI-generated commands are displayed before execution

## Best Practices

### For Users

1. **Always use dry-run mode first** for unfamiliar commands
2. **Never run with elevated privileges** (sudo/admin) unless absolutely necessary
3. **Review every command** before execution
4. **Use in isolated environments** (VMs, containers) when possible
5. **Keep regular backups** of important data
6. **Don't paste commands** from untrusted sources

### For Developers

1. **Review all PRs** for security implications
2. **Expand dangerous pattern list** as new risks are identified
3. **Consider implementing**:
   - Command whitelisting for safe mode
   - Proper sandboxing mechanisms
   - Audit logging
   - Rate limiting

## Reporting Security Vulnerabilities

If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. Email security concerns to: [security@example.com] (replace with actual email)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Future Security Enhancements

Planned security improvements for beta release:

1. **Safe Mode**: Whitelist of read-only commands
2. **Sandboxing**: Container or VM-based execution
3. **Audit Logging**: Persistent logs of all executed commands
4. **User Authentication**: Multi-user support with permissions
5. **Command Signing**: Cryptographic verification of commands
6. **Rate Limiting**: Prevent rapid command execution

## Disclaimer

This software is provided "as is" without warranty of any kind. Users assume all risks associated with command execution. The developers are not responsible for any damage, data loss, or security breaches resulting from use of this application.

## Security Checklist for Deployment

- [ ] Run only in development environments
- [ ] Use dry-run mode by default
- [ ] Regular backups in place
- [ ] Isolated from production systems
- [ ] Limited user permissions
- [ ] Monitoring enabled
- [ ] Emergency recovery plan ready

---

**Remember**: With great power comes great responsibility. Use Desktop Commander wisely and safely.