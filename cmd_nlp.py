#!/usr/bin/env python3
"""
Windows CMD/PowerShell NLP Parser
Natural language interface for Windows Command Prompt and PowerShell
Cross-platform command generation
"""

import re
import json
import os
import subprocess
import sys
import platform
from datetime import datetime, timezone
from typing import Optional, Tuple, List, Dict, Callable, Any, Union

# Try to import prompt_toolkit for interactive history support
try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import FileHistory
    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False


class ShellType:
    """Supported shell types"""
    CMD = "cmd"
    POWERSHELL = "powershell"
    AUTO = "auto"


class CommandPattern:
    """Represents a single command pattern with regex and generators for each shell"""

    def __init__(self, pattern: str, generators: Union[Callable, Dict[str, Callable]], 
                 description: str, safe: bool = True, category: str = "general"):
        self.pattern = re.compile(pattern, re.IGNORECASE)
        self.description = description
        self.safe = safe  # False if command is destructive
        self.category = category
        
        # Support both single generator (CMD only) and dict of generators
        if callable(generators):
            # Legacy support: single generator = CMD command
            self.generators = {
                ShellType.CMD: generators,
                ShellType.POWERSHELL: generators  # Will be same as CMD
            }
        else:
            self.generators = generators

    def match(self, text: str) -> Optional[re.Match]:
        return self.pattern.match(text)
    
    def get_command(self, shell: str, match: re.Match) -> Optional[str]:
        """Get command for specific shell type"""
        generator = self.generators.get(shell)
        if generator:
            try:
                result = generator(match)
                return str(result) if result else None
            except Exception:
                return None
        return None


class CMDNLPParser:
    """Natural language parser for Windows CMD and PowerShell commands"""

    CONFIG_FILE = "cmd_nlp_config.json"

    def __init__(self, log_file: str = "logs/command_history.jsonl", dry_run: bool = False, 
                 no_emoji: bool = False, config_file: Optional[str] = None, 
                 history_file: str = ".nlp_history", shell: str = ShellType.AUTO):
        self.patterns: List[CommandPattern] = []
        self.log_file = log_file
        self.dry_run = dry_run
        self.no_emoji = no_emoji
        self.config_file = config_file or self.CONFIG_FILE
        self.history_file = history_file
        self.shell_mode = shell
        self.custom_patterns: List[Dict[str, Any]] = []
        
        # Auto-detect shell if needed
        if self.shell_mode == ShellType.AUTO:
            self.shell_mode = self._detect_shell()
        
        self._setup_patterns()
        self._load_custom_patterns()
        self._setup_logging()

    def _detect_shell(self) -> str:
        """Detect the current shell environment"""
        # Check environment variables
        ps_module_path = os.environ.get('PSModulePath', '')
        if ps_module_path:
            return ShellType.POWERSHELL
        
        # Check if we're in a PowerShell session
        if os.environ.get('POWERSHELL_DISTRIBUTION_CHANNEL'):
            return ShellType.POWERSHELL
        
        # Check for pwsh or powershell in parent process
        try:
            import psutil
            parent = psutil.Process().parent()
            if parent:
                parent_name = parent.name().lower()
                if 'pwsh' in parent_name or 'powershell' in parent_name:
                    return ShellType.POWERSHELL
        except ImportError:
            pass
        
        # Default to CMD on Windows
        if platform.system() == 'Windows':
            return ShellType.CMD
        
        # On non-Windows, default to PowerShell-compatible commands
        return ShellType.POWERSHELL

    def _add_pattern(self, pattern: str, generators: Union[Callable, Dict[str, Callable]], 
                     description: str, safe: bool = True, category: str = "general") -> None:
        """Helper to add a pattern with proper categorization"""
        self.patterns.append(CommandPattern(pattern, generators, description, safe, category))

    def _setup_patterns(self) -> None:
        """Initialize all command patterns by category"""
        # Order matters: more specific patterns should come before general ones
        self._setup_navigation_patterns()
        self._setup_file_operation_patterns()
        self._setup_system_patterns()
        self._setup_search_patterns()
        self._setup_process_patterns()
        self._setup_environment_patterns()
        self._setup_network_patterns()
        self._setup_file_property_patterns()
        self._setup_text_file_patterns()
        self._setup_alias_patterns()

    def _setup_navigation_patterns(self) -> None:
        """Navigation-related command patterns"""
        self._add_pattern(
            r"go to (.+)",
            {
                ShellType.CMD: lambda m: f"cd {m.group(1).strip().title()}",
                ShellType.POWERSHELL: lambda m: f"Set-Location -Path '{m.group(1).strip()}'"
            },
            "Change directory",
            safe=True,
            category="navigation"
        )
        self._add_pattern(
            r"go back",
            {
                ShellType.CMD: lambda m: "cd ..",
                ShellType.POWERSHELL: lambda m: "Set-Location .."
            },
            "Go to parent directory",
            safe=True,
            category="navigation"
        )
        self._add_pattern(
            r"show (current directory|current path)",
            {
                ShellType.CMD: lambda m: "cd",
                ShellType.POWERSHELL: lambda m: "Get-Location"
            },
            "Show current directory",
            safe=True,
            category="navigation"
        )
        self._add_pattern(
            r"where am i",
            {
                ShellType.CMD: lambda m: "cd",
                ShellType.POWERSHELL: lambda m: "Get-Location"
            },
            "Show current directory",
            safe=True,
            category="navigation"
        )

    def _setup_file_operation_patterns(self) -> None:
        """File operation command patterns"""
        # List files sorted - more specific first
        self._add_pattern(
            r"list files (?:sorted|sort) by (size|name|date)",
            {
                ShellType.CMD: lambda m: {
                    "size": "dir /O-S",
                    "name": "dir /O-N",
                    "date": "dir /O-D"
                }.get(m.group(1).lower(), "dir"),
                ShellType.POWERSHELL: lambda m: {
                    "size": "Get-ChildItem | Sort-Object Length -Descending",
                    "name": "Get-ChildItem | Sort-Object Name",
                    "date": "Get-ChildItem | Sort-Object LastWriteTime -Descending"
                }.get(m.group(1).lower(), "Get-ChildItem")
            },
            "List files sorted",
            safe=True,
            category="files"
        )
        # General list files
        self._add_pattern(
            r"list files",
            {
                ShellType.CMD: lambda m: "dir",
                ShellType.POWERSHELL: lambda m: "Get-ChildItem"
            },
            "List files",
            safe=True,
            category="files"
        )
        # Create directory
        self._add_pattern(
            r"create (folder|directory) (.+)",
            {
                ShellType.CMD: lambda m: f"mkdir {m.group(2).strip()}",
                ShellType.POWERSHELL: lambda m: f"New-Item -ItemType Directory -Path '{m.group(2).strip()}'"
            },
            "Create directory",
            safe=True,
            category="files"
        )
        # Delete file
        self._add_pattern(
            r"delete (?:the )?file (.+)",
            {
                ShellType.CMD: lambda m: f'del "{m.group(1).strip()}"',
                ShellType.POWERSHELL: lambda m: f"Remove-Item -Path '{m.group(1).strip()}' -Force"
            },
            "Delete file",
            safe=False,
            category="files"
        )
        # Delete folder
        self._add_pattern(
            r"delete (?:the )?(folder|directory) (.+)",
            {
                ShellType.CMD: lambda m: f'rmdir /s /q "{m.group(2).strip()}"',
                ShellType.POWERSHELL: lambda m: f"Remove-Item -Path '{m.group(2).strip()}' -Recurse -Force"
            },
            "Delete directory",
            safe=False,
            category="files"
        )
        # Copy file
        self._add_pattern(
            r"copy (.+) (?:to|into) (.+)",
            {
                ShellType.CMD: lambda m: f'copy "{m.group(1).strip()}" "{m.group(2).strip()}"',
                ShellType.POWERSHELL: lambda m: f"Copy-Item -Path '{m.group(1).strip()}' -Destination '{m.group(2).strip()}'"
            },
            "Copy file",
            safe=True,
            category="files"
        )
        # Move file
        self._add_pattern(
            r"move (.+) (?:to|into) (.+)",
            {
                ShellType.CMD: lambda m: f'move "{m.group(1).strip()}" "{m.group(2).strip()}"',
                ShellType.POWERSHELL: lambda m: f"Move-Item -Path '{m.group(1).strip()}' -Destination '{m.group(2).strip()}'"
            },
            "Move file",
            safe=False,
            category="files"
        )

    def _setup_system_patterns(self) -> None:
        """System operation command patterns"""
        self._add_pattern(
            r"open (.+)",
            {
                ShellType.CMD: lambda m: f"start {m.group(1).strip()}",
                ShellType.POWERSHELL: lambda m: f"Start-Process '{m.group(1).strip()}'"
            },
            "Open program",
            safe=True,
            category="system"
        )
        self._add_pattern(
            r"clear|clean",
            {
                ShellType.CMD: lambda m: "cls",
                ShellType.POWERSHELL: lambda m: "Clear-Host"
            },
            "Clear screen",
            safe=True,
            category="system"
        )
        self._add_pattern(
            r"show disk space",
            {
                ShellType.CMD: lambda m: "wmic logicaldisk get size,freespace,caption",
                ShellType.POWERSHELL: lambda m: "Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{N='Used(GB)';E={[math]::Round($_.Used/1GB,2)}}, @{N='Free(GB)';E={[math]::Round($_.Free/1GB,2)}}"
            },
            "Show disk space",
            safe=True,
            category="system"
        )
        self._add_pattern(
            r"show ip address",
            {
                ShellType.CMD: lambda m: "ipconfig",
                ShellType.POWERSHELL: lambda m: "Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike '*Loopback*'}"
            },
            "Show IP address",
            safe=True,
            category="system"
        )
        self._add_pattern(
            r"show my ip",
            {
                ShellType.CMD: lambda m: "ipconfig",
                ShellType.POWERSHELL: lambda m: "Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike '*Loopback*'}"
            },
            "Show IP address",
            safe=True,
            category="system"
        )
        self._add_pattern(
            r"show date",
            {
                ShellType.CMD: lambda m: "date /t",
                ShellType.POWERSHELL: lambda m: "Get-Date -Format 'yyyy-MM-dd'"
            },
            "Show current date",
            safe=True,
            category="system"
        )
        self._add_pattern(
            r"show time",
            {
                ShellType.CMD: lambda m: "time /t",
                ShellType.POWERSHELL: lambda m: "Get-Date -Format 'HH:mm:ss'"
            },
            "Show current time",
            safe=True,
            category="system"
        )

    def _setup_search_patterns(self) -> None:
        """Search operation command patterns"""
        self._add_pattern(
            r"find files (?:named|containing|with) (.+)",
            {
                ShellType.CMD: lambda m: f'dir /s /b | findstr /i "{m.group(1).strip()}"',
                ShellType.POWERSHELL: lambda m: f"Get-ChildItem -Recurse -Filter '*{m.group(1).strip()}*' | Select-Object FullName"
            },
            "Find files by name",
            safe=True,
            category="search"
        )
        self._add_pattern(
            r"find text (.+) (?:in|within) files",
            {
                ShellType.CMD: lambda m: f'findstr /s /i "{m.group(1).strip()}" *.*',
                ShellType.POWERSHELL: lambda m: f"Get-ChildItem -Recurse -File | Select-String -Pattern '{m.group(1).strip()}' | Select-Object Path, LineNumber, Line"
            },
            "Find text in files",
            safe=True,
            category="search"
        )

    def _setup_process_patterns(self) -> None:
        """Process management command patterns"""
        self._add_pattern(
            r"show (?:running )?process(?:es)?",
            {
                ShellType.CMD: lambda m: "tasklist",
                ShellType.POWERSHELL: lambda m: "Get-Process | Select-Object Id, ProcessName, CPU, WorkingSet | Format-Table -AutoSize"
            },
            "List running processes",
            safe=True,
            category="process"
        )
        self._add_pattern(
            r"kill (?:process )?(.+)",
            {
                ShellType.CMD: lambda m: f'taskkill /F /IM "{m.group(1).strip()}"',
                ShellType.POWERSHELL: lambda m: f"Stop-Process -Name '{m.group(1).strip()}' -Force"
            },
            "Kill process",
            safe=False,
            category="process"
        )

    def _setup_environment_patterns(self) -> None:
        """Environment variable command patterns"""
        self._add_pattern(
            r"set (?:variable )?(.+) (?:to|equal|=) (.+)",
            {
                ShellType.CMD: lambda m: f"set {m.group(1).strip()}={m.group(2).strip()}",
                ShellType.POWERSHELL: lambda m: f"$env:{m.group(1).strip()} = '{m.group(2).strip()}'"
            },
            "Set environment variable",
            safe=True,
            category="environment"
        )
        self._add_pattern(
            r"show variable (.+)",
            {
                ShellType.CMD: lambda m: f"echo %{m.group(1).strip()}%",
                ShellType.POWERSHELL: lambda m: f"$env:{m.group(1).strip()}"
            },
            "Show environment variable",
            safe=True,
            category="environment"
        )

    def _setup_network_patterns(self) -> None:
        """Network utility command patterns"""
        self._add_pattern(
            r"ping (.+)",
            {
                ShellType.CMD: lambda m: f"ping {m.group(1).strip()}",
                ShellType.POWERSHELL: lambda m: f"Test-Connection -ComputerName {m.group(1).strip()} -Count 4"
            },
            "Ping host",
            safe=True,
            category="network"
        )
        self._add_pattern(
            r"trace route to (.+)",
            {
                ShellType.CMD: lambda m: f"tracert {m.group(1).strip()}",
                ShellType.POWERSHELL: lambda m: f"Test-NetConnection -ComputerName {m.group(1).strip()} -TraceRoute"
            },
            "Trace route",
            safe=True,
            category="network"
        )

    def _setup_file_property_patterns(self) -> None:
        """File property command patterns - must come before general 'show' patterns"""
        self._add_pattern(
            r"show hidden files",
            {
                ShellType.CMD: lambda m: "dir /ah",
                ShellType.POWERSHELL: lambda m: "Get-ChildItem -Hidden | Select-Object Name, Attributes"
            },
            "List hidden files",
            safe=True,
            category="properties"
        )
        self._add_pattern(
            r"show (?:file )?(?:attributes|props|properties) (.+)",
            {
                ShellType.CMD: lambda m: f"attrib {m.group(1).strip()}",
                ShellType.POWERSHELL: lambda m: f"Get-ItemProperty -Path '{m.group(1).strip()}' | Select-Object *"
            },
            "Show file attributes",
            safe=True,
            category="properties"
        )
        self._add_pattern(
            r"hide (?:file )?(.+)",
            {
                ShellType.CMD: lambda m: f"attrib +h {m.group(1).strip()}",
                ShellType.POWERSHELL: lambda m: f"$file = Get-Item '{m.group(1).strip()}'; $file.Attributes = $file.Attributes -bor [System.IO.FileAttributes]::Hidden"
            },
            "Hide file",
            safe=True,
            category="properties"
        )

    def _setup_text_file_patterns(self) -> None:
        """Text file operation patterns - broad patterns that need specific ones first"""
        # Note: 'file' keyword is required to avoid matching other 'show' commands like 'show date'
        self._add_pattern(
            r"(?:show|read|display|cat) file (.+)",
            {
                ShellType.CMD: lambda m: f"type {m.group(1).strip()}",
                ShellType.POWERSHELL: lambda m: f"Get-Content -Path '{m.group(1).strip()}'"
            },
            "Display file contents",
            safe=True,
            category="text"
        )
        self._add_pattern(
            r"(?:edit|open) (?:file )?(.+)",
            {
                ShellType.CMD: lambda m: f"notepad {m.group(1).strip()}",
                ShellType.POWERSHELL: lambda m: f"notepad.exe '{m.group(1).strip()}'"
            },
            "Edit file",
            safe=True,
            category="text"
        )

    def _setup_alias_patterns(self) -> None:
        """Alias/shortcut patterns - Unix-style commands that work in both shells"""
        # These are common Unix commands that users might type
        # PowerShell has built-in aliases for many of these
        self._add_pattern(
            r"^ls$",
            {
                ShellType.CMD: lambda m: "dir",
                ShellType.POWERSHELL: lambda m: "Get-ChildItem"  # ls is aliased in PS but we're explicit
            },
            "List files (alias)",
            safe=True,
            category="alias"
        )
        self._add_pattern(
            r"^pwd$",
            {
                ShellType.CMD: lambda m: "cd",
                ShellType.POWERSHELL: lambda m: "Get-Location"
            },
            "Show directory (alias)",
            safe=True,
            category="alias"
        )
        self._add_pattern(
            r"^mkdir (.+)$",
            {
                ShellType.CMD: lambda m: f"mkdir {m.group(1)}",
                ShellType.POWERSHELL: lambda m: f"New-Item -ItemType Directory -Path '{m.group(1)}'"
            },
            "Make directory (alias)",
            safe=True,
            category="alias"
        )
        self._add_pattern(
            r"^rm (.+)$",
            {
                ShellType.CMD: lambda m: f'del "{m.group(1)}"',
                ShellType.POWERSHELL: lambda m: f"Remove-Item -Path '{m.group(1)}' -Force"
            },
            "Remove file (alias)",
            safe=False,
            category="alias"
        )
        # PowerShell-specific aliases
        self._add_pattern(
            r"^gci$",
            {
                ShellType.CMD: lambda m: "dir",
                ShellType.POWERSHELL: lambda m: "Get-ChildItem"
            },
            "Get-ChildItem alias",
            safe=True,
            category="alias"
        )
        self._add_pattern(
            r"^gl$",
            {
                ShellType.CMD: lambda m: "cd",
                ShellType.POWERSHELL: lambda m: "Get-Location"
            },
            "Get-Location alias",
            safe=True,
            category="alias"
        )

    def _load_custom_patterns(self) -> None:
        """Load custom patterns from JSON configuration file"""
        if not os.path.exists(self.config_file):
            return

        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)

            custom_patterns = config.get("patterns", [])
            for p in custom_patterns:
                try:
                    pattern = p.get("pattern")
                    cmd_template = p.get("cmd_command") or p.get("command")
                    ps_template = p.get("ps_command") or cmd_template
                    description = p.get("description", "Custom pattern")
                    safe = p.get("safe", True)
                    category = p.get("category", "custom")

                    if not pattern or not cmd_template:
                        continue

                    # Create generators for each shell
                    def make_generator(template):
                        return lambda m: self._substitute_groups(template, m)

                    generators = {
                        ShellType.CMD: make_generator(cmd_template),
                        ShellType.POWERSHELL: make_generator(ps_template)
                    }

                    self._add_pattern(
                        pattern,
                        generators,
                        description,
                        safe,
                        category
                    )
                    self.custom_patterns.append(p)
                except Exception as e:
                    if not self.no_emoji:
                        print(f"⚠️  Warning: Failed to load custom pattern: {e}")

        except json.JSONDecodeError as e:
            if not self.no_emoji:
                print(f"⚠️  Warning: Invalid JSON in config file: {e}")
        except IOError as e:
            if not self.no_emoji:
                print(f"⚠️  Warning: Could not read config file: {e}")

    def _substitute_groups(self, template: str, match) -> str:
        """Substitute regex match groups into command template"""
        result = template
        for i in range(1, match.lastindex + 1 if match.lastindex else 1):
            placeholder = f"{{{i}}}"
            if placeholder in result:
                result = result.replace(placeholder, match.group(i))
        return result

    def _setup_logging(self) -> None:
        """Setup logging directory"""
        log_dir = os.path.dirname(self.log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

    def _fmt(self, emoji: str, text: str) -> str:
        """Format output with optional emoji"""
        if self.no_emoji:
            return text
        return f"{emoji} {text}"

    @property
    def shell_name(self) -> str:
        """Get human-readable shell name"""
        return {
            ShellType.CMD: "CMD",
            ShellType.POWERSHELL: "PowerShell"
        }.get(self.shell_mode, "CMD")

    def parse(self, text: str) -> Tuple[Optional[str], Optional[CommandPattern]]:
        """
        Parse natural language text into shell command

        Args:
            text: Natural language input

        Returns:
            Tuple of (command, pattern) or (None, None) if no match
        """
        text = text.strip()

        for pattern in self.patterns:
            match = pattern.match(text)
            if match:
                command = pattern.get_command(self.shell_mode, match)
                if command:
                    return command, pattern

        return None, None

    def parse_all(self, text: str) -> Dict[str, Tuple[Optional[str], Optional[CommandPattern]]]:
        """
        Parse natural language text and return commands for all shells

        Args:
            text: Natural language input

        Returns:
            Dict mapping shell type to (command, pattern) tuple
        """
        text = text.strip()
        results = {}

        for pattern in self.patterns:
            match = pattern.match(text)
            if match:
                for shell in [ShellType.CMD, ShellType.POWERSHELL]:
                    command = pattern.get_command(shell, match)
                    if command:
                        results[shell] = (command, pattern)
                return results

        return results

    def log_command(self, input_text: str, command: str, pattern: CommandPattern, 
                    executed: bool, shell: str = None) -> None:
        """Log command to history file"""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "input": input_text,
            "command": command,
            "shell": shell or self.shell_mode,
            "pattern_description": pattern.description,
            "category": pattern.category,
            "safe": pattern.safe,
            "executed": executed
        }

        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except IOError as e:
            if not self.no_emoji:
                print(f"⚠️  Warning: Could not write to log file: {e}")
            else:
                print(f"Warning: Could not write to log file: {e}")

    def execute(self, text: str, auto_confirm: bool = False) -> bool:
        """
        Parse and execute natural language command

        Args:
            text: Natural language input
            auto_confirm: If True, execute unsafe commands without confirmation

        Returns:
            True if command was executed, False otherwise
        """
        command, pattern = self.parse(text)

        if not command:
            print(self._fmt("❓", f"I don't understand: '{text}'"))
            print("Try one of these patterns:")
            self._show_examples()
            return False

        print(f"\n{self._fmt('📝', f'Input: {text}')}")
        print(self._fmt("🎯", f"Intent: {pattern.description}"))
        print(self._fmt("⚡", f"[{self.shell_name}] {command}"))

        # Check if safe
        if not pattern.safe and not auto_confirm:
            print(f"\n{self._fmt('⚠️', 'This is a destructive command!')}")
            confirm = input("Execute? (y/n): ").strip().lower()
            if confirm != "y":
                print(self._fmt("❌", "Cancelled"))
                self.log_command(text, command, pattern, executed=False)
                return False

        # Execute or dry run
        if self.dry_run:
            print(self._fmt("🔍", "Dry run: Command not executed"))
            self.log_command(text, command, pattern, executed=False)
            return True

        print(self._fmt("✅", "Executing..."))
        
        # Actually execute the command
        executed = self._run_command(command)
        if executed:
            print(self._fmt("✨", "Done!"))
        return executed

    def _run_command(self, command: str) -> bool:
        """
        Execute a command using the appropriate shell
        
        Returns:
            True if command executed successfully, False otherwise
        """
        try:
            if self.shell_mode == ShellType.POWERSHELL:
                # Use PowerShell to execute
                result = subprocess.run(
                    ["pwsh", "-NoProfile", "-Command", command],
                    capture_output=True,
                    text=True,
                    shell=False
                )
            else:
                # Use CMD to execute
                result = subprocess.run(
                    ["cmd", "/c", command],
                    capture_output=True,
                    text=True,
                    shell=False
                )
            
            if result.returncode == 0:
                if result.stdout:
                    print(result.stdout)
                return True
            else:
                if not self.no_emoji:
                    print(f"❌ Command failed with exit code {result.returncode}")
                else:
                    print(f"Command failed with exit code {result.returncode}")
                if result.stderr:
                    print(result.stderr)
                return False
        except FileNotFoundError as e:
            shell_exe = "pwsh" if self.shell_mode == ShellType.POWERSHELL else "cmd.exe"
            if not self.no_emoji:
                print(f"⚠️  {shell_exe} not available. Command logged but not executed.")
            else:
                print(f"Warning: {shell_exe} not available. Command logged but not executed.")
            return True  # Still return True since we logged it
        except Exception as e:
            if not self.no_emoji:
                print(f"❌ Error executing command: {e}")
            else:
                print(f"Error executing command: {e}")
            return False

    def _show_examples(self) -> None:
        """Show example patterns"""
        examples = [
            "go to downloads",
            "list files",
            "create folder my-project",
            "find files containing config",
            "show disk space",
        ]
        for example in examples:
            print(f"  • {example}")

    def show_stats(self) -> None:
        """Show statistics from command history"""
        if not os.path.exists(self.log_file):
            print("No command history yet")
            return

        stats = {
            "total": 0,
            "executed": 0,
            "safe": 0,
            "destructive": 0,
            "categories": {},
            "patterns": {},
            "shells": {}
        }

        try:
            with open(self.log_file, "r") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    stats["total"] += 1
                    if entry.get("executed"):
                        stats["executed"] += 1
                    if entry.get("safe"):
                        stats["safe"] += 1
                    else:
                        stats["destructive"] += 1

                    category = entry.get("category", "unknown")
                    stats["categories"][category] = stats["categories"].get(category, 0) + 1

                    pattern = entry.get("pattern_description", "unknown")
                    stats["patterns"][pattern] = stats["patterns"].get(pattern, 0) + 1
                    
                    shell = entry.get("shell", "unknown")
                    stats["shells"][shell] = stats["shells"].get(shell, 0) + 1
        except IOError as e:
            print(f"Error reading log file: {e}")
            return

        print(self._fmt("📊", "Command Statistics:"))
        print(f"  Total commands: {stats['total']}")
        print(f"  Executed: {stats['executed']}")
        print(f"  Safe operations: {stats['safe']}")
        print(f"  Destructive operations: {stats['destructive']}")
        
        if stats["shells"]:
            print(self._fmt("🖥️", "Commands by shell:"))
            for shell, count in stats["shells"].items():
                print(f"  • {shell}: {count}")

        if stats["categories"]:
            print(self._fmt("📁", "Commands by category:"))
            sorted_categories = sorted(stats["categories"].items(), key=lambda x: x[1], reverse=True)
            for category, count in sorted_categories:
                print(f"  • {category}: {count}")

        if stats["patterns"]:
            print(self._fmt("🔢", "Most used patterns:"))
            sorted_patterns = sorted(stats["patterns"].items(), key=lambda x: x[1], reverse=True)
            for pattern, count in sorted_patterns[:5]:
                print(f"  • {pattern}: {count}")

    def get_patterns_by_category(self) -> Dict[str, List[CommandPattern]]:
        """Get all patterns organized by category"""
        categories: Dict[str, List[CommandPattern]] = {}
        for pattern in self.patterns:
            if pattern.category not in categories:
                categories[pattern.category] = []
            categories[pattern.category].append(pattern)
        return categories

    def show_patterns(self) -> None:
        """Display all available patterns organized by category"""
        categories = self.get_patterns_by_category()
        
        print(self._fmt("📋", f"Available Command Patterns (Shell: {self.shell_name}):"))
        print()
        
        for category, patterns in sorted(categories.items()):
            print(f"{category.upper()}:")
            for pattern in patterns:
                safety = " (destructive)" if not pattern.safe else ""
                print(f"  • {pattern.description}{safety}")
            print()


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Windows CMD/PowerShell NLP Parser")
    parser.add_argument("command", nargs="?", help="Natural language command")
    parser.add_argument("--dry-run", action="store_true", help="Show command without executing")
    parser.add_argument("--auto-confirm", action="store_true", help="Execute destructive commands without confirmation")
    parser.add_argument("--stats", action="store_true", help="Show command statistics")
    parser.add_argument("--interactive", action="store_true", help="Start interactive mode")
    parser.add_argument("--no-emoji", action="store_true", help="Disable emoji output")
    parser.add_argument("--patterns", action="store_true", help="Show all available patterns")
    parser.add_argument("--config", help="Path to custom patterns config file (JSON)")
    parser.add_argument("--shell", choices=["cmd", "powershell", "auto"], default="auto",
                        help="Shell to use: cmd, powershell, or auto (default: auto)")
    parser.add_argument("--show-both", action="store_true", help="Show both CMD and PowerShell commands")

    args = parser.parse_args()

    # Map CLI args to shell types
    shell_map = {
        "cmd": ShellType.CMD,
        "powershell": ShellType.POWERSHELL,
        "auto": ShellType.AUTO
    }

    cmd_nlp = CMDNLPParser(
        dry_run=args.dry_run, 
        no_emoji=args.no_emoji, 
        config_file=args.config,
        shell=shell_map.get(args.shell, ShellType.AUTO)
    )

    if args.stats:
        cmd_nlp.show_stats()
        return

    if args.patterns:
        cmd_nlp.show_patterns()
        return

    if args.show_both and args.command:
        # Show commands for both shells
        results = cmd_nlp.parse_all(args.command)
        if results:
            print(f"\n📝 Input: {args.command}")
            for shell, (cmd, pattern) in results.items():
                shell_name = "CMD" if shell == ShellType.CMD else "PowerShell"
                print(f"  [{shell_name}] {cmd}")
        else:
            print(f"❓ Could not parse: '{args.command}'")
        return

    if args.interactive:
        greeting = f"{cmd_nlp.shell_name} NLP Parser (Interactive Mode)" if args.no_emoji else f"🤖 {cmd_nlp.shell_name} NLP Parser (Interactive Mode)"
        print(greeting)
        print("Type 'exit' or 'quit' to leave")
        print(f"Active shell: {cmd_nlp.shell_name}")
        if PROMPT_TOOLKIT_AVAILABLE:
            print("Use UP/DOWN arrows to recall previous commands\n")
        else:
            print("(Install prompt_toolkit for command history: pip install prompt_toolkit)\n")

        # Set up prompt_toolkit session with history if available
        session = None
        if PROMPT_TOOLKIT_AVAILABLE:
            try:
                session = PromptSession(
                    history=FileHistory(cmd_nlp.history_file),
                    enable_history_search=True
                )
            except Exception as e:
                print(f"Warning: Could not load history: {e}")

        while True:
            try:
                prompt_text = "What would you like to do? " if args.no_emoji else "❓ What would you like to do? "
                
                # Use prompt_toolkit if available, fall back to input()
                if session:
                    text = session.prompt(prompt_text).strip()
                else:
                    text = input(prompt_text).strip()
                
                if text.lower() in ["exit", "quit"]:
                    goodbye = "Goodbye!" if args.no_emoji else "👋 Goodbye!"
                    print(goodbye)
                    break
                if not text:
                    continue
                cmd_nlp.execute(text, auto_confirm=args.auto_confirm)
                print()
            except KeyboardInterrupt:
                goodbye = "Goodbye!" if args.no_emoji else "👋 Goodbye!"
                print(f"\n{goodbye}")
                break
    elif args.command:
        cmd_nlp.execute(args.command, auto_confirm=args.auto_confirm)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
