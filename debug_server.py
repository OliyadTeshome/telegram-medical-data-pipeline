#!/usr/bin/env python3
"""
Debug script to check server status and test endpoints
"""

import requests
import time

def debug_server():
    """Debug the server status"""
    base_url = "http://localhost:8000"
    
    print("🔍 Debugging FastAPI Server")
    print("=" * 40)
    
    # Test 1: Basic connectivity
    try:
        print("1. Testing basic connectivity...")
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return
    
    # Test 2: Channel activity (the problematic endpoint)
    try:
        print("\n2. Testing channel activity endpoint...")
        # First get channels
        response = requests.get(f"{base_url}/api/channels", timeout=5)
        if response.status_code == 200:
            channels = response.json()
            if channels:
                channel_name = channels[0]['channel_name']
                print(f"   Testing with channel: {channel_name}")
                
                # Test the problematic endpoint
                response = requests.get(f"{base_url}/api/channels/{channel_name}/activity?period=daily&limit=3", timeout=5)
                print(f"   Status Code: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ SUCCESS! Found {len(data)} activity records")
                else:
                    print(f"   ❌ FAILED: {response.text}")
            else:
                print("   No channels found")
        else:
            print(f"   ❌ Cannot get channels: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Check if server is running the updated code
    try:
        print("\n3. Testing root endpoint...")
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   API Version: {data.get('version', 'unknown')}")
            print(f"   Database Status: {data.get('database_status', 'unknown')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    debug_server() 