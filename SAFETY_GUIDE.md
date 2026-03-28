# 🛡️ Safety & Security Guide

## Overview

The Local AI Agent is designed with safety as a top priority. It provides terminal access while protecting your system from dangerous operations.

## 🔒 Safety Features

### 1. **Command Whitelisting/Blacklisting**

#### Safe Commands (Allowed)
The agent only allows safe, read-only commands:

**File Viewing:**
- `ls`, `dir`, `cat`, `head`, `tail`
- `find`, `grep`, `awk`, `sed`
- `wc`, `sort`, `uniq`, `diff`

**System Information:**
- `pwd`, `whoami`, `uname`, `hostname`
- `df`, `du`, `free`, `top`, `ps`
- `date`, `uptime`, `cal`

**Network Information (Read-only):**
- `ping`, `traceroute`, `nslookup`
- `curl`, `wget` (for reading)
- `ifconfig`, `netstat`

**Development:**
- `git`, `python`, `node`, `java`
- `gcc`, `make`, `cmake`

#### Blocked Commands (Dangerous)
These commands are **always blocked**:

**System Destruction:**
- `rm`, `rmdir`, `del`, `format`
- `dd`, `shred`, `wipe`

**System Control:**
- `shutdown`, `reboot`, `halt`
- `systemctl`, `service`, `launchctl`

**Permission Changes:**
- `chmod`, `chown`, `chgrp`
- `sudo`, `su`

**Package Managers:**
- `apt`, `yum`, `dnf`, `brew`
- `pip`, `npm` (can break system)

**Dangerous Patterns:**
- `rm -rf`, `rm -r /`
- `| bash`, `| sh`
- `> /dev/`

### 2. **Resource Limits**

#### Time Limits
- **Maximum execution time:** 30 seconds
- Commands that take longer are automatically killed

#### Output Limits
- **Maximum output size:** 1MB
- Prevents memory exhaustion

#### Working Directory Restrictions
- Only allowed directories can be accessed:
  - User home directory (`~`)
  - Temporary directory (`/tmp`)
  - Current working directory

### 3. **Risk Assessment**

Every command is assessed for risk:

| Risk Level | Description | Action |
|------------|-------------|--------|
| **SAFE** | Known safe command | Execute immediately |
| **LOW** | Probably safe | Execute with logging |
| **MEDIUM** | Unknown command | Execute with caution |
| **HIGH** | Potentially dangerous | Warn user |
| **BLOCKED** | Dangerous command | Block execution |

### 4. **Audit Logging**

All command executions are logged:
- Command executed
- Risk level
- Execution time
- Return code
- Success/failure

Logs are stored in: `~/ai-agent/logs/`

## 🌍 Platform Independence

### Supported Platforms

| Platform | Status | Notes |
|----------|--------|-------|
| **macOS** | ✅ Full Support | Intel & Apple Silicon |
| **Linux** | ✅ Full Support | Ubuntu, Debian, Fedora, etc. |
| **Windows** | ✅ Full Support | Native & WSL |
| **WSL** | ✅ Full Support | Windows Subsystem for Linux |

### Platform-Specific Features

#### macOS
- Homebrew integration
- Apple Silicon optimization
- macOS-specific commands (`open`, `pbcopy`)

#### Linux
- Multiple package manager support (apt, yum, dnf, pacman)
- Linux-specific commands
- Systemd integration (optional)

#### Windows
- Batch file management
- PowerShell support
- Windows-specific commands (`dir`, `type`, `tasklist`)

#### WSL (Windows Subsystem for Linux)
- Full Linux compatibility
- Windows integration
- Shared file system access

## 🔧 Configuration

### Customizing Safety Settings

Edit `~/ai-agent/config/safety.json`:

```json
{
  "max_execution_time": 30,
  "max_output_size": 1048576,
  "allowed_working_dirs": [
    "~/ai-agent",
    "~/projects",
    "/tmp"
  ],
  "additional_safe_commands": [
    "my_custom_command"
  ],
  "additional_blocked_commands": [
    "dangerous_tool"
  ]
}
```

### Adding Safe Commands

```bash
# Via management script
./manage.sh add-safe-command my_command

# Or edit config file directly
```

### Removing Safe Commands

```bash
./manage.sh remove-safe-command my_command
```

## 🚨 What's Protected

### Your System is Safe From:

1. **Accidental Deletion**
   - Cannot delete files or directories
   - Cannot format drives

2. **System Modification**
   - Cannot change permissions
   - Cannot install packages
   - Cannot modify system files

3. **Resource Exhaustion**
   - Time limits prevent infinite loops
   - Output limits prevent memory issues
   - Working directory restrictions

4. **Privilege Escalation**
   - Cannot use sudo/su
   - Cannot change ownership
   - Cannot modify system services

### What You CAN Do:

1. **View Files and Directories**
   - Read file contents
   - List directory contents
   - Search for files

2. **Get System Information**
   - Check disk usage
   - View running processes
   - Get network information

3. **Run Development Tools**
   - Execute Python scripts
   - Run Node.js applications
   - Compile code (gcc, make)

4. **Process Data**
   - Parse text files
   - Transform data
   - Generate reports

## 🔐 Security Best Practices

### 1. **Review Commands**
Before executing, the agent shows:
- Command to be executed
- Risk level
- Working directory

### 2. **Monitor Logs**
Regularly check logs for suspicious activity:
```bash
./manage.sh logs
```

### 3. **Update Regularly**
Keep the agent updated for security patches:
```bash
./manage.sh update
```

### 4. **Use Strong Models**
Use reputable AI models from Ollama:
```bash
ollama pull llama3.2
ollama pull mistral
```

## 🆘 Emergency Procedures

### If Something Goes Wrong

1. **Stop the Agent Immediately**
   ```bash
   ./manage.sh stop
   ```

2. **Check Logs**
   ```bash
   tail -100 ~/ai-agent/logs/agent.log
   ```

3. **Review Recent Commands**
   ```bash
   grep "BLOCKED" ~/ai-agent/logs/agent.log
   ```

4. **Reset Configuration**
   ```bash
   rm ~/ai-agent/config/safety.json
   ./manage.sh restart
   ```

## 📊 Safety Statistics

View safety statistics:
```bash
./manage.sh safety-stats
```

Output:
```
=== Safety Statistics ===
Total commands executed: 1,234
Safe commands: 1,100 (89%)
Low risk: 100 (8%)
Medium risk: 30 (2%)
High risk: 4 (0.3%)
Blocked: 0 (0%)
```

## 🤝 Contributing to Safety

### Report Security Issues

If you find a security vulnerability:
1. Do NOT open a public issue
2. Email: security@ai-agent.local
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact

### Improve Safety Rules

Submit pull requests to:
- Add new safe commands
- Improve risk assessment
- Enhance logging

## 📚 Additional Resources

- [User Guide](USER_GUIDE.md)
- [Enhanced Features](ENHANCED_FEATURES.md)
- [Troubleshooting](USER_GUIDE.md#troubleshooting)

---

**Your system is safe. Your data is private. Your AI is powerful.**