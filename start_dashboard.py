#!/usr/bin/env python3
"""Simple script to start the Streamlit dashboard."""

import subprocess
import sys
import os
import platform
import socket
import signal
import time

def kill_process_on_port(port):
    """Kill any process running on the specified port."""
    print(f"Checking for processes on port {port}...")
    
    if platform.system() == "Windows":
        try:
            # Windows approach
            netstat_output = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True).decode()
            if netstat_output:
                lines = netstat_output.strip().split("\n")
                for line in lines:
                    if "LISTENING" in line:
                        pid = line.strip().split()[-1]
                        print(f"Found process with PID {pid} on port {port}. Killing it...")
                        subprocess.call(f"taskkill /F /PID {pid}", shell=True)
                        print(f"Process with PID {pid} killed.")
                        time.sleep(1)  # Give it a moment to close
        except subprocess.CalledProcessError:
            print(f"No process found on port {port}.")
    else:
        # Linux/Mac approach
        try:
            cmd = f"lsof -i :{port} -t"
            pid = subprocess.check_output(cmd, shell=True).decode().strip()
            if pid:
                print(f"Found process with PID {pid} on port {port}. Killing it...")
                os.kill(int(pid), signal.SIGKILL)
                print(f"Process with PID {pid} killed.")
                time.sleep(1)  # Give it a moment to close
        except:
            print(f"No process found on port {port}.")

def main():
    """Start the Streamlit dashboard."""
    # Kill any process on port 8501
    kill_process_on_port(8501)
    
    # Change to the project directory
    os.chdir(r"C:\Users\kimyo\.docker\wsmcpservers")
    
    # Get the Python executable from the virtual environment
    python_exe = r"C:\Users\kimyo\.docker\wsmcpservers\.venv\Scripts\python.exe"
    
    # Run Streamlit
    cmd = [
        python_exe, "-m", "streamlit", "run", 
        "dashboard/app.py", "--server.port", "8501",
        "--logger.level", "error"
    ]
    
    print("Starting Streamlit dashboard...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nDashboard stopped by user.")
    except Exception as e:
        print(f"Error starting dashboard: {e}")

if __name__ == "__main__":
    main()
