# Windows CMD NLP Parser

Natural language interface for Windows Command Prompt. Type like a human, get commands executed.

## Purpose

Remove friction from Windows command-line usage by translating natural language into CMD commands. Perfect for quick tasks without memorizing syntax.

## Features

- **Natural patterns**: "go to downloads" → `cd Downloads`
- **Extensible**: Add new command patterns easily
- **Safe mode**: Confirmation for destructive operations
- **Learning**: Logs patterns for future improvement
- **Clean output**: `--no-emoji` flag for professional environments
- **Pattern discovery**: `--patterns` flag shows all available commands
- **Categorized**: Commands organized by category (files, network, system, etc.)

## Installation

```bash
git clone https://github.com/luinbytes/windows-cmd-nlp.git
cd windows-cmd-nlp
```

No dependencies required - uses Python standard library only.

## Usage

### Basic Commands

```bash
# Parse and show command
python cmd_nlp.py "go to downloads" --dry-run

# Execute command
python cmd_nlp.py "create folder my-project"

# Interactive mode
python cmd_nlp.py --interactive
```

### CLI Options

```bash
python cmd_nlp.py [command] [options]

Options:
  --dry-run          Show command without executing
  --auto-confirm     Execute destructive commands without confirmation
  --stats            Show command statistics from history
  --interactive      Start interactive mode
  --no-emoji         Disable emoji output (clean text)
  --patterns         Show all available command patterns
  -h, --help         Show help message
```

### Professional/Clean Output

For environments where emoji output isn't appropriate:

```bash
python cmd_nlp.py --no-emoji "list files"
# Output:
# Input: list files
# Intent: List files
# Command: dir
```

### List All Patterns

```bash
python cmd_nlp.py --patterns
```

Shows all available commands organized by category:
- NAVIGATION: Directory navigation
- FILES: File operations (list, create, delete, copy, move)
- SYSTEM: System operations
- SEARCH: File and text search
- PROCESS: Process management
- ENVIRONMENT: Environment variables
- NETWORK: Network utilities
- PROPERTIES: File properties
- TEXT: Text file operations
- ALIAS: Shortcut commands

## Supported Patterns

### Navigation
| Pattern | Command |
|---------|---------|
| "go to [dir]" | `cd [dir]` |
| "go back" | `cd ..` |
| "show current directory" | `cd` |
| "where am i" | `cd` |
| "pwd" | `cd` |

### File Operations
| Pattern | Command | Safety |
|---------|---------|--------|
| "list files" | `dir` | Safe |
| "list files sorted by size" | `dir /O-S` | Safe |
| "list files sorted by name" | `dir /O-N` | Safe |
| "list files sorted by date" | `dir /O-D` | Safe |
| "create folder [name]" | `mkdir [name]` | Safe |
| "create directory [name]" | `mkdir [name]` | Safe |
| "delete file [name]" | `del "[name]"` | **Destructive** |
| "delete folder [name]" | `rmdir /s /q "[name]"` | **Destructive** |
| "copy [src] to [dst]" | `copy "[src]" "[dst]"` | Safe |
| "move [src] to [dst]" | `move "[src]" "[dst]"` | **Destructive** |
| "ls" | `dir` | Safe |
| "mkdir [name]" | `mkdir [name]` | Safe |
| "rm [file]" | `del "[file]"` | **Destructive** |

### System Operations
| Pattern | Command |
|---------|---------|
| "open [program]" | `start [program]` |
| "clear" / "clean" | `cls` |
| "show disk space" | `wmic logicaldisk get size,freespace,caption` |
| "show ip address" | `ipconfig` |
| "show my ip" | `ipconfig` |

### Search Operations
| Pattern | Command |
|---------|---------|
| "find files containing [pattern]" | `dir /s /b \| findstr /i "[pattern]"` |
| "find text [text] in files" | `findstr /s /i "[text]" *.*` |

### Process Management
| Pattern | Command | Safety |
|---------|---------|--------|
| "show running processes" | `tasklist` | Safe |
| "kill process [name]" | `taskkill /F /IM "[name]"` | **Destructive** |

### Environment Variables
| Pattern | Command |
|---------|---------|
| "set variable [name] to [value]" | `set [name]=[value]` |
| "show variable [name]" | `echo %[name]%` |

### Network Utilities
| Pattern | Command |
|---------|---------|
| "ping [host]" | `ping [host]` |
| "trace route to [host]" | `tracert [host]` |

### File Properties
| Pattern | Command |
|---------|---------|
| "show hidden files" | `dir /ah` |
| "show file attributes [name]" | `attrib [name]` |
| "hide file [name]" | `attrib +h [name]` |

### Text File Operations
| Pattern | Command |
|---------|---------|
| "read file [name]" / "show file [name]" | `type [name]` |
| "edit file [name]" | `notepad [name]` |

## Architecture

```
cmd_nlp.py
├── CommandPattern Class
│   ├── pattern (regex)
│   ├── generator (lambda)
│   ├── description
│   ├── safe (bool)
│   └── category
├── CMDNLPParser Class
│   ├── Pattern setup (by category)
│   ├── Parser
│   ├── Safety layer
│   ├── Execution engine
│   └── Statistics
└── CLI interface
```

## Safety Features

1. **Confirmation required**: Destructive commands need user approval
2. **Dry-run mode**: Preview commands without executing (`--dry-run`)
3. **Command logging**: All commands logged to `logs/command_history.jsonl`
4. **Statistics tracking**: Analyze usage patterns and optimize
5. **Destructive flagging**: Commands marked as safe/unsafe

## Extending

### Adding New Patterns

Edit `cmd_nlp.py` and add to the appropriate `_setup_*_patterns()` method:

```python
def _setup_custom_patterns(self) -> None:
    self._add_pattern(
        r"your pattern (.+)",
        lambda m: f"your command {m.group(1)}",
        "Description of what it does",
        safe=True,  # or False for destructive commands
        category="custom"
    )
```

Then call `self._setup_custom_patterns()` from `_setup_patterns()`.

### Pattern Guidelines

1. **More specific first**: Place specific patterns before general ones
2. **Use non-capturing groups**: `(?:optional)` for optional text
3. **Quote file paths**: Always wrap file paths in quotes in generated commands
4. **Mark destructive commands**: Set `safe=False` for delete/remove operations
5. **Test thoroughly**: Add test cases to `test_cmd_nlp.py`

## Statistics

View command usage statistics:

```bash
python cmd_nlp.py --stats
```

Shows:
- Total commands executed
- Safe vs destructive operations
- Commands by category
- Most frequently used patterns

## Integration Ideas

### PowerShell Alias

Add to your PowerShell profile (`$PROFILE`):

```powershell
function nlp { python C:\path\to\windows-cmd-nlp\cmd_nlp.py @args }
Set-Alias -Name "ask" -Value nlp
```

Now use:
```powershell
ask "go to downloads"
ask --interactive
```

### CMD Batch File

The `nlp.bat` wrapper is included for easy Windows usage:

```batch
# Add to your PATH, then use anywhere:
nlp "go to downloads"
nlp --interactive
nlp --stats
```

Or run directly:
```batch
C:\path\to\windows-cmd-nlp\nlp.bat "list files"
```

To create your own wrapper:
```batch
@echo off
python C:\path\to\windows-cmd-nlp\cmd_nlp.py %*
```

### Raycast Extension

Create a Raycast script command that:
1. Takes natural language input
2. Calls parser
3. Displays command and executes on confirmation

## Future Improvements

- [ ] Configuration file for custom patterns
- [ ] LLM-based understanding for complex queries
- [ ] Command history and favorites
- [ ] Alias system for frequent tasks
- [ ] Voice input support
- [ ] Windows Service mode

## Development

### Running Tests

```bash
python test_cmd_nlp.py
```

### Project Structure

```
windows-cmd-nlp/
├── cmd_nlp.py           # Core parser
├── test_cmd_nlp.py      # Test suite
├── README.md            # This file
├── example_usage.md     # Usage examples
├── requirements.txt     # Dependencies (empty - stdlib only)
└── logs/                # Command history (created at runtime)
```

## License

MIT License - See LICENSE file

## Contributing

See CONTRIBUTING.md for guidelines.
