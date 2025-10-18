@echo off
setlocal
chcp 65001 >nul

pushd "%~dp0"
title Thumb Points Mall - Backend Service

echo ====================================
echo Thumb Points Mall - Backend Startup
echo ====================================
echo.

if exist venv (
    echo [OK] Virtual environment detected, activating...
    call venv\Scripts\activate
) else (
    echo [!] Virtual environment not found, using system Python
)

python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python not found.
    echo [!] Please install Python 3.8+ and ensure it is in PATH.
    pause
    exit /b 1
)

echo.
echo [*] Checking Python dependencies...

python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [!] Dependencies missing, installing from requirements.txt...
    echo.
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    echo.
    if errorlevel 1 (
        echo [X] Failed to install dependencies.
        echo [!] Please check your network connection or install manually: pip install -r requirements.txt
        pause
        exit /b 1
    )
) else (
    echo [OK] Dependencies are already installed.
)

echo.
echo ====================================
echo   Backend URL: http://localhost:5000
echo   Press Ctrl+C to stop the server
echo ====================================
echo.

python app.py
if errorlevel 1 (
    echo.
    echo [X] Application failed to start. Please review the logs above.
    pause
    exit /b 1
)

echo.
echo [*] Backend server stopped.
pause

popd
endlocal
