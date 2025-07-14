#!/usr/bin/env python3
"""
Script to load Telegram message JSON files into PostgreSQL database.

This script:
1. Reads Telegram message JSON files from notebooks/data/raw/telegram_messages/
2. Parses messages and inserts them into raw.telegram_messages table
3. Uses SQLAlchemy for database operations
4. Avoids duplicate inserts using message_id as unique key
5. Logs number of rows inserted and source filename
6. Uses environment variables for DB credentials
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import glob

from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.dialects.postgresql import JSONB
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_loader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TelegramMessageLoader:
    """Class to handle loading Telegram messages into PostgreSQL"""
    
    def __init__(self):
        """Initialize the loader with database connection"""
        self.engine = None
        self.metadata = MetaData()
        self.setup_database_connection()
        self.create_table_if_not_exists()
    
    def setup_database_connection(self):
        """Setup database connection using environment variables"""
        try:
            # Get database credentials from environment variables
            db_host = os.getenv('POSTGRES_HOST', 'localhost')
            db_port = os.getenv('POSTGRES_PORT', '5432')
            db_name = os.getenv('POSTGRES_DB', 'telegram_medical')  # Use the specified database name
            db_user = os.getenv('POSTGRES_USER', 'postgres')
            db_password = os.getenv('POSTGRES_PASSWORD', '')
            
            # Create database URL
            database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            
            # Create SQLAlchemy engine
            self.engine = create_engine(database_url, echo=False)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info(f"Successfully connected to database: {db_name} on {db_host}:{db_port}")
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def create_table_if_not_exists(self):
        """Create the telegram_messages table if it doesn't exist"""
        try:
            # Define the table schema
            telegram_messages = Table(
                'telegram_messages', 
                self.metadata,
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
                Column('raw_data', JSONB, nullable=True),  # Store complete JSON for flexibility
                Column('created_at', DateTime, default=datetime.utcnow),
                schema='raw'
            )
            
            # Create schema if it doesn't exist
            with self.engine.connect() as conn:
                conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))
                conn.commit()
            
            # Create table if it doesn't exist
            self.metadata.create_all(self.engine, tables=[telegram_messages])
            logger.info("Table raw.telegram_messages created/verified successfully")
            
        except Exception as e:
            logger.error(f"Failed to create table: {e}")
            raise
    
    def parse_message_date(self, date_str: str) -> Optional[datetime]:
        """Parse message date string to datetime object"""
        try:
            if date_str:
                # Handle ISO format with timezone
                if '+' in date_str:
                    return datetime.fromisoformat(date_str.replace('+00:00', ''))
                else:
                    return datetime.fromisoformat(date_str)
            return None
        except Exception as e:
            logger.warning(f"Failed to parse date '{date_str}': {e}")
            return None
    
    def prepare_message_data(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare message data for database insertion"""
        try:
            return {
                'message_id': message.get('message_id'),
                'chat_id': message.get('chat_id'),
                'chat_title': message.get('chat_title'),
                'sender_id': message.get('sender_id'),
                'sender_username': message.get('sender_username'),
                'sender_first_name': message.get('sender_first_name'),
                'sender_last_name': message.get('sender_last_name'),
                'message_text': message.get('message_text'),
                'message_date': self.parse_message_date(message.get('message_date')),
                'has_media': message.get('has_media'),
                'media_type': message.get('media_type'),
                'media_path': message.get('media_path'),
                'reply_to_msg_id': message.get('reply_to_msg_id'),
                'forward_from': str(message.get('forward_from')) if message.get('forward_from') else None,
                'scraped_at': self.parse_message_date(message.get('scraped_at')),
                'channel_name': message.get('channel_name'),
                'raw_data': message  # Store complete JSON
            }
        except Exception as e:
            logger.error(f"Failed to prepare message data: {e}")
            return None
    
    def insert_messages(self, messages: List[Dict[str, Any]], filename: str) -> int:
        """Insert messages into database, avoiding duplicates"""
        if not messages:
            logger.warning(f"No messages to insert from {filename}")
            return 0
        
        inserted_count = 0
        skipped_count = 0
        
        try:
            with self.engine.connect() as conn:
                for message in messages:
                    try:
                        # Prepare message data
                        message_data = self.prepare_message_data(message)
                        if not message_data:
                            continue
                        
                        # Insert message
                        insert_query = text("""
                            INSERT INTO raw.telegram_messages (
                                message_id, chat_id, chat_title, sender_id, sender_username,
                                sender_first_name, sender_last_name, message_text, message_date,
                                has_media, media_type, media_path, reply_to_msg_id, forward_from,
                                scraped_at, channel_name, raw_data
                            ) VALUES (
                                :message_id, :chat_id, :chat_title, :sender_id, :sender_username,
                                :sender_first_name, :sender_last_name, :message_text, :message_date,
                                :has_media, :media_type, :media_path, :reply_to_msg_id, :forward_from,
                                :scraped_at, :channel_name, :raw_data
                            )
                            ON CONFLICT (message_id) DO NOTHING
                        """)
                        
                        result = conn.execute(insert_query, message_data)
                        conn.commit()
                        
                        if result.rowcount > 0:
                            inserted_count += 1
                        else:
                            skipped_count += 1
                            
                    except IntegrityError:
                        # Message already exists (duplicate message_id)
                        skipped_count += 1
                        conn.rollback()
                    except Exception as e:
                        logger.error(f"Failed to insert message {message.get('message_id')}: {e}")
                        conn.rollback()
                        continue
                
                logger.info(f"File {filename}: {inserted_count} messages inserted, {skipped_count} skipped")
                return inserted_count
                
        except Exception as e:
            logger.error(f"Failed to insert messages from {filename}: {e}")
            return 0
    
    def load_json_file(self, filepath: str) -> List[Dict[str, Any]]:
        """Load and parse JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                return data
            else:
                logger.warning(f"Expected list in JSON file {filepath}, got {type(data)}")
                return []
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON file {filepath}: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to read file {filepath}: {e}")
            return []
    
    def process_files(self, base_path: str = "notebooks/data/raw/telegram_messages") -> Dict[str, int]:
        """Process all JSON files in the specified directory structure"""
        base_path = Path(base_path)
        
        if not base_path.exists():
            logger.error(f"Base path does not exist: {base_path}")
            return {}
        
        # Find all JSON files recursively
        json_files = list(base_path.rglob("*.json"))
        
        if not json_files:
            logger.warning(f"No JSON files found in {base_path}")
            return {}
        
        logger.info(f"Found {len(json_files)} JSON files to process")
        
        results = {}
        total_inserted = 0
        
        for filepath in json_files:
            try:
                logger.info(f"Processing file: {filepath}")
                
                # Load messages from JSON file
                messages = self.load_json_file(str(filepath))
                
                if messages:
                    # Insert messages into database
                    inserted = self.insert_messages(messages, filepath.name)
                    results[str(filepath)] = inserted
                    total_inserted += inserted
                else:
                    logger.warning(f"No messages found in {filepath}")
                    results[str(filepath)] = 0
                    
            except Exception as e:
                logger.error(f"Failed to process file {filepath}: {e}")
                results[str(filepath)] = 0
        
        logger.info(f"Processing complete. Total messages inserted: {total_inserted}")
        return results


def main():
    """Main function to run the Telegram message loader"""
    try:
        logger.info("Starting Telegram message loader")
        
        # Initialize loader
        loader = TelegramMessageLoader()
        
        # Process files
        results = loader.process_files()
        
        # Print summary
        print("\n" + "="*50)
        print("TELEGRAM MESSAGE LOADER SUMMARY")
        print("="*50)
        
        total_files = len(results)
        total_inserted = sum(results.values())
        
        print(f"Total files processed: {total_files}")
        print(f"Total messages inserted: {total_inserted}")
        print("\nFile-by-file results:")
        
        for filepath, inserted in results.items():
            print(f"  {Path(filepath).name}: {inserted} messages")
        
        print("="*50)
        
    except Exception as e:
        logger.error(f"Failed to run Telegram message loader: {e}")
        raise


if __name__ == "__main__":
    main() 