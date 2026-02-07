@echo off
REM Windows CMD NLP Parser Wrapper
REM Usage: nlp [natural language command]
REM Example: nlp go to downloads

setlocal enabledelayedexpansion

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"

REM Build command from all arguments
set "USER_INPUT=%*"

if "%USER_INPUT%"=="" (
    echo Usage: nlp [natural language command]
    echo Example: nlp go to downloads
    echo Example: nlp create folder my-project
    exit /b 1
)

REM Run the Python script with the input
python "%~dp0cmd_nlp.py" %*
