#!/usr/bin/env python3
"""
Test suite for Windows CMD NLP Parser
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cmd_nlp import CMDNLPParser

def test_parser():
    """Run test cases"""
    parser = CMDNLPParser(dry_run=True)

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

    print("🧪 Running Tests")
    print("=" * 60)

    passed = 0
    failed = 0

    for input_text, expected_start, description in test_cases:
        command, pattern = parser.parse(input_text)

        if command and expected_start in command:
            print(f"✅ {description}")
            print(f"   Input: '{input_text}'")
            print(f"   Command: {command}")
            passed += 1
        else:
            print(f"❌ {description}")
            print(f"   Input: '{input_text}'")
            print(f"   Expected: {expected_start}")
            print(f"   Got: {command}")
            failed += 1
        print()

    print("=" * 60)
    print(f"📊 Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return 1

def test_edge_cases():
    """Test edge cases"""
    parser = CMDNLPParser(dry_run=True)

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

if __name__ == "__main__":
    result = test_parser()
    test_edge_cases()
    sys.exit(result)
