@echo off
chcp 65001 >nul
echo Installing dependencies for Data Web Application...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not properly installed or not in PATH.
    echo.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    echo If you installed Python from Microsoft Store, please:
    echo 1. Uninstall it from Settings > Apps
    echo 2. Download and install from https://www.python.org/downloads/
    echo 3. Make sure to check "Add Python to PATH"
    pause
    exit /b 1
)

echo Found Python: 
python --version
echo.

REM Create virtual environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment and install dependencies
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Dependencies installed successfully!
echo.
echo To run the application:
echo   call venv\Scripts\activate
echo   uvicorn app.main:app --reload
pause
