from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# Base schemas
class ChannelBase(BaseModel):
    channel_name: str
    chat_id: int
    chat_title: str

class MessageBase(BaseModel):
    message_text: str
    message_date: datetime
    sender_username: str
    chat_title: str

class MedicalInsightBase(BaseModel):
    message_text: str
    message_date: datetime
    sender_username: str
    chat_title: str
    has_media: bool
    medical_entities: Optional[Dict[str, Any]] = None
    sentiment_score: Optional[float] = None
    urgency_level: Optional[str] = None

# Response schemas
class ChannelResponse(ChannelBase):
    channel_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class MessageResponse(MessageBase):
    message_id: int
    channel_id: Optional[int] = None
    date_id: Optional[str] = None
    telegram_message_id: int
    chat_id: int
    channel_name: Optional[str] = None
    sender_id: int
    sender_first_name: Optional[str] = None
    sender_last_name: Optional[str] = None
    has_media: bool
    has_image: bool
    media_type: Optional[str] = None
    media_path: Optional[str] = None
    reply_to_msg_id: Optional[int] = None
    forward_from: Optional[str] = None
    scraped_at: Optional[datetime] = None
    created_at: datetime
    raw_data: Optional[Dict[str, Any]] = None
    
    class Config:
        orm_mode = True

class MedicalInsightResponse(MedicalInsightBase):
    message_id: int
    sentiment_category: Optional[str] = None
    has_medical_content: bool
    medical_entity_count: Optional[int] = None
    
    class Config:
        orm_mode = True

class TopProductResponse(BaseModel):
    product_name: str
    mention_count: int
    channels: List[str]
    last_mentioned: datetime

class ChannelActivityResponse(BaseModel):
    channel_name: str
    date: str
    message_count: int
    medical_content_count: int
    average_sentiment: float

class SearchResultResponse(BaseModel):
    message_id: int
    message_text: str
    sender_username: str
    chat_title: str
    message_date: datetime
    relevance_score: Optional[float] = None

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultResponse]
    total_count: int
    limit: int

# Request schemas
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    limit: int = Field(default=50, ge=1, le=100, description="Maximum number of results")

class TopProductsRequest(BaseModel):
    limit: int = Field(default=10, ge=1, le=100, description="Number of top products to return")

class ChannelActivityRequest(BaseModel):
    period: str = Field(default="daily", regex="^(daily|weekly|monthly)$", description="Activity period")
    limit: int = Field(default=30, ge=1, le=365, description="Number of periods to return")

# Statistics schemas
class StatisticsResponse(BaseModel):
    total_messages: int
    total_channels: int
    total_medical_insights: int
    average_sentiment: float
    top_channels: List[Dict[str, Any]]
    urgency_distribution: Dict[str, int]
    medical_entity_distribution: Dict[str, int] 