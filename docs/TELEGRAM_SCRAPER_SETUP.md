# Telegram Scraper Setup Guide

## Overview
The Telegram scraper is an asynchronous Python application that scrapes messages from public Telegram channels and saves them in JSON format. It's designed to be modular and ready for scheduling.

## Features
- ✅ Asynchronous scraping using Telethon
- ✅ Rate limit handling with automatic retry
- ✅ Comprehensive error handling for various Telegram errors
- ✅ Detailed logging with progress tracking
- ✅ Modular design for easy scheduling
- ✅ Date-based file organization
- ✅ Support for multiple channels

## Target Channels
The scraper is configured to scrape the following medical-related channels:
1. `https://t.me/CheMed123`
2. `https://t.me/lobelia4cosmetics`
3. `https://t.me/tikvahpharma`

## Environment Variables Setup

Create a `.env` file in the project root with the following variables:

```bash
# Telegram API Configuration
# Get these from https://my.telegram.org/apps
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE=your_phone_number_here
TELEGRAM_SESSION_NAME=medical_pipeline_session

# Optional: Data paths (defaults provided)
RAW_DATA_PATH=data/raw
PROCESSED_DATA_PATH=data/processed
```

### Getting Telegram API Credentials

1. Go to https://my.telegram.org/apps
2. Log in with your phone number
3. Create a new application
4. Copy the `api_id` and `api_hash`
5. Add your phone number in international format (e.g., +1234567890)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your `.env` file with the required credentials

3. Run the test script:
```bash
python scripts/test_scraper.py
```

## Usage

### Basic Usage
```python
from src.scraper.telegram_scraper import TelegramScraper
import asyncio

async def main():
    scraper = TelegramScraper()
    
    # Connect to Telegram
    if await scraper.connect():
        # Scrape all channels
        results = await scraper.scrape_all_channels()
        
        # Print results
        for result in results:
            print(f"{result['channel_name']}: {result['message_count']} messages")
        
        await scraper.disconnect()

asyncio.run(main())
```

### Scraping Individual Channels
```python
# Scrape a single channel
result = await scraper.scrape_channel('https://t.me/CheMed123')
print(f"Scraped {result['message_count']} messages from {result['channel_name']}")
```

## Output Structure

The scraper saves data in the following structure:
```
data/raw/
└── YYYY-MM-DD/
    ├── CheMed123/
    │   └── messages.json
    ├── lobelia4cosmetics/
    │   └── messages.json
    └── tikvahpharma/
        └── messages.json
```

## Message Data Format

Each message is saved with the following structure:
```json
{
  "message_id": 12345,
  "chat_id": 67890,
  "chat_title": "Channel Name",
  "sender_id": 11111,
  "sender_username": "username",
  "sender_first_name": "First",
  "sender_last_name": "Last",
  "message_text": "Message content",
  "message_date": "2024-01-15T10:30:00+00:00",
  "has_media": false,
  "media_type": null,
  "reply_to_msg_id": null,
  "forward_from": null,
  "scraped_at": "2024-01-15T10:35:00+00:00",
  "channel_name": "CheMed123"
}
```

## Error Handling

The scraper handles various Telegram errors:

- **FloodWaitError**: Automatically waits and retries
- **ChannelPrivateError**: Logs error for private channels
- **UsernameNotOccupiedError**: Logs error for non-existent channels
- **ChatAdminRequiredError**: Logs error for admin-only channels
- **SessionPasswordNeededError**: Handles 2FA requirements

## Logging

The scraper provides detailed logging:
- Connection status
- Scraping progress (every 100 messages)
- Error details
- Summary statistics

Logs are saved to `telegram_scraper.log` and also displayed in console.

## Scheduling

The scraper is designed to be easily scheduled. You can:

1. **Use cron jobs**:
```bash
# Run daily at 2 AM
0 2 * * * cd /path/to/project && python src/scraper/telegram_scraper.py
```

2. **Use Airflow DAGs** (see `dags/telegram_pipeline.py`)

3. **Use systemd timers** or other scheduling tools

## Rate Limiting

The scraper includes built-in rate limiting:
- 2-second delay between channels
- Automatic handling of Telegram's flood wait errors
- Progress logging to monitor scraping speed

## Troubleshooting

### Common Issues

1. **"Missing required environment variables"**
   - Ensure your `.env` file exists and has all required variables

2. **"Two-factor authentication required"**
   - Check your Telegram account for 2FA requirements
   - You may need to log in manually first

3. **"Channel is private"**
   - Some channels may be private or restricted
   - Check channel URLs are correct and public

4. **"Rate limit hit"**
   - The scraper will automatically wait and retry
   - Consider reducing the number of channels or frequency

### Debug Mode

Enable debug logging by modifying the logging level:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Security Notes

- Never commit your `.env` file to version control
- Keep your Telegram API credentials secure
- The session file contains authentication data - keep it secure
- Consider using environment variables in production

## Performance

- Scrapes up to 1000 messages per channel
- Asynchronous design for better performance
- Automatic rate limiting to avoid API restrictions
- Progress tracking for long-running scrapes 