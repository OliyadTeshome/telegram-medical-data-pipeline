-- Create tables for raw data

-- Create tables for raw data
CREATE TABLE IF NOT EXISTS raw_messages (
    id SERIAL PRIMARY KEY,
    message_id BIGINT,
    chat_id BIGINT,
    chat_title TEXT,
    sender_id BIGINT,
    sender_username TEXT,
    message_text TEXT,
    message_date TIMESTAMP,
    has_media BOOLEAN DEFAULT FALSE,
    media_type TEXT,
    media_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS processed_images (
    id SERIAL PRIMARY KEY,
    message_id BIGINT,
    image_path TEXT,
    detection_results JSONB,
    confidence_scores JSONB,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS enriched_messages (
    id SERIAL PRIMARY KEY,
    raw_message_id INTEGER REFERENCES raw_messages(id),
    medical_entities JSONB,
    sentiment_score FLOAT,
    urgency_level TEXT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_raw_messages_chat_id ON raw_messages(chat_id);
CREATE INDEX IF NOT EXISTS idx_raw_messages_date ON raw_messages(message_date);
CREATE INDEX IF NOT EXISTS idx_processed_images_message_id ON processed_images(message_id);
CREATE INDEX IF NOT EXISTS idx_enriched_messages_raw_id ON enriched_messages(raw_message_id); 