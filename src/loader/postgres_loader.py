import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class PostgresLoader:
    def __init__(self):
        self.connection_params = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', 'medical_data'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', '')
        }
        self.conn = None
        
    def connect(self):
        """Establish connection to PostgreSQL"""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            print("Connected to PostgreSQL successfully")
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")
            raise
            
    def disconnect(self):
        """Close PostgreSQL connection"""
        if self.conn:
            self.conn.close()
            
    def load_raw_messages(self, messages: List[Dict[str, Any]]) -> int:
        """Load raw messages into PostgreSQL"""
        if not self.conn:
            self.connect()
            
        cursor = self.conn.cursor()
        inserted_count = 0
        
        try:
            for message in messages:
                cursor.execute("""
                    INSERT INTO raw_messages 
                    (message_id, chat_id, chat_title, sender_id, sender_username, 
                     message_text, message_date, has_media, media_type, media_path)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (message_id) DO NOTHING
                """, (
                    message.get('message_id'),
                    message.get('chat_id'),
                    message.get('chat_title'),
                    message.get('sender_id'),
                    message.get('sender_username'),
                    message.get('message_text'),
                    message.get('message_date'),
                    message.get('has_media', False),
                    message.get('media_type'),
                    message.get('media_path')
                ))
                inserted_count += cursor.rowcount
                
            self.conn.commit()
            print(f"Inserted {inserted_count} new messages")
            
        except Exception as e:
            self.conn.rollback()
            print(f"Error loading messages: {e}")
            raise
        finally:
            cursor.close()
            
        return inserted_count
    
    def load_processed_images(self, image_data: List[Dict[str, Any]]) -> int:
        """Load processed image data into PostgreSQL"""
        if not self.conn:
            self.connect()
            
        cursor = self.conn.cursor()
        inserted_count = 0
        
        try:
            for image in image_data:
                cursor.execute("""
                    INSERT INTO processed_images 
                    (message_id, image_path, detection_results, confidence_scores)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (message_id) DO UPDATE SET
                    detection_results = EXCLUDED.detection_results,
                    confidence_scores = EXCLUDED.confidence_scores,
                    processed_at = CURRENT_TIMESTAMP
                """, (
                    image.get('message_id'),
                    image.get('image_path'),
                    json.dumps(image.get('detection_results', {})),
                    json.dumps(image.get('confidence_scores', {}))
                ))
                inserted_count += cursor.rowcount
                
            self.conn.commit()
            print(f"Inserted/updated {inserted_count} processed images")
            
        except Exception as e:
            self.conn.rollback()
            print(f"Error loading processed images: {e}")
            raise
        finally:
            cursor.close()
            
        return inserted_count
    
    def load_enriched_messages(self, enriched_data: List[Dict[str, Any]]) -> int:
        """Load enriched message data into PostgreSQL"""
        if not self.conn:
            self.connect()
            
        cursor = self.conn.cursor()
        inserted_count = 0
        
        try:
            for enriched in enriched_data:
                cursor.execute("""
                    INSERT INTO enriched_messages 
                    (raw_message_id, medical_entities, sentiment_score, urgency_level)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (raw_message_id) DO UPDATE SET
                    medical_entities = EXCLUDED.medical_entities,
                    sentiment_score = EXCLUDED.sentiment_score,
                    urgency_level = EXCLUDED.urgency_level,
                    processed_at = CURRENT_TIMESTAMP
                """, (
                    enriched.get('raw_message_id'),
                    json.dumps(enriched.get('medical_entities', {})),
                    enriched.get('sentiment_score'),
                    enriched.get('urgency_level')
                ))
                inserted_count += cursor.rowcount
                
            self.conn.commit()
            print(f"Inserted/updated {inserted_count} enriched messages")
            
        except Exception as e:
            self.conn.rollback()
            print(f"Error loading enriched messages: {e}")
            raise
        finally:
            cursor.close()
            
        return inserted_count
    
    def execute_query(self, query: str, params: tuple = None) -> None:
        """Execute a SQL query"""
        if not self.conn:
            self.connect()
            
        cursor = self.conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.conn.commit()
            
        except Exception as e:
            self.conn.rollback()
            print(f"Error executing query: {e}")
            raise
        finally:
            cursor.close()
    
    def get_raw_messages(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve raw messages from PostgreSQL"""
        if not self.conn:
            self.connect()
            
        cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            cursor.execute("""
                SELECT * FROM raw_messages 
                ORDER BY message_date DESC 
                LIMIT %s
            """, (limit,))
            
            messages = cursor.fetchall()
            return [dict(msg) for msg in messages]
            
        except Exception as e:
            print(f"Error retrieving messages: {e}")
            raise
        finally:
            cursor.close()

def main():
    """Test function for the loader"""
    loader = PostgresLoader()
    
    # Test connection
    loader.connect()
    
    # Test data retrieval
    messages = loader.get_raw_messages(limit=10)
    print(f"Retrieved {len(messages)} messages")
    
    loader.disconnect()

if __name__ == "__main__":
    main() 