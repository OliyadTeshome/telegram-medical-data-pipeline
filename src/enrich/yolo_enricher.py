import os
import cv2
import torch
import logging
from typing import List, Dict, Any, Optional
from ultralytics import YOLO
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class YOLOEnricher:
    """
    YOLO-based image enrichment for medical content detection.
    Processes images downloaded from Telegram messages.
    """
    
    def __init__(self, model_path: Optional[str] = None, confidence_threshold: float = 0.5):
        """
        Initialize YOLO enricher
        
        Args:
            model_path: Path to YOLO model file
            confidence_threshold: Minimum confidence for detections
        """
        self.confidence_threshold = confidence_threshold
        self.model = None
        
        # Set default model path if not provided
        if not model_path:
            model_path = os.getenv('YOLO_MODEL_PATH', 'yolov8n.pt')
        
        self.model_path = model_path
        self._load_model()
    
    def _load_model(self):
        """Load YOLO model with safe globals"""
        try:
            logger.info(f"Loading YOLO model from: {self.model_path}")
            
            # Add safe globals for ultralytics models
            import torch.serialization
            torch.serialization.add_safe_globals(['ultralytics.nn.tasks.DetectionModel'])
            
            # Load model with weights_only=False for compatibility
            self.model = YOLO(self.model_path)
            
            logger.info("✅ YOLO model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading YOLO model: {e}")
            # Try alternative loading method
            try:
                logger.info("Trying alternative model loading method...")
                self.model = YOLO('yolov8n.pt')  # Use default model
                logger.info("✅ YOLO model loaded with default weights")
            except Exception as e2:
                logger.error(f"Failed to load YOLO model: {e2}")
                self.model = None
    
    def process_image(self, image_path: str) -> Dict[str, Any]:
        """
        Process a single image with YOLO
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dict containing detection results
        """
        if not self.model:
            return {
                'status': 'failed',
                'error': 'YOLO model not loaded',
                'detections': []
            }
        
        try:
            # Check if image exists
            if not os.path.exists(image_path):
                return {
                    'status': 'failed',
                    'error': f'Image file not found: {image_path}',
                    'detections': []
                }
            
            # Run inference
            results = self.model(image_path, conf=self.confidence_threshold)
            
            detections = []
            for result in results:
                if result.boxes is not None:
                    for box in result.boxes:
                        detection = {
                            'class': result.names[int(box.cls[0])],
                            'confidence': float(box.conf[0]),
                            'bbox': box.xyxy[0].tolist(),
                            'image_path': image_path
                        }
                        detections.append(detection)
            
            return {
                'status': 'success',
                'detections': detections,
                'total_detections': len(detections)
            }
            
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'detections': []
            }
    
    def process_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Process all images in a directory
        
        Args:
            directory_path: Path to directory containing images
            
        Returns:
            Dict containing processing results
        """
        if not os.path.exists(directory_path):
            return {
                'status': 'failed',
                'error': f'Directory not found: {directory_path}',
                'images_processed': 0,
                'detections_found': 0
            }
        
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        processed_images = 0
        total_detections = 0
        all_detections = []
        
        # Walk through directory
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    image_path = os.path.join(root, file)
                    
                    try:
                        result = self.process_image(image_path)
                        
                        if result['status'] == 'success':
                            processed_images += 1
                            total_detections += result['total_detections']
                            all_detections.extend(result['detections'])
                            
                            logger.info(f"Processed {file}: {result['total_detections']} detections")
                        else:
                            logger.warning(f"Failed to process {file}: {result['error']}")
                    
                    except Exception as e:
                        logger.error(f"Error processing {file}: {e}")
        
        return {
            'status': 'success',
            'images_processed': processed_images,
            'detections_found': total_detections,
            'detections': all_detections
        }
    
    def save_detections(self, detections: List[Dict[str, Any]], output_path: str):
        """
        Save detection results to JSON file
        
        Args:
            detections: List of detection results
            output_path: Path to save the JSON file
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Add metadata
            output_data = {
                'timestamp': datetime.now().isoformat(),
                'model_path': self.model_path,
                'confidence_threshold': self.confidence_threshold,
                'total_detections': len(detections),
                'detections': detections
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2)
            
            logger.info(f"Saved {len(detections)} detections to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving detections: {e}")
    
    def get_medical_detections(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter detections for medical-related content
        
        Args:
            detections: List of all detections
            
        Returns:
            List of medical-related detections
        """
        medical_keywords = [
            'person', 'human', 'face', 'head', 'body',
            'medical', 'hospital', 'doctor', 'patient',
            'medicine', 'pill', 'tablet', 'syringe',
            'bandage', 'wound', 'injury'
        ]
        
        medical_detections = []
        
        for detection in detections:
            class_name = detection['class'].lower()
            
            # Check if detection class contains medical keywords
            if any(keyword in class_name for keyword in medical_keywords):
                medical_detections.append(detection)
        
        return medical_detections 