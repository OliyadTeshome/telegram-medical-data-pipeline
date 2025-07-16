from dagster import (
    job, op, graph, Out, In, Config, 
    get_dagster_logger, schedule, 
    ScheduleDefinition, DefaultScheduleStatus,
    DagsterInstance, define_asset_job
)
from typing import List, Dict, Any, Optional
import asyncio
import os
import subprocess
import sys
from datetime import datetime, timedelta
import json

from src.scraper.telegram_scraper import TelegramScraper
from src.loader.postgres_loader import PostgresLoader
from src.enrich.yolo_enricher import YOLOEnricher
from src.dbt_runner.dbt_executor import DBTExecutor
from src.utils.config import get_config

# =============================================================================
# OPERATIONS (OPS)
# =============================================================================

@op
def scrape_telegram_data(context) -> Dict[str, Any]:
    """
    Scrape data from Telegram channels using Telethon scraper.
    
    Returns:
        Dict containing scrape results and metadata
    """
    logger = get_dagster_logger()
    logger.info("Starting Telegram data scraping operation")
    
    try:
        # Run async scraper
        async def run_scraper():
            scraper = TelegramScraper()
            results = []
            
            try:
                # Connect to Telegram
                if not await scraper.connect():
                    logger.error("Failed to connect to Telegram")
                    return {
                        'status': 'failed',
                        'error': 'Telegram connection failed',
                        'message_count': 0,
                        'channels_processed': 0
                    }
                
                logger.info("Successfully connected to Telegram")
                
                # Scrape all channels
                scrape_results = await scraper.scrape_all_channels()
                
                # Process results
                total_messages = 0
                successful_channels = 0
                
                for result in scrape_results:
                    if result['status'] == 'success':
                        successful_channels += 1
                        total_messages += result.get('message_count', 0)
                        logger.info(f"Successfully scraped {result['message_count']} messages from {result['channel_name']}")
                    else:
                        logger.warning(f"Failed to scrape {result['channel_name']}: {result['error']}")
                
                await scraper.disconnect()
                
                return {
                    'status': 'success',
                    'message_count': total_messages,
                    'channels_processed': len(scrape_results),
                    'successful_channels': successful_channels,
                    'scrape_results': scrape_results
                }
                
            except Exception as e:
                logger.error(f"Error in scraper: {e}")
                await scraper.disconnect()
                return {
                    'status': 'failed',
                    'error': str(e),
                    'message_count': 0,
                    'channels_processed': 0
                }
        
        # Handle async execution in Jupyter environment
        try:
            # Try to get the current event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in Jupyter, use asyncio.create_task
                import nest_asyncio
                nest_asyncio.apply()
                result = asyncio.run(run_scraper())
            else:
                result = asyncio.run(run_scraper())
        except RuntimeError:
            # Fallback for Jupyter environment
            result = asyncio.run(run_scraper())
        logger.info(f"Scraping completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Unexpected error in scrape_telegram_data: {e}")
        raise

@op
def load_raw_to_postgres(context, scrape_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse JSON data and load to PostgreSQL raw database.
    
    Args:
        scrape_results: Results from the scraping operation
        
    Returns:
        Dict containing load results and metadata
    """
    logger = get_dagster_logger()
    logger.info("Starting raw data loading to PostgreSQL")
    
    try:
        if scrape_results.get('status') != 'success':
            logger.warning("Skipping load operation due to failed scraping")
            return {
                'status': 'skipped',
                'reason': 'Scraping failed',
                'records_loaded': 0
            }
        
        loader = PostgresLoader()
        
        # Load raw messages from JSON files
        # The scraper saves messages to JSON files, so we need to load them
        raw_data_path = get_config().raw_data_path
        total_loaded = 0
        
        # Walk through raw data directory to find JSON files
        for root, dirs, files in os.walk(raw_data_path):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            messages = json.load(f)
                        
                        if isinstance(messages, list):
                            loaded_count = loader.load_raw_messages(messages)
                            total_loaded += loaded_count
                            logger.info(f"Loaded {loaded_count} messages from {file}")
                        
                    except Exception as e:
                        logger.error(f"Error loading file {file}: {e}")
        
        result = {
            'status': 'success',
            'records_loaded': total_loaded,
            'files_processed': len([f for f in os.listdir(raw_data_path) if f.endswith('.json')])
        }
        
        logger.info(f"Raw data loading completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in load_raw_to_postgres: {e}")
        raise

@op
def run_dbt_transformations(context) -> Dict[str, Any]:
    """
    Run dbt transformations via subprocess.
    
    Returns:
        Dict containing dbt execution results
    """
    logger = get_dagster_logger()
    logger.info("Starting dbt transformations")
    
    try:
        executor = DBTExecutor()
        
        # Run dbt debug
        logger.info("Running dbt debug...")
        debug_result = executor.debug()
        
        if not debug_result['success']:
            logger.error(f"dbt debug failed: {debug_result['stderr']}")
            return {
                'status': 'failed',
                'error': 'dbt configuration error',
                'debug_success': False,
                'deps_success': False,
                'run_success': False,
                'test_success': False
            }
        
        # Run dbt deps
        logger.info("Running dbt deps...")
        deps_result = executor.deps()
        
        # Run dbt models
        logger.info("Running dbt models...")
        run_result = executor.run()
        
        if not run_result['success']:
            logger.error(f"dbt run failed: {run_result['stderr']}")
            return {
                'status': 'failed',
                'error': 'dbt run failed',
                'debug_success': True,
                'deps_success': deps_result['success'],
                'run_success': False,
                'test_success': False
            }
        
        # Run dbt tests
        logger.info("Running dbt tests...")
        test_result = executor.test()
        
        # Generate dbt docs
        logger.info("Generating dbt docs...")
        docs_result = executor.generate_docs()
        
        result = {
            'status': 'success',
            'debug_success': debug_result['success'],
            'deps_success': deps_result['success'],
            'run_success': run_result['success'],
            'test_success': test_result['success'],
            'docs_success': docs_result['success']
        }
        
        logger.info(f"dbt transformations completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in run_dbt_transformations: {e}")
        raise

@op
def run_yolo_enrichment(context) -> Dict[str, Any]:
    """
    Process images with YOLO for medical content detection.
    
    Returns:
        Dict containing YOLO processing results
    """
    logger = get_dagster_logger()
    logger.info("Starting YOLO image enrichment")
    
    try:
        enricher = YOLOEnricher()
        
        # Get image paths from raw data directory
        raw_data_path = get_config().raw_data_path
        image_paths = []
        
        # Walk through raw data directory to find images
        for root, dirs, files in os.walk(raw_data_path):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    image_paths.append(os.path.join(root, file))
        
        if not image_paths:
            logger.info("No images found for processing")
            return {
                'status': 'success',
                'images_processed': 0,
                'detections_found': 0,
                'message': 'No images found'
            }
        
        logger.info(f"Processing {len(image_paths)} images with YOLO")
        results = enricher.process_image_batch(image_paths)
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(
            get_config().processed_data_path, 
            f"yolo_results_{timestamp}.json"
        )
        enricher.save_results(results, output_path)
        
        # Count detections
        total_detections = sum(
            len(result.get('detection_results', {}).get('detections', []))
            for result in results
        )
        
        result = {
            'status': 'success',
            'images_processed': len(results),
            'detections_found': total_detections,
            'output_path': output_path
        }
        
        logger.info(f"YOLO enrichment completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in run_yolo_enrichment: {e}")
        raise

@op
def generate_pipeline_report(context, 
                           scrape_results: Dict[str, Any],
                           load_results: Dict[str, Any],
                           dbt_results: Dict[str, Any],
                           yolo_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a comprehensive pipeline report.
    
    Returns:
        Dict containing pipeline execution summary
    """
    logger = get_dagster_logger()
    logger.info("Generating pipeline report")
    
    try:
        report = {
            'timestamp': datetime.now().isoformat(),
            'pipeline_status': 'completed',
            'execution_summary': {
                'scraping': {
                    'status': scrape_results.get('status', 'unknown'),
                    'messages_scraped': scrape_results.get('message_count', 0),
                    'channels_processed': scrape_results.get('channels_processed', 0)
                },
                'loading': {
                    'status': load_results.get('status', 'unknown'),
                    'records_loaded': load_results.get('records_loaded', 0)
                },
                'dbt_transformations': {
                    'status': dbt_results.get('status', 'unknown'),
                    'run_success': dbt_results.get('run_success', False),
                    'test_success': dbt_results.get('test_success', False)
                },
                'yolo_enrichment': {
                    'status': yolo_results.get('status', 'unknown'),
                    'images_processed': yolo_results.get('images_processed', 0),
                    'detections_found': yolo_results.get('detections_found', 0)
                }
            },
            'errors': []
        }
        
        # Check for errors
        if scrape_results.get('status') == 'failed':
            report['errors'].append(f"Scraping failed: {scrape_results.get('error', 'Unknown error')}")
        
        if load_results.get('status') == 'failed':
            report['errors'].append(f"Loading failed: {load_results.get('error', 'Unknown error')}")
        
        if dbt_results.get('status') == 'failed':
            report['errors'].append(f"dbt failed: {dbt_results.get('error', 'Unknown error')}")
        
        if yolo_results.get('status') == 'failed':
            report['errors'].append(f"YOLO failed: {yolo_results.get('error', 'Unknown error')}")
        
        logger.info(f"Pipeline report generated: {report}")
        return report
        
    except Exception as e:
        logger.error(f"Error generating pipeline report: {e}")
        raise

# =============================================================================
# JOB DEFINITION
# =============================================================================

@job
def telegram_pipeline_job():
    """
    Main Dagster job for the Telegram medical data pipeline.
    
    This job orchestrates the following operations:
    1. scrape_telegram_data: Scrapes data from Telegram channels
    2. load_raw_to_postgres: Loads raw data to PostgreSQL
    3. run_dbt_transformations: Runs dbt transformations
    4. run_yolo_enrichment: Processes images with YOLO
    5. generate_pipeline_report: Generates execution report
    """
    
    # Step 1: Scrape Telegram data
    scrape_results = scrape_telegram_data()
    
    # Step 2: Load raw data to PostgreSQL
    load_results = load_raw_to_postgres(scrape_results)
    
    # Step 3: Run dbt transformations
    dbt_results = run_dbt_transformations()
    
    # Step 4: Run YOLO enrichment (can run in parallel with dbt)
    yolo_results = run_yolo_enrichment()
    
    # Step 5: Generate pipeline report
    generate_pipeline_report(scrape_results, load_results, dbt_results, yolo_results)

# =============================================================================
# SCHEDULES
# =============================================================================

@schedule(
    job=telegram_pipeline_job,
    cron_schedule="0 2 * * *",  # Run at 2 AM every day
    default_status=DefaultScheduleStatus.RUNNING,
    description="Daily Telegram medical data pipeline"
)
def daily_telegram_pipeline_schedule(context):
    """
    Schedule to run the Telegram pipeline every 24 hours at 2 AM.
    """
    return {}

# =============================================================================
# CONFIGURATION
# =============================================================================

def get_pipeline_config():
    """
    Get default configuration for the pipeline.
    
    Returns:
        Dict containing pipeline configuration
    """
    return {
        "ops": {
            "scrape_telegram_data": {
                "config": {
                    "max_messages_per_channel": 1000,
                    "include_media": True
                }
            },
            "load_raw_to_postgres": {
                "config": {
                    "batch_size": 1000,
                    "retry_attempts": 3
                }
            },
            "run_dbt_transformations": {
                "config": {
                    "dbt_project_dir": "dbt",
                    "profiles_dir": "dbt"
                }
            },
            "run_yolo_enrichment": {
                "config": {
                    "confidence_threshold": 0.5,
                    "model_path": "models/yolo_medical.pt"
                }
            }
        }
    }

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    # This allows running the pipeline directly for testing
    from dagster import execute_job, DagsterInstance
    
    # Create an instance and execute the job
    instance = DagsterInstance.ephemeral()
    result = execute_job(telegram_pipeline_job, instance=instance)
    
    if result.success:
        print("Pipeline executed successfully!")
    else:
        print("Pipeline execution failed!")
        for event in result.all_events:
            if event.event_type_value == "STEP_FAILURE":
                print(f"Step {event.step_key} failed: {event}") 