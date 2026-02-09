@echo off
REM Install Windows CMD NLP Parser to PATH
REM Usage: Run install.bat (as Administrator for system-wide install)

setlocal enabledelayedexpansion

echo ==========================================
echo Windows CMD NLP Parser - Installer
echo ==========================================
echo.

set "INSTALL_DIR=%~dp0"

REM Verify installation directory
if not exist "%INSTALL_DIR%cmd_nlp.py" (
    echo [!] ERROR: cmd_nlp.py not found in current directory
    echo [!] Please run this installer from the project folder
    pause
    exit /b 1
)

if not exist "%INSTALL_DIR%nlp.bat" (
    echo [!] ERROR: nlp.bat not found in current directory
    echo [!] Please run this installer from the project folder
    pause
    exit /b 1
)

REM Check if Python is available
python --version > nul 2>&1
if errorlevel 1 (
    echo [!] ERROR: Python not found in PATH
    echo [!] Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [+] Python found
echo.

REM Check if running as admin
net session > nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Not running as Administrator
    echo [!] Will install for current user only
    echo.
    set "TARGET=USER"
) else (
    echo [+] Running as Administrator
    echo [+] Can install system-wide
    echo.
    choice /C YN /M "Install for all users (system-wide)"
    if errorlevel 2 (
        set "TARGET=USER"
        echo [+] Installing for current user only
    ) else (
        set "TARGET=SYSTEM"
        echo [+] Installing system-wide
    )
    echo.
)

echo Installation directory: %INSTALL_DIR%
echo.

REM Add to PATH
if "%TARGET%"=="SYSTEM" (
    echo [+] Adding to system PATH...
    setx /M PATH "%PATH%;%INSTALL_DIR%" > nul 2>&1
    if !errorlevel! equ 0 (
        echo [+] Successfully added to system PATH
    ) else (
        echo [!] Failed to add to system PATH
        echo [!] Falling back to user PATH...
        set "TARGET=USER"
    )
)

if "%TARGET%"=="USER" (
    echo [+] Adding to user PATH...
    setx PATH "%PATH%;%INSTALL_DIR%" > nul 2>&1
    if !errorlevel! equ 0 (
        echo [+] Successfully added to user PATH
    ) else (
        echo [!] Failed to add to PATH automatically
        echo [!] Please add this directory manually to your PATH:
        echo.
        echo     %INSTALL_DIR%
        echo.
    )
)

echo.
echo ==========================================
echo Installation Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Close and reopen CMD
if "%TARGET%"=="SYSTEM" (
    echo 2. You can now use 'nlp' from any CMD window
) else (
    echo 2. You can now use 'nlp' from your user CMD
)
echo.
echo Usage:
echo     nlp [natural language command]
echo.
echo Examples:
echo     nlp go to downloads
echo     nlp create folder my-project
echo     nlp list files
echo     nlp show ip address
echo.
pause
