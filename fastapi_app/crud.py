from sqlalchemy.orm import Session
from sqlalchemy import func, text, desc, and_, or_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re

from . import models, schemas

# Channel operations
def get_channels(db: Session, skip: int = 0, limit: int = 100):
    """Get all channels from fct_messages"""
    # Get unique channels from fct_messages since dim_channels might not be synced
    channels_query = db.query(
        models.FctMessages.chat_title,
        func.count(models.FctMessages.message_id).label('message_count')
    ).group_by(
        models.FctMessages.chat_title
    ).order_by(
        desc('message_count')
    ).offset(skip).limit(limit)
    
    return [
        {
            "channel_name": row.chat_title,
            "message_count": row.message_count
        }
        for row in channels_query.all()
    ]

def get_channel_by_name(db: Session, channel_name: str):
    """Get channel by name from fct_messages"""
    # Check if channel exists in fct_messages
    channel_exists = db.query(models.FctMessages).filter(
        models.FctMessages.chat_title == channel_name
    ).first()
    
    if channel_exists:
        return {"channel_name": channel_name, "exists": True}
    return None

# Message operations
def get_messages(db: Session, skip: int = 0, limit: int = 100, channel_name: Optional[str] = None):
    """Get messages with optional channel filter"""
    query = db.query(models.FctMessages)
    if channel_name:
        query = query.filter(models.FctMessages.chat_title == channel_name)
    return query.offset(skip).limit(limit).all()

def get_message_by_id(db: Session, message_id: int):
    """Get message by ID"""
    return db.query(models.FctMessages).filter(models.FctMessages.message_id == message_id).first()

# Medical insights operations
def get_medical_insights(db: Session, skip: int = 0, limit: int = 100):
    """Get medical insights - using fct_messages as fallback"""
    return db.query(models.FctMessages).offset(skip).limit(limit).all()

def get_medical_insights_by_channel(db: Session, channel_name: str, skip: int = 0, limit: int = 100):
    """Get medical insights for a specific channel - using fct_messages as fallback"""
    return db.query(models.FctMessages).filter(
        models.FctMessages.chat_title == channel_name
    ).offset(skip).limit(limit).all()

# Analytics operations
def get_top_products(db: Session, limit: int = 10):
    """Get most frequently mentioned products from messages"""
    # Using fct_messages instead of fct_medical_insights
    query = """
    WITH product_mentions AS (
        SELECT 
            'Medical Product' as product_name,
            COUNT(*) as mention_count,
            MAX(message_date) as last_mentioned,
            array_agg(DISTINCT chat_title) as channels
        FROM fct_messages 
        WHERE message_text ILIKE '%medicine%' 
           OR message_text ILIKE '%drug%'
           OR message_text ILIKE '%pill%'
           OR message_text ILIKE '%tablet%'
           OR message_text ILIKE '%syrup%'
           OR message_text ILIKE '%injection%'
        
        UNION ALL
        
        SELECT 
            'Pain Relief' as product_name,
            COUNT(*) as mention_count,
            MAX(message_date) as last_mentioned,
            array_agg(DISTINCT chat_title) as channels
        FROM fct_messages 
        WHERE message_text ILIKE '%paracetamol%' 
           OR message_text ILIKE '%ibuprofen%'
           OR message_text ILIKE '%aspirin%'
           OR message_text ILIKE '%pain%'
        
        UNION ALL
        
        SELECT 
            'Antibiotics' as product_name,
            COUNT(*) as mention_count,
            MAX(message_date) as last_mentioned,
            array_agg(DISTINCT chat_title) as channels
        FROM fct_messages 
        WHERE message_text ILIKE '%antibiotic%' 
           OR message_text ILIKE '%amoxicillin%'
           OR message_text ILIKE '%penicillin%'
    )
    SELECT 
        product_name,
        mention_count,
        channels,
        last_mentioned
    FROM product_mentions
    WHERE mention_count > 0
    ORDER BY mention_count DESC
    LIMIT :limit
    """
    
    result = db.execute(text(query), {"limit": limit})
    return [
        {
            "product_name": row.product_name,
            "mention_count": row.mention_count,
            "channels": row.channels,
            "last_mentioned": row.last_mentioned
        }
        for row in result
    ]

def get_channel_activity(db: Session, channel_name: str, period: str = "daily", limit: int = 30):
    """Get channel activity by period (daily/weekly/monthly)"""
    try:
        if period == "daily":
            date_format = "%Y-%m-%d"
            # Use text() for date functions to avoid SQLAlchemy compatibility issues
            from sqlalchemy import text
            query = db.execute(text("""
                SELECT 
                    DATE(message_date) as date,
                    COUNT(*) as message_count,
                    COUNT(*) as medical_content_count,
                    0.0 as average_sentiment
                FROM fct_messages 
                WHERE chat_title = :channel_name
                GROUP BY DATE(message_date)
                ORDER BY date DESC
                LIMIT :limit
            """), {"channel_name": channel_name, "limit": limit})
        elif period == "weekly":
            date_format = "%Y-W%U"
            query = db.execute(text("""
                SELECT 
                    DATE_TRUNC('week', message_date) as date,
                    COUNT(*) as message_count,
                    COUNT(*) as medical_content_count,
                    0.0 as average_sentiment
                FROM fct_messages 
                WHERE chat_title = :channel_name
                GROUP BY DATE_TRUNC('week', message_date)
                ORDER BY date DESC
                LIMIT :limit
            """), {"channel_name": channel_name, "limit": limit})
        else:  # monthly
            date_format = "%Y-%m"
            query = db.execute(text("""
                SELECT 
                    DATE_TRUNC('month', message_date) as date,
                    COUNT(*) as message_count,
                    COUNT(*) as medical_content_count,
                    0.0 as average_sentiment
                FROM fct_messages 
                WHERE chat_title = :channel_name
                GROUP BY DATE_TRUNC('month', message_date)
                ORDER BY date DESC
                LIMIT :limit
            """), {"channel_name": channel_name, "limit": limit})
        
        return [
            {
                "channel_name": channel_name,
                "date": row.date.strftime(date_format) if row.date else None,
                "message_count": row.message_count,
                "medical_content_count": row.medical_content_count,
                "average_sentiment": float(row.average_sentiment) if row.average_sentiment else 0.0
            }
            for row in query
        ]
    except Exception as e:
        print(f"Error in get_channel_activity: {str(e)}")
        return []

def search_messages(db: Session, query: str, limit: int = 50):
    """Full-text search across messages"""
    # Using PostgreSQL full-text search capabilities
    search_query = f"%{query}%"
    
    # Search in message text
    results = db.query(models.FctMessages).filter(
        or_(
            models.FctMessages.message_text.ilike(search_query),
            models.FctMessages.chat_title.ilike(search_query),
            models.FctMessages.sender_username.ilike(search_query)
        )
    ).order_by(
        desc(models.FctMessages.message_date)
    ).limit(limit).all()
    
    # Calculate simple relevance score based on match position
    search_results = []
    for result in results:
        relevance_score = 0.0
        text_lower = result.message_text.lower()
        query_lower = query.lower()
        
        if query_lower in text_lower:
            # Higher score for exact matches
            relevance_score += 1.0
            # Bonus for matches at the beginning
            if text_lower.startswith(query_lower):
                relevance_score += 0.5
        
        search_results.append({
            "message_id": result.message_id,
            "message_text": result.message_text,
            "sender_username": result.sender_username,
            "chat_title": result.chat_title,
            "message_date": result.message_date,
            "relevance_score": relevance_score
        })
    
    # Sort by relevance score
    search_results.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    return {
        "query": query,
        "results": search_results,
        "total_count": len(search_results),
        "limit": limit
    }

def get_statistics(db: Session):
    """Get comprehensive statistics"""
    # Total messages
    total_messages = db.query(func.count(models.FctMessages.message_id)).scalar()
    
    # Total channels (from fct_messages)
    total_channels = db.query(func.count(func.distinct(models.FctMessages.chat_title))).scalar()
    
    # Total medical insights (using fct_messages as fallback)
    total_medical_insights = db.query(func.count(models.FctMessages.message_id)).scalar()
    
    # Average sentiment (default to 0 since we don't have sentiment data)
    average_sentiment = 0.0
    
    # Top channels by message count
    top_channels_query = db.query(
        models.FctMessages.chat_title,
        func.count(models.FctMessages.message_id).label('message_count')
    ).group_by(
        models.FctMessages.chat_title
    ).order_by(
        desc('message_count')
    ).limit(10)
    
    top_channels = [
        {"channel_name": row.chat_title, "message_count": row.message_count}
        for row in top_channels_query.all()
    ]
    
    # Urgency distribution (default since we don't have this data)
    urgency_distribution = {
        "low": 0,
        "medium": 0,
        "high": 0
    }
    
    # Medical entity distribution (simplified)
    medical_entity_distribution = {
        "high": 0,
        "medium": 0,
        "low": 0
    }
    
    return {
        "total_messages": total_messages,
        "total_channels": total_channels,
        "total_medical_insights": total_medical_insights,
        "average_sentiment": average_sentiment,
        "top_channels": top_channels,
        "urgency_distribution": urgency_distribution,
        "medical_entity_distribution": medical_entity_distribution
    } 