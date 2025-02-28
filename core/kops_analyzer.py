"""
Analyzer for Knee Over Pedal Spindle (KOPS) measurement.
"""
import cv2
import numpy as np
from typing import Tuple, Optional

from bike_fit_analyzer.models.angles import PoseData

class KOPSAnalyzer:
    """Analyzes knee position relative to the pedal spindle."""
    
    def __init__(self):
        """Initialize the KOPS analyzer."""
        # Default tolerance in pixels
        self.tolerance = 20
        
    def detect_pedal_spindle(self, frame, knee_position):
        """
        Detect the pedal spindle position when crank is horizontal.
        This is a simplified placeholder - actual implementation would use
        object detection or color tracking to find the pedal position.
        """
        # This would use computer vision to detect the pedal
        # For now, we'll estimate based on the ankle position
        # In a real implementation, this would detect the actual pedal
        
        # Return estimated pedal spindle position
        return (knee_position[0], knee_position[1] + 100)  # Just an example
        
    def analyze_kops(self, frame, pose_data) -> Tuple[float, str, Optional[np.ndarray]]:
        """
        Analyze the KOPS alignment.
        
        Args:
            frame: Input frame
            pose_data: Processed pose data
            
        Returns:
            Tuple of (deviation in cm, assessment, visualization frame)
        """
        # Get knee position
        knee_position = pose_data.landmarks["knee"].as_tuple()
        
        # Detect pedal spindle
        pedal_position = self.detect_pedal_spindle(frame, knee_position)
        
        # Calculate horizontal deviation
        deviation_pixels = knee_position[0] - pedal_position[0]
        
        # Convert to cm (would need proper calibration)
        # Assuming 1 cm = x pixels based on calibration data
        pixels_per_cm = 10  # This would come from calibration
        deviation_cm = deviation_pixels / pixels_per_cm
        
        # Assess the alignment
        if abs(deviation_cm) < 1.0:
            assessment = "Good KOPS alignment"
        elif deviation_cm < 0:
            assessment = f"Knee is {abs(deviation_cm):.1f} cm behind pedal spindle"
        else:
            assessment = f"Knee is {deviation_cm:.1f} cm ahead of pedal spindle"
            
        # Create visualization
        viz_frame = self.create_visualization(frame, knee_position, pedal_position, deviation_cm)
        
        return (deviation_cm, assessment, viz_frame)
    
    def create_visualization(self, frame, knee_pos, pedal_pos, deviation):
        """Create visualization showing KOPS alignment."""
        result = frame.copy()
        
        # Draw vertical line from knee
        cv2.line(result, 
                 (knee_pos[0], knee_pos[1]), 
                 (knee_pos[0], pedal_pos[1]), 
                 (0, 255, 255), 2)
        
        # Draw point at pedal spindle
        cv2.circle(result, pedal_pos, 8, (0, 0, 255), -1)
        
        # Add text showing deviation
        cv2.putText(result, 
                    f"KOPS: {deviation:.1f} cm", 
                    (knee_pos[0] + 10, (knee_pos[1] + pedal_pos[1]) // 2), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        return result