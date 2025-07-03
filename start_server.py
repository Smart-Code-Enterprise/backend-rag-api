#!/usr/bin/env python3
"""
Startup script for the RAG Backend API
"""
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Get configuration from environment variables with defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    print(f"Starting RAG Backend API...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Log Level: {log_level}")
    print(f"API Documentation: http://{host}:{port}/docs")
    print(f"Interactive API: http://{host}:{port}/redoc")
    
    # Start the server
    uvicorn.run(
        "fastapi_app:app",
        host=host,
        port=port,
        reload=True,  # Enable auto-reload during development
        log_level=log_level
    )
