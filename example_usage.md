# Windows CMD NLP Parser - Usage Examples

## Basic Usage

### Command Line
```bash
# Parse and show command (dry run)
python cmd_nlp.py "go to downloads" --dry-run

# Execute command (with confirmation for unsafe operations)
python cmd_nlp.py "create folder my-project"

# Execute without confirmation (auto-confirm)
python cmd_nlp.py "delete file test.txt" --auto-confirm

# Interactive mode
python cmd_nlp.py --interactive

# Show statistics
python cmd_nlp.py --stats
```

### Python API
```python
from cmd_nlp import CMDNLPParser

# Create parser
parser = CMDNLPParser(dry_run=False)

# Parse natural language
command, pattern = parser.parse("go to downloads")
print(f"Command: {command}")
# Output: Command: cd Downloads

# Execute command
parser.execute("create folder my-project")
```

## Example Sessions

### Session 1: Navigation
```
❓ What would you like to do? go to downloads

📝 Input: go to downloads
🎯 Intent: Change directory
⚡ Command: cd Downloads

✅ Executing...
✨ Done!
```

### Session 2: File Operations
```
❓ What would you like to do? create folder my-project

📝 Input: create folder my-project
🎯 Intent: Create directory
⚡ Command: mkdir my-project

✅ Executing...
✨ Done!

❓ What would you like to do? list files

📝 Input: list files
🎯 Intent: List files
⚡ Command: dir

✅ Executing...
✨ Done!
```

### Session 3: Destructive Operation (with confirmation)
```
❓ What would you like to do? delete file old-backup.txt

📝 Input: delete file old-backup.txt
🎯 Intent: Delete file
⚡ Command: del "old-backup.txt"

⚠️  This is a destructive command!
Execute? (y/n): y

✅ Executing...
✨ Done!
```

### Session 4: Search
```
❓ What would you like to do? find files containing config

📝 Input: find files containing config
🎯 Intent: Find files by name
⚡ Command: dir /s /b | findstr /i "config"

✅ Executing...
✨ Done!
```

## Common Patterns

| Natural Language | CMD Command | Description |
|-----------------|-------------|-------------|
| go to downloads | cd Downloads | Navigate to folder |
| go back | cd .. | Go to parent directory |
| list files | dir | List contents |
| list files sorted by size | dir /O-S | List by size |
| create folder my-project | mkdir my-project | Create directory |
| delete file readme.txt | del "readme.txt" | Delete file |
| open notepad | start notepad | Open program |
| show disk space | wmic logicaldisk get size,freespace,caption | Disk info |
| show ip address | ipconfig | Network info |
| find files containing config | dir /s /b \| findstr /i "config" | Search files |

## Interactive Mode

Start interactive mode for continuous conversation:

```bash
python cmd_nlp.py --interactive
```

Example session:
```
🤖 Windows CMD NLP Parser (Interactive Mode)
Type 'exit' or 'quit' to leave

❓ What would you like to do? create folder test
📝 Input: create folder test
🎯 Intent: Create directory
⚡ Command: mkdir test
✅ Executing...
✨ Done!

❓ What would you like to do? go to test
📝 Input: go to test
🎯 Intent: Change directory
⚡ Command: cd test
✅ Executing...
✨ Done!

❓ What would you like to do? exit
👋 Goodbye!
```

## Statistics

Track usage patterns:

```bash
python cmd_nlp.py --stats
```

Output:
```
📊 Command Statistics:
  Total commands: 25
  Executed: 20
  Safe operations: 18
  Destructive operations: 2

🔢 Most used patterns:
  • List files: 8
  • Change directory: 6
  • Create directory: 4
  • Delete file: 2
  • Find files by name: 2
```

## Extending with Custom Patterns

Edit `cmd_nlp.py` and add to `_setup_patterns()`:

```python
# Custom pattern: "git status"
CommandPattern(
    r"git status",
    lambda m: "git status",
    "Git status",
    safe=True
)

# Custom pattern: "npm install [package]"
CommandPattern(
    r"npm install (.+)",
    lambda m: f"npm install {m.group(1).strip()}",
    "Install npm package",
    safe=True
)
```

## Safety Features

1. **Destructive command confirmation**: Delete, remove operations require confirmation
2. **Dry-run mode**: Preview commands without executing
3. **Command logging**: All commands logged to `logs/command_history.jsonl`
4. **Pattern learning**: Statistics show most-used patterns for optimization

## Integration Ideas

- **Shell alias**: Add to `~/.bashrc` or PowerShell profile
  ```bash
  alias nlp="python ~/projects/windows-cmd-nlp/cmd_nlp.py"
  ```
- **Windows Service**: Run as background service for voice commands
- **Raycast Extension**: Integrate with Raycast for quick commands
- **Clipboard monitoring**: Parse clipboard content automatically
