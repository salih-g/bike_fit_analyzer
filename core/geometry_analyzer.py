"""
Analyzer for bike geometry measurements (stack and reach).
"""
import cv2
import numpy as np
from typing import Dict, Tuple, Optional

class GeometryAnalyzer:
    """Analyzes bike geometry including stack and reach."""
    
    def __init__(self):
        """Initialize the geometry analyzer."""
        self.calibration_factor = 1.0  # Pixels to cm
        
    def detect_bike_points(self, frame):
        """
        Detect key points on the bike frame.
        This would use image processing to detect:
        - Bottom bracket
        - Top of head tube
        - Other key frame points
        """
        # This is a placeholder - actual implementation would use 
        # computer vision to detect frame points
        
        # Mock detection for demonstration
        height, width = frame.shape[:2]
        bottom_bracket = (width // 2, height // 3 * 2)
        head_tube_top = (width // 3, height // 2)
        
        return {
            "bottom_bracket": bottom_bracket,
            "head_tube_top": head_tube_top
        }
        
    def calculate_stack_reach(self, frame) -> Tuple[Dict[str, float], Optional[np.ndarray]]:
        """
        Calculate stack and reach measurements.
        
        Args:
            frame: Input frame
            
        Returns:
            Tuple of (measurements dict, visualization frame)
        """
        # Detect key bike points
        points = self.detect_bike_points(frame)
        
        # Calculate stack (vertical distance)
        stack_pixels = points["bottom_bracket"][1] - points["head_tube_top"][1]
        stack_cm = stack_pixels * self.calibration_factor
        
        # Calculate reach (horizontal distance)
        reach_pixels = points["head_tube_top"][0] - points["bottom_bracket"][0]
        reach_cm = reach_pixels * self.calibration_factor
        
        # Create measurements dictionary
        measurements = {
            "stack": stack_cm,
            "reach": reach_cm,
            "stack_to_reach_ratio": stack_cm / reach_cm if reach_cm > 0 else 0
        }
        
        # Create visualization
        viz_frame = self.create_visualization(frame, points, measurements)
        
        return (measurements, viz_frame)
    
    def create_visualization(self, frame, points, measurements):
        """Create visualization showing stack and reach measurements."""
        result = frame.copy()
        
        bb = points["bottom_bracket"]
        ht = points["head_tube_top"]
        
        # Draw bottom bracket point
        cv2.circle(result, bb, 8, (0, 0, 255), -1)
        
        # Draw head tube top point
        cv2.circle(result, ht, 8, (0, 0, 255), -1)
        
        # Draw stack line (vertical)
        cv2.line(result, 
                 (ht[0], bb[1]), 
                 (ht[0], ht[1]), 
                 (0, 255, 0), 2)
        
        # Draw reach line (horizontal)
        cv2.line(result, 
                 (bb[0], bb[1]), 
                 (ht[0], bb[1]), 
                 (255, 0, 0), 2)
        
        # Add text for measurements
        cv2.putText(result, 
                    f"Stack: {measurements['stack']:.1f} cm", 
                    (ht[0] + 10, (ht[1] + bb[1]) // 2), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.putText(result, 
                    f"Reach: {measurements['reach']:.1f} cm", 
                    ((bb[0] + ht[0]) // 2, bb[1] + 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        return result