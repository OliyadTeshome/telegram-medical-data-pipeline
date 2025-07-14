import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from telethon import TelegramClient
from telethon.tl.types import Message, Chat, User
from dotenv import load_dotenv

load_dotenv()

class TelegramScraper:
    def __init__(self):
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.phone = os.getenv('TELEGRAM_PHONE')
        self.session_name = os.getenv('TELEGRAM_SESSION_NAME', 'medical_pipeline_session')
        self.client = None
        
    async def connect(self):
        """Initialize and connect to Telegram client"""
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
        await self.client.start(phone=self.phone)
        
    async def disconnect(self):
        """Disconnect from Telegram client"""
        if self.client:
            await self.client.disconnect()
            
    async def get_channel_messages(self, channel_username: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Extract messages from a Telegram channel"""
        if not self.client:
            await self.connect()
            
        messages = []
        try:
            channel = await self.client.get_entity(channel_username)
            async for message in self.client.iter_messages(channel, limit=limit):
                if message.text:  # Only process text messages for now
                    message_data = {
                        'message_id': message.id,
                        'chat_id': message.chat_id,
                        'chat_title': getattr(message.chat, 'title', ''),
                        'sender_id': message.sender_id,
                        'sender_username': getattr(message.sender, 'username', ''),
                        'message_text': message.text,
                        'message_date': message.date.isoformat(),
                        'has_media': message.media is not None,
                        'media_type': type(message.media).__name__ if message.media else None,
                        'media_path': None  # Will be handled separately
                    }
                    messages.append(message_data)
        except Exception as e:
            print(f"Error scraping channel {channel_username}: {e}")
            
        return messages
    
    async def download_media(self, message_id: int, save_path: str) -> str:
        """Download media from a message"""
        if not self.client:
            await self.connect()
            
        try:
            message = await self.client.get_messages(self.chat_id, ids=message_id)
            if message and message.media:
                file_path = await message.download_media(save_path)
                return file_path
        except Exception as e:
            print(f"Error downloading media for message {message_id}: {e}")
            
        return None
    
    def save_messages_to_json(self, messages: List[Dict[str, Any]], channel_name: str):
        """Save messages to JSON file with date-based directory structure"""
        today = datetime.now().strftime('%Y-%m-%d')
        base_path = os.getenv('RAW_DATA_PATH', 'data/raw')
        channel_path = os.path.join(base_path, today, channel_name)
        
        os.makedirs(channel_path, exist_ok=True)
        
        file_path = os.path.join(channel_path, 'messages.json')
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
            
        return file_path

async def main():
    """Main function for testing the scraper"""
    scraper = TelegramScraper()
    
    # Example channels (replace with actual medical channels)
    channels = ['@medical_channel_1', '@health_news']
    
    for channel in channels:
        print(f"Scraping channel: {channel}")
        messages = await scraper.get_channel_messages(channel, limit=50)
        
        if messages:
            file_path = scraper.save_messages_to_json(messages, channel.replace('@', ''))
            print(f"Saved {len(messages)} messages to {file_path}")
    
    await scraper.disconnect()

if __name__ == "__main__":
    asyncio.run(main()) 