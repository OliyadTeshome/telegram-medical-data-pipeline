#!/usr/bin/env python3
"""
Setup script to create database tables for the Telegram medical data pipeline
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from src.loader.postgres_loader import PostgresLoader
from src.utils.config import get_config

def setup_database():
    """Setup database tables"""
    print("🗄️  Setting up database tables")
    print("=" * 50)
    
    try:
        # Get configuration
        config = get_config()
        print(f"Database: {config.postgres_db}")
        print(f"Host: {config.postgres_host}")
        print(f"Port: {config.postgres_port}")
        
        # Create loader instance
        loader = PostgresLoader()
        
        # Create tables
        print("\n📋 Creating database tables...")
        
        # Create raw_messages table
        raw_messages_sql = """
        CREATE TABLE IF NOT EXISTS raw_messages (
            id SERIAL PRIMARY KEY,
            message_id BIGINT,
            chat_id BIGINT,
            chat_title VARCHAR(255),
            sender_id BIGINT,
            sender_username VARCHAR(100),
            sender_first_name VARCHAR(100),
            sender_last_name VARCHAR(100),
            message_text TEXT,
            message_date TIMESTAMP,
            has_media BOOLEAN,
            media_path VARCHAR(500),
            channel_name VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Create processed_messages table
        processed_messages_sql = """
        CREATE TABLE IF NOT EXISTS processed_messages (
            id SERIAL PRIMARY KEY,
            raw_message_id INTEGER REFERENCES raw_messages(id),
            processed_text TEXT,
            sentiment_score FLOAT,
            medical_keywords TEXT[],
            image_analysis JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Create yolo_detections table
        yolo_detections_sql = """
        CREATE TABLE IF NOT EXISTS yolo_detections (
            id SERIAL PRIMARY KEY,
            image_path VARCHAR(500),
            detection_class VARCHAR(100),
            confidence FLOAT,
            bbox_coordinates JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Execute table creation
        tables_sql = [
            ("raw_messages", raw_messages_sql),
            ("processed_messages", processed_messages_sql),
            ("yolo_detections", yolo_detections_sql)
        ]
        
        for table_name, sql in tables_sql:
            try:
                loader.execute_query(sql)
                print(f"✅ Created table: {table_name}")
            except Exception as e:
                print(f"⚠️  Table {table_name} might already exist: {e}")
        
        print("\n🎉 Database setup completed!")
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

if __name__ == "__main__":
    success = setup_database()
    
    if success:
        print("\n✅ Database is ready for the pipeline!")
    else:
        print("\n❌ Database setup failed!") 