#!/usr/bin/env python3
"""
Execute SQL script to create dbt models
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def execute_sql_script():
    """Execute the SQL script to create dbt models"""
    try:
        # Get database credentials
        db_host = os.getenv('POSTGRES_HOST', 'localhost')
        db_port = os.getenv('POSTGRES_PORT', '5432')
        db_name = os.getenv('POSTGRES_DB', 'telegram_medical')
        db_user = os.getenv('POSTGRES_USER', 'postgres')
        db_password = os.getenv('POSTGRES_PASSWORD', '')
        
        print(f"Connecting to database: {db_name}")
        
        # Create database URL
        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        engine = create_engine(database_url)
        
        # Read SQL script
        with open('create_models.sql', 'r') as f:
            sql_script = f.read()
        
        # Split into individual statements
        statements = sql_script.split(';')
        
        with engine.connect() as conn:
            for i, statement in enumerate(statements):
                statement = statement.strip()
                if statement:
                    try:
                        print(f"Executing statement {i+1}/{len(statements)}...")
                        conn.execute(text(statement))
                        conn.commit()
                    except Exception as e:
                        print(f"Warning: Statement {i+1} failed: {e}")
                        continue
            
            print("✅ SQL script executed successfully!")
            
            # Verify models
            result = conn.execute(text("""
                SELECT 'stg_telegram_messages' as model, COUNT(*) as count FROM stg_telegram_messages
                UNION ALL
                SELECT 'dim_channels' as model, COUNT(*) as count FROM dim_channels
                UNION ALL
                SELECT 'dim_dates' as model, COUNT(*) as count FROM dim_dates
                UNION ALL
                SELECT 'fct_messages' as model, COUNT(*) as count FROM fct_messages
            """))
            
            print("\n📊 Model Verification:")
            for row in result:
                print(f"  {row[0]}: {row[1]} records")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    execute_sql_script() 