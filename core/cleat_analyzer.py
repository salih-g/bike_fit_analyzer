"""
Analyzer for cycling shoe cleat positioning.
"""
import cv2
import numpy as np
from typing import Dict, Tuple, Optional

from bike_fit_analyzer.models.angles import PoseData

class CleatAnalyzer:
    """Analyzes cycling shoe cleat positioning."""
    
    def __init__(self):
        """Initialize the cleat analyzer."""
        self.calibration_factor = 1.0  # Pixels to cm
        
    def detect_foot_points(self, frame, pose_data):
        """
        Detect foot and cleat points in the frame.
        This requires detailed foot detection beyond standard pose estimation.
        """
        # This would require a specialized foot detector
        # We use ankle position from pose data as reference
        
        ankle_position = pose_data.landmarks["ankle"].as_tuple()
        
        # Estimate other points based on ankle position
        # In a real implementation, we would use a foot keypoint detector
        toe_position = (ankle_position[0] + 50, ankle_position[1] + 20)
        heel_position = (ankle_position[0] - 30, ankle_position[1] + 15)
        
        # Estimate cleat position (typically under ball of foot)
        ball_of_foot = (ankle_position[0] + 30, ankle_position[1] + 20)
        
        return {
            "ankle": ankle_position,
            "toe": toe_position,
            "heel": heel_position,
            "ball_of_foot": ball_of_foot
        }
        
    def analyze_cleat_position(self, frame, pose_data) -> Tuple[Dict[str, float], Optional[np.ndarray]]:
        """
        Analyze cleat positioning relative to foot landmarks.
        
        Args:
            frame: Input frame
            pose_data: Processed pose data
            
        Returns:
            Tuple of (measurements dict, visualization frame)
        """
        # Detect foot points
        points = self.detect_foot_points(frame, pose_data)
        
        # Calculate foot length
        foot_length_pixels = np.linalg.norm(
            np.array(points["toe"]) - np.array(points["heel"])
        )
        foot_length_cm = foot_length_pixels * self.calibration_factor
        
        # Calculate cleat position as percentage from heel
        # (ball of foot is typically at 60-70% of foot length from heel)
        heel_to_ball_pixels = np.linalg.norm(
            np.array(points["ball_of_foot"]) - np.array(points["heel"])
        )
        
        cleat_position_percent = (heel_to_ball_pixels / foot_length_pixels) * 100
        
        # Create measurements dictionary
        measurements = {
            "foot_length": foot_length_cm,
            "cleat_position_percent": cleat_position_percent
        }
        
        # Analyze cleat position
        if 60 <= cleat_position_percent <= 70:
            assessment = "Optimal cleat position"
        elif cleat_position_percent < 60:
            assessment = "Cleat position too far back"
        else:
            assessment = "Cleat position too far forward"
            
        measurements["assessment"] = assessment
        
        # Create visualization
        viz_frame = self.create_visualization(frame, points, measurements)
        
        return (measurements, viz_frame)
    
    def create_visualization(self, frame, points, measurements):
        """Create visualization showing cleat positioning."""
        result = frame.copy()
        
        # Draw foot outline
        cv2.line(result, 
                 points["heel"], 
                 points["ankle"], 
                 (0, 255, 255), 2)
        
        cv2.line(result, 
                 points["ankle"], 
                 points["toe"], 
                 (0, 255, 255), 2)
        
        # Draw ball of foot (cleat position)
        cv2.circle(result, points["ball_of_foot"], 8, (0, 0, 255), -1)
        
        # Add text showing cleat position
        cv2.putText(result, 
                    f"Cleat: {measurements['cleat_position_percent']:.1f}%", 
                    (points["ball_of_foot"][0] + 10, points["ball_of_foot"][1]), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        # Add assessment
        cv2.putText(result, 
                    measurements["assessment"], 
                    (points["ankle"][0] - 50, points["ankle"][1] - 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                    (0, 255, 0) if "Optimal" in measurements["assessment"] else (0, 0, 255), 
                    2)
        
        return result