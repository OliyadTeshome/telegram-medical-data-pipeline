#!/usr/bin/env python3
"""
Test script for the FastAPI application
"""

import requests
import json
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_health_check() -> bool:
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Is it running?")
        return False

def test_root_endpoint() -> bool:
    """Test the root endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint passed: {data.get('message', 'Unknown')}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
        return False

def test_channels_endpoint() -> bool:
    """Test the channels endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/channels?limit=5")
        if response.status_code == 200:
            channels = response.json()
            print(f"✅ Channels endpoint passed: {len(channels)} channels returned")
            return True
        else:
            print(f"❌ Channels endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Channels endpoint error: {e}")
        return False

def test_messages_endpoint() -> bool:
    """Test the messages endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/messages?limit=5")
        if response.status_code == 200:
            messages = response.json()
            print(f"✅ Messages endpoint passed: {len(messages)} messages returned")
            return True
        else:
            print(f"❌ Messages endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Messages endpoint error: {e}")
        return False

def test_search_endpoint() -> bool:
    """Test the search endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/search/messages?query=test&limit=5")
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Search endpoint passed: {results.get('total_count', 0)} results found")
            return True
        else:
            print(f"❌ Search endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Search endpoint error: {e}")
        return False

def test_statistics_endpoint() -> bool:
    """Test the statistics endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/statistics")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Statistics endpoint passed: {stats.get('total_messages', 0)} total messages")
            return True
        else:
            print(f"❌ Statistics endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Statistics endpoint error: {e}")
        return False

def test_top_products_endpoint() -> bool:
    """Test the top products endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/reports/top-products?limit=5")
        if response.status_code == 200:
            products = response.json()
            print(f"✅ Top products endpoint passed: {len(products)} products returned")
            return True
        else:
            print(f"❌ Top products endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Top products endpoint error: {e}")
        return False

def test_documentation_endpoints() -> bool:
    """Test if documentation endpoints are accessible"""
    try:
        # Test Swagger UI
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ Swagger UI accessible")
        else:
            print(f"❌ Swagger UI not accessible: {response.status_code}")
            return False
        
        # Test ReDoc
        response = requests.get(f"{BASE_URL}/redoc")
        if response.status_code == 200:
            print("✅ ReDoc accessible")
        else:
            print(f"❌ ReDoc not accessible: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Documentation endpoints error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing FastAPI Application")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Root Endpoint", test_root_endpoint),
        ("Channels Endpoint", test_channels_endpoint),
        ("Messages Endpoint", test_messages_endpoint),
        ("Search Endpoint", test_search_endpoint),
        ("Statistics Endpoint", test_statistics_endpoint),
        ("Top Products Endpoint", test_top_products_endpoint),
        ("Documentation Endpoints", test_documentation_endpoints),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"⚠️  {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The API is working correctly.")
        print(f"📖 Visit http://localhost:8000/docs for API documentation")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 