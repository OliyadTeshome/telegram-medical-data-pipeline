#!/usr/bin/env python3
"""
Setup database tables for YOLO image detection pipeline
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.loader.postgres_loader import PostgresLoader

load_dotenv()

def setup_database():
    """Create necessary database tables"""
    loader = PostgresLoader()
    loader.connect()
    
    try:
        cursor = loader.conn.cursor()
        
        # Create processed_images table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS processed_images (
            id SERIAL PRIMARY KEY,
            message_id BIGINT,
            image_path TEXT,
            detection_results JSONB,
            confidence_scores JSONB,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        cursor.execute(create_table_sql)
        loader.conn.commit()
        print("✅ processed_images table created successfully")
        
        # Create index for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_processed_images_message_id 
            ON processed_images(message_id);
        """)
        loader.conn.commit()
        print("✅ Index created successfully")
        
        # Verify table exists
        cursor.execute("""
            SELECT COUNT(*) FROM processed_images;
        """)
        count = cursor.fetchone()[0]
        print(f"📊 processed_images table has {count} existing records")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        loader.conn.rollback()
    finally:
        cursor.close()
        loader.disconnect()
        print("🔌 Database connection closed")

if __name__ == "__main__":
    setup_database() 