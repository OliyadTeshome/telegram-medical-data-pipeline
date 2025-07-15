#!/usr/bin/env python3
"""
Script to properly restart the FastAPI server with all fixes
"""

import os
import subprocess
import time
import signal
import sys

def kill_processes_on_port(port=8000):
    """Kill all processes using the specified port"""
    try:
        # Find processes using the port
        result = subprocess.run(
            ["netstat", "-ano"], 
            capture_output=True, 
            text=True
        )
        
        killed = False
        for line in result.stdout.split('\n'):
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    print(f"Killing process {pid} on port {port}")
                    subprocess.run(["taskkill", "/PID", pid, "/F"])
                    killed = True
                    time.sleep(1)
        
        if not killed:
            print(f"No processes found on port {port}")
        else:
            print(f"Killed processes on port {port}")
            
    except Exception as e:
        print(f"Warning: Could not kill processes: {e}")

def kill_all_python():
    """Kill all Python processes"""
    try:
        print("Killing all Python processes...")
        subprocess.run(["taskkill", "/F", "/IM", "python.exe"])
        time.sleep(2)
        print("All Python processes killed")
    except Exception as e:
        print(f"Warning: Could not kill Python processes: {e}")

def start_server():
    """Start the FastAPI server"""
    print("Starting FastAPI server with fixes...")
    print("=" * 50)
    
    try:
        # Start the server
        subprocess.run([
            sys.executable, "-m", "fastapi_app.main_new"
        ])
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    print("🔄 Restarting FastAPI Server")
    print("=" * 50)
    
    # Step 1: Kill all processes
    kill_processes_on_port(8000)
    kill_all_python()
    
    # Step 2: Wait a moment
    print("Waiting for processes to fully terminate...")
    time.sleep(3)
    
    # Step 3: Start the server
    start_server() 