#!/usr/bin/env python3
"""
Test script to verify path issues and fix them
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from src.utils.config import get_config

def test_paths():
    """Test and fix path issues"""
    print("🔍 Testing Path Configuration")
    print("=" * 50)
    
    config = get_config()
    
    # Test raw data path
    raw_path = config.raw_data_path
    print(f"Raw data path: {raw_path}")
    print(f"Path exists: {os.path.exists(raw_path)}")
    print(f"Path is absolute: {os.path.isabs(raw_path)}")
    
    # Test processed data path
    processed_path = config.processed_data_path
    print(f"Processed data path: {processed_path}")
    print(f"Path exists: {os.path.exists(processed_path)}")
    print(f"Path is absolute: {os.path.isabs(processed_path)}")
    
    # Create directories if they don't exist
    print("\n📁 Creating directories if needed...")
    
    for path in [raw_path, processed_path]:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            print(f"✅ Created directory: {path}")
        else:
            print(f"✅ Directory already exists: {path}")
    
    # Test file operations
    print("\n📄 Testing file operations...")
    
    # Create a test JSON file
    test_file = os.path.join(raw_path, "test_messages.json")
    test_data = [
        {
            "message_id": 1,
            "chat_id": 123456789,
            "chat_title": "Test Channel",
            "sender_id": 987654321,
            "sender_username": "test_user",
            "sender_first_name": "Test",
            "sender_last_name": "User",
            "message_text": "This is a test message",
            "message_date": "2025-07-16T02:50:00",
            "has_media": False,
            "media_path": None,
            "channel_name": "test_channel"
        }
    ]
    
    try:
        import json
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2)
        print(f"✅ Created test file: {test_file}")
        
        # Test reading the file
        with open(test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Successfully read test file with {len(data)} records")
        
        # Clean up test file
        os.remove(test_file)
        print(f"✅ Cleaned up test file")
        
    except Exception as e:
        print(f"❌ Error with file operations: {e}")
        return False
    
    print("\n🎉 All path tests passed!")
    return True

if __name__ == "__main__":
    success = test_paths()
    
    if success:
        print("\n✅ Path configuration is working correctly!")
    else:
        print("\n❌ Path configuration has issues!") 