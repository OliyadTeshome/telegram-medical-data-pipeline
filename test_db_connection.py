#!/usr/bin/env python3
"""
Test script to check database connection and identify issues
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test database connection and basic operations"""
    
    # Database configuration
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:your_password_here@localhost:5432/medical_data"
    )
    
    print(f"Testing connection to: {DATABASE_URL}")
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        # Test connection
        with engine.connect() as connection:
            print("✓ Database connection successful!")
            
            # Test basic query
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()
            print(f"✓ PostgreSQL version: {version[0]}")
            
            # Check if tables exist
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result.fetchall()]
            print(f"✓ Available tables: {tables}")
            
            # Test fct_messages table
            if 'fct_messages' in tables:
                result = connection.execute(text("SELECT COUNT(*) FROM fct_messages"))
                count = result.fetchone()[0]
                print(f"✓ fct_messages table has {count} records")
                
                # Test a sample query
                result = connection.execute(text("""
                    SELECT chat_title, COUNT(*) as message_count 
                    FROM fct_messages 
                    GROUP BY chat_title 
                    ORDER BY message_count DESC 
                    LIMIT 5
                """))
                
                channels = result.fetchall()
                print("✓ Top channels by message count:")
                for channel in channels:
                    print(f"  - {channel[0]}: {channel[1]} messages")
            else:
                print("✗ fct_messages table not found!")
                
    except Exception as e:
        print(f"✗ Database connection failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing FastAPI Database Connection...")
    print("=" * 50)
    
    success = test_database_connection()
    
    print("=" * 50)
    if success:
        print("✓ All database tests passed!")
    else:
        print("✗ Database tests failed!")
        sys.exit(1) 