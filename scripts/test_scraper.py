#!/usr/bin/env python3
"""
Test script for the Telegram scraper
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from scraper.telegram_scraper import TelegramScraper
import logging

async def test_scraper():
    """Test the Telegram scraper functionality"""
    
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Initialize scraper
        scraper = TelegramScraper()
        print("✅ Scraper initialized successfully")
        
        # Test connection
        connected = await scraper.connect()
        if connected:
            print("✅ Successfully connected to Telegram")
        else:
            print("❌ Failed to connect to Telegram")
            return
        
        # Test scraping a single channel
        print("\n🔍 Testing single channel scrape...")
        test_channel = 'https://t.me/CheMed123'
        result = await scraper.scrape_channel(test_channel)
        
        print(f"Channel: {result['channel_name']}")
        print(f"Status: {result['status']}")
        print(f"Messages scraped: {result['message_count']}")
        if result['file_path']:
            print(f"File saved: {result['file_path']}")
        if result['error']:
            print(f"Error: {result['error']}")
        
        # Test scraping all channels
        print("\n🔍 Testing all channels scrape...")
        results = await scraper.scrape_all_channels()
        
        print("\n📊 Final Results:")
        for result in results:
            status_icon = "✅" if result['status'] == 'success' else "❌"
            print(f"{status_icon} {result['channel_name']}: {result['message_count']} messages")
        
        await scraper.disconnect()
        print("\n✅ Test completed successfully")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        logging.error(f"Test error: {e}")

if __name__ == "__main__":
    asyncio.run(test_scraper()) 