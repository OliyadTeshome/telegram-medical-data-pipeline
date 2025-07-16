#!/usr/bin/env python3
"""
Startup script for FastAPI server with proper error handling
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import psycopg2
        print("✓ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def check_database_connection():
    """Test database connection"""
    try:
        from fastapi_app.database import engine
        from sqlalchemy import text
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✓ Database connection successful")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {str(e)}")
        print("Please ensure:")
        print("1. PostgreSQL is running")
        print("2. Database 'medical_data' exists")
        print("3. User 'postgres' with password 'your_password_here' has access")
        return False

def kill_existing_processes():
    """Kill any existing Python processes on port 8000"""
    try:
        # On Windows, use netstat to find processes
        result = subprocess.run(
            ["netstat", "-ano"], 
            capture_output=True, 
            text=True
        )
        
        for line in result.stdout.split('\n'):
            if ':8000' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    print(f"Killing process {pid} on port 8000")
                    subprocess.run(["taskkill", "/PID", pid, "/F"])
                    time.sleep(1)
    except Exception as e:
        print(f"Warning: Could not kill existing processes: {e}")

def start_server():
    """Start the FastAPI server"""
    print("Starting FastAPI server...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Check database connection
    if not check_database_connection():
        return False
    
    # Kill existing processes
    kill_existing_processes()
    
    # Start the server
    try:
        print("Starting server on http://localhost:8000")
        print("API documentation available at http://localhost:8000/docs")
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Run the server
        subprocess.run([
            sys.executable, "-m", "fastapi_app.main_new"
        ])
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("FastAPI Medical Data Analytics Server")
    print("=" * 50)
    
    success = start_server()
    
    if not success:
        print("\nFailed to start server. Please check the errors above.")
        sys.exit(1) 