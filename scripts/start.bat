@echo off
REM Windows batch script to start Google Business Analytics MCP servers

echo Starting Google Business Analytics MCP Servers...
echo.

REM Set environment variables
set PYTHONPATH=%~dp0..\src
set USE_MOCK_DATA=true
set DEBUG_MODE=false

REM Change to project directory
cd /d %~dp0..

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if required packages are installed
python -c "import mcp, pydantic, streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Required packages not installed. Run: pip install -e .[dev]
    pause
    exit /b 1
)

REM Start the services using the Python script
python scripts\start.py

pause
