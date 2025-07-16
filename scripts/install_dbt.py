#!/usr/bin/env python3
"""
Install and configure dbt for the Telegram medical data pipeline
"""

import os
import sys
import subprocess
from pathlib import Path

def install_dbt():
    """Install dbt and configure it"""
    print("🔧 Installing and configuring dbt")
    print("=" * 50)
    
    try:
        # Check if dbt is installed
        print("📋 Checking dbt installation...")
        result = subprocess.run(['dbt', '--version'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ dbt is already installed")
            print(f"Version: {result.stdout.strip()}")
        else:
            print("📦 Installing dbt...")
            subprocess.run(['pip', 'install', 'dbt-postgres'], check=True)
            print("✅ dbt installed successfully")
        
        # Create dbt project structure if it doesn't exist
        dbt_dir = Path("dbt")
        if not dbt_dir.exists():
            print("📁 Creating dbt project structure...")
            dbt_dir.mkdir(exist_ok=True)
            
            # Create dbt_project.yml
            dbt_project_content = """
name: 'telegram_medical_pipeline'
version: '1.0.0'
config-version: 2

profile: 'telegram_medical_pipeline'

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

target-path: "target"
clean-targets:
    - "target"
    - "dbt_packages"

models:
  telegram_medical_pipeline:
    staging:
      +materialized: view
    marts:
      +materialized: table
"""
            
            with open(dbt_dir / "dbt_project.yml", "w") as f:
                f.write(dbt_project_content.strip())
            
            # Create profiles.yml
            profiles_content = """
telegram_medical_pipeline:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      port: 5432
      user: postgres
      password: password
      dbname: medical_data
      schema: public
      threads: 4
      keepalives_idle: 0
      connect_timeout: 10
"""
            
            profiles_dir = dbt_dir / "profiles.yml"
            with open(profiles_dir, "w") as f:
                f.write(profiles_content.strip())
            
            # Create models directory
            models_dir = dbt_dir / "models"
            models_dir.mkdir(exist_ok=True)
            
            # Create basic models
            staging_dir = models_dir / "staging"
            staging_dir.mkdir(exist_ok=True)
            
            # Create stg_raw_messages.sql
            stg_raw_messages_content = """
{{
  config(
    materialized='view'
  )
}}

select
    id,
    message_id,
    chat_id,
    chat_title,
    sender_id,
    sender_username,
    sender_first_name,
    sender_last_name,
    message_text,
    message_date,
    has_media,
    media_path,
    channel_name,
    created_at
from {{ source('raw', 'raw_messages') }}
"""
            
            with open(staging_dir / "stg_raw_messages.sql", "w") as f:
                f.write(stg_raw_messages_content.strip())
            
            # Create sources.yml
            sources_content = """
version: 2

sources:
  - name: raw
    database: medical_data
    schema: public
    tables:
      - name: raw_messages
        description: "Raw messages from Telegram channels"
"""
            
            with open(models_dir / "sources.yml", "w") as f:
                f.write(sources_content.strip())
            
            print("✅ dbt project structure created")
        
        # Test dbt configuration
        print("\n🧪 Testing dbt configuration...")
        os.chdir(dbt_dir)
        
        # Run dbt debug
        debug_result = subprocess.run(['dbt', 'debug'], capture_output=True, text=True)
        
        if debug_result.returncode == 0:
            print("✅ dbt configuration is working")
        else:
            print("⚠️  dbt debug output:")
            print(debug_result.stdout)
            print(debug_result.stderr)
        
        return True
        
    except Exception as e:
        print(f"❌ dbt setup failed: {e}")
        return False

if __name__ == "__main__":
    success = install_dbt()
    
    if success:
        print("\n✅ dbt is ready for the pipeline!")
    else:
        print("\n❌ dbt setup failed!") 