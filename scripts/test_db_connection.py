#!/usr/bin/env python3
"""
Test script to verify database connection and table creation.
Run this before running the main telegram loader script.
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test database connection and create table"""
    try:
        # Get database credentials
        db_host = os.getenv('POSTGRES_HOST', 'localhost')
        db_port = os.getenv('POSTGRES_PORT', '5432')
        db_name = os.getenv('POSTGRES_DB', 'telegram_medical')
        db_user = os.getenv('POSTGRES_USER', 'postgres')
        db_password = os.getenv('POSTGRES_PASSWORD', '')
        
        print(f"Testing connection to database: {db_name} on {db_host}:{db_port}")
        print(f"User: {db_user}")
        print(f"Password: {'*' * len(db_password) if db_password else 'Not set'}")
        
        # Create database URL
        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        
        # Create SQLAlchemy engine
        engine = create_engine(database_url, echo=False)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            
            # Check if database exists
            result = conn.execute(text("SELECT current_database()"))
            current_db = result.fetchone()[0]
            print(f"✅ Connected to database: {current_db}")
            
            # Create schema if it doesn't exist
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))
            conn.commit()
            print("✅ Schema 'raw' created/verified")
            
            # Create table
            metadata = MetaData()
            telegram_messages = Table(
                'telegram_messages', 
                metadata,
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('message_id', Integer, nullable=False, unique=True),
                Column('chat_id', Integer, nullable=True),
                Column('chat_title', String(500), nullable=True),
                Column('sender_id', Integer, nullable=True),
                Column('sender_username', String(100), nullable=True),
                Column('sender_first_name', String(100), nullable=True),
                Column('sender_last_name', String(100), nullable=True),
                Column('message_text', Text, nullable=True),
                Column('message_date', DateTime, nullable=True),
                Column('has_media', Boolean, nullable=True),
                Column('media_type', String(100), nullable=True),
                Column('media_path', String(500), nullable=True),
                Column('reply_to_msg_id', Integer, nullable=True),
                Column('forward_from', String(500), nullable=True),
                Column('scraped_at', DateTime, nullable=True),
                Column('channel_name', String(100), nullable=True),
                Column('raw_data', JSONB, nullable=True),
                Column('created_at', DateTime, default=datetime.utcnow),
                schema='raw'
            )
            
            metadata.create_all(engine, tables=[telegram_messages])
            print("✅ Table 'raw.telegram_messages' created/verified")
            
            # Test insert
            test_data = {
                'message_id': 999999,
                'chat_id': -1001569871437,
                'chat_title': 'Test Channel',
                'message_text': 'Test message',
                'channel_name': 'test_channel',
                'raw_data': {'test': 'data'}
            }
            
            insert_query = text("""
                INSERT INTO raw.telegram_messages (
                    message_id, chat_id, chat_title, message_text, channel_name, raw_data
                ) VALUES (
                    :message_id, :chat_id, :chat_title, :message_text, :channel_name, :raw_data
                )
                ON CONFLICT (message_id) DO NOTHING
            """)
            
            result = conn.execute(insert_query, test_data)
            conn.commit()
            
            if result.rowcount > 0:
                print("✅ Test insert successful")
            else:
                print("⚠️  Test insert skipped (message_id already exists)")
            
            # Clean up test data
            conn.execute(text("DELETE FROM raw.telegram_messages WHERE message_id = 999999"))
            conn.commit()
            print("✅ Test data cleaned up")
            
        print("\n🎉 All tests passed! Database is ready for the telegram loader.")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check your .env file has correct database credentials")
        print("3. Ensure the 'telegram_medical' database exists")
        print("4. Verify your PostgreSQL user has proper permissions")
        return False

def check_environment():
    """Check if required environment variables are set"""
    print("Checking environment variables...")
    
    required_vars = ['POSTGRES_HOST', 'POSTGRES_DB', 'POSTGRES_USER']
    optional_vars = ['POSTGRES_PASSWORD', 'POSTGRES_PORT']
    
    missing_required = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_required.append(var)
        else:
            print(f"✅ {var}: {value}")
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"⚠️  {var}: Not set (using default)")
    
    if missing_required:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_required)}")
        print("Please set these in your .env file")
        return False
    
    return True

def main():
    """Main test function"""
    print("=" * 50)
    print("DATABASE CONNECTION TEST")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    
    # Test database connection
    if test_database_connection():
        print("\n✅ All tests passed! You can now run the telegram loader.")
        print("Run: python scripts/load_telegram_messages.py")
    else:
        print("\n❌ Tests failed. Please fix the issues above before running the loader.")
        sys.exit(1)

if __name__ == "__main__":
    main() 