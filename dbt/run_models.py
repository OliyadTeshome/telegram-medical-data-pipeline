#!/usr/bin/env python3
"""
Script to manually run dbt models using SQLAlchemy
This is a workaround when dbt CLI is not available
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_database_connection():
    """Create database connection"""
    db_host = os.getenv('POSTGRES_HOST', 'localhost')
    db_port = os.getenv('POSTGRES_PORT', '5432')
    db_name = os.getenv('POSTGRES_DB', 'telegram_medical')
    db_user = os.getenv('POSTGRES_USER', 'postgres')
    db_password = os.getenv('POSTGRES_PASSWORD', '')
    
    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    return create_engine(database_url)

def run_staging_model(engine):
    """Run the staging model"""
    print("🏗️ Creating staging model: stg_telegram_messages")
    
    staging_sql = """
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
    """
    
    try:
        with engine.connect() as conn:
            conn.execute(text(staging_sql))
            conn.commit()
            print("✅ Staging model created successfully!")
            return True
    except Exception as e:
        print(f"❌ Error creating staging model: {e}")
        return False

def run_dim_channels(engine):
    """Run the channels dimension model"""
    print("🏗️ Creating dimension model: dim_channels")
    
    dim_channels_sql = """
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
    """
    
    try:
        with engine.connect() as conn:
            conn.execute(text(dim_channels_sql))
            conn.commit()
            print("✅ Channels dimension created successfully!")
            return True
    except Exception as e:
        print(f"❌ Error creating channels dimension: {e}")
        return False

def run_dim_dates(engine):
    """Run the dates dimension model"""
    print("🏗️ Creating dimension model: dim_dates")
    
    dim_dates_sql = """
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
    """
    
    try:
        with engine.connect() as conn:
            conn.execute(text(dim_dates_sql))
            conn.commit()
            print("✅ Dates dimension created successfully!")
            return True
    except Exception as e:
        print(f"❌ Error creating dates dimension: {e}")
        return False

def run_fct_messages(engine):
    """Run the fact table model"""
    print("🏗️ Creating fact table: fct_messages")
    
    fct_messages_sql = """
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
    """
    
    try:
        with engine.connect() as conn:
            conn.execute(text(fct_messages_sql))
            conn.commit()
            print("✅ Fact table created successfully!")
            return True
    except Exception as e:
        print(f"❌ Error creating fact table: {e}")
        return False

def main():
    """Main function to run all models"""
    print("🚀 Starting dbt model creation...")
    
    # Create database connection
    engine = get_database_connection()
    
    # Test connection
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Run models in order
    models = [
        ("Staging", run_staging_model),
        ("Channels Dimension", run_dim_channels),
        ("Dates Dimension", run_dim_dates),
        ("Fact Table", run_fct_messages)
    ]
    
    success_count = 0
    for model_name, model_func in models:
        print(f"\n{'='*50}")
        print(f"Running {model_name}...")
        if model_func(engine):
            success_count += 1
    
    print(f"\n{'='*50}")
    print(f"✅ Successfully created {success_count}/{len(models)} models!")
    
    if success_count == len(models):
        print("🎉 All dbt models created successfully!")
        print("You can now run the analysis notebook.")
    else:
        print("⚠️ Some models failed to create. Check the errors above.")

if __name__ == "__main__":
    main() 