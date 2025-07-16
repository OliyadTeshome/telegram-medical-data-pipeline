#!/usr/bin/env python3
"""
Test script to verify Telegram API connection
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import (
    FloodWaitError, 
    ChannelPrivateError, 
    UsernameNotOccupiedError,
    ChatAdminRequiredError,
    SessionPasswordNeededError
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_telegram_connection():
    """Test Telegram API connection"""
    
    # Get credentials from environment
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    phone = os.getenv('TELEGRAM_PHONE')
    session_name = os.getenv('TELEGRAM_SESSION_NAME', 'test_session')
    
    # Validate credentials
    if not api_id or api_id == 'your_api_id_here':
        print("❌ ERROR: TELEGRAM_API_ID not set or invalid")
        print("Please set your API ID in the .env file")
        return False
        
    if not api_hash or api_hash == 'your_api_hash_here':
        print("❌ ERROR: TELEGRAM_API_HASH not set or invalid")
        print("Please set your API hash in the .env file")
        return False
        
    if not phone or phone == 'your_phone_number_here':
        print("❌ ERROR: TELEGRAM_PHONE not set or invalid")
        print("Please set your phone number in the .env file")
        return False
    
    print(f"🔧 Testing connection with:")
    print(f"   API ID: {api_id}")
    print(f"   Phone: {phone}")
    print(f"   Session: {session_name}")
    
    try:
        # Create client
        client = TelegramClient(session_name, api_id, api_hash)
        
        # Start client
        print("📱 Connecting to Telegram...")
        print("📲 Check your Telegram app for a verification code!")
        print("   The code will be sent as a message from 'Telegram'")
        print("   Enter the 5-digit code when prompted below")
        
        await client.start(phone=phone)
        
        # Test connection
        me = await client.get_me()
        print(f"✅ Successfully connected!")
        print(f"   Logged in as: {me.first_name} (@{me.username})")
        
        # Test getting a public channel
        try:
            channel = await client.get_entity('https://t.me/CheMed123')
            print(f"✅ Successfully accessed test channel: {channel.title}")
        except Exception as e:
            print(f"⚠️  Warning: Could not access test channel: {e}")
        
        # Disconnect
        await client.disconnect()
        print("🔌 Disconnected from Telegram")
        
        return True
        
    except SessionPasswordNeededError:
        print("❌ ERROR: Two-factor authentication required")
        print("Please check your Telegram account for 2FA code")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: Failed to connect: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure your API credentials are correct")
        print("2. Check if your phone number is in international format (+1234567890)")
        print("3. Ensure you have internet connection")
        print("4. Try deleting the session file and reconnecting")
        print("5. Check your Telegram app for the verification code")
        return False

if __name__ == "__main__":
    print("🚀 Telegram API Connection Test")
    print("=" * 40)
    
    # Run the test
    success = asyncio.run(test_telegram_connection())
    
    if success:
        print("\n🎉 All tests passed! Your Telegram API is working correctly.")
    else:
        print("\n💥 Connection test failed. Please check the errors above.") 