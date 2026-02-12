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

### 3. Optional: DOSKEY Aliases (No 'nlp' Prefix!)

Run `setup_doskey.bat` as Administrator to enable natural language without typing 'nlp':

```cmd
ls              # Same as: nlp list files
go downloads    # Same as: nlp go to downloads
find *.txt      # Same as: nlp find files *.txt
create folder x # Same as: nlp create folder x
show ip         # Same as: nlp show ip address
```

**Available aliases:** `ls`, `ll`, `go`, `back`, `find`, `create`, `make`, `delete`, `show`, `open`, `status`, `commit`, and more!

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
- `setup_doskey.bat` — DOSKEY alias installer
- `setup_doskey_uninstall.bat` — Remove DOSKEY aliases
- `doskey_macros.bat` — Alias definitions
- `patterns/` — Pattern definitions

## DOSKEY Aliases

Want to type even less? DOSKEY aliases let you skip the `nlp` prefix entirely!

### Setup

Run as Administrator:
```cmd
setup_doskey.bat
```

Close and reopen CMD. Now you can type:

| Shortcut | Natural Language | CMD Command |
|----------|-----------------|-------------|
| `ls` | `list files` | `dir` |
| `ll` | `list files detailed` | `dir` |
| `go downloads` | `go to downloads` | `cd Downloads` |
| `back` | `go back` | `cd ..` |
| `find *.txt` | `find files *.txt` | `dir *.txt /s` |
| `create folder x` | `create folder x` | `mkdir x` |
| `delete file.txt` | `delete file.txt` | `del file.txt` |
| `show ip` | `show ip address` | `ipconfig` |
| `open notepad` | `open notepad` | `start notepad` |
| `clear` | `clear` | `cls` |
| `status` | `git status` | `git status` |

### How It Works

DOSKEY macros are loaded automatically via the Windows Registry (`AutoRun` key) every time CMD starts. The macros intercept common commands and route them through `nlp`.

### Uninstall

To remove DOSKEY aliases:
```cmd
setup_doskey_uninstall.bat
```

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
