#!/usr/bin/env python3
"""
Test suite for Windows CMD/PowerShell NLP Parser
Cross-platform command generation tests
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cmd_nlp import CMDNLPParser, ShellType

def test_cmd_parser():
    """Run test cases for CMD commands"""
    parser = CMDNLPParser(dry_run=True, shell=ShellType.CMD)

    test_cases = [
        # (input, expected_command_start, description)
        ("go to downloads", "cd Downloads", "Navigation: go to directory"),
        ("go back", "cd ..", "Navigation: go back"),
        ("show current directory", "cd", "Navigation: show current directory"),
        ("where am i", "cd", "Navigation: where am i"),
        ("list files", "dir", "Files: list files"),
        ("list files sorted by size", "dir /O-S", "Files: list by size"),
        ("list files sorted by name", "dir /O-N", "Files: list by name"),
        ("create folder my-project", "mkdir my-project", "Files: create folder"),
        ("create directory test", "mkdir test", "Files: create directory"),
        ("delete file readme.txt", 'del "readme.txt"', "Files: delete file"),
        ("delete folder old-stuff", 'rmdir /s /q "old-stuff"', "Files: delete folder"),
        ("open notepad", "start notepad", "System: open program"),
        ("clear", "cls", "System: clear screen"),
        ("show disk space", "wmic logicaldisk", "System: disk space"),
        ("show ip address", "ipconfig", "System: IP address"),
        ("show my ip", "ipconfig", "System: my IP"),
        ("show date", "date /t", "System: show date"),
        ("show time", "time /t", "System: show time"),
        ("find files containing config", "dir /s /b | findstr", "Search: find files"),
        ("find text error in files", "findstr /s /i", "Search: find text"),
        ("copy file1.txt to backup", 'copy "file1.txt" "backup"', "Files: copy"),
        ("move file.txt to archive", 'move "file.txt" "archive"', "Files: move"),
        ("show running processes", "tasklist", "Process: list processes"),
        ("kill process notepad", 'taskkill /F /IM "notepad"', "Process: kill process"),
        ("set variable PATH to C:\\bin", "set PATH=C:\\bin", "Environment: set variable"),
        ("show variable PATH", "echo %PATH%", "Environment: show variable"),
        ("ping google.com", "ping google.com", "Network: ping"),
        ("trace route to google.com", "tracert google.com", "Network: trace route"),
        ("read file readme.txt", "type readme.txt", "Text: show file"),
        ("edit file config.txt", "notepad config.txt", "Text: edit file"),
        ("show file attributes readme.txt", "attrib readme.txt", "Properties: show attributes"),
        ("hide file secret.txt", "attrib +h secret.txt", "Properties: hide file"),
        ("show hidden files", "dir /ah", "Properties: list hidden"),
        ("ls", "dir", "Alias: ls"),
        ("pwd", "cd", "Alias: pwd"),
        ("mkdir testdir", "mkdir testdir", "Alias: mkdir"),
        ("rm file.txt", 'del "file.txt"', "Alias: rm"),
    ]

    print("🧪 Running CMD Tests")
    print("=" * 60)

    passed = 0
    failed = 0

    for input_text, expected_start, description in test_cases:
        command, pattern = parser.parse(input_text)

        if command and expected_start in command:
            print(f"✅ {description}")
            print(f"   Input: '{input_text}'")
            print(f"   CMD: {command}")
            passed += 1
        else:
            print(f"❌ {description}")
            print(f"   Input: '{input_text}'")
            print(f"   Expected: {expected_start}")
            print(f"   Got: {command}")
            failed += 1
        print()

    print("=" * 60)
    print(f"📊 CMD Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("\n🎉 All CMD tests passed!")
        return 0
    else:
        print(f"\n⚠️  {failed} CMD test(s) failed")
        return 1


def test_powershell_parser():
    """Run test cases for PowerShell commands"""
    parser = CMDNLPParser(dry_run=True, shell=ShellType.POWERSHELL)

    test_cases = [
        # (input, expected_command_part, description)
        ("go to downloads", "Set-Location", "Navigation: go to directory"),
        ("go back", "Set-Location ..", "Navigation: go back"),
        ("show current directory", "Get-Location", "Navigation: show current directory"),
        ("where am i", "Get-Location", "Navigation: where am i"),
        ("list files", "Get-ChildItem", "Files: list files"),
        ("list files sorted by size", "Sort-Object Length", "Files: list by size"),
        ("list files sorted by name", "Sort-Object Name", "Files: list by name"),
        ("create folder my-project", "New-Item -ItemType Directory", "Files: create folder"),
        ("create directory test", "New-Item -ItemType Directory", "Files: create directory"),
        ("delete file readme.txt", "Remove-Item", "Files: delete file"),
        ("delete folder old-stuff", "Remove-Item", "Files: delete folder"),
        ("open notepad", "Start-Process", "System: open program"),
        ("clear", "Clear-Host", "System: clear screen"),
        ("show disk space", "Get-PSDrive", "System: disk space"),
        ("show ip address", "Get-NetIPAddress", "System: IP address"),
        ("show my ip", "Get-NetIPAddress", "System: my IP"),
        ("show date", "Get-Date", "System: show date"),
        ("show time", "Get-Date", "System: show time"),
        ("find files containing config", "Get-ChildItem -Recurse", "Search: find files"),
        ("find text error in files", "Select-String", "Search: find text"),
        ("copy file1.txt to backup", "Copy-Item", "Files: copy"),
        ("move file.txt to archive", "Move-Item", "Files: move"),
        ("show running processes", "Get-Process", "Process: list processes"),
        ("kill process notepad", "Stop-Process", "Process: kill process"),
        ("set variable PATH to C:\\bin", "$env:PATH", "Environment: set variable"),
        ("show variable PATH", "$env:PATH", "Environment: show variable"),
        ("ping google.com", "Test-Connection", "Network: ping"),
        ("trace route to google.com", "Test-NetConnection", "Network: trace route"),
        ("read file readme.txt", "Get-Content", "Text: show file"),
        ("edit file config.txt", "notepad.exe", "Text: edit file"),
        ("show file attributes readme.txt", "Get-ItemProperty", "Properties: show attributes"),
        ("hide file secret.txt", "[System.IO.FileAttributes]::Hidden", "Properties: hide file"),
        ("show hidden files", "Get-ChildItem -Hidden", "Properties: list hidden"),
        ("ls", "Get-ChildItem", "Alias: ls"),
        ("pwd", "Get-Location", "Alias: pwd"),
        ("mkdir testdir", "New-Item -ItemType Directory", "Alias: mkdir"),
        ("rm file.txt", "Remove-Item", "Alias: rm"),
    ]

    print("\n🧪 Running PowerShell Tests")
    print("=" * 60)

    passed = 0
    failed = 0

    for input_text, expected_part, description in test_cases:
        command, pattern = parser.parse(input_text)

        if command and expected_part in command:
            print(f"✅ {description}")
            print(f"   Input: '{input_text}'")
            print(f"   PowerShell: {command}")
            passed += 1
        else:
            print(f"❌ {description}")
            print(f"   Input: '{input_text}'")
            print(f"   Expected part: {expected_part}")
            print(f"   Got: {command}")
            failed += 1
        print()

    print("=" * 60)
    print(f"📊 PowerShell Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("\n🎉 All PowerShell tests passed!")
        return 0
    else:
        print(f"\n⚠️  {failed} PowerShell test(s) failed")
        return 1


def test_dual_shell_output():
    """Test that both shells can produce commands for the same input"""
    parser = CMDNLPParser(dry_run=True, shell=ShellType.CMD)

    print("\n🧪 Testing Dual Shell Output")
    print("=" * 60)

    test_inputs = [
        "go to downloads",
        "list files",
        "delete file test.txt",
        "show ip address",
        "ping google.com",
    ]

    all_passed = True
    for input_text in test_inputs:
        results = parser.parse_all(input_text)
        
        if ShellType.CMD in results and ShellType.POWERSHELL in results:
            cmd_cmd, _ = results[ShellType.CMD]
            ps_cmd, _ = results[ShellType.POWERSHELL]
            print(f"✅ '{input_text}'")
            print(f"   CMD:        {cmd_cmd}")
            print(f"   PowerShell: {ps_cmd}")
        else:
            print(f"❌ '{input_text}' - Missing shell output")
            all_passed = False
        print()

    print("=" * 60)
    if all_passed:
        print("🎉 All dual shell tests passed!")
    return 0 if all_passed else 1


def test_edge_cases():
    """Test edge cases"""
    parser = CMDNLPParser(dry_run=True, shell=ShellType.CMD)

    print("\n🧪 Testing Edge Cases")
    print("=" * 60)

    edge_cases = [
        ("", "Empty input"),
        ("go to", "Incomplete command"),
        ("xyz123", "Unrecognized command"),
        ("delete file", "Missing filename"),
    ]

    for input_text, description in edge_cases:
        command, pattern = parser.parse(input_text)
        if command is None:
            print(f"✅ {description}: Correctly returned None")
        else:
            print(f"⚠️  {description}: Unexpected command '{command}'")

    print("=" * 60)


def test_shell_detection():
    """Test shell detection"""
    print("\n🧪 Testing Shell Detection")
    print("=" * 60)
    
    # Test explicit shell selection
    cmd_parser = CMDNLPParser(dry_run=True, shell=ShellType.CMD)
    ps_parser = CMDNLPParser(dry_run=True, shell=ShellType.POWERSHELL)
    
    print(f"✅ CMD parser shell: {cmd_parser.shell_name}")
    print(f"✅ PowerShell parser shell: {ps_parser.shell_name}")
    
    # Test auto-detection
    auto_parser = CMDNLPParser(dry_run=True, shell=ShellType.AUTO)
    print(f"✅ Auto-detected shell: {auto_parser.shell_name}")
    
    print("=" * 60)
    return 0


if __name__ == "__main__":
    result1 = test_cmd_parser()
    result2 = test_powershell_parser()
    result3 = test_dual_shell_output()
    test_edge_cases()
    result4 = test_shell_detection()
    
    total_failed = result1 + result2 + result3 + result4
    sys.exit(total_failed)
