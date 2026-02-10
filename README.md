# Windows CMD NLP Parser v2

Natural language interface for Windows Command Prompt. Type like a human, execute commands instantly.

## Quick Start

### 1. Install

Double-click `install.bat` (or run as Administrator for system-wide install)

### 2. Use

Open CMD and type:

```cmd
nlp go to downloads
nlp create folder my-project
nlp list files
nlp show ip address
```

## Installation Options

### Option A: Automatic (Recommended)

```cmd
cd windows-cmd-nlp
install.bat
```

Restart CMD, then use `nlp` command anywhere.

### Option B: Manual PATH Add

Add the project folder to your PATH:
1. Copy the project folder path
2. Open System Properties → Environment Variables
3. Edit PATH variable
4. Add the folder path
5. Restart CMD

### Option C: Use Full Path

Without adding to PATH:

```cmd
C:\path\to\windows-cmd-nlp\nlp.bat go to downloads
```

## Usage Examples

| Natural Language | CMD Command |
|-----------------|-------------|
| `nlp go to downloads` | `cd Downloads` |
| `nlp go back` | `cd ..` |
| `nlp list files` | `dir` |
| `nlp create folder test` | `mkdir test` |
| `nlp delete file readme.txt` | `del readme.txt` |
| `nlp show ip address` | `ipconfig` |
| `nlp clear` | `cls` |
| `nlp open notepad` | `start notepad` |

## How It Works

```
nlp [your natural language command]
    ↓
nlp.bat (wrapper)
    ↓
cmd_nlp.py (parser)
    ↓
Execute CMD command
```

## Files

- `nlp.bat` — Command wrapper (what you type)
- `cmd_nlp.py` — NLP parser engine
- `install.bat` — PATH installer
- `patterns/` — Pattern definitions

## Advanced Usage

### Dry Run Mode

See what command would execute without running it:

```cmd
set NLP_DRY_RUN=1
nlp delete file important.txt
```

### Debug Mode

See pattern matching details:

```cmd
set NLP_DEBUG=1
nlp find files containing password
```

## Requirements

- Windows 10/11
- Python 3.8+ (in PATH)
- CMD or PowerShell

## Migration from v1

Old way (still works):
```cmd
python cmd_nlp.py "go to downloads"
```

New way (recommended):
```cmd
nlp go to downloads
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "nlp is not recognized" | Run `install.bat` and restart CMD |
| "python not found" | Add Python to PATH |
| Commands not executing | Check Python 3.8+ is installed |

## License

MIT
