# Telegram Message Loader

This script reads Telegram message JSON files and loads them into a PostgreSQL database.

## Features

- Reads JSON files from `notebooks/data/raw/telegram_messages/`
- Inserts messages into `raw.telegram_messages` table
- Avoids duplicate inserts using `message_id` as unique key
- Comprehensive logging and error handling
- Uses environment variables for database configuration

## Database Schema

The script creates a `raw.telegram_messages` table with the following columns:

- `id`: Auto-incrementing primary key
- `message_id`: Unique identifier for the message (used for duplicate prevention)
- `chat_id`: Telegram chat ID
- `chat_title`: Chat title
- `sender_id`: Sender's Telegram ID
- `sender_username`: Sender's username
- `sender_first_name`: Sender's first name
- `sender_last_name`: Sender's last name
- `message_text`: Message content
- `message_date`: Message timestamp
- `has_media`: Boolean indicating if message has media
- `media_type`: Type of media (if any)
- `media_path`: Path to media file (if any)
- `reply_to_msg_id`: ID of message being replied to
- `forward_from`: Forward source information
- `scraped_at`: When the message was scraped
- `channel_name`: Channel name
- `raw_data`: Complete JSON data (for flexibility)
- `created_at`: When the record was inserted

## Setup

1. **Environment Variables**: Create a `.env` file in the project root with:

```bash
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=telegram_medical
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
```

2. **Database**: Ensure PostgreSQL is running and the `telegram_medical` database exists:

```sql
CREATE DATABASE telegram_medical;
```

3. **Dependencies**: Install required packages:

```bash
pip install sqlalchemy psycopg2-binary python-dotenv
```

## Usage

Run the script from the project root:

```bash
python scripts/load_telegram_messages.py
```

## Expected File Structure

The script expects JSON files in the following structure:

```
notebooks/data/raw/telegram_messages/
├── 2025-07-14/
│   ├── tikvahpharma/
│   │   └── tikvahpharma.json
│   ├── lobelia4cosmetics/
│   │   └── lobelia4cosmetics.json
│   └── CheMed123/
│       └── CheMed123.json
```

## JSON Format

Each JSON file should contain an array of message objects with fields like:

```json
[
  {
    "message_id": 172656,
    "chat_id": -1001569871437,
    "chat_title": "Tikvah | Pharma",
    "sender_id": -1001353257880,
    "sender_username": "tikvah_tena",
    "message_text": "Message content...",
    "message_date": "2025-07-14T18:27:36+00:00",
    "has_media": false,
    "media_type": null,
    "channel_name": "tikvahpharma"
  }
]
```

## Logging

The script creates a `telegram_loader.log` file with detailed information about:
- Database connection status
- Files processed
- Number of messages inserted per file
- Errors and warnings

## Error Handling

- Duplicate messages are automatically skipped
- Invalid JSON files are logged and skipped
- Database connection errors are handled gracefully
- Individual message insertion failures don't stop the entire process

## Output

The script provides a summary showing:
- Total files processed
- Total messages inserted
- File-by-file breakdown of insertions 