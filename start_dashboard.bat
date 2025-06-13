@echo off
cd /d "C:\Users\kimyo\.docker\wsmcpservers"
echo Attempting to kill any process on port 8501...
FOR /F "tokens=5" %%T IN ('netstat -a -n -o ^| findstr :8501 ^| findstr LISTENING') DO (
    echo Found process: %%T
    taskkill /F /PID %%T
    echo Process killed.
)
echo Waiting for port to be released...
timeout /t 2 /nobreak >nul

echo Starting Williams Sonoma Dashboard...
echo.
"C:\Users\kimyo\.docker\wsmcpservers\.venv\Scripts\python.exe" -m streamlit run dashboard/app.py --server.port 8501 --logger.level error
pause
