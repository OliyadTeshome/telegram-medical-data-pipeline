#!/usr/bin/env python3
"""
Quick test to verify the FastAPI fixes work
"""

import requests
import time

def quick_test():
    """Quick test of the main endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Quick FastAPI Test")
    print("=" * 30)
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check: PASS")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Database: {data.get('database')}")
        else:
            print(f"❌ Health check: FAIL ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Health check: ERROR ({e})")
        return False
    
    # Test 2: Statistics
    try:
        response = requests.get(f"{base_url}/api/statistics", timeout=5)
        if response.status_code == 200:
            print("✅ Statistics: PASS")
            data = response.json()
            print(f"   Messages: {data.get('total_messages', 0)}")
            print(f"   Channels: {data.get('total_channels', 0)}")
        else:
            print(f"❌ Statistics: FAIL ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Statistics: ERROR ({e})")
        return False
    
    # Test 3: Top products
    try:
        response = requests.get(f"{base_url}/api/reports/top-products?limit=3", timeout=5)
        if response.status_code == 200:
            print("✅ Top products: PASS")
            data = response.json()
            print(f"   Products found: {len(data)}")
        else:
            print(f"❌ Top products: FAIL ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Top products: ERROR ({e})")
        return False
    
    # Test 4: Channel activity (this was the problematic one)
    try:
        # First get a channel name
        response = requests.get(f"{base_url}/api/channels", timeout=5)
        if response.status_code == 200:
            channels = response.json()
            if channels:
                channel_name = channels[0]['channel_name']
                # Test channel activity
                response = requests.get(f"{base_url}/api/channels/{channel_name}/activity?period=daily&limit=3", timeout=5)
                if response.status_code == 200:
                    print("✅ Channel activity: PASS")
                    data = response.json()
                    print(f"   Activity records: {len(data)}")
                else:
                    print(f"❌ Channel activity: FAIL ({response.status_code})")
                    print(f"   Response: {response.text}")
                    return False
            else:
                print("⚠️  Channel activity: SKIP (no channels)")
        else:
            print(f"❌ Get channels: FAIL ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Channel activity: ERROR ({e})")
        return False
    
    print("\n🎉 All tests passed! The notebook should work correctly now.")
    return True

if __name__ == "__main__":
    print("Testing FastAPI fixes...")
    success = quick_test()
    
    if success:
        print("\n✅ Ready to run the notebook!")
        print("💡 Restart your Jupyter kernel and run the notebook cells.")
    else:
        print("\n❌ Some tests failed. Check the server and try again.") 