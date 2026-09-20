@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo     GROWTH OS : GITHUB CLOUD BUILD TRIGGER
echo ===================================================
echo.

where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] Git not found in PATH yet. Checking standard install path...
    if exist "C:\Program Files\Git\cmd\git.exe" (
        set "PATH=%PATH%;C:\Program Files\Git\cmd"
    ) else (
        echo [-] Git is still finishing installation. Please wait a moment and try again.
        pause
        exit /b 1
    )
)

echo [+] Initializing Git repository...
git init
git config --global init.defaultBranch main

echo [+] Staging all Growth OS files...
git add .
git commit -m "Growth OS v1.0.0 Release - Cloud ISO Build"

echo.
set /p REPO_URL="Enter your GitHub Repository URL (e.g. https://github.com/YourUsername/GrowthOS.git): "

if "%REPO_URL%"=="" (
    echo [-] No URL entered. Aborting.
    pause
    exit /b 1
)

git remote remove origin >nul 2>nul
git remote add origin %REPO_URL%
git branch -M main

echo [+] Pushing to GitHub...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ===================================================
    echo [OK] SUCCESS! Pushed to GitHub!
    echo.
    echo Now open your browser to:
    echo   %REPO_URL%/actions
    echo.
    echo Watch the 'Build Growth OS Bootable ISO' action.
    echo In ~10 minutes, your GrowthOS-x86_64.iso will be ready to download!
    echo ===================================================
) else (
    echo.
    echo [-] Push failed. Make sure your GitHub repository is created and you have permissions.
)

pause
