@echo off
REM Git Commands Helper for ISP Project
REM This file makes it easier to run Git commands on Windows

echo Git Commands Helper for ISP Project
echo ===================================
echo.
echo Available commands:
echo 1. git-status    - Check repository status
echo 2. git-add       - Add all files to staging
echo 3. git-commit    - Commit changes with message
echo 4. git-push      - Push to remote repository
echo 5. git-log       - View commit history
echo 6. git-branch    - List branches
echo.
echo Usage: git-commands.bat [command] [optional-message]
echo Example: git-commands.bat commit "Updated user interface"
echo.

if "%1"=="status" (
    "C:\Program Files\Git\bin\git.exe" status
) else if "%1"=="add" (
    "C:\Program Files\Git\bin\git.exe" add .
    echo All files added to staging area.
) else if "%1"=="commit" (
    if "%2"=="" (
        "C:\Program Files\Git\bin\git.exe" commit -m "Update"
    ) else (
        "C:\Program Files\Git\bin\git.exe" commit -m "%2"
    )
    echo Changes committed successfully.
) else if "%1"=="push" (
    "C:\Program Files\Git\bin\git.exe" push
) else if "%1"=="log" (
    "C:\Program Files\Git\bin\git.exe" log --oneline -10
) else if "%1"=="branch" (
    "C:\Program Files\Git\bin\git.exe" branch -a
) else (
    echo Invalid command. Use one of: status, add, commit, push, log, branch
) 