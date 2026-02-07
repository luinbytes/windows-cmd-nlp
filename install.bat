@echo off
REM Install Windows CMD NLP Parser to PATH
REM Run as Administrator for system-wide install

echo ==========================================
echo Windows CMD NLP Parser - Installer
echo ==========================================
echo.

set "INSTALL_DIR=%~dp0"

REM Check if running as admin
net session > nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Not running as Administrator
    echo [!] Installing for current user only
    echo.
    set "TARGET=USER"
) else (
    echo [+] Running as Administrator
    echo [+] Can install system-wide
    echo.
    set "TARGET=SYSTEM"
)

echo Installation directory: %INSTALL_DIR%
echo.

REM Add to PATH
if "%TARGET%"=="SYSTEM" (
    echo [+] Adding to system PATH...
    setx /M PATH "%PATH%;%INSTALL_DIR%" > nul 2>&1
    if %errorlevel% equ 0 (
        echo [+] Successfully added to system PATH
    ) else (
        echo [!] Failed to add to system PATH
        echo [!] Attempting user PATH...
        goto :user_install
    )
) else (
    :user_install
    echo [+] Adding to user PATH...
    setx PATH "%PATH%;%INSTALL_DIR%" > nul 2>&1
    if %errorlevel% equ 0 (
        echo [+] Successfully added to user PATH
    ) else (
        echo [!] Failed to add to PATH
        echo [!] You may need to add manually:
        echo     %INSTALL_DIR%
    )
)

echo.
echo ==========================================
echo Installation Complete!
echo ==========================================
echo.
echo Usage:
echo     nlp [command]
echo.
echo Examples:
echo     nlp go to downloads
echo     nlp create folder my-project
echo     nlp list files
echo.
echo Note: Restart CMD for PATH changes to take effect
echo.
pause
