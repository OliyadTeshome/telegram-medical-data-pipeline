-- Create dbt models manually
-- Run this script in your PostgreSQL database

-- 1. Create staging view
CREATE OR REPLACE VIEW stg_telegram_messages AS
SELECT
    -- Primary keys
    id as message_id,
    message_id as telegram_message_id,
    
    -- Chat information
    chat_id,
    chat_title,
    channel_name,
    
    -- Sender information
    sender_id,
    sender_username,
    sender_first_name,
    sender_last_name,
    
    -- Message content
    message_text,
    message_date,
    
    -- Media information
    has_media,
    media_type,
    media_path,
    
    -- Extract has_image boolean from has_media and media_type
    CASE 
        WHEN has_media = true AND media_type IN ('MessageMediaPhoto', 'MessageMediaDocument') THEN true
        ELSE false
    END as has_image,
    
    -- Message metadata
    reply_to_msg_id,
    forward_from,
    scraped_at,
    created_at,
    
    -- Raw data for flexibility
    raw_data
    
FROM raw.telegram_messages;

-- 2. Create channels dimension
CREATE TABLE IF NOT EXISTS dim_channels (
    channel_id SERIAL PRIMARY KEY,
    channel_name VARCHAR(100) UNIQUE NOT NULL,
    chat_id BIGINT,
    chat_title VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO dim_channels (channel_name, chat_id, chat_title)
SELECT DISTINCT
    channel_name,
    chat_id,
    chat_title
FROM stg_telegram_messages
WHERE channel_name IS NOT NULL
ON CONFLICT (channel_name) DO NOTHING;

-- 3. Create dates dimension
CREATE TABLE IF NOT EXISTS dim_dates (
    date_id DATE PRIMARY KEY,
    year INTEGER,
    month INTEGER,
    day INTEGER,
    day_of_week INTEGER,
    day_of_year INTEGER,
    month_name VARCHAR(20),
    day_name VARCHAR(20),
    is_weekend BOOLEAN,
    season VARCHAR(10)
);

INSERT INTO dim_dates (date_id, year, month, day, day_of_week, day_of_year, month_name, day_name, is_weekend, season)
SELECT 
    date_series::date as date_id,
    EXTRACT(year FROM date_series::date) as year,
    EXTRACT(month FROM date_series::date) as month,
    EXTRACT(day FROM date_series::date) as day,
    EXTRACT(dow FROM date_series::date) as day_of_week,
    EXTRACT(doy FROM date_series::date) as day_of_year,
    TO_CHAR(date_series::date, 'Month') as month_name,
    TO_CHAR(date_series::date, 'Day') as day_name,
    CASE 
        WHEN EXTRACT(dow FROM date_series::date) IN (0, 6) THEN true 
        ELSE false 
    END as is_weekend,
    CASE 
        WHEN EXTRACT(month FROM date_series::date) IN (12, 1, 2) THEN 'Winter'
        WHEN EXTRACT(month FROM date_series::date) IN (3, 4, 5) THEN 'Spring'
        WHEN EXTRACT(month FROM date_series::date) IN (6, 7, 8) THEN 'Summer'
        ELSE 'Fall'
    END as season
FROM generate_series(
    (SELECT MIN(DATE(message_date)) FROM stg_telegram_messages),
    (SELECT MAX(DATE(message_date)) FROM stg_telegram_messages),
    interval '1 day'
) as date_series
ON CONFLICT (date_id) DO NOTHING;

-- 4. Create fact table
CREATE TABLE IF NOT EXISTS fct_messages (
    message_id INTEGER PRIMARY KEY,
    channel_id INTEGER,
    date_id DATE,
    telegram_message_id INTEGER,
    chat_id BIGINT,
    chat_title VARCHAR(500),
    channel_name VARCHAR(100),
    sender_id BIGINT,
    sender_username VARCHAR(100),
    sender_first_name VARCHAR(100),
    sender_last_name VARCHAR(100),
    message_text TEXT,
    message_date TIMESTAMP,
    has_media BOOLEAN,
    has_image BOOLEAN,
    media_type VARCHAR(100),
    media_path VARCHAR(500),
    reply_to_msg_id INTEGER,
    forward_from VARCHAR(500),
    scraped_at TIMESTAMP,
    created_at TIMESTAMP,
    raw_data JSONB,
    FOREIGN KEY (channel_id) REFERENCES dim_channels(channel_id),
    FOREIGN KEY (date_id) REFERENCES dim_dates(date_id)
);

INSERT INTO fct_messages (
    message_id, channel_id, date_id, telegram_message_id, chat_id, chat_title,
    channel_name, sender_id, sender_username, sender_first_name, sender_last_name,
    message_text, message_date, has_media, has_image, media_type, media_path,
    reply_to_msg_id, forward_from, scraped_at, created_at, raw_data
)
SELECT 
    s.message_id,
    c.channel_id,
    d.date_id,
    s.telegram_message_id,
    s.chat_id,
    s.chat_title,
    s.channel_name,
    s.sender_id,
    s.sender_username,
    s.sender_first_name,
    s.sender_last_name,
    s.message_text,
    s.message_date,
    s.has_media,
    s.has_image,
    s.media_type,
    s.media_path,
    s.reply_to_msg_id,
    s.forward_from,
    s.scraped_at,
    s.created_at,
    s.raw_data
FROM stg_telegram_messages s
LEFT JOIN dim_channels c ON s.channel_name = c.channel_name
LEFT JOIN dim_dates d ON DATE(s.message_date) = d.date_id
ON CONFLICT (message_id) DO NOTHING;

-- 5. Verify models
SELECT 'stg_telegram_messages' as model, COUNT(*) as count FROM stg_telegram_messages
UNION ALL
SELECT 'dim_channels' as model, COUNT(*) as count FROM dim_channels
UNION ALL
SELECT 'dim_dates' as model, COUNT(*) as count FROM dim_dates
UNION ALL
SELECT 'fct_messages' as model, COUNT(*) as count FROM fct_messages; 