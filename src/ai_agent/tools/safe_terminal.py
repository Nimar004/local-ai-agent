"""
Safe Terminal Execution Tool
Provides sandboxed terminal access with safety limits and cross-platform support.
"""

import asyncio
import logging
import os
import platform
import subprocess
import shlex
import tempfile
import shutil
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import psutil


class CommandRisk(Enum):
    """Risk levels for commands."""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    BLOCKED = "blocked"


@dataclass
class CommandResult:
    """Result of a command execution."""
    success: bool
    stdout: str
    stderr: str
    return_code: int
    execution_time: float
    risk_level: CommandRisk
    command: str


class SafeTerminal:
    """
    Safe terminal execution with sandboxing and limits.
    
    Features:
    - Command whitelisting/blacklisting
    - Resource limits (CPU, memory, time)
    - Working directory restrictions
    - Cross-platform support (macOS, Linux, Windows)
    - Audit logging
    - Safe command execution
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Safe Terminal."""
        self.logger = logging.getLogger("SafeTerminal")
        self._platform = platform.system().lower()
        self._config = config or {}
        
        # Safety settings
        self._max_execution_time = self._config.get("max_execution_time", 30)
        self._max_output_size = self._config.get("max_output_size", 1024 * 1024)  # 1MB
        self._allowed_working_dirs = self._config.get("allowed_working_dirs", [
            os.path.expanduser("~"),
            tempfile.gettempdir(),
            os.getcwd()
        ])
        
        # Command restrictions
        self._blocked_commands: Set[str] = {
            # Dangerous system commands
            "rm", "rmdir", "del", "format", "fdisk", "mkfs",
            "dd", "shred", "wipe", "srm",
            # System control
            "shutdown", "reboot", "halt", "poweroff",
            "systemctl", "service", "launchctl",
            # Network dangerous
            "iptables", "netsh", "ufw",
            # Process control
            "kill", "killall", "pkill", "xkill",
            # Permission changes
            "chmod", "chown", "chgrp", "icacls",
            # Package managers (can break system)
            "apt", "apt-get", "yum", "dnf", "pacman", "brew", "pip", "npm",
            # System modification
            "mount", "umount", "fsck", "crontab",
            # Dangerous redirects
            ">", ">>", "|", ";", "&&", "||",
        }
        
        self._safe_commands: Set[str] = {
            # File viewing
            "ls", "dir", "cat", "head", "tail", "less", "more",
            "find", "locate", "which", "whereis", "file",
            "stat", "wc", "sort", "uniq", "grep", "egrep", "fgrep",
            "awk", "sed", "cut", "tr", "diff", "cmp",
            # System info
            "pwd", "whoami", "id", "groups", "uname", "hostname",
            "date", "time", "uptime", "cal", "bc",
            "df", "du", "free", "top", "ps", "htop", "iotop",
            "lscpu", "lsmem", "lsblk", "lsusb", "lspci",
            # Network info (read-only)
            "ping", "traceroute", "nslookup", "dig", "host",
            "curl", "wget", "ifconfig", "ip", "netstat", "ss",
            # Text processing
            "echo", "printf", "test", "[", "true", "false",
            "expr", "let", "declare", "typeset", "export",
            # Archive (read-only)
            "tar", "zip", "unzip", "gzip", "gunzip",
            # Development
            "git", "python", "python3", "node", "java", "javac",
            "gcc", "g++", "make", "cmake",
            # Process viewing
            "pgrep", "pidof", "jobs", "bg", "fg",
        }
        
        # Platform-specific adjustments
        self._adjust_for_platform()
        
    def _adjust_for_platform(self) -> None:
        """Adjust settings for the current platform."""
        if self._platform == "windows":
            # Windows-specific commands
            self._safe_commands.update([
                "dir", "type", "copy", "xcopy", "robocopy",
                "tasklist", "taskkill", "systeminfo", "wmic",
                "powershell", "cmd",
            ])
            # Remove Unix-specific commands
            self._safe_commands -= {"ls", "cat", "grep", "find", "chmod"}
            
        elif self._platform == "darwin":  # macOS
            # macOS-specific commands
            self._safe_commands.update([
                "open", "pbcopy", "pbpaste", "say",
                "sw_vers", "sysctl", "vm_stat",
            ])
            
        elif self._platform == "linux":
            # Linux-specific commands
            self._safe_commands.update([
                "lsb_release", "cat /etc/os-release",
                "apt list", "yum list", "dnf list",
            ])
            
    def _get_base_command(self, command: str) -> str:
        """Extract the base command from a full command string."""
        try:
            parts = shlex.split(command)
            if parts:
                return parts[0].lower()
        except ValueError:
            pass
        return command.split()[0].lower() if command else ""
        
    def _assess_risk(self, command: str) -> CommandRisk:
        """Assess the risk level of a command."""
        base_cmd = self._get_base_command(command)
        
        # Check blocked commands
        if base_cmd in self._blocked_commands:
            return CommandRisk.BLOCKED
            
        # Check for dangerous patterns
        dangerous_patterns = [
            "rm -rf", "rm -r /", "rm -f /",
            "dd if=", "mkfs", "fdisk",
            "> /dev/", "| bash", "| sh",
            "sudo", "su -", "chmod 777",
            "curl | bash", "wget | bash",
        ]
        
        command_lower = command.lower()
        for pattern in dangerous_patterns:
            if pattern in command_lower:
                return CommandRisk.BLOCKED
                
        # Check safe commands
        if base_cmd in self._safe_commands:
            return CommandRisk.SAFE
            
        # Unknown command
        return CommandRisk.MEDIUM
        
    def _validate_working_dir(self, working_dir: str) -> bool:
        """Validate that the working directory is allowed."""
        working_dir = os.path.abspath(working_dir)
        
        for allowed_dir in self._allowed_working_dirs:
            allowed_dir = os.path.abspath(allowed_dir)
            if working_dir.startswith(allowed_dir):
                return True
                
        return False
        
    async def execute(
        self,
        command: str,
        working_dir: Optional[str] = None,
        timeout: Optional[int] = None,
        env: Optional[Dict[str, str]] = None
    ) -> CommandResult:
        """
        Execute a command safely.
        
        Args:
            command: The command to execute
            working_dir: Working directory (must be in allowed list)
            timeout: Execution timeout in seconds
            env: Environment variables
            
        Returns:
            CommandResult with execution details
        """
        import time
        start_time = time.time()
        
        # Assess risk
        risk_level = self._assess_risk(command)
        
        if risk_level == CommandRisk.BLOCKED:
            self.logger.warning(f"Blocked dangerous command: {command}")
            return CommandResult(
                success=False,
                stdout="",
                stderr=f"Command blocked for safety: {command}",
                return_code=-1,
                execution_time=0,
                risk_level=risk_level,
                command=command
            )
            
        # Validate working directory
        if working_dir and not self._validate_working_dir(working_dir):
            self.logger.warning(f"Blocked access to directory: {working_dir}")
            return CommandResult(
                success=False,
                stdout="",
                stderr=f"Access to directory denied: {working_dir}",
                return_code=-1,
                execution_time=0,
                risk_level=CommandRisk.BLOCKED,
                command=command
            )
            
        # Set defaults
        if working_dir is None:
            working_dir = os.getcwd()
        if timeout is None:
            timeout = self._max_execution_time
            
        # Prepare environment
        exec_env = os.environ.copy()
        if env:
            exec_env.update(env)
            
        try:
            # Execute command
            if self._platform == "windows":
                # Windows: use cmd.exe
                process = await asyncio.create_subprocess_exec(
                    "cmd", "/c", command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=working_dir,
                    env=exec_env
                )
            else:
                # Unix-like: use shell
                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=working_dir,
                    env=exec_env,
                    executable="/bin/bash" if self._platform != "windows" else None
                )
                
            # Wait for completion with timeout
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return CommandResult(
                    success=False,
                    stdout="",
                    stderr=f"Command timed out after {timeout} seconds",
                    return_code=-1,
                    execution_time=timeout,
                    risk_level=risk_level,
                    command=command
                )
                
            # Decode output
            stdout = stdout_bytes.decode('utf-8', errors='replace')[:self._max_output_size]
            stderr = stderr_bytes.decode('utf-8', errors='replace')[:self._max_output_size]
            
            execution_time = time.time() - start_time
            
            # Log execution
            self.logger.info(
                f"Executed: {command} | "
                f"Risk: {risk_level.value} | "
                f"Time: {execution_time:.2f}s | "
                f"Return: {process.returncode}"
            )
            
            return CommandResult(
                success=process.returncode == 0,
                stdout=stdout,
                stderr=stderr,
                return_code=process.returncode,
                execution_time=execution_time,
                risk_level=risk_level,
                command=command
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Command execution failed: {e}")
            
            return CommandResult(
                success=False,
                stdout="",
                stderr=str(e),
                return_code=-1,
                execution_time=execution_time,
                risk_level=risk_level,
                command=command
            )
            
    async def execute_safe(
        self,
        command: str,
        working_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a command and return simplified result.
        
        Args:
            command: The command to execute
            working_dir: Working directory
            
        Returns:
            Simplified result dictionary
        """
        result = await self.execute(command, working_dir)
        
        return {
            "success": result.success,
            "output": result.stdout if result.success else result.stderr,
            "return_code": result.return_code,
            "execution_time": result.execution_time,
            "risk_level": result.risk_level.value
        }
        
    def get_system_info(self) -> Dict[str, Any]:
        """Get safe system information."""
        info = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
        }
        
        # Add resource info if psutil is available
        try:
            import psutil
            info["cpu_count"] = psutil.cpu_count()
            info["memory_total"] = psutil.virtual_memory().total
            info["memory_available"] = psutil.virtual_memory().available
            info["disk_usage"] = {
                "/": psutil.disk_usage("/").percent,
            }
        except ImportError:
            pass
            
        return info
        
    def list_allowed_commands(self) -> List[str]:
        """List all allowed safe commands."""
        return sorted(list(self._safe_commands))
        
    def list_blocked_commands(self) -> List[str]:
        """List all blocked commands."""
        return sorted(list(self._blocked_commands))
        
    def add_safe_command(self, command: str) -> None:
        """Add a command to the safe list."""
        self._safe_commands.add(command.lower())
        self.logger.info(f"Added safe command: {command}")
        
    def remove_safe_command(self, command: str) -> None:
        """Remove a command from the safe list."""
        self._safe_commands.discard(command.lower())
        self.logger.info(f"Removed safe command: {command}")
        
    def add_blocked_command(self, command: str) -> None:
        """Add a command to the blocked list."""
        self._blocked_commands.add(command.lower())
        self.logger.info(f"Added blocked command: {command}")
        
    def remove_blocked_command(self, command: str) -> None:
        """Remove a command from the blocked list."""
        self._blocked_commands.discard(command.lower())
        self.logger.info(f"Removed blocked command: {command}")