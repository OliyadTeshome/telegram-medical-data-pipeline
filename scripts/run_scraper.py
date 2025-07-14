#!/usr/bin/env python3
"""
Standalone script to run the Telegram scraper
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from scraper.telegram_scraper import TelegramScraper
import logging

async def run_scraper():
    """Run the Telegram scraper"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    print("🚀 Starting Telegram Medical Data Scraper")
    print("=" * 50)
    
    try:
        # Initialize scraper
        scraper = TelegramScraper()
        print("✅ Scraper initialized")
        
        # Connect to Telegram
        print("🔌 Connecting to Telegram...")
        if not await scraper.connect():
            print("❌ Failed to connect to Telegram")
            return
        
        print("✅ Connected to Telegram")
        
        # Scrape all channels
        print("\n📡 Starting to scrape channels...")
        results = await scraper.scrape_all_channels()
        
        # Print results
        print("\n📊 Scraping Results:")
        print("-" * 30)
        
        total_messages = 0
        successful_channels = 0
        
        for result in results:
            status_icon = "✅" if result['status'] == 'success' else "❌"
            print(f"{status_icon} {result['channel_name']}")
            print(f"   Messages: {result['message_count']}")
            print(f"   Status: {result['status']}")
            
            if result['file_path']:
                print(f"   File: {result['file_path']}")
            
            if result['error']:
                print(f"   Error: {result['error']}")
            
            if result['status'] == 'success':
                successful_channels += 1
                total_messages += result['message_count']
            
            print()
        
        # Summary
        print("=" * 50)
        print(f"📈 Summary:")
        print(f"   Successful channels: {successful_channels}/{len(results)}")
        print(f"   Total messages scraped: {total_messages}")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if successful_channels > 0:
            print("✅ Scraping completed successfully!")
        else:
            print("⚠️  No channels were scraped successfully")
        
        await scraper.disconnect()
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(run_scraper()) 