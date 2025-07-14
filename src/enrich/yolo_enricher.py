import os
import cv2
import json
import numpy as np
from typing import List, Dict, Any, Tuple
from ultralytics import YOLO
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

class YOLOEnricher:
    def __init__(self):
        self.model_path = os.getenv('YOLO_MODEL_PATH', 'yolov8n.pt')
        self.confidence_threshold = float(os.getenv('CONFIDENCE_THRESHOLD', 0.5))
        self.model = None
        self.medical_classes = [
            'person', 'bottle', 'cup', 'bowl', 'knife', 'spoon', 'fork',
            'cell phone', 'laptop', 'mouse', 'remote', 'keyboard', 'book',
            'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
        ]
        
    def load_model(self):
        """Load YOLO model"""
        try:
            self.model = YOLO(self.model_path)
            print(f"Loaded YOLO model from {self.model_path}")
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            raise
            
    def detect_objects(self, image_path: str) -> Dict[str, Any]:
        """Detect objects in an image using YOLO"""
        if not self.model:
            self.load_model()
            
        try:
            # Load and process image
            results = self.model(image_path, conf=self.confidence_threshold)
            
            detections = []
            confidence_scores = {}
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        
                        # Get confidence and class
                        confidence = float(box.conf[0].cpu().numpy())
                        class_id = int(box.cls[0].cpu().numpy())
                        class_name = self.model.names[class_id]
                        
                        detection = {
                            'bbox': [float(x1), float(y1), float(x2), float(y2)],
                            'confidence': confidence,
                            'class_id': class_id,
                            'class_name': class_name
                        }
                        detections.append(detection)
                        
                        # Track confidence scores by class
                        if class_name not in confidence_scores:
                            confidence_scores[class_name] = []
                        confidence_scores[class_name].append(confidence)
            
            # Calculate average confidence for each class
            avg_confidence = {}
            for class_name, scores in confidence_scores.items():
                avg_confidence[class_name] = sum(scores) / len(scores)
            
            return {
                'detections': detections,
                'confidence_scores': avg_confidence,
                'total_detections': len(detections),
                'image_path': image_path
            }
            
        except Exception as e:
            print(f"Error detecting objects in {image_path}: {e}")
            return {
                'detections': [],
                'confidence_scores': {},
                'total_detections': 0,
                'image_path': image_path,
                'error': str(e)
            }
    
    def analyze_medical_relevance(self, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze medical relevance of detected objects"""
        medical_keywords = {
            'person': 1.0,
            'bottle': 0.8,
            'cup': 0.6,
            'bowl': 0.5,
            'knife': 0.9,
            'spoon': 0.7,
            'fork': 0.7,
            'cell phone': 0.3,
            'laptop': 0.4,
            'book': 0.8,
            'clock': 0.2,
            'scissors': 0.9,
            'toothbrush': 0.9
        }
        
        medical_score = 0.0
        medical_objects = []
        
        for detection in detections:
            class_name = detection['class_name']
            confidence = detection['confidence']
            
            if class_name in medical_keywords:
                relevance_score = medical_keywords[class_name] * confidence
                medical_score += relevance_score
                medical_objects.append({
                    'object': class_name,
                    'confidence': confidence,
                    'relevance_score': relevance_score
                })
        
        # Normalize medical score
        if medical_objects:
            medical_score = medical_score / len(medical_objects)
        
        return {
            'medical_score': medical_score,
            'medical_objects': medical_objects,
            'is_medical_content': medical_score > 0.5
        }
    
    def process_image_batch(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """Process multiple images in batch"""
        results = []
        
        for image_path in image_paths:
            if os.path.exists(image_path):
                detection_result = self.detect_objects(image_path)
                medical_analysis = self.analyze_medical_relevance(detection_result['detections'])
                
                result = {
                    'image_path': image_path,
                    'detection_results': detection_result,
                    'medical_analysis': medical_analysis,
                    'processed_at': str(np.datetime64('now'))
                }
                results.append(result)
            else:
                print(f"Image not found: {image_path}")
                
        return results
    
    def save_results(self, results: List[Dict[str, Any]], output_path: str):
        """Save detection results to JSON file"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
            
        print(f"Saved {len(results)} results to {output_path}")

def main():
    """Test function for YOLO enricher"""
    enricher = YOLOEnricher()
    
    # Test with a sample image (replace with actual image path)
    test_image = "test_image.jpg"
    
    if os.path.exists(test_image):
        result = enricher.detect_objects(test_image)
        medical_analysis = enricher.analyze_medical_relevance(result['detections'])
        
        print(f"Detected {result['total_detections']} objects")
        print(f"Medical score: {medical_analysis['medical_score']:.2f}")
        print(f"Is medical content: {medical_analysis['is_medical_content']}")
    else:
        print(f"Test image {test_image} not found")

if __name__ == "__main__":
    main() 