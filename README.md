# Windows CMD NLP Parser

Type naturally. Execute commands. No syntax memorization required.

## Quick Start

### Installation

1. Download or clone this repository
2. Double-click `install.bat` (or run as Administrator for system-wide install)
3. Restart CMD
4. Type: `nlp go to downloads`

### Usage

```cmd
nlp [natural language command]
```

## Examples

| Natural Language | CMD Command |
|-----------------|-------------|
| `nlp go to downloads` | `cd Downloads` |
| `nlp go back` | `cd ..` |
| `nlp list files` | `dir` |
| `nlp create folder test` | `mkdir test` |
| `nlp delete file readme.txt` | `del readme.txt` |
| `nlp show ip address` | `ipconfig` |
| `nlp clear screen` | `cls` |
| `nlp open notepad` | `start notepad` |

## How It Works

```
nlp [your command]
    ↓
nlp.bat (Windows wrapper)
    ↓
cmd_nlp.py (NLP parser)
    ↓
Execute CMD command
```

## Files

- `nlp.bat` — Windows command wrapper (what you type)
- `cmd_nlp.py` — Natural language parser
- `install.bat` — Installation script
- `patterns/` — Command pattern definitions

## Requirements

- Windows 10/11
- Python 3.8+ (must be in PATH)
- CMD or PowerShell

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "nlp is not recognized" | Run `install.bat` and restart CMD |
| "Python not found" | Install Python and add to PATH |
| Command not understood | Check examples above for supported patterns |

## Advanced

### Dry Run Mode

Preview what command would execute:

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

## License

MIT
