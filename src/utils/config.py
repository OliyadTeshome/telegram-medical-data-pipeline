import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration management for the telegram medical data pipeline"""
    
    def __init__(self):
        self.load_environment()
    
    def load_environment(self):
        """Load environment variables"""
        # Telegram Configuration
        self.telegram_api_id = os.getenv('TELEGRAM_API_ID')
        self.telegram_api_hash = os.getenv('TELEGRAM_API_HASH')
        self.telegram_phone = os.getenv('TELEGRAM_PHONE')
        self.telegram_session_name = os.getenv('TELEGRAM_SESSION_NAME', 'medical_pipeline_session')
        
        # PostgreSQL Configuration
        self.postgres_host = os.getenv('POSTGRES_HOST', 'localhost')
        self.postgres_port = os.getenv('POSTGRES_PORT', '5432')
        self.postgres_db = os.getenv('POSTGRES_DB', 'medical_data')
        self.postgres_user = os.getenv('POSTGRES_USER', 'postgres')
        self.postgres_password = os.getenv('POSTGRES_PASSWORD', '')
        
        # Database URLs
        self.database_url = os.getenv('DATABASE_URL')
        # Use relative path for dbt profiles directory
        default_dbt_dir = os.path.join(os.getcwd(), 'dbt')
        self.dbt_profiles_dir = os.getenv('DBT_PROFILES_DIR', default_dbt_dir)
        
        # FastAPI Configuration
        self.fastapi_host = os.getenv('FASTAPI_HOST', '0.0.0.0')
        self.fastapi_port = int(os.getenv('FASTAPI_PORT', '8000'))
        self.fastapi_reload = os.getenv('FASTAPI_RELOAD', 'true').lower() == 'true'
        
        # Dagster Configuration
        self.dagster_home = os.getenv('DAGSTER_HOME', '/opt/dagster/dagster_home')
        self.dagster_host = os.getenv('DAGSTER_HOST', '0.0.0.0')
        self.dagster_port = int(os.getenv('DAGSTER_PORT', '3000'))
        
        # Data Storage - Use relative paths for Windows compatibility
        default_raw_path = os.path.join(os.getcwd(), 'data', 'raw')
        default_processed_path = os.path.join(os.getcwd(), 'data', 'processed')
        self.raw_data_path = os.getenv('RAW_DATA_PATH', default_raw_path)
        self.processed_data_path = os.getenv('PROCESSED_DATA_PATH', default_processed_path)
        
        # YOLO Configuration
        self.yolo_model_path = os.getenv('YOLO_MODEL_PATH', '/app/models/yolov8n.pt')
        self.confidence_threshold = float(os.getenv('CONFIDENCE_THRESHOLD', '0.5'))
    
    def get_database_url(self) -> str:
        """Get database URL for SQLAlchemy"""
        if self.database_url:
            return self.database_url
        else:
            return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    def get_postgres_config(self) -> Dict[str, Any]:
        """Get PostgreSQL configuration dictionary"""
        return {
            'host': self.postgres_host,
            'port': self.postgres_port,
            'database': self.postgres_db,
            'user': self.postgres_user,
            'password': self.postgres_password
        }
    
    def validate_config(self) -> Dict[str, bool]:
        """Validate configuration and return status"""
        validation_results = {
            'telegram': bool(self.telegram_api_id and self.telegram_api_hash and self.telegram_phone),
            'postgres': bool(self.postgres_host and self.postgres_db and self.postgres_user),
            'fastapi': True,  # Default values are always valid
            'dagster': True,   # Default values are always valid
            'yolo': True       # Default values are always valid
        }
        
        return validation_results
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration"""
        return {
            'telegram': {
                'api_id': self.telegram_api_id,
                'api_hash': '***' if self.telegram_api_hash else None,
                'phone': self.telegram_phone,
                'session_name': self.telegram_session_name
            },
            'postgres': {
                'host': self.postgres_host,
                'port': self.postgres_port,
                'database': self.postgres_db,
                'user': self.postgres_user,
                'password': '***' if self.postgres_password else None
            },
            'fastapi': {
                'host': self.fastapi_host,
                'port': self.fastapi_port,
                'reload': self.fastapi_reload
            },
            'dagster': {
                'home': self.dagster_home,
                'host': self.dagster_host,
                'port': self.dagster_port
            },
            'data_paths': {
                'raw': self.raw_data_path,
                'processed': self.processed_data_path
            },
            'yolo': {
                'model_path': self.yolo_model_path,
                'confidence_threshold': self.confidence_threshold
            }
        }

# Global config instance
config = Config()

def get_config() -> Config:
    """Get the global configuration instance"""
    return config 