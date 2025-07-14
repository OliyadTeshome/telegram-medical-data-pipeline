import os
import json
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from telethon import TelegramClient
from telethon.errors import (
    FloodWaitError, 
    ChannelPrivateError, 
    UsernameNotOccupiedError,
    ChatAdminRequiredError,
    SessionPasswordNeededError
)
from telethon.tl.types import Message, Chat, User, MessageMediaPhoto, MessageMediaDocument
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TelegramScraper:
    """
    Asynchronous Telegram scraper using Telethon library.
    Scrapes messages from public channels and saves them in JSON format.
    Also downloads image attachments.
    """
    
    def __init__(self):
        """Initialize the scraper with configuration"""
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.phone = os.getenv('TELEGRAM_PHONE')
        self.session_name = os.getenv('TELEGRAM_SESSION_NAME', 'medical_pipeline_session')
        self.client: Optional[TelegramClient] = None
        
        # Validate required environment variables
        if not all([self.api_id, self.api_hash, self.phone]):
            raise ValueError("Missing required environment variables: TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE")
        
        # Target channels for medical data
        self.target_channels = [
            'https://t.me/CheMed123',
            'https://t.me/lobelia4cosmetics', 
            'https://t.me/tikvahpharma'
        ]
        
        logger.info(f"Initialized TelegramScraper with {len(self.target_channels)} target channels")
    
    async def connect(self) -> bool:
        """
        Initialize and connect to Telegram client
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
            await self.client.start(phone=self.phone)
            logger.info("Successfully connected to Telegram")
            return True
        except SessionPasswordNeededError:
            logger.error("Two-factor authentication required. Please check your Telegram account.")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to Telegram: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from Telegram client"""
        if self.client:
            await self.client.disconnect()
            logger.info("Disconnected from Telegram")
    
    def _extract_channel_name(self, channel_url: str) -> str:
        """
        Extract channel name from URL
        
        Args:
            channel_url: Telegram channel URL
            
        Returns:
            str: Channel name without @ symbol
        """
        return channel_url.split('/')[-1]
    
    def _safe_serialize_value(self, value) -> Any:
        """
        Safely serialize a value for JSON output
        
        Args:
            value: Any value to serialize
            
        Returns:
            Any: JSON-serializable value
        """
        if value is None:
            return None
        elif isinstance(value, (str, int, float, bool)):
            return value
        elif hasattr(value, '__dict__'):
            # For Telegram objects, try to get string representation
            return str(value)
        else:
            # For other objects, convert to string
            return str(value)
    
    async def download_media(self, message: Message, channel_name: str) -> Optional[str]:
        """
        Download media from a message if it's an image
        
        Args:
            message: Telegram message object
            channel_name: Name of the channel
            
        Returns:
            Optional[str]: Path to downloaded image or None if not an image
        """
        if not message.media:
            return None
        
        try:
            # Check if it's a photo
            if isinstance(message.media, MessageMediaPhoto):
                today = datetime.now().strftime('%Y-%m-%d')
                base_path = 'data/raw/telegram_images'
                channel_path = os.path.join(base_path, today, channel_name)
                
                # Create directory structure
                os.makedirs(channel_path, exist_ok=True)
                
                # Generate filename using message ID
                filename = f"{message.id}.jpg"
                file_path = os.path.join(channel_path, filename)
                
                # Download the photo
                await self.client.download_media(message.media, file_path)
                
                logger.info(f"Downloaded image: {file_path}")
                return file_path
                
        except Exception as e:
            logger.error(f"Error downloading media for message {message.id}: {e}")
            return None
        
        return None
    
    async def get_channel_messages(self, channel_url: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Extract messages from a Telegram channel
        
        Args:
            channel_url: Telegram channel URL
            limit: Maximum number of messages to scrape
            
        Returns:
            List[Dict[str, Any]]: List of message data dictionaries
        """
        if not self.client:
            connected = await self.connect()
            if not connected:
                return []
        
        messages = []
        channel_name = self._extract_channel_name(channel_url)
        
        try:
            logger.info(f"Starting to scrape channel: {channel_name}")
            
            # Get channel entity
            channel = await self.client.get_entity(channel_url)
            
            # Iterate through messages
            message_count = 0
            async for message in self.client.iter_messages(channel, limit=limit):
                if message and message.text:  # Only process text messages
                    # Download media if present
                    media_path = await self.download_media(message, channel_name)
                    
                    message_data = {
                        'message_id': self._safe_serialize_value(message.id),
                        'chat_id': self._safe_serialize_value(message.chat_id),
                        'chat_title': self._safe_serialize_value(getattr(message.chat, 'title', '')),
                        'sender_id': self._safe_serialize_value(message.sender_id),
                        'sender_username': self._safe_serialize_value(getattr(message.sender, 'username', '')),
                        'sender_first_name': self._safe_serialize_value(getattr(message.sender, 'first_name', '')),
                        'sender_last_name': self._safe_serialize_value(getattr(message.sender, 'last_name', '')),
                        'message_text': self._safe_serialize_value(message.text),
                        'message_date': self._safe_serialize_value(message.date.isoformat()),
                        'has_media': self._safe_serialize_value(message.media is not None),
                        'media_type': self._safe_serialize_value(type(message.media).__name__ if message.media else None),
                        'media_path': self._safe_serialize_value(media_path),
                        'reply_to_msg_id': self._safe_serialize_value(message.reply_to_msg_id),
                        'forward_from': self._safe_serialize_value(getattr(message.forward, 'from_id', None) if message.forward else None),
                        'scraped_at': self._safe_serialize_value(datetime.now().isoformat()),
                        'channel_name': self._safe_serialize_value(channel_name)
                    }
                    messages.append(message_data)
                    message_count += 1
                    
                    # Log progress every 100 messages
                    if message_count % 100 == 0:
                        logger.info(f"Scraped {message_count} messages from {channel_name}")
            
            logger.info(f"Successfully scraped {len(messages)} messages from {channel_name}")
            return messages
            
        except FloodWaitError as e:
            wait_time = e.seconds
            logger.warning(f"Rate limit hit for {channel_name}. Waiting {wait_time} seconds...")
            await asyncio.sleep(wait_time)
            return await self.get_channel_messages(channel_url, limit)
            
        except ChannelPrivateError:
            logger.error(f"Channel {channel_name} is private and cannot be accessed")
            return []
            
        except UsernameNotOccupiedError:
            logger.error(f"Channel {channel_name} does not exist or has been deleted")
            return []
            
        except ChatAdminRequiredError:
            logger.error(f"Admin privileges required to access {channel_name}")
            return []
            
        except Exception as e:
            logger.error(f"Error scraping channel {channel_name}: {e}")
            return []
    
    def save_messages_to_json(self, messages: List[Dict[str, Any]], channel_name: str) -> str:
        """
        Save messages to JSON file with date-based directory structure
        
        Args:
            messages: List of message dictionaries
            channel_name: Name of the channel
            
        Returns:
            str: Path to the saved JSON file
        """
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            base_path = 'data/raw/telegram_messages'
            channel_path = os.path.join(base_path, today, channel_name)
            
            # Create directory structure
            os.makedirs(channel_path, exist_ok=True)
            
            file_path = os.path.join(channel_path, f'{channel_name}.json')
            
            # Additional safety check for JSON serialization
            def safe_json_serialize(obj):
                """Custom JSON encoder to handle non-serializable objects"""
                if hasattr(obj, '__dict__'):
                    return str(obj)
                return obj
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(messages, f, ensure_ascii=False, indent=2, default=safe_json_serialize)
            
            logger.info(f"Saved {len(messages)} messages to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving messages for {channel_name}: {e}")
            raise
    
    async def scrape_channel(self, channel_url: str) -> Dict[str, Any]:
        """
        Scrape a single channel and save results
        
        Args:
            channel_url: Telegram channel URL
            
        Returns:
            Dict[str, Any]: Scraping results summary
        """
        channel_name = self._extract_channel_name(channel_url)
        start_time = datetime.now()
        
        try:
            logger.info(f"Starting scrape for channel: {channel_name}")
            
            # Get messages
            messages = await self.get_channel_messages(channel_url, limit=1000)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if messages:
                # Save to JSON
                file_path = self.save_messages_to_json(messages, channel_name)
                
                logger.info(f"Completed scraping {channel_name}: {len(messages)} messages in {duration:.2f}s")
                
                return {
                    'channel_name': channel_name,
                    'channel_url': channel_url,
                    'message_count': len(messages),
                    'file_path': file_path,
                    'status': 'success',
                    'error': None,
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'duration_seconds': duration
                }
            else:
                logger.warning(f"No messages found for {channel_name}")
                
                return {
                    'channel_name': channel_name,
                    'channel_url': channel_url,
                    'message_count': 0,
                    'file_path': None,
                    'status': 'no_messages',
                    'error': 'No messages found or channel inaccessible',
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'duration_seconds': duration
                }
                
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.error(f"Failed to scrape {channel_name}: {e}")
            
            # Check if it's a JSON serialization error
            if "JSON serializable" in str(e) or "not JSON serializable" in str(e):
                error_msg = f"JSON serialization error: {str(e)}. This usually happens with Telegram objects that can't be serialized."
            else:
                error_msg = str(e)
            
            return {
                'channel_name': channel_name,
                'channel_url': channel_url,
                'message_count': 0,
                'file_path': None,
                'status': 'error',
                'error': error_msg,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration
            }
    
    async def scrape_all_channels(self) -> List[Dict[str, Any]]:
        """
        Scrape all target channels
        
        Returns:
            List[Dict[str, Any]]: List of scraping results for each channel
        """
        overall_start_time = datetime.now()
        logger.info(f"Starting scrape for {len(self.target_channels)} channels")
        
        results = []
        for channel_url in self.target_channels:
            result = await self.scrape_channel(channel_url)
            results.append(result)
            
            # Add delay between channels to avoid rate limiting
            await asyncio.sleep(2)
        
        overall_end_time = datetime.now()
        overall_duration = (overall_end_time - overall_start_time).total_seconds()
        
        # Log summary
        successful_scrapes = sum(1 for r in results if r['status'] == 'success')
        total_messages = sum(r['message_count'] for r in results)
        
        logger.info(f"Scraping completed in {overall_duration:.2f}s. "
                   f"{successful_scrapes}/{len(self.target_channels)} channels successful. "
                   f"Total messages scraped: {total_messages}")
        
        return results

async def main():
    """Main function for testing the scraper"""
    scraper = TelegramScraper()
    
    try:
        # Connect to Telegram
        if not await scraper.connect():
            logger.error("Failed to connect to Telegram. Exiting.")
            return
        
        # Scrape all channels
        results = await scraper.scrape_all_channels()
        
        # Print summary
        print("\n=== Scraping Summary ===")
        for result in results:
            status_icon = "✅" if result['status'] == 'success' else "❌"
            print(f"{status_icon} {result['channel_name']}: {result['message_count']} messages")
            if result['error']:
                print(f"   Error: {result['error']}")
        
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
    
    finally:
        await scraper.disconnect()

if __name__ == "__main__":
    asyncio.run(main()) 