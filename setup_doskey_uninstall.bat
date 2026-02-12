@echo off
REM Uninstall DOSKEY macros for natural language CMD

setlocal enabledelayedexpansion

echo ==========================================
echo DOSKEY Alias Removal
echo ==========================================
echo.

REM Check if running as admin
net session >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] Administrator privileges recommended
    echo [!] Some entries may not be removable without admin
    echo.
)

echo [+] Removing AutoRun registry entries...

REM Remove system-wide AutoRun
reg delete "HKLM\SOFTWARE\Microsoft\Command Processor" /v AutoRun /f >nul 2>nul
if !errorlevel! equ 0 (
    echo [+] Removed system-wide AutoRun
) else (
    echo [ ] No system-wide AutoRun found
)

REM Remove user-level AutoRun
reg delete "HKCU\SOFTWARE\Microsoft\Command Processor" /v AutoRun /f >nul 2>nul
if !errorlevel! equ 0 (
    echo [+] Removed user-level AutoRun
) else (
    echo [ ] No user-level AutoRun found
)

echo.
echo ==========================================
echo DOSKEY Aliases Removed!
echo ==========================================
echo.
echo Close and reopen CMD windows for changes to take effect.
echo.
pause