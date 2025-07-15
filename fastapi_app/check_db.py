#!/usr/bin/env python3
"""
Script to check database tables
"""

import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_database_tables():
    """Check what tables exist in the database"""
    try:
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/telegram_medical_data")
        
        print(f"Connecting to database...")
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        # Get all tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        tables = cur.fetchall()
        
        print(f"\n📋 Available tables in database:")
        print("=" * 50)
        
        if tables:
            for table in tables:
                print(f"  ✅ {table[0]}")
        else:
            print("  ❌ No tables found")
        
        # Check specific tables we need
        required_tables = [
            'fct_medical_insights',
            'fct_messages', 
            'dim_channels',
            'raw_messages',
            'enriched_messages'
        ]
        
        print(f"\n🔍 Checking required tables:")
        print("=" * 50)
        
        existing_tables = [table[0] for table in tables]
        
        for table in required_tables:
            if table in existing_tables:
                print(f"  ✅ {table}")
            else:
                print(f"  ❌ {table} - MISSING")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        print("\n💡 Make sure:")
        print("  1. PostgreSQL is running")
        print("  2. Database 'telegram_medical_data' exists")
        print("  3. Your .env file has correct DATABASE_URL")

if __name__ == "__main__":
    check_database_tables() 