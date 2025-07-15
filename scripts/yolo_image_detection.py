import os
import sys
import argparse
import logging
from glob import glob
from datetime import datetime
from typing import List, Dict, Any

# Import YOLOEnricher and PostgresLoader from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.enrich.yolo_enricher import YOLOEnricher
from src.loader.postgres_loader import PostgresLoader

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('yolo_image_detection.log')
    ]
)
logger = logging.getLogger(__name__)

def get_image_files(base_dir: str) -> List[str]:
    """Recursively get all jpg image files in the directory tree."""
    return glob(os.path.join(base_dir, '*', '*.jpg'))

def extract_message_id(image_path: str) -> int:
    """Extract message_id from image filename (e.g., 123456.jpg)."""
    filename = os.path.basename(image_path)
    try:
        return int(os.path.splitext(filename)[0])
    except Exception:
        logger.error(f"Could not extract message_id from {filename}")
        return None

def main(date: str, channel: str = None):
    # Directory pattern
    base_dir = os.path.join('notebooks', 'data', 'raw', 'telegram_images', date)
    if channel:
        base_dir = os.path.join(base_dir, channel)
    if not os.path.exists(base_dir):
        logger.error(f"Directory not found: {base_dir}")
        sys.exit(1)

    image_files = get_image_files(base_dir) if not channel else glob(os.path.join(base_dir, '*.jpg'))
    logger.info(f"Found {len(image_files)} images to process in {base_dir}")

    yolo = YOLOEnricher()
    loader = PostgresLoader()
    loader.connect()

    processed_data = []
    for image_path in image_files:
        message_id = extract_message_id(image_path)
        if message_id is None:
            continue
        try:
            detection_result = yolo.detect_objects(image_path)
            detections = detection_result.get('detections', [])
            logger.info(f"Processed {image_path}: {len(detections)} objects detected.")
            processed_data.append({
                'message_id': message_id,
                'image_path': image_path,
                'detection_results': detection_result.get('detections', []),
                'confidence_scores': detection_result.get('confidence_scores', {}),
            })
        except Exception as e:
            logger.error(f"Error processing {image_path}: {e}")

    if processed_data:
        try:
            loader.load_processed_images(processed_data)
            logger.info(f"Saved {len(processed_data)} detection results to PostgreSQL.")
        except Exception as e:
            logger.error(f"Error saving results to PostgreSQL: {e}")
    else:
        logger.warning("No images were processed successfully.")

    loader.disconnect()
    logger.info("Processing complete.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='YOLOv8 Object Detection for Telegram Images')
    parser.add_argument('--date', required=True, help='Date folder (YYYY-MM-DD)')
    parser.add_argument('--channel', required=False, help='Channel name (optional)')
    args = parser.parse_args()
    main(args.date, args.channel) 