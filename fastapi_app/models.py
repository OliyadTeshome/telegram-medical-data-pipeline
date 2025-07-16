from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, BigInteger, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base

class DimChannels(Base):
    __tablename__ = "dim_channels"
    
    channel_id = Column(Integer, primary_key=True, index=True)
    channel_name = Column(String, unique=True, index=True)
    chat_id = Column(BigInteger)
    chat_title = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DimDates(Base):
    __tablename__ = "dim_dates"
    
    date_id = Column(String, primary_key=True, index=True)
    date = Column(DateTime)
    year = Column(Integer)
    month = Column(Integer)
    day = Column(Integer)
    day_of_week = Column(Integer)
    is_weekend = Column(Boolean)

class FctMessages(Base):
    __tablename__ = "fct_messages"
    
    message_id = Column(BigInteger, primary_key=True, index=True)
    channel_id = Column(Integer, index=True)
    date_id = Column(String, index=True)
    telegram_message_id = Column(BigInteger)
    chat_id = Column(BigInteger)
    chat_title = Column(String)
    channel_name = Column(String, index=True)
    sender_id = Column(BigInteger)
    sender_username = Column(String)
    sender_first_name = Column(String)
    sender_last_name = Column(String)
    message_text = Column(Text)
    message_date = Column(DateTime, index=True)
    has_media = Column(Boolean)
    has_image = Column(Boolean)
    media_type = Column(String)
    media_path = Column(String)
    reply_to_msg_id = Column(BigInteger)
    forward_from = Column(String)
    scraped_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    raw_data = Column(JSON)

class FctMedicalInsights(Base):
    __tablename__ = "fct_medical_insights"
    
    message_id = Column(BigInteger, primary_key=True, index=True)
    chat_title = Column(String)
    sender_username = Column(String)
    message_text = Column(Text)
    message_date = Column(DateTime, index=True)
    has_media = Column(Boolean)
    medical_entities = Column(JSON)
    sentiment_score = Column(Float)
    urgency_level = Column(String)
    sentiment_category = Column(String)
    has_medical_content = Column(Boolean)
    medical_entity_count = Column(Integer)

class RawMessages(Base):
    __tablename__ = "raw_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(BigInteger)
    chat_id = Column(BigInteger)
    chat_title = Column(String)
    sender_id = Column(BigInteger)
    sender_username = Column(String)
    message_text = Column(Text)
    message_date = Column(DateTime)
    has_media = Column(Boolean, default=False)
    media_type = Column(String)
    media_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class EnrichedMessages(Base):
    __tablename__ = "enriched_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    raw_message_id = Column(Integer, index=True)
    medical_entities = Column(JSON)
    sentiment_score = Column(Float)
    urgency_level = Column(String)
    processed_at = Column(DateTime, default=datetime.utcnow)

class ProcessedImages(Base):
    __tablename__ = "processed_images"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(BigInteger, index=True)
    image_path = Column(String)
    detection_results = Column(JSON)
    confidence_scores = Column(JSON)
    processed_at = Column(DateTime, default=datetime.utcnow) 