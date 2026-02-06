# Windows CMD NLP Parser

Natural language interface for Windows Command Prompt. Type like a human, get commands executed.

## Purpose

Remove friction from Windows command-line usage by translating natural language into CMD commands. Perfect for quick tasks without memorizing syntax.

## Features

- **Natural patterns**: "go to downloads" → `cd Downloads`
- **Extensible**: Add new command patterns easily
- **Safe mode**: Confirmation for destructive operations
- **Learning**: Logs patterns for future improvement
- **Multi-step**: Handle compound commands

## Usage

```bash
python cmd_nlp.py "go to downloads"
python cmd_nlp.py "create folder my-project"
python cmd_nlp.py "list files"
```

## Supported Patterns

### Navigation
- "go to [dir]" → `cd [dir]`
- "go back" → `cd ..`
- "show current directory" → `cd`
- "show current path" → `cd`

### File Operations
- "list files" → `dir`
- "list files sorted by size" → `dir /O-S`
- "create folder [name]" → `mkdir [name]`
- "delete file [name]" → `del [name]` (with confirmation)
- "delete folder [name]" → `rmdir [name]` (with confirmation)

### System
- "open [program]" → `start [program]`
- "clear" → `cls`
- "show disk space" → `wmic logicaldisk get size,freespace,caption`
- "show ip address" → `ipconfig`

### Search
- "find files containing [pattern]" → `dir /s /b | findstr [pattern]`
- "find text [text] in files" → `findstr /s /i [text] *.*`

## Architecture

```
cmd_nlp.py
├── Command patterns (regex-based)
├── Intent classifier
├── Command generator
├── Safety layer
└── Execution/preview mode
```

## Safety Features

1. **Confirmation required**: Destructive commands need user approval
2. **Dry-run mode**: Show command without executing
3. **Pattern logging**: Learn from successful commands
4. **Blacklist**: Block dangerous commands (format, shutdown, etc.)

## Extending

Add new patterns in `PATTERNS` dict:

```python
PATTERNS = {
    r"my pattern (.+)": lambda match: f"cmd {match.group(1)}",
}
```

## Future Improvements

- LLM-based understanding for complex queries
- Command history and favorites
- Alias system for frequent tasks
- Integration with file explorer
- Voice input support
