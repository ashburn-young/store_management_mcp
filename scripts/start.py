#!/usr/bin/env python3
"""Startup script for the Google Business Analytics MCP servers."""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path
from typing import List


class ServerManager:
    """Manages MCP server processes."""
    
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.project_root = Path(__file__).parent.parent
        
    def start_collection_agent(self) -> subprocess.Popen:
        """Start the collection agent server."""
        print("🚀 Starting Collection Agent Server...")
        
        env = os.environ.copy()
        env.update({
            "PYTHONPATH": str(self.project_root / "src"),
            "USE_MOCK_DATA": "true",
            "DEBUG_MODE": "false"
        })
        
        process = subprocess.Popen(
            [sys.executable, "-m", "google_business_analytics.collection_agent.server"],
            cwd=self.project_root,
            env=env
        )
        
        self.processes.append(process)
        print(f"✅ Collection Agent started (PID: {process.pid})")
        return process
    
    def start_aggregation_agent(self) -> subprocess.Popen:
        """Start the aggregation agent server."""
        print("🚀 Starting Aggregation Agent Server...")
        
        env = os.environ.copy()
        env.update({
            "PYTHONPATH": str(self.project_root / "src"),
            "USE_MOCK_DATA": "true", 
            "DEBUG_MODE": "false"
        })
        
        process = subprocess.Popen(
            [sys.executable, "-m", "google_business_analytics.aggregation_agent.server"],
            cwd=self.project_root,
            env=env
        )
        
        self.processes.append(process)
        print(f"✅ Aggregation Agent started (PID: {process.pid})")
        return process
    
    def start_dashboard(self) -> subprocess.Popen:
        """Start the Streamlit dashboard."""
        print("🚀 Starting Streamlit Dashboard...")
        
        env = os.environ.copy()
        env.update({
            "PYTHONPATH": str(self.project_root / "src")
        })
        
        process = subprocess.Popen(
            ["streamlit", "run", "dashboard/app.py", "--server.port", "8501"],
            cwd=self.project_root,
            env=env
        )
        
        self.processes.append(process)
        print(f"✅ Dashboard started (PID: {process.pid})")
        print("📊 Dashboard available at: http://localhost:8501")
        return process
    
    def stop_all(self):
        """Stop all running processes."""
        print("\n🛑 Stopping all services...")
        
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ Process {process.pid} stopped")
            except subprocess.TimeoutExpired:
                print(f"⚠️  Force killing process {process.pid}")
                process.kill()
            except Exception as e:
                print(f"❌ Error stopping process {process.pid}: {e}")
        
        self.processes.clear()
        print("✅ All services stopped")
    
    def start_all(self):
        """Start all services."""
        print("🌟 Starting Google Business Analytics MCP Servers")
        print("=" * 50)
        
        try:
            # Start MCP servers
            self.start_collection_agent()
            time.sleep(2)  # Give it time to start
            
            self.start_aggregation_agent() 
            time.sleep(2)  # Give it time to start
            
            # Start dashboard
            self.start_dashboard()
            
            print("\n🎉 All services started successfully!")
            print("=" * 50)
            print("📡 Collection Agent: Running")
            print("🔄 Aggregation Agent: Running") 
            print("📊 Dashboard: http://localhost:8501")
            print("=" * 50)
            print("\n💡 Press Ctrl+C to stop all services")
            
            # Wait for interrupt
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n🔄 Received interrupt signal...")
            self.stop_all()
        except Exception as e:
            print(f"\n❌ Error starting services: {e}")
            self.stop_all()
            sys.exit(1)


def main():
    """Main entry point."""
    manager = ServerManager()
    
    # Set up signal handlers
    def signal_handler(signum, frame):
        manager.stop_all()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "collection":
            manager.start_collection_agent()
        elif command == "aggregation":
            manager.start_aggregation_agent()
        elif command == "dashboard":
            manager.start_dashboard()
        elif command == "stop":
            manager.stop_all()
        else:
            print("Usage: python start.py [collection|aggregation|dashboard|stop]")
            print("       python start.py  # Start all services")
            sys.exit(1)
    else:
        manager.start_all()


if __name__ == "__main__":
    main()
