#!/usr/bin/env python3
"""
Windows CMD NLP Parser
Natural language interface for Windows Command Prompt
"""

import re
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from typing import Optional, Tuple, List, Dict, Callable, Any

# Try to import prompt_toolkit for interactive history and completion support
try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.completion import WordCompleter, FuzzyCompleter
    from prompt_toolkit.document import Document
    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False


class CommandPattern:
    """Represents a single command pattern with regex and generator"""

    def __init__(self, pattern: str, generator: Callable, description: str, safe: bool = True, category: str = "general"):
        self.pattern = re.compile(pattern, re.IGNORECASE)
        self.generator = generator
        self.description = description
        self.safe = safe  # False if command is destructive
        self.category = category

    def match(self, text: str) -> Optional[re.Match]:
        return self.pattern.match(text)


class CMDNLPParser:
    """Natural language parser for Windows CMD commands"""

    CONFIG_FILE = "cmd_nlp_config.json"

    def __init__(self, log_file: str = "logs/command_history.jsonl", dry_run: bool = False, no_emoji: bool = False, config_file: Optional[str] = None, history_file: str = ".nlp_history"):
        self.patterns: List[CommandPattern] = []
        self.log_file = log_file
        self.dry_run = dry_run
        self.no_emoji = no_emoji
        self.config_file = config_file or self.CONFIG_FILE
        self.history_file = history_file
        self.custom_patterns: List[Dict[str, Any]] = []
        self._setup_patterns()
        self._load_custom_patterns()
        self._setup_logging()

    def _add_pattern(self, pattern: str, generator: Callable, description: str, 
                     safe: bool = True, category: str = "general") -> None:
        """Helper to add a pattern with proper categorization"""
        self.patterns.append(CommandPattern(pattern, generator, description, safe, category))

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
            lambda m: f"cd {m.group(1).strip().title()}",
            "Change directory",
            safe=True,
            category="navigation"
        )
        self._add_pattern(
            r"go back",
            lambda m: "cd ..",
            "Go to parent directory",
            safe=True,
            category="navigation"
        )
        self._add_pattern(
            r"show (current directory|current path)",
            lambda m: "cd",
            "Show current directory",
            safe=True,
            category="navigation"
        )
        self._add_pattern(
            r"where am i",
            lambda m: "cd",
            "Show current directory",
            safe=True,
            category="navigation"
        )

    def _setup_file_operation_patterns(self) -> None:
        """File operation command patterns"""
        # List files sorted - more specific first
        self._add_pattern(
            r"list files (?:sorted|sort) by (size|name|date)",
            lambda m: {
                "size": "dir /O-S",
                "name": "dir /O-N",
                "date": "dir /O-D"
            }.get(m.group(1).lower(), "dir"),
            "List files sorted",
            safe=True,
            category="files"
        )
        # General list files
        self._add_pattern(
            r"list files",
            lambda m: "dir",
            "List files",
            safe=True,
            category="files"
        )
        # Create directory
        self._add_pattern(
            r"create (folder|directory) (.+)",
            lambda m: f"mkdir {m.group(2).strip()}",
            "Create directory",
            safe=True,
            category="files"
        )
        # Delete file
        self._add_pattern(
            r"delete (?:the )?file (.+)",
            lambda m: f'del "{m.group(1).strip()}"',
            "Delete file",
            safe=False,
            category="files"
        )
        # Delete folder
        self._add_pattern(
            r"delete (?:the )?(folder|directory) (.+)",
            lambda m: f'rmdir /s /q "{m.group(2).strip()}"',
            "Delete directory",
            safe=False,
            category="files"
        )
        # Copy file
        self._add_pattern(
            r"copy (.+) (?:to|into) (.+)",
            lambda m: f'copy "{m.group(1).strip()}" "{m.group(2).strip()}"',
            "Copy file",
            safe=True,
            category="files"
        )
        # Move file
        self._add_pattern(
            r"move (.+) (?:to|into) (.+)",
            lambda m: f'move "{m.group(1).strip()}" "{m.group(2).strip()}"',
            "Move file",
            safe=False,
            category="files"
        )

    def _setup_system_patterns(self) -> None:
        """System operation command patterns"""
        self._add_pattern(
            r"open (.+)",
            lambda m: f"start {m.group(1).strip()}",
            "Open program",
            safe=True,
            category="system"
        )
        self._add_pattern(
            r"clear|clean",
            lambda m: "cls",
            "Clear screen",
            safe=True,
            category="system"
        )
        self._add_pattern(
            r"show disk space",
            lambda m: "wmic logicaldisk get size,freespace,caption",
            "Show disk space",
            safe=True,
            category="system"
        )
        self._add_pattern(
            r"show ip address",
            lambda m: "ipconfig",
            "Show IP address",
            safe=True,
            category="system"
        )
        self._add_pattern(
            r"show my ip",
            lambda m: "ipconfig",
            "Show IP address",
            safe=True,
            category="system"
        )
        self._add_pattern(
            r"show date",
            lambda m: "date /t",
            "Show current date",
            safe=True,
            category="system"
        )
        self._add_pattern(
            r"show time",
            lambda m: "time /t",
            "Show current time",
            safe=True,
            category="system"
        )

    def _setup_search_patterns(self) -> None:
        """Search operation command patterns"""
        self._add_pattern(
            r"find files (?:named|containing|with) (.+)",
            lambda m: f'dir /s /b | findstr /i "{m.group(1).strip()}"',
            "Find files by name",
            safe=True,
            category="search"
        )
        self._add_pattern(
            r"find text (.+) (?:in|within) files",
            lambda m: f'findstr /s /i "{m.group(1).strip()}" *.*',
            "Find text in files",
            safe=True,
            category="search"
        )

    def _setup_process_patterns(self) -> None:
        """Process management command patterns"""
        self._add_pattern(
            r"show (?:running )?process(?:es)?",
            lambda m: "tasklist",
            "List running processes",
            safe=True,
            category="process"
        )
        self._add_pattern(
            r"kill (?:process )?(.+)",
            lambda m: f'taskkill /F /IM "{m.group(1).strip()}"',
            "Kill process",
            safe=False,
            category="process"
        )

    def _setup_environment_patterns(self) -> None:
        """Environment variable command patterns"""
        self._add_pattern(
            r"set (?:variable )?(.+) (?:to|equal|=) (.+)",
            lambda m: f"set {m.group(1).strip()}={m.group(2).strip()}",
            "Set environment variable",
            safe=True,
            category="environment"
        )
        self._add_pattern(
            r"show variable (.+)",
            lambda m: f"echo %{m.group(1).strip()}%",
            "Show environment variable",
            safe=True,
            category="environment"
        )

    def _setup_network_patterns(self) -> None:
        """Network utility command patterns"""
        self._add_pattern(
            r"ping (.+)",
            lambda m: f"ping {m.group(1).strip()}",
            "Ping host",
            safe=True,
            category="network"
        )
        self._add_pattern(
            r"trace route to (.+)",
            lambda m: f"tracert {m.group(1).strip()}",
            "Trace route",
            safe=True,
            category="network"
        )

    def _setup_file_property_patterns(self) -> None:
        """File property command patterns - must come before general 'show' patterns"""
        self._add_pattern(
            r"show hidden files",
            lambda m: "dir /ah",
            "List hidden files",
            safe=True,
            category="properties"
        )
        self._add_pattern(
            r"show (?:file )?(?:attributes|props|properties) (.+)",
            lambda m: f"attrib {m.group(1).strip()}",
            "Show file attributes",
            safe=True,
            category="properties"
        )
        self._add_pattern(
            r"hide (?:file )?(.+)",
            lambda m: f"attrib +h {m.group(1).strip()}",
            "Hide file",
            safe=True,
            category="properties"
        )

    def _setup_text_file_patterns(self) -> None:
        """Text file operation patterns - broad patterns that need specific ones first"""
        # Note: 'file' keyword is required to avoid matching other 'show' commands like 'show date'
        self._add_pattern(
            r"(?:show|read|display|cat) file (.+)",
            lambda m: f"type {m.group(1).strip()}",
            "Display file contents",
            safe=True,
            category="text"
        )
        self._add_pattern(
            r"(?:edit|open) (?:file )?(.+)",
            lambda m: f"notepad {m.group(1).strip()}",
            "Edit file",
            safe=True,
            category="text"
        )

    def _setup_alias_patterns(self) -> None:
        """Alias/shortcut patterns"""
        aliases = [
            (r"ls", lambda m: "dir", "List files (alias)", True),
            (r"pwd", lambda m: "cd", "Show directory (alias)", True),
            (r"mkdir (.+)", lambda m: f"mkdir {m.group(1)}", "Make directory (alias)", True),
            (r"rm (.+)", lambda m: f'del "{m.group(1)}"', "Remove file (alias)", False),
        ]
        for pattern, generator, description, safe in aliases:
            self._add_pattern(pattern, generator, description, safe, category="alias")

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
                    command_template = p.get("command")
                    description = p.get("description", "Custom pattern")
                    safe = p.get("safe", True)
                    category = p.get("category", "custom")

                    if not pattern or not command_template:
                        continue

                    # Create generator that substitutes match groups
                    def make_generator(template):
                        return lambda m: self._substitute_groups(template, m)

                    self._add_pattern(
                        pattern,
                        make_generator(command_template),
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

    def parse(self, text: str) -> Tuple[Optional[str], Optional[CommandPattern]]:
        """
        Parse natural language text into CMD command

        Args:
            text: Natural language input

        Returns:
            Tuple of (command, pattern) or (None, None) if no match
        """
        text = text.strip()

        for pattern in self.patterns:
            match = pattern.match(text)
            if match:
                try:
                    command = pattern.generator(match)
                    # Handle if generator returned string or dict
                    if isinstance(command, str):
                        return command, pattern
                    else:
                        # Handle generator returned dict (for multiple options)
                        return str(command), pattern
                except Exception as e:
                    print(f"Error generating command: {e}")
                    continue

        return None, None

    def log_command(self, input_text: str, command: str, pattern: CommandPattern, executed: bool) -> None:
        """Log command to history file"""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "input": input_text,
            "command": command,
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
        print(self._fmt("⚡", f"Command: {command}"))

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
        
        # Actually execute the command on Windows
        executed = self._run_command(command)
        if executed:
            print(self._fmt("✨", "Done!"))
        return executed

    def _run_command(self, command: str) -> bool:
        """
        Execute a CMD command using subprocess
        
        Returns:
            True if command executed successfully, False otherwise
        """
        try:
            # Use cmd.exe /c to execute Windows commands
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
        except FileNotFoundError:
            # Not on Windows or cmd.exe not available
            if not self.no_emoji:
                print("⚠️  cmd.exe not available (not on Windows). Command logged but not executed.")
            else:
                print("Warning: cmd.exe not available (not on Windows). Command logged but not executed.")
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
            "patterns": {}
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
        except IOError as e:
            print(f"Error reading log file: {e}")
            return

        print(self._fmt("📊", "Command Statistics:"))
        print(f"  Total commands: {stats['total']}")
        print(f"  Executed: {stats['executed']}")
        print(f"  Safe operations: {stats['safe']}")
        print(f"  Destructive operations: {stats['destructive']}")

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

    def get_completion_keywords(self) -> List[str]:
        """Extract all keywords from pattern descriptions for tab completion"""
        keywords = set()
        
        # Common action words
        action_words = [
            "go", "to", "back", "show", "current", "directory", "path", "where", "am", "i",
            "list", "files", "sorted", "sort", "by", "size", "name", "date", "create",
            "folder", "directory", "delete", "the", "file", "copy", "into", "move",
            "open", "clear", "clean", "disk", "space", "ip", "address", "my", "date",
            "time", "find", "named", "containing", "with", "text", "in", "within",
            "running", "process", "processes", "kill", "set", "variable", "equal",
            "ping", "trace", "route", "hidden", "attributes", "props", "properties",
            "hide", "read", "display", "cat", "edit", "ls", "pwd", "mkdir", "rm"
        ]
        keywords.update(action_words)
        
        # Extract words from pattern descriptions
        for pattern in self.patterns:
            # Split description into words and add unique ones
            words = pattern.description.lower().split()
            for word in words:
                # Remove punctuation
                word = word.strip(".,!?():;")
                if word and len(word) > 2:
                    keywords.add(word)
            
            # Also extract from regex pattern (remove regex syntax)
            import re as regex_module
            pattern_text = pattern.pattern.pattern
            # Remove regex special chars and extract words
            clean_pattern = regex_module.sub(r'[?.*+^$()\[\]{}|\\]', ' ', pattern_text)
            words = clean_pattern.lower().split()
            for word in words:
                word = word.strip(".,!?():;")
                if word and len(word) > 2 and not word.startswith('<'):
                    keywords.add(word)
        
        return sorted(list(keywords))

    def create_completer(self) -> Optional[Any]:
        """Create a tab completer for interactive mode"""
        if not PROMPT_TOOLKIT_AVAILABLE:
            return None
        
        keywords = self.get_completion_keywords()
        
        # Create a fuzzy completer for better matching
        word_completer = WordCompleter(
            keywords,
            ignore_case=True,
            match_middle=True,
            sentence=True,
            meta_dict=self._get_completion_metadata()
        )
        
        return FuzzyCompleter(word_completer)
    
    def _get_completion_metadata(self) -> Dict[str, str]:
        """Get metadata for completion items (shown in popup)"""
        metadata = {}
        
        # Map common keywords to helpful descriptions
        keyword_patterns = {
            "go": "Navigate to directory",
            "back": "Go to parent directory",
            "list": "List files or directories",
            "files": "Work with files",
            "sorted": "Sort results by criteria",
            "create": "Create new item",
            "folder": "Directory operations",
            "delete": "Remove files or folders",
            "copy": "Copy files",
            "move": "Move files",
            "show": "Display information",
            "find": "Search for files or text",
            "kill": "Terminate processes",
            "set": "Configure variables",
            "ping": "Network connectivity test",
            "hide": "Hide files",
            "edit": "Open file in editor",
        }
        
        return keyword_patterns

    def show_patterns(self) -> None:
        """Display all available patterns organized by category"""
        categories = self.get_patterns_by_category()
        
        print(self._fmt("📋", "Available Command Patterns:"))
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

    parser = argparse.ArgumentParser(description="Windows CMD NLP Parser")
    parser.add_argument("command", nargs="?", help="Natural language command")
    parser.add_argument("--dry-run", action="store_true", help="Show command without executing")
    parser.add_argument("--auto-confirm", action="store_true", help="Execute destructive commands without confirmation")
    parser.add_argument("--stats", action="store_true", help="Show command statistics")
    parser.add_argument("--interactive", action="store_true", help="Start interactive mode")
    parser.add_argument("--no-emoji", action="store_true", help="Disable emoji output")
    parser.add_argument("--patterns", action="store_true", help="Show all available patterns")
    parser.add_argument("--config", help="Path to custom patterns config file (JSON)")
    parser.add_argument("--complete", action="store_true", help="Output completion keywords for shell integration")

    args = parser.parse_args()

    cmd_nlp = CMDNLPParser(dry_run=args.dry_run, no_emoji=args.no_emoji, config_file=args.config)

    if args.complete:
        # Output completion keywords for shell integration
        keywords = cmd_nlp.get_completion_keywords()
        print(" ".join(keywords))
        return

    if args.stats:
        cmd_nlp.show_stats()
        return

    if args.patterns:
        cmd_nlp.show_patterns()
        return

    if args.interactive:
        greeting = "Windows CMD NLP Parser (Interactive Mode)" if args.no_emoji else "🤖 Windows CMD NLP Parser (Interactive Mode)"
        print(greeting)
        print("Type 'exit' or 'quit' to leave")
        if PROMPT_TOOLKIT_AVAILABLE:
            print("Use UP/DOWN arrows for history, TAB for completion\n")
        else:
            print("(Install prompt_toolkit for command history: pip install prompt_toolkit)\n")

        # Set up prompt_toolkit session with history and completion if available
        session = None
        if PROMPT_TOOLKIT_AVAILABLE:
            try:
                completer = cmd_nlp.create_completer()
                session = PromptSession(
                    history=FileHistory(cmd_nlp.history_file),
                    enable_history_search=True,
                    completer=completer,
                    complete_while_typing=True,
                    complete_in_thread=True
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
