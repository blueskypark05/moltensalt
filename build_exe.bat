@echo off
cd /d "%~dp0"

where pyinstaller >nul 2>&1
if errorlevel 1 (
    python -m PyInstaller --noconfirm --clean program.spec
) else (
    pyinstaller --noconfirm --clean program.spec
)

if errorlevel 1 (
    echo.
    echo Build failed. Check the error message above.
    pause
    exit /b 1
)

echo.
echo Build completed: dist\moltensalt.exe
pause
