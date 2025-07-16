#!/usr/bin/env python3
"""
Minimal FastAPI test app to identify issues
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Test API")

@app.get("/")
async def root():
    return {"message": "Test API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("Starting test FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8001) 