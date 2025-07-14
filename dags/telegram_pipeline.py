from dagster import (
    job, op, graph, Out, In, Config, 
    get_dagster_logger, op_context
)
from typing import List, Dict, Any
import asyncio
import os
from datetime import datetime, timedelta

from src.scraper.telegram_scraper import TelegramScraper
from src.loader.postgres_loader import PostgresLoader
from src.enrich.yolo_enricher import YOLOEnricher
from src.dbt_runner.dbt_executor import DBTExecutor
from src.utils.config import get_config

# Configuration
@op
def scrape_telegram_messages(context) -> List[Dict[str, Any]]:
    """Scrape messages from Telegram channels using the new scraper"""
    logger = get_dagster_logger()
    
    logger.info("Starting to scrape Telegram channels")
    
    # Run async scraper
    async def run_scraper():
        scraper = TelegramScraper()
        all_messages = []
        
        try:
            # Connect to Telegram
            if not await scraper.connect():
                logger.error("Failed to connect to Telegram")
                return []
            
            # Scrape all channels
            results = await scraper.scrape_all_channels()
            
            # Collect all messages from successful scrapes
            for result in results:
                if result['status'] == 'success' and result['file_path']:
                    logger.info(f"Successfully scraped {result['message_count']} messages from {result['channel_name']}")
                    # Note: Messages are already saved to JSON files by the scraper
                    # We could load them here if needed for the pipeline
                else:
                    logger.warning(f"Failed to scrape {result['channel_name']}: {result['error']}")
            
            # For now, return empty list since messages are saved to files
            # In a real implementation, you might want to load the messages here
            await scraper.disconnect()
            return all_messages
            
        except Exception as e:
            logger.error(f"Error in scraper: {e}")
            await scraper.disconnect()
            return []
    
    messages = asyncio.run(run_scraper())
    logger.info(f"Scraping completed")
    return messages

@op
def load_messages_to_postgres(context, messages: List[Dict[str, Any]]) -> int:
    """Load scraped messages to PostgreSQL"""
    logger = get_dagster_logger()
    
    if not messages:
        logger.warning("No messages to load")
        return 0
    
    try:
        loader = PostgresLoader()
        inserted_count = loader.load_raw_messages(messages)
        logger.info(f"Loaded {inserted_count} messages to PostgreSQL")
        return inserted_count
    except Exception as e:
        logger.error(f"Error loading messages to PostgreSQL: {e}")
        raise

@op
def process_images_with_yolo(context) -> List[Dict[str, Any]]:
    """Process images with YOLO for medical content detection"""
    logger = get_dagster_logger()
    
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
            return []
        
        logger.info(f"Processing {len(image_paths)} images with YOLO")
        results = enricher.process_image_batch(image_paths)
        
        # Save results
        output_path = os.path.join(get_config().processed_data_path, f"yolo_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        enricher.save_results(results, output_path)
        
        logger.info(f"Processed {len(results)} images, results saved to {output_path}")
        return results
        
    except Exception as e:
        logger.error(f"Error processing images with YOLO: {e}")
        raise

@op
def load_image_analysis_to_postgres(context, image_results: List[Dict[str, Any]]) -> int:
    """Load YOLO analysis results to PostgreSQL"""
    logger = get_dagster_logger()
    
    if not image_results:
        logger.warning("No image analysis results to load")
        return 0
    
    try:
        loader = PostgresLoader()
        
        # Transform results for database
        db_results = []
        for result in image_results:
            if 'detection_results' in result:
                db_results.append({
                    'message_id': result.get('message_id', 0),
                    'image_path': result.get('image_path', ''),
                    'detection_results': result['detection_results'].get('detections', []),
                    'confidence_scores': result['detection_results'].get('confidence_scores', {})
                })
        
        inserted_count = loader.load_processed_images(db_results)
        logger.info(f"Loaded {inserted_count} image analysis results to PostgreSQL")
        return inserted_count
        
    except Exception as e:
        logger.error(f"Error loading image analysis to PostgreSQL: {e}")
        raise

@op
def enrich_messages_with_medical_analysis(context) -> List[Dict[str, Any]]:
    """Enrich messages with medical entity extraction and sentiment analysis"""
    logger = get_dagster_logger()
    
    try:
        loader = PostgresLoader()
        messages = loader.get_raw_messages(limit=1000)  # Get recent messages
        
        enriched_messages = []
        
        for message in messages:
            # Simple medical keyword detection (placeholder for more sophisticated NLP)
            medical_keywords = [
                'covid', 'vaccine', 'symptom', 'treatment', 'diagnosis', 'patient',
                'hospital', 'doctor', 'medicine', 'disease', 'infection', 'fever',
                'cough', 'headache', 'pain', 'emergency', 'urgent', 'critical'
            ]
            
            text = message.get('message_text', '').lower()
            medical_entities = []
            
            for keyword in medical_keywords:
                if keyword in text:
                    medical_entities.append(keyword)
            
            # Simple sentiment analysis (placeholder)
            positive_words = ['good', 'better', 'improved', 'recovered', 'healthy']
            negative_words = ['bad', 'worse', 'sick', 'pain', 'emergency', 'critical']
            
            sentiment_score = 0.0
            for word in positive_words:
                if word in text:
                    sentiment_score += 0.1
            for word in negative_words:
                if word in text:
                    sentiment_score -= 0.1
            
            # Urgency level
            urgency_level = 'normal'
            if any(word in text for word in ['emergency', 'urgent', 'critical']):
                urgency_level = 'high'
            elif any(word in text for word in ['urgent', 'important']):
                urgency_level = 'medium'
            
            enriched_message = {
                'raw_message_id': message['id'],
                'medical_entities': medical_entities,
                'sentiment_score': max(-1.0, min(1.0, sentiment_score)),
                'urgency_level': urgency_level
            }
            
            enriched_messages.append(enriched_message)
        
        # Load to database
        inserted_count = loader.load_enriched_messages(enriched_messages)
        logger.info(f"Enriched and loaded {inserted_count} messages")
        
        return enriched_messages
        
    except Exception as e:
        logger.error(f"Error enriching messages: {e}")
        raise

@op
def run_dbt_transformations(context) -> Dict[str, Any]:
    """Run dbt transformations on the data"""
    logger = get_dagster_logger()
    
    try:
        executor = DBTExecutor()
        
        logger.info("Running dbt debug...")
        debug_result = executor.debug()
        
        if not debug_result['success']:
            logger.error(f"dbt debug failed: {debug_result['stderr']}")
            raise Exception("dbt configuration error")
        
        logger.info("Running dbt deps...")
        deps_result = executor.deps()
        
        logger.info("Running dbt models...")
        run_result = executor.run()
        
        if not run_result['success']:
            logger.error(f"dbt run failed: {run_result['stderr']}")
            raise Exception("dbt run failed")
        
        logger.info("Running dbt tests...")
        test_result = executor.test()
        
        logger.info("Generating dbt docs...")
        docs_result = executor.generate_docs()
        
        return {
            'debug_success': debug_result['success'],
            'deps_success': deps_result['success'],
            'run_success': run_result['success'],
            'test_success': test_result['success'],
            'docs_success': docs_result['success']
        }
        
    except Exception as e:
        logger.error(f"Error running dbt transformations: {e}")
        raise

@op
def generate_pipeline_report(context, 
                           scraped_count: int,
                           loaded_count: int,
                           image_results: List[Dict[str, Any]],
                           enriched_count: int,
                           dbt_results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a comprehensive pipeline report"""
    logger = get_dagster_logger()
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'pipeline_status': 'completed',
        'metrics': {
            'messages_scraped': scraped_count,
            'messages_loaded': loaded_count,
            'images_processed': len(image_results),
            'messages_enriched': enriched_count,
            'dbt_success': all(dbt_results.values())
        },
        'dbt_results': dbt_results,
        'errors': []
    }
    
    logger.info(f"Pipeline report generated: {report}")
    return report

# Define the job
@job
def telegram_medical_pipeline():
    """Main pipeline for telegram medical data processing"""
    
    # Step 1: Scrape messages
    messages = scrape_telegram_messages()
    
    # Step 2: Load to PostgreSQL
    loaded_count = load_messages_to_postgres(messages)
    
    # Step 3: Process images with YOLO
    image_results = process_images_with_yolo()
    
    # Step 4: Load image analysis
    image_loaded_count = load_image_analysis_to_postgres(image_results)
    
    # Step 5: Enrich messages
    enriched_messages = enrich_messages_with_medical_analysis()
    
    # Step 6: Run dbt transformations
    dbt_results = run_dbt_transformations()
    
    # Step 7: Generate report
    generate_pipeline_report(
        scraped_count=len(messages),
        loaded_count=loaded_count,
        image_results=image_results,
        enriched_count=len(enriched_messages),
        dbt_results=dbt_results
    )

# Configuration for the job
def get_pipeline_config():
    """Get default configuration for the pipeline"""
    return {
        "ops": {
            # The scraper now uses hardcoded channels from the TelegramScraper class
            # No additional configuration needed
        }
    }

if __name__ == "__main__":
    # This would be run by Dagster
    pass 