#!/usr/bin/env python3
"""
Test script to verify that the notebook errors are fixed
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api_health():
    """Test if the API is running and healthy"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ API Health Check:")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Database: {data.get('database', 'unknown')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

def test_statistics():
    """Test the statistics endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/statistics")
        if response.status_code == 200:
            data = response.json()
            print("✅ Statistics Endpoint:")
            print(f"   Total Messages: {data.get('total_messages', 0)}")
            print(f"   Total Channels: {data.get('total_channels', 0)}")
            return True
        else:
            print(f"❌ Statistics failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Statistics error: {e}")
        return False

def test_top_products():
    """Test the top products endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/reports/top-products?limit=5")
        if response.status_code == 200:
            data = response.json()
            print("✅ Top Products Endpoint:")
            print(f"   Products found: {len(data)}")
            for product in data[:3]:
                print(f"   - {product.get('product_name', 'Unknown')}: {product.get('mention_count', 0)} mentions")
            return True
        else:
            print(f"❌ Top products failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Top products error: {e}")
        return False

def test_search():
    """Test the search endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/search/messages?query=medicine&limit=5")
        if response.status_code == 200:
            data = response.json()
            print("✅ Search Endpoint:")
            print(f"   Results found: {data.get('total_count', 0)}")
            return True
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Search error: {e}")
        return False

def test_channel_activity():
    """Test the channel activity endpoint"""
    try:
        # First get channels to find a valid channel name
        response = requests.get(f"{BASE_URL}/api/channels")
        if response.status_code == 200:
            channels = response.json()
            if channels:
                channel_name = channels[0]['channel_name']
                # Test channel activity
                response = requests.get(f"{BASE_URL}/api/channels/{channel_name}/activity?period=daily&limit=5")
                if response.status_code == 200:
                    data = response.json()
                    print("✅ Channel Activity Endpoint:")
                    print(f"   Channel: {channel_name}")
                    print(f"   Activity records: {len(data)}")
                    return True
                else:
                    print(f"❌ Channel activity failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
            else:
                print("❌ No channels found to test activity")
                return False
        else:
            print(f"❌ Cannot get channels: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Channel activity error: {e}")
        return False

def test_all_endpoints():
    """Test all endpoints"""
    print("🧪 Testing All Endpoints")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_api_health),
        ("Statistics", test_statistics),
        ("Top Products", test_top_products),
        ("Search", test_search),
        ("Channel Activity", test_channel_activity)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Testing: {test_name}")
        success = test_func()
        results.append((test_name, success))
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\n🎯 Overall: {successful}/{total} tests passed")
    
    if successful == total:
        print("🎉 All tests passed! The notebook should work correctly now.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    print("Testing FastAPI Notebook Fixes")
    print("=" * 50)
    test_all_endpoints() 