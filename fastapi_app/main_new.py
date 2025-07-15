from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from dotenv import load_dotenv

from .database import get_db
from . import crud, schemas, models

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Telegram Medical Data Analytics API",
    description="API for serving analytics endpoints from medical data extracted from Telegram channels",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Telegram Medical Data Analytics API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    }

# Analytics Endpoints

@app.get("/api/reports/top-products", response_model=List[schemas.TopProductResponse])
async def get_top_products(
    limit: int = Query(default=10, ge=1, le=100, description="Number of top products to return"),
    db: Session = Depends(get_db)
):
    """
    Get most frequently mentioned products from medical insights.
    
    Returns the top products mentioned across all channels with their mention counts,
    channels where they were mentioned, and last mention date.
    """
    try:
        products = crud.get_top_products(db, limit=limit)
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving top products: {str(e)}")

@app.get("/api/channels/{channel_name}/activity", response_model=List[schemas.ChannelActivityResponse])
async def get_channel_activity(
    channel_name: str,
    period: str = Query(default="daily", regex="^(daily|weekly|monthly)$", description="Activity period"),
    limit: int = Query(default=30, ge=1, le=365, description="Number of periods to return"),
    db: Session = Depends(get_db)
):
    """
    Get channel activity by period (daily/weekly/monthly).
    
    Returns activity metrics including message count, medical content count,
    and average sentiment for the specified channel over time.
    """
    try:
        # Verify channel exists
        channel = crud.get_channel_by_name(db, channel_name)
        if not channel:
            raise HTTPException(status_code=404, detail=f"Channel '{channel_name}' not found")
        
        activity = crud.get_channel_activity(db, channel_name, period, limit)
        return activity
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving channel activity: {str(e)}")

@app.get("/api/search/messages", response_model=schemas.SearchResponse)
async def search_messages(
    query: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(default=50, ge=1, le=100, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """
    Full-text search across messages.
    
    Searches message text, channel names, and sender usernames.
    Returns results sorted by relevance score.
    """
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="Search query cannot be empty")
        
        results = crud.search_messages(db, query, limit)
        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching messages: {str(e)}")

# Additional Analytics Endpoints

@app.get("/api/statistics", response_model=schemas.StatisticsResponse)
async def get_statistics(db: Session = Depends(get_db)):
    """
    Get comprehensive analytics statistics.
    
    Returns overall pipeline statistics including message counts,
    channel information, sentiment analysis, and distributions.
    """
    try:
        stats = crud.get_statistics(db)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")

@app.get("/api/channels", response_model=List[schemas.ChannelResponse])
async def get_channels(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Get all channels with pagination.
    """
    try:
        channels = crud.get_channels(db, skip=skip, limit=limit)
        return channels
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving channels: {str(e)}")

@app.get("/api/messages", response_model=List[schemas.MessageResponse])
async def get_messages(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of records to return"),
    channel_name: Optional[str] = Query(default=None, description="Filter by channel name"),
    db: Session = Depends(get_db)
):
    """
    Get messages with optional channel filtering and pagination.
    """
    try:
        messages = crud.get_messages(db, skip=skip, limit=limit, channel_name=channel_name)
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving messages: {str(e)}")

@app.get("/api/medical-insights", response_model=List[schemas.MedicalInsightResponse])
async def get_medical_insights(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of records to return"),
    channel_name: Optional[str] = Query(default=None, description="Filter by channel name"),
    db: Session = Depends(get_db)
):
    """
    Get medical insights with optional channel filtering and pagination.
    """
    try:
        if channel_name:
            insights = crud.get_medical_insights_by_channel(db, channel_name, skip, limit)
        else:
            insights = crud.get_medical_insights(db, skip, limit)
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving medical insights: {str(e)}")

@app.get("/api/messages/{message_id}", response_model=schemas.MessageResponse)
async def get_message_by_id(message_id: int, db: Session = Depends(get_db)):
    """
    Get a specific message by ID.
    """
    try:
        message = crud.get_message_by_id(db, message_id)
        if not message:
            raise HTTPException(status_code=404, detail=f"Message with ID {message_id} not found")
        return message
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving message: {str(e)}")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Resource not found", "detail": str(exc)}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "detail": str(exc)}

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment variables
    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    port = int(os.getenv("FASTAPI_PORT", "8000"))
    reload = os.getenv("FASTAPI_RELOAD", "true").lower() == "true"
    
    uvicorn.run(
        "fastapi_app.main_new:app",
        host=host,
        port=port,
        reload=reload
    ) 