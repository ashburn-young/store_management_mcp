#!/usr/bin/env python3
"""Demo script to launch the Google Business Analytics dashboard."""

import os
import sys
import subprocess
import time
from pathlib import Path

def main():
    """Run the demo by launching all required components."""
    # Get the project root directory
    project_dir = Path(__file__).parent.parent
    
    print("🚀 Starting Google Business Analytics Demo")
    
    # Set environment variables
    os.environ["USE_MOCK_DATA"] = "true"
    
    print("\n📊 Starting Streamlit dashboard...")
    # Start the Streamlit dashboard
    dashboard_cmd = ["streamlit", "run", str(project_dir / "dashboard" / "app.py")]
    
    try:
        # Use subprocess.Popen to start process non-blocking
        dashboard_process = subprocess.Popen(
            dashboard_cmd, 
            cwd=str(project_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print("✅ Streamlit dashboard started")
        print("🌐 Open your browser to http://localhost:8501")
        
        # Wait for user to exit
        print("\n⏳ Press Ctrl+C to stop the demo...")
        while True:
            # Check if dashboard is still running
            if dashboard_process.poll() is not None:
                print("❌ Dashboard process exited unexpectedly")
                break
                
            # Read output from the dashboard process
            stdout_line = dashboard_process.stdout.readline()
            if stdout_line:
                print(f"Dashboard: {stdout_line.strip()}")
                
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping demo...")
    finally:
        # Clean up processes
        if 'dashboard_process' in locals() and dashboard_process.poll() is None:
            print("Stopping dashboard...")
            dashboard_process.terminate()
            dashboard_process.wait(timeout=5)
            
    print("✨ Demo completed")

if __name__ == "__main__":
    main()
