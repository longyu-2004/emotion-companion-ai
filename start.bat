@echo off
chcp 65001 >nul
echo ============================================
echo   情感陪护虚拟数字人系统 - 启动脚本
echo ============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

:: Install dependencies
echo [1/3] Installing dependencies...
pip install -r requirements.txt -q

:: Check API key
if "%LLM_API_KEY%"=="" (
    echo.
    echo [WARN] LLM_API_KEY not set!
    echo Please set it before running:
    echo   set LLM_API_KEY=your-api-key
    echo   set LLM_API_BASE=https://api.deepseek.com
    echo   set LLM_MODEL=deepseek-chat
    echo.
    echo Or edit config.py to set default values.
    echo.
)

:: Start server
echo [2/3] Initializing database...
echo [3/3] Starting server...
echo.
echo ============================================
echo   Open: http://127.0.0.1:5000
echo   Press Ctrl+C to stop
echo ============================================
echo.
python app.py
pause
