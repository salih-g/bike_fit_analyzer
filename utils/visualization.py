"""
Visualization utilities for the Bike Fit Analyzer.
"""
import cv2
import numpy as np
import time
from typing import Tuple, Dict, List

from bike_fit_analyzer.models.angles import Point, Angle, PoseData
from bike_fit_analyzer.config.settings import (
    IDEAL_ANGLES, COLORS, FONT, LINE_THICKNESS, POINT_RADIUS
)


class Visualizer:
    """Handles visualization of pose data and UI elements."""
    
    def __init__(self):
        """Initialize the visualizer."""
        self.prev_time = 0
        self.current_time = 0
    
    def get_color(self, angle: Angle) -> Tuple[int, int, int]:
        """Get color based on whether angle is in ideal range."""
        if angle.is_in_range(IDEAL_ANGLES):
            return COLORS["in_range"]
        return COLORS["out_of_range"]
    
    def draw_angle_arc(self, image: np.ndarray, angle: Angle) -> None:
        """
        Draw an arc to visualize the angle.
        
        Args:
            image: Image to draw on
            angle: Angle to visualize
        """
        point_a = angle.point_a.as_tuple()
        point_b = angle.point_b.as_tuple()
        point_c = angle.point_c.as_tuple()
        
        # Calculate radius based on distance
        radius = int(np.linalg.norm(np.array(point_b) - np.array(point_a)) * 0.3)
        
        # Calculate angles for arc
        vector1 = np.array([point_a[0] - point_b[0], point_a[1] - point_b[1]])
        vector2 = np.array([point_c[0] - point_b[0], point_c[1] - point_b[1]])
        
        angle1 = np.arctan2(vector1[1], vector1[0]) * 180 / np.pi
        angle2 = np.arctan2(vector2[1], vector2[0]) * 180 / np.pi
        
        # Ensure angles are in the proper range
        start_angle = (min(angle1, angle2) + 360) % 360
        end_angle = (max(angle1, angle2) + 360) % 360
        
        # Swap if we need to draw the minor arc
        if end_angle - start_angle > 180:
            start_angle, end_angle = end_angle, start_angle + 360
            
        color = self.get_color(angle)
            
        # Draw the arc
        cv2.ellipse(image, point_b, (radius, radius), 0, start_angle, end_angle, color, 2)
        
        # Position for the text
        text_offset_x = radius * np.cos(np.radians((start_angle + end_angle) / 2))
        text_offset_y = radius * np.sin(np.radians((start_angle + end_angle) / 2))
        text_position = (
            int(point_b[0] + 1.2 * text_offset_x), 
            int(point_b[1] + 1.2 * text_offset_y)
        )
        
        # Add the angle text
        cv2.putText(
            image, 
            f"{angle.value:.1f}°", 
            text_position, 
            FONT, 
            0.6, 
            COLORS["text_color"], 
            2
        )
    
    def draw_pose(self, frame: np.ndarray, pose_data: PoseData) -> np.ndarray:
        """
        Draw pose landmarks, connections, and angles on the frame.
        
        Args:
            frame: Input frame
            pose_data: Pose data to visualize
            
        Returns:
            Frame with visualization elements added
        """
        # Draw key points
        for point in pose_data.landmarks.values():
            cv2.circle(frame, point.as_tuple(), POINT_RADIUS, COLORS["highlight"], -1)
        
        # Draw connecting lines
        connections = [
            (pose_data.landmarks["nose"], pose_data.landmarks["shoulder"]),
            (pose_data.landmarks["shoulder"], pose_data.landmarks["elbow"]),
            (pose_data.landmarks["elbow"], pose_data.landmarks["wrist"]),
            (pose_data.landmarks["shoulder"], pose_data.landmarks["hip"]),
            (pose_data.landmarks["hip"], pose_data.landmarks["knee"]),
            (pose_data.landmarks["knee"], pose_data.landmarks["ankle"])
        ]
        
        for start_point, end_point in connections:
            cv2.line(
                frame, 
                start_point.as_tuple(), 
                end_point.as_tuple(), 
                COLORS["line_color"], 
                LINE_THICKNESS
            )
        
        # Draw angles with arcs
        for angle in pose_data.angles.values():
            self.draw_angle_arc(frame, angle)
        
        return frame
    
    def add_reference_info(self, frame: np.ndarray) -> np.ndarray:
        """
        Add reference information to the frame.
        
        Args:
            frame: Input frame
            
        Returns:
            Frame with reference information added
        """
        # Add ideal angle ranges as reference
        y_offset = 30
        for i, (angle_type, (min_val, max_val)) in enumerate(IDEAL_ANGLES.items()):
            text = f"{angle_type.replace('_', ' ').title()}: {min_val}°-{max_val}°"
            cv2.putText(
                frame, 
                text, 
                (10, y_offset + i * 30), 
                FONT, 
                0.6, 
                COLORS["text_color"], 
                2
            )
        
        # Calculate and display FPS
        self.current_time = time.time()
        fps = 1 / (self.current_time - self.prev_time) if (self.current_time - self.prev_time) > 0 else 0
        self.prev_time = self.current_time
        
        cv2.putText(
            frame, 
            f"FPS: {int(fps)}", 
            (10, frame.shape[0] - 10), 
            FONT, 
            0.7, 
            COLORS["text_color"], 
            2
        )
        
        return frame
    
    def visualize_frame(self, frame: np.ndarray, pose_data: PoseData = None) -> np.ndarray:
        """
        Visualize the frame with pose data and reference information.
        
        Args:
            frame: Input frame
            pose_data: Optional pose data to visualize
            
        Returns:
            Visualized frame
        """
        output_frame = frame.copy()
        
        if pose_data:
            output_frame = self.draw_pose(output_frame, pose_data)
        
        output_frame = self.add_reference_info(output_frame)
        
        return output_frame
