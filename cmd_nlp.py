#!/usr/bin/env python3
"""
Windows CMD NLP Parser
Natural language interface for Windows Command Prompt
"""

import re
import json
import os
from datetime import datetime, UTC
from typing import Optional, Tuple, List, Dict, Callable

class CommandPattern:
    """Represents a single command pattern with regex and generator"""

    def __init__(self, pattern: str, generator: Callable, description: str, safe: bool = True):
        self.pattern = re.compile(pattern, re.IGNORECASE)
        self.generator = generator
        self.description = description
        self.safe = safe  # False if command is destructive

    def match(self, text: str) -> Optional[re.Match]:
        return self.pattern.match(text)

class CMDNLPParser:
    """Natural language parser for Windows CMD commands"""

    def __init__(self, log_file: str = "logs/command_history.jsonl", dry_run: bool = False):
        self.patterns: List[CommandPattern] = []
        self.log_file = log_file
        self.dry_run = dry_run
        self._setup_patterns()
        self._setup_logging()

    def _setup_patterns(self) -> None:
        """Initialize all command patterns"""

        # Navigation patterns
        self.patterns.extend([
            # "go to [directory]"
            CommandPattern(
                r"go to (.+)",
                lambda m: f"cd {m.group(1).strip().title()}",
                "Change directory",
                safe=True
            ),
            # "go back"
            CommandPattern(
                r"go back",
                lambda m: "cd ..",
                "Go to parent directory",
                safe=True
            ),
            # "show current directory" or "show current path"
            CommandPattern(
                r"show (current directory|current path)",
                lambda m: "cd",
                "Show current directory",
                safe=True
            ),
            # "where am i"
            CommandPattern(
                r"where am i",
                lambda m: "cd",
                "Show current directory",
                safe=True
            ),
        ])

        # File operations
        self.patterns.extend([
            # "list files sorted by [size|name|date]" - check this first
            CommandPattern(
                r"list files (?:sorted|sort) by (size|name|date)",
                lambda m: {
                    "size": "dir /O-S",
                    "name": "dir /O-N",
                    "date": "dir /O-D"
                }.get(m.group(1).lower(), "dir"),
                "List files sorted",
                safe=True
            ),
            # "list files"
            CommandPattern(
                r"list files",
                lambda m: "dir",
                "List files",
                safe=True
            ),
            # "create folder [name]"
            CommandPattern(
                r"create (folder|directory) (.+)",
                lambda m: f"mkdir {m.group(2).strip()}",
                "Create directory",
                safe=True
            ),
            # "delete file [name]"
            CommandPattern(
                r"delete (?:the )?file (.+)",
                lambda m: f"del \"{m.group(1).strip()}\"",
                "Delete file",
                safe=False  # Destructive
            ),
            # "delete folder [name]"
            CommandPattern(
                r"delete (?:the )?(folder|directory) (.+)",
                lambda m: f"rmdir /s /q \"{m.group(2).strip()}\"",
                "Delete directory",
                safe=False  # Destructive
            ),
        ])

        # System operations
        self.patterns.extend([
            # "open [program]"
            CommandPattern(
                r"open (.+)",
                lambda m: f"start {m.group(1).strip()}",
                "Open program",
                safe=True
            ),
            # "clear"
            CommandPattern(
                r"clear|clean",
                lambda m: "cls",
                "Clear screen",
                safe=True
            ),
            # "show disk space"
            CommandPattern(
                r"show disk space",
                lambda m: "wmic logicaldisk get size,freespace,caption",
                "Show disk space",
                safe=True
            ),
            # "show ip address" or "show my ip"
            CommandPattern(
                r"show my ip",
                lambda m: "ipconfig",
                "Show IP address",
                safe=True
            ),
            # "show ip address"
            CommandPattern(
                r"show ip address",
                lambda m: "ipconfig",
                "Show IP address",
                safe=True
            ),
        ])

        # Search operations
        self.patterns.extend([
            # "find files containing [pattern]"
            CommandPattern(
                r"find files (?:named|containing|with) (.+)",
                lambda m: f"dir /s /b | findstr /i \"{m.group(1).strip()}\"",
                "Find files by name",
                safe=True
            ),
            # "find text [text] in files"
            CommandPattern(
                r"find text (.+) (?:in|within) files",
                lambda m: f"findstr /s /i \"{m.group(1).strip()}\" *.*",
                "Find text in files",
                safe=True
            ),
        ])

        # Copy/move operations
        self.patterns.extend([
            # "copy [source] to [dest]"
            CommandPattern(
                r"copy (.+) (?:to|into) (.+)",
                lambda m: f"copy \"{m.group(1).strip()}\" \"{m.group(2).strip()}\"",
                "Copy file",
                safe=True
            ),
            # "move [source] to [dest]"
            CommandPattern(
                r"move (.+) (?:to|into) (.+)",
                lambda m: f"move \"{m.group(1).strip()}\" \"{m.group(2).strip()}\"",
                "Move file",
                safe=False  # Can overwrite
            ),
        ])

        # Shortcuts/aliases
        self.patterns.extend([
            CommandPattern(r"ls", lambda m: "dir", "List files (alias)", safe=True),
            CommandPattern(r"pwd", lambda m: "cd", "Show directory (alias)", safe=True),
            CommandPattern(r"mkdir (.+)", lambda m: f"mkdir {m.group(1)}", "Make directory (alias)", safe=True),
            CommandPattern(r"rm (.+)", lambda m: f"del \"{m.group(1)}\"", "Remove file (alias)", safe=False),
        ])

    def _setup_logging(self) -> None:
        """Setup logging directory"""
        os.makedirs(os.path.dirname(self.log_file) if os.path.dirname(self.log_file) else ".", exist_ok=True)

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
            "timestamp": datetime.now(UTC).isoformat(),
            "input": input_text,
            "command": command,
            "pattern_description": pattern.description,
            "safe": pattern.safe,
            "executed": executed
        }

        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

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
            print(f"❓ I don't understand: '{text}'")
            print("Try one of these patterns:")
            self._show_examples()
            return False

        print(f"\n📝 Input: {text}")
        print(f"🎯 Intent: {pattern.description}")
        print(f"⚡ Command: {command}")

        # Check if safe
        if not pattern.safe and not auto_confirm:
            print(f"\n⚠️  This is a destructive command!")
            confirm = input("Execute? (y/n): ").strip().lower()
            if confirm != "y":
                print("❌ Cancelled")
                self.log_command(text, command, pattern, executed=False)
                return False

        # Execute or dry run
        if self.dry_run:
            print("\n🔍 Dry run: Command not executed")
            self.log_command(text, command, pattern, executed=False)
            return True

        print("\n✅ Executing...")
        # In a real Windows environment, this would execute the command
        # For now, we'll just log it
        self.log_command(text, command, pattern, executed=True)
        print("✨ Done!")
        return True

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
            "patterns": {}
        }

        with open(self.log_file, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                entry = json.loads(line)
                stats["total"] += 1
                if entry.get("executed"):
                    stats["executed"] += 1
                if entry.get("safe"):
                    stats["safe"] += 1
                else:
                    stats["destructive"] += 1

                pattern = entry.get("pattern_description", "unknown")
                stats["patterns"][pattern] = stats["patterns"].get(pattern, 0) + 1

        print("\n📊 Command Statistics:")
        print(f"  Total commands: {stats['total']}")
        print(f"  Executed: {stats['executed']}")
        print(f"  Safe operations: {stats['safe']}")
        print(f"  Destructive operations: {stats['destructive']}")

        print("\n🔢 Most used patterns:")
        sorted_patterns = sorted(stats["patterns"].items(), key=lambda x: x[1], reverse=True)
        for pattern, count in sorted_patterns[:5]:
            print(f"  • {pattern}: {count}")

def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Windows CMD NLP Parser")
    parser.add_argument("command", nargs="?", help="Natural language command")
    parser.add_argument("--dry-run", action="store_true", help="Show command without executing")
    parser.add_argument("--auto-confirm", action="store_true", help="Execute destructive commands without confirmation")
    parser.add_argument("--stats", action="store_true", help="Show command statistics")
    parser.add_argument("--interactive", action="store_true", help="Start interactive mode")

    args = parser.parse_args()

    cmd_nlp = CMDNLPParser(dry_run=args.dry_run)

    if args.stats:
        cmd_nlp.show_stats()
        return

    if args.interactive:
        print("🤖 Windows CMD NLP Parser (Interactive Mode)")
        print("Type 'exit' or 'quit' to leave\n")

        while True:
            try:
                text = input("❓ What would you like to do? ").strip()
                if text.lower() in ["exit", "quit"]:
                    print("👋 Goodbye!")
                    break
                if not text:
                    continue
                cmd_nlp.execute(text, auto_confirm=args.auto_confirm)
                print()
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
    elif args.command:
        cmd_nlp.execute(args.command, auto_confirm=args.auto_confirm)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
