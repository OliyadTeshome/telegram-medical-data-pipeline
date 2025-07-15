#!/usr/bin/env python3
"""
Startup script for the FastAPI application
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Start the FastAPI application"""
    
    # Configuration
    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    port = int(os.getenv("FASTAPI_PORT", "8000"))
    reload = os.getenv("FASTAPI_RELOAD", "true").lower() == "true"
    
    print("🚀 Starting Telegram Medical Data Analytics API")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🔄 Reload: {reload}")
    print(f"📖 Documentation: http://{host}:{port}/docs")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "main_new:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 