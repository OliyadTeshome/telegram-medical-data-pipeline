#!/usr/bin/env python3
"""
Test script to verify JSON serialization fix
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from scraper.telegram_scraper import TelegramScraper
import logging

async def test_json_fix():
    """Test the JSON serialization fix"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Initialize scraper
        scraper = TelegramScraper()
        print("✅ Scraper initialized")
        
        # Test connection
        if not await scraper.connect():
            print("❌ Failed to connect to Telegram")
            return
        
        print("✅ Connected to Telegram")
        
        # Test with first channel
        test_channel = scraper.target_channels[0]
        print(f"🔍 Testing with channel: {test_channel}")
        
        result = await scraper.scrape_channel(test_channel)
        
        print(f"\n📊 Test Results:")
        print(f"Channel: {result['channel_name']}")
        print(f"Status: {result['status']}")
        print(f"Messages: {result['message_count']}")
        print(f"Error: {result['error']}")
        
        if result['file_path']:
            print(f"File: {result['file_path']}")
            print("✅ JSON serialization successful!")
        else:
            print("❌ JSON serialization failed")
        
        await scraper.disconnect()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_json_fix()) 