#!/usr/bin/env python3
"""
Simple database connection test
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    """Test database connection"""
    try:
        # Get database credentials
        db_host = os.getenv('POSTGRES_HOST', 'localhost')
        db_port = os.getenv('POSTGRES_PORT', '5432')
        db_name = os.getenv('POSTGRES_DB', 'telegram_medical')
        db_user = os.getenv('POSTGRES_USER', 'postgres')
        db_password = os.getenv('POSTGRES_PASSWORD', '')
        
        print(f"Connecting to: {db_host}:{db_port}/{db_name}")
        print(f"User: {db_user}")
        
        # Create database URL
        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            
            # Check if raw table exists
            result = conn.execute(text("""
                SELECT COUNT(*) FROM raw.telegram_messages
            """))
            count = result.fetchone()[0]
            print(f"📊 Raw table has {count} messages")
            
            # Create staging view
            print("Creating staging view...")
            staging_sql = """
            CREATE OR REPLACE VIEW stg_telegram_messages AS
            SELECT
                id as message_id,
                message_id as telegram_message_id,
                chat_id,
                chat_title,
                channel_name,
                sender_id,
                sender_username,
                sender_first_name,
                sender_last_name,
                message_text,
                message_date,
                has_media,
                media_type,
                media_path,
                CASE 
                    WHEN has_media = true AND media_type IN ('MessageMediaPhoto', 'MessageMediaDocument') THEN true
                    ELSE false
                END as has_image,
                reply_to_msg_id,
                forward_from,
                scraped_at,
                created_at,
                raw_data
            FROM raw.telegram_messages;
            """
            
            conn.execute(text(staging_sql))
            conn.commit()
            print("✅ Staging view created!")
            
            # Test staging view
            result = conn.execute(text("SELECT COUNT(*) FROM stg_telegram_messages"))
            count = result.fetchone()[0]
            print(f"📊 Staging view has {count} messages")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_connection() 