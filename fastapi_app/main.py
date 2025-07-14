from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime, timedelta

from src.utils.config import get_config
from src.loader.postgres_loader import PostgresLoader

app = FastAPI(
    title="Telegram Medical Data Pipeline API",
    description="API for serving insights from medical data extracted from Telegram channels",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class MessageResponse(BaseModel):
    id: int
    message_id: int
    chat_title: str
    sender_username: str
    message_text: str
    message_date: str
    has_media: bool
    media_type: Optional[str] = None

class EnrichedMessageResponse(BaseModel):
    id: int
    raw_message_id: int
    medical_entities: Dict[str, Any]
    sentiment_score: Optional[float]
    urgency_level: Optional[str]
    processed_at: str

class ImageAnalysisResponse(BaseModel):
    id: int
    message_id: int
    image_path: str
    detection_results: Dict[str, Any]
    confidence_scores: Dict[str, Any]
    processed_at: str

class StatisticsResponse(BaseModel):
    total_messages: int
    total_images: int
    medical_content_count: int
    average_sentiment: float
    urgency_distribution: Dict[str, int]
    top_channels: List[Dict[str, Any]]

# Dependency
def get_db():
    config = get_config()
    loader = PostgresLoader()
    loader.connect()
    try:
        yield loader
    finally:
        loader.disconnect()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Telegram Medical Data Pipeline API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    config = get_config()
    validation = config.validate_config()
    
    return {
        "status": "healthy" if all(validation.values()) else "unhealthy",
        "components": validation,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/messages", response_model=List[MessageResponse])
async def get_messages(
    limit: int = 100,
    offset: int = 0,
    channel: Optional[str] = None,
    db: PostgresLoader = Depends(get_db)
):
    """Get raw messages from the database"""
    try:
        messages = db.get_raw_messages(limit=limit)
        
        # Apply filters
        if channel:
            messages = [msg for msg in messages if msg.get('chat_title', '').lower() == channel.lower()]
        
        # Apply pagination
        messages = messages[offset:offset + limit]
        
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving messages: {str(e)}")

@app.get("/messages/enriched", response_model=List[EnrichedMessageResponse])
async def get_enriched_messages(
    limit: int = 100,
    offset: int = 0,
    db: PostgresLoader = Depends(get_db)
):
    """Get enriched messages with medical analysis"""
    try:
        if not db.conn:
            db.connect()
            
        cursor = db.conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT * FROM enriched_messages 
            ORDER BY processed_at DESC 
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        messages = cursor.fetchall()
        cursor.close()
        
        return [dict(msg) for msg in messages]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving enriched messages: {str(e)}")

@app.get("/images/analysis", response_model=List[ImageAnalysisResponse])
async def get_image_analysis(
    limit: int = 100,
    offset: int = 0,
    db: PostgresLoader = Depends(get_db)
):
    """Get image analysis results"""
    try:
        if not db.conn:
            db.connect()
            
        cursor = db.conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT * FROM processed_images 
            ORDER BY processed_at DESC 
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        images = cursor.fetchall()
        cursor.close()
        
        return [dict(img) for img in images]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving image analysis: {str(e)}")

@app.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(db: PostgresLoader = Depends(get_db)):
    """Get pipeline statistics"""
    try:
        if not db.conn:
            db.connect()
            
        cursor = db.conn.cursor(cursor_factory=RealDictCursor)
        
        # Get total messages
        cursor.execute("SELECT COUNT(*) as count FROM raw_messages")
        total_messages = cursor.fetchone()['count']
        
        # Get total images
        cursor.execute("SELECT COUNT(*) as count FROM processed_images")
        total_images = cursor.fetchone()['count']
        
        # Get medical content count
        cursor.execute("""
            SELECT COUNT(*) as count FROM enriched_messages 
            WHERE medical_entities IS NOT NULL AND medical_entities != '{}'
        """)
        medical_content_count = cursor.fetchone()['count']
        
        # Get average sentiment
        cursor.execute("""
            SELECT AVG(sentiment_score) as avg_sentiment 
            FROM enriched_messages 
            WHERE sentiment_score IS NOT NULL
        """)
        avg_sentiment_result = cursor.fetchone()
        average_sentiment = float(avg_sentiment_result['avg_sentiment']) if avg_sentiment_result['avg_sentiment'] else 0.0
        
        # Get urgency distribution
        cursor.execute("""
            SELECT urgency_level, COUNT(*) as count 
            FROM enriched_messages 
            WHERE urgency_level IS NOT NULL 
            GROUP BY urgency_level
        """)
        urgency_distribution = {row['urgency_level']: row['count'] for row in cursor.fetchall()}
        
        # Get top channels
        cursor.execute("""
            SELECT chat_title, COUNT(*) as message_count 
            FROM raw_messages 
            GROUP BY chat_title 
            ORDER BY message_count DESC 
            LIMIT 10
        """)
        top_channels = [dict(row) for row in cursor.fetchall()]
        
        cursor.close()
        
        return StatisticsResponse(
            total_messages=total_messages,
            total_images=total_images,
            medical_content_count=medical_content_count,
            average_sentiment=average_sentiment,
            urgency_distribution=urgency_distribution,
            top_channels=top_channels
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")

@app.get("/channels")
async def get_channels(db: PostgresLoader = Depends(get_db)):
    """Get list of channels"""
    try:
        if not db.conn:
            db.connect()
            
        cursor = db.conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT DISTINCT chat_title, COUNT(*) as message_count 
            FROM raw_messages 
            GROUP BY chat_title 
            ORDER BY message_count DESC
        """)
        
        channels = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        
        return {"channels": channels}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving channels: {str(e)}")

@app.get("/messages/search")
async def search_messages(
    query: str,
    limit: int = 50,
    db: PostgresLoader = Depends(get_db)
):
    """Search messages by text content"""
    try:
        if not db.conn:
            db.connect()
            
        cursor = db.conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT * FROM raw_messages 
            WHERE message_text ILIKE %s 
            ORDER BY message_date DESC 
            LIMIT %s
        """, (f"%{query}%", limit))
        
        messages = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        
        return {"messages": messages, "query": query, "count": len(messages)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching messages: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    config = get_config()
    uvicorn.run(
        "fastapi_app.main:app",
        host=config.fastapi_host,
        port=config.fastapi_port,
        reload=config.fastapi_reload
    ) 