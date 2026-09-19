@echo off
chcp 65001 >nul

REM Check if virtual environment exists
if not exist venv\Scripts\python.exe (
    echo Virtual environment not found.
    echo Please run install_deps.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment and run the app
call venv\Scripts\activate
uvicorn app.main:app --reload
