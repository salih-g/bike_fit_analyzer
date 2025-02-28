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
        
        # Visual cues generator
        from bike_fit_analyzer.guidance.visual_cues import VisualCues
        self.visual_cues = VisualCues()
    
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
         image, f"{angle.value:.1f} deg", text_position, FONT, 0.6, COLORS["text_color"], 2
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
            text = f"{angle_type.replace('_', ' ').title()}: {min_val}deg-{max_val}deg"
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
    
    def visualize_frame(self, frame, pose_data=None, adjustments=None, 
                       show_skeleton=True, show_landmarks=True, show_angles=True, 
                       show_guidance=True, show_arrows=True, show_color_coding=True,
                       show_text_cues=True, show_target_pose=False, view_mode="Normal View"):
        """
        Visualize the frame with pose data and reference information.
        
        Args:
            frame: Input frame
            pose_data: Optional pose data to visualize
            adjustments: Optional adjustment recommendations
            show_skeleton: Whether to show the skeleton
            show_landmarks: Whether to show landmarks
            show_angles: Whether to show angles
            show_guidance: Whether to show guidance cues
            show_arrows: Whether to show adjustment arrows
            show_color_coding: Whether to show color coding
            show_text_cues: Whether to show text cues
            show_target_pose: Whether to show target pose overlay
            view_mode: Visualization mode
            
        Returns:
            Visualized frame
        """
        output_frame = frame.copy()
        
        # Use view_mode specific visualization if specified
        if view_mode != "Normal View" and pose_data:
            output_frame = self.visual_cues.enhance_frame_visualization(
                output_frame, pose_data, view_mode.lower().replace(' ', '_')
            )
            return output_frame
        
        # Draw pose if we have data and skeleton/landmarks are enabled
        if pose_data:
            if show_skeleton:
                output_frame = self.draw_skeleton(output_frame, pose_data)
                
            if show_landmarks:
                output_frame = self.draw_landmarks(output_frame, pose_data)
                
            if show_angles:
                output_frame = self.draw_angles(output_frame, pose_data)
                
            if show_guidance and adjustments:
                output_frame = self.visual_cues.apply_all_guidance_cues(
                    output_frame, pose_data, adjustments,
                    show_arrows=show_arrows,
                    show_target_pose=show_target_pose,
                    show_text=show_text_cues
                )
        
        # Add reference information (FPS, etc.)
        output_frame = self.add_reference_info(output_frame)
        
        return output_frame

    def draw_skeleton(self, frame, pose_data):
        """
        Draw the skeleton lines connecting landmarks.
        
        Args:
            frame: Input frame
            pose_data: Processed pose data
            
        Returns:
            Frame with skeleton drawn
        """
        if not pose_data:
            return frame
        
        result_frame = frame.copy()
        landmarks = pose_data.landmarks
        
        # Define the connections between landmarks
        connections = [
            ("nose", "shoulder"),
            ("shoulder", "elbow"),
            ("elbow", "wrist"),
            ("shoulder", "hip"),
            ("hip", "knee"),
            ("knee", "ankle")
        ]
        
        # Draw lines for each connection
        for start_point_name, end_point_name in connections:
            if start_point_name in landmarks and end_point_name in landmarks:
                start_point = landmarks[start_point_name].as_tuple()
                end_point = landmarks[end_point_name].as_tuple()
                
                from bike_fit_analyzer.config.settings import COLORS, LINE_THICKNESS
                cv2.line(
                    result_frame, 
                    start_point, 
                    end_point, 
                    COLORS["line_color"], 
                    LINE_THICKNESS
                )
        
        return result_frame

    def draw_landmarks(self, frame, pose_data):
        """
        Draw landmark points on the frame.
        
        Args:
            frame: Input frame
            pose_data: Processed pose data
            
        Returns:
            Frame with landmarks drawn
        """
        if not pose_data:
            return frame
        
        result_frame = frame.copy()
        landmarks = pose_data.landmarks
        
        # Draw each landmark as a circle
        for point_name, point in landmarks.items():
            from bike_fit_analyzer.config.settings import COLORS, POINT_RADIUS
            cv2.circle(
                result_frame, 
                point.as_tuple(), 
                POINT_RADIUS, 
                COLORS["highlight"], 
                -1  # Filled circle
            )
        
        return result_frame

    def draw_angles(self, frame, pose_data):
        """
        Draw angle measurements on the frame.
        
        Args:
            frame: Input frame
            pose_data: Processed pose data
            
        Returns:
            Frame with angles drawn
        """
        if not pose_data:
            return frame
        
        result_frame = frame.copy()
        
        # For each angle, draw an arc and label
        for angle_type, angle in pose_data.angles.items():
            # Get the degree symbol safely
            degree_symbol = chr(176)  # ASCII code for degree symbol
            
            # Calculate arc positions
            point_a = angle.point_a.as_tuple()
            point_b = angle.point_b.as_tuple()
            point_c = angle.point_c.as_tuple()
            
            # Get color based on whether angle is in ideal range
            from bike_fit_analyzer.config.settings import IDEAL_ANGLES, COLORS, FONT
            
            # Determine if angle is in the ideal range
            in_range = False
            if angle_type in IDEAL_ANGLES:
                min_val, max_val = IDEAL_ANGLES[angle_type]
                in_range = min_val <= angle.value <= max_val
            
            # Choose color based on whether angle is in range
            color = COLORS["in_range"] if in_range else COLORS["out_of_range"]
            
            # Draw angle arc
            # Calculate vectors from vertex (point_b) to the other points
            import numpy as np
            import math
            
            v1 = np.array([point_a[0] - point_b[0], point_a[1] - point_b[1]])
            v2 = np.array([point_c[0] - point_b[0], point_c[1] - point_b[1]])
            
            # Calculate angles for arc
            angle1 = math.atan2(v1[1], v1[0])
            angle2 = math.atan2(v2[1], v2[0])
            
            # Convert to degrees
            start_angle = math.degrees(angle1)
            end_angle = math.degrees(angle2)
            
            # Ensure proper ordering for arc drawing
            if start_angle > end_angle:
                start_angle, end_angle = end_angle, start_angle
            
            # Calculate radius for arc based on vector lengths
            radius = int(min(np.linalg.norm(v1), np.linalg.norm(v2)) * 0.3)
            radius = max(radius, 20)  # Minimum radius for visibility
            
            # Draw arc
            cv2.ellipse(
                result_frame,
                point_b,
                (radius, radius),
                0,
                start_angle,
                end_angle,
                color,
                2
            )
            
            # Add text with angle value
            midpoint_angle = (start_angle + end_angle) / 2
            text_x = int(point_b[0] + (radius + 10) * math.cos(math.radians(midpoint_angle)))
            text_y = int(point_b[1] + (radius + 10) * math.sin(math.radians(midpoint_angle)))
            
            cv2.putText(
                result_frame,
                f"{angle.value:.1f}{degree_symbol}",
                (text_x, text_y),
                FONT,
                0.6,
                COLORS["text_color"],
                2
            )
        
        return result_frame