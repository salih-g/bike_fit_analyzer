"""
Analyzer for saddle positioning and setback.
"""
import cv2
import numpy as np
from typing import Tuple, Optional

from bike_fit_analyzer.models.angles import PoseData

class SaddleAnalyzer:
    """Analyzes saddle position including setback."""
    
    def __init__(self):
        """Initialize the saddle analyzer."""
        self.calibration_factor = 1.0  # Pixels to cm
        
    def detect_saddle_points(self, frame):
        """
        Detect saddle points in the frame.
        This would detect:
        - Saddle tip
        - Saddle reference point (typically 60-70mm from tip)
        - Bottom bracket
        """
        # This is a placeholder - actual implementation would use 
        # computer vision to detect the saddle
        
        # Mock detection for demonstration
        height, width = frame.shape[:2]
        saddle_tip = (width // 2 + 50, height // 2 - 50)
        saddle_reference = (width // 2, height // 2 - 50)
        bottom_bracket = (width // 2, height // 3 * 2)
        
        return {
            "saddle_tip": saddle_tip,
            "saddle_reference": saddle_reference,
            "bottom_bracket": bottom_bracket
        }
        
    def calculate_setback(self, frame, pose_data) -> Tuple[Dict[str, float], Optional[np.ndarray]]:
        """
        Calculate saddle setback and related measurements.
        
        Args:
            frame: Input frame
            pose_data: Processed pose data
            
        Returns:
            Tuple of (measurements dict, visualization frame)
        """
        # Detect saddle points
        points = self.detect_saddle_points(frame)
        
        # Calculate setback from bottom bracket (horizontal distance)
        setback_pixels = points["saddle_reference"][0] - points["bottom_bracket"][0]
        setback_cm = setback_pixels * self.calibration_factor
        
        # Use hip position from pose data to calculate effective saddle height
        hip_position = pose_data.landmarks["hip"].as_tuple()
        
        # Calculate effective saddle height (vertical distance from bottom bracket to hip)
        saddle_height_pixels = points["bottom_bracket"][1] - hip_position[1]
        saddle_height_cm = saddle_height_pixels * self.calibration_factor
        
        # Create measurements dictionary
        measurements = {
            "setback": setback_cm,
            "saddle_height": saddle_height_cm,
            "setback_ratio": setback_cm / saddle_height_cm * 100 if saddle_height_cm > 0 else 0  # as percentage
        }
        
        # Create visualization
        viz_frame = self.create_visualization(frame, points, hip_position, measurements)
        
        return (measurements, viz_frame)
    
    def create_visualization(self, frame, points, hip_position, measurements):
        """Create visualization showing saddle setback and height."""
        result = frame.copy()
        
        bb = points["bottom_bracket"]
        sr = points["saddle_reference"]
        
        # Draw bottom bracket point
        cv2.circle(result, bb, 8, (0, 0, 255), -1)
        
        # Draw saddle reference point
        cv2.circle(result, sr, 8, (0, 255, 255), -1)
        
        # Draw hip position
        cv2.circle(result, hip_position, 8, (255, 0, 255), -1)
        
        # Draw setback line (horizontal from BB to vertical line from saddle)
        cv2.line(result, 
                 (bb[0], sr[1]), 
                 (sr[0], sr[1]), 
                 (255, 0, 0), 2)
        
        # Draw vertical line from bottom bracket
        cv2.line(result, 
                 (bb[0], bb[1]), 
                 (bb[0], sr[1]), 
                 (0, 255, 0), 2)
        
        # Add text for measurements
        cv2.putText(result, 
                    f"Setback: {measurements['setback']:.1f} cm", 
                    ((bb[0] + sr[0]) // 2, sr[1] - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        cv2.putText(result, 
                    f"Saddle Height: {measurements['saddle_height']:.1f} cm", 
                    (bb[0] - 200, (bb[1] + hip_position[1]) // 2), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return result