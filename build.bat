@echo off
REM Build script for Honeygotchi executable (Windows)

echo Building Honeygotchi executable...

REM Check if PyInstaller is installed
where pyinstaller >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Create build directory
if not exist "dist" mkdir dist

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist\honeygotchi.exe" del /q "dist\honeygotchi.exe"

REM Build executable
echo Building executable...
pyinstaller honeygotchi.spec

REM Copy config file to dist if it exists
if exist "config.yaml" (
    echo Copying config.yaml to dist...
    copy config.yaml dist\
)

echo Build complete! Executable is in: dist\honeygotchi.exe
