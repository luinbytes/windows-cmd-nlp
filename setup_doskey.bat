@echo off
REM Install DOSKEY macros for natural language CMD
REM This enables typing natural language without 'nlp' prefix

setlocal enabledelayedexpansion

echo ==========================================
echo DOSKEY Alias Setup for NLP
echo ==========================================
echo.
echo This will create DOSKEY macros so you can type:
echo   ls           -^> nlp list files
echo   go downloads -^> nlp go to downloads
echo   find *.txt   -^> nlp find files *.txt
echo.
echo Without typing 'nlp' first!
echo.

REM Check if running as admin (required for AutoRun)
net session >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] Administrator privileges required for AutoRun setup
    echo [!] Please right-click and "Run as Administrator"
    pause
    exit /b 1
)

set "INSTALL_DIR=%~dp0"
set "MACROS_FILE=%INSTALL_DIR%doskey_macros.bat"

REM Verify macros file exists
if not exist "%MACROS_FILE%" (
    echo [!] ERROR: doskey_macros.bat not found
    echo [!] Expected at: %MACROS_FILE%
    pause
    exit /b 1
)

echo [+] Found macros file: %MACROS_FILE%
echo.

REM Add AutoRun registry entry for Command Processor
echo [+] Setting up AutoRun in registry...
reg add "HKLM\SOFTWARE\Microsoft\Command Processor" /v AutoRun /t REG_EXPAND_SZ /d "%MACROS_FILE%" /f >nul 2>nul
if !errorlevel! equ 0 (
    echo [+] Successfully registered AutoRun (system-wide)
) else (
    echo [!] Failed to set system-wide AutoRun
    echo [+] Trying user-level AutoRun...
    reg add "HKCU\SOFTWARE\Microsoft\Command Processor" /v AutoRun /t REG_EXPAND_SZ /d "%MACROS_FILE%" /f >nul 2>nul
    if !errorlevel! equ 0 (
        echo [+] Successfully registered AutoRun (user-level)
    ) else (
        echo [!] Failed to register AutoRun
        pause
        exit /b 1
    )
)

echo.
echo ==========================================
echo DOSKEY Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Close ALL CMD windows completely
echo 2. Open a new CMD window
echo 3. Try typing natural language directly:
echo.
echo    ls              (lists files)
echo    go downloads    (changes to downloads folder)
echo    create folder test
echo    find *.txt
echo    show ip
echo.
echo Available shortcuts:
echo   ls, ll, dir     - List files
echo   go, cd          - Navigate (go to...)
echo   back, up        - Go back/up directories
echo   find            - Find files
echo   create, make    - Create files/folders
echo   delete, remove  - Delete files/folders
echo   show            - Show system info
echo   open, run       - Open applications
echo   clear           - Clear screen
echo   status          - Git status
echo   commit          - Git commit
echo.
echo To remove DOSKEY macros, run: setup_doskey_uninstall.bat
pause