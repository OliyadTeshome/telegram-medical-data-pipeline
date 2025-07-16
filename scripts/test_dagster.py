#!/usr/bin/env python3
"""
Test script for Dagster pipeline setup.
This script verifies that all components are properly configured.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_dagster_imports():
    """Test that all Dagster imports work correctly."""
    try:
        from dagster import job, op, get_dagster_logger
        print("✅ Dagster imports successful")
        return True
    except ImportError as e:
        print(f"❌ Dagster import failed: {e}")
        return False

def test_pipeline_imports():
    """Test that the pipeline module can be imported."""
    try:
        from dags.telegram_pipeline import (
            telegram_pipeline_job,
            scrape_telegram_data,
            load_raw_to_postgres,
            run_dbt_transformations,
            run_yolo_enrichment,
            generate_pipeline_report
        )
        print("✅ Pipeline imports successful")
        return True
    except ImportError as e:
        print(f"❌ Pipeline import failed: {e}")
        return False

def test_source_imports():
    """Test that all source modules can be imported."""
    try:
        from src.scraper.telegram_scraper import TelegramScraper
        from src.loader.postgres_loader import PostgresLoader
        from src.enrich.yolo_enricher import YOLOEnricher
        from src.dbt_runner.dbt_executor import DBTExecutor
        from src.utils.config import get_config
        print("✅ Source module imports successful")
        return True
    except ImportError as e:
        print(f"❌ Source module import failed: {e}")
        return False

def test_dagster_dev_command():
    """Test that dagster dev command is available."""
    try:
        import subprocess
        result = subprocess.run(
            ["dagster", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        if result.returncode == 0:
            print(f"✅ Dagster CLI available: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Dagster CLI failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Dagster CLI test failed: {e}")
        return False

def test_environment_variables():
    """Test that required environment variables are set."""
    required_vars = [
        'TELEGRAM_API_ID',
        'TELEGRAM_API_HASH', 
        'TELEGRAM_PHONE',
        'DATABASE_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {missing_vars}")
        print("   Please set these variables in your .env file")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def test_dagster_workspace():
    """Test that the Dagster workspace can be loaded."""
    try:
        from dagster import DagsterInstance
        
        # Create a temporary instance
        instance = DagsterInstance.ephemeral()
        
        print("✅ Dagster workspace loads successfully")
        return True
    except Exception as e:
        print(f"❌ Dagster workspace test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Dagster Pipeline Setup")
    print("=" * 50)
    
    tests = [
        ("Dagster Imports", test_dagster_imports),
        ("Pipeline Imports", test_pipeline_imports),
        ("Source Module Imports", test_source_imports),
        ("Dagster CLI", test_dagster_dev_command),
        ("Environment Variables", test_environment_variables),
        ("Dagster Workspace", test_dagster_workspace),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Dagster pipeline is ready.")
        print("\n🚀 To start the Dagster UI, run:")
        print("   dagster dev")
        print("\n📅 To run the pipeline manually:")
        print("   python dags/telegram_pipeline.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 