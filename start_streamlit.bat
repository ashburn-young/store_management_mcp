@echo off
cd /d "c:\Users\kimyo\.docker\wsmcpservers"
echo Starting Williams Sonoma Store Analytics Dashboard...
echo Dashboard will be available at: http://localhost:8501
python -m streamlit run dashboard/app.py --server.port 8501 --server.headless true
pause
