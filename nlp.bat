@echo off
REM Windows CMD NLP Parser Wrapper
REM Usage: nlp [natural language command]
REM Example: nlp go to downloads

setlocal enabledelayedexpansion

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_PATH=%SCRIPT_DIR%cmd_nlp.py"

REM Check if Python is available
python --version > nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    exit /b 1
)

REM Check if the Python script exists
if not exist "%SCRIPT_PATH%" (
    echo Error: Could not find cmd_nlp.py in %SCRIPT_DIR%
    exit /b 1
)

REM Build command from all arguments
set "USER_INPUT=%*"

if "%USER_INPUT%"=="" (
    echo.
    echo Windows CMD NLP Parser
    echo.
    echo Usage: nlp [natural language command]
    echo.
    echo Examples:
    echo   nlp go to downloads
    echo   nlp create folder my-project
    echo   nlp list files
    echo   nlp show ip address
    echo.
    exit /b 0
)

REM Run the Python script with the input
python "%SCRIPT_PATH%" %*
if errorlevel 1 (
    echo.
    echo Error: Command failed. Check if your input was understood.
    exit /b 1
)

exit /b 0
