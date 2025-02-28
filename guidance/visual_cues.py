"""
Visual cues for bike fit guidance.
"""
import cv2
import numpy as np
import math
from typing import Dict, List, Tuple, Optional

from bike_fit_analyzer.models.angles import Angle, Point, PoseData
from bike_fit_analyzer.config.settings import IDEAL_ANGLES, COLORS, FONT
from bike_fit_analyzer.guidance.bike_adjustments import AdjustmentRecommendation


class VisualCues:
    """Generates visual cues for bike fit guidance."""
    
    def __init__(self):
        """Initialize the visual cues generator."""
        # Arrow settings
        self.arrow_length = 40
        self.arrow_thickness = 2
        self.arrow_head_length = 10
        
        # Text settings
        self.text_offset = 30
        self.font_scale = 0.7
        self.text_thickness = 2
        
        # Guidance line settings
        self.line_dash_length = 10
        self.line_gap_length = 5
    
    def draw_adjustment_arrows(self, frame: np.ndarray, pose_data: PoseData, 
                              adjustments: List[AdjustmentRecommendation]) -> np.ndarray:
        """
        Draw directional arrows for suggested adjustments.
        
        Args:
            frame: Input frame
            pose_data: Processed pose data
            adjustments: List of adjustment recommendations
            
        Returns:
            Frame with adjustment arrows
        """
        if not adjustments:
            return frame
        
        result_frame = frame.copy()
        
        # Group adjustments by component
        component_adjustments = {}
        for adjustment in adjustments:
            component = adjustment.component
            if component not in component_adjustments:
                component_adjustments[component] = []
            component_adjustments[component].append(adjustment)
        
        # Draw arrows for each component
        landmarks = pose_data.landmarks
        for component, adj_list in component_adjustments.items():
            # Get highest priority adjustment for this component
            adjustment = min(adj_list, key=lambda x: x.priority)
            
            # Determine arrow position based on component
            if component == "saddle":
                # Position arrow near hip
                position = (landmarks["hip"].x, landmarks["hip"].y - 50)
                self._draw_vertical_arrow(result_frame, position, adjustment.direction)
                
            elif component == "handlebar":
                # Position arrow near hands/elbow
                position = (landmarks["elbow"].x + 50, landmarks["elbow"].y)
                if adjustment.direction in ["raise", "lower"]:
                    self._draw_vertical_arrow(result_frame, position, adjustment.direction)
                else:
                    self._draw_horizontal_arrow(result_frame, position, adjustment.direction)
                    
            elif component == "stem":
                # Position arrow near the handlebar/stem area
                position = (landmarks["shoulder"].x + 80, landmarks["shoulder"].y - 30)
                self._draw_horizontal_arrow(result_frame, position, adjustment.direction)
        
        return result_frame
    
    def _draw_vertical_arrow(self, frame: np.ndarray, position: Tuple[int, int], direction: str):
        """Draw a vertical arrow."""
        x, y = position
        if direction in ["up", "raise"]:
            pt1 = (x, y + self.arrow_length // 2)
            pt2 = (x, y - self.arrow_length // 2)
        else:  # down, lower
            pt1 = (x, y - self.arrow_length // 2)
            pt2 = (x, y + self.arrow_length // 2)
        
        cv2.arrowedLine(
            frame, pt1, pt2, 
            COLORS["highlight"], 
            thickness=self.arrow_thickness,
            tipLength=0.3
        )
        
        # Add text label
        text_position = (x + 10, y)
        cv2.putText(
            frame, 
            direction.title(), 
            text_position, 
            FONT, 
            self.font_scale, 
            COLORS["text_color"], 
            self.text_thickness
        )
    
    def _draw_horizontal_arrow(self, frame: np.ndarray, position: Tuple[int, int], direction: str):
        """Draw a horizontal arrow."""
        x, y = position
        if direction in ["left", "shorten", "back"]:
            pt1 = (x + self.arrow_length // 2, y)
            pt2 = (x - self.arrow_length // 2, y)
        else:  # right, extend, forward
            pt1 = (x - self.arrow_length // 2, y)
            pt2 = (x + self.arrow_length // 2, y)
        
        cv2.arrowedLine(
            frame, pt1, pt2, 
            COLORS["highlight"], 
            thickness=self.arrow_thickness,
            tipLength=0.3
        )
        
        # Add text label
        text_position = (x, y - 10)
        cv2.putText(
            frame, 
            direction.title(), 
            text_position, 
            FONT, 
            self.font_scale, 
            COLORS["text_color"], 
            self.text_thickness
        )
    
    def draw_target_pose_overlay(self, frame: np.ndarray, pose_data: PoseData) -> np.ndarray:
        """
        Draw target pose overlay showing ideal positions.
        
        Args:
            frame: Input frame
            pose_data: Processed pose data
            
        Returns:
            Frame with target pose overlay
        """
        result_frame = frame.copy()
        
        # Create a transparent overlay
        overlay = result_frame.copy()
        
        # Draw target pose - this is a simplified example
        # For each angle that's outside ideal range, draw a line showing the target position
        landmarks = pose_data.landmarks
        angles = pose_data.angles
        
        for angle_type, angle in angles.items():
            if angle_type in IDEAL_ANGLES and not angle.is_in_range(IDEAL_ANGLES):
                min_val, max_val = IDEAL_ANGLES[angle_type]
                
                # Calculate target angle (mid-point of ideal range)
                target_angle = (min_val + max_val) / 2
                
                # Draw the ideal angle line
                if angle_type == "neck_angle":
                    self._draw_target_angle_line(
                        overlay, 
                        landmarks["nose"], 
                        landmarks["shoulder"], 
                        target_angle,
                        angle.value
                    )
                elif angle_type == "shoulder_angle":
                    self._draw_target_angle_line(
                        overlay, 
                        landmarks["hip"], 
                        landmarks["shoulder"], 
                        target_angle,
                        angle.value
                    )
                elif angle_type == "elbow_angle":
                    self._draw_target_angle_line(
                        overlay, 
                        landmarks["shoulder"], 
                        landmarks["elbow"], 
                        target_angle,
                        angle.value
                    )
                elif angle_type == "hip_angle":
                    self._draw_target_angle_line(
                        overlay, 
                        landmarks["shoulder"], 
                        landmarks["hip"], 
                        target_angle,
                        angle.value
                    )
                elif angle_type == "knee_angle":
                    self._draw_target_angle_line(
                        overlay, 
                        landmarks["hip"], 
                        landmarks["knee"], 
                        target_angle,
                        angle.value
                    )
        
        # Blend the overlay with the original frame
        alpha = 0.4  # Transparency factor
        cv2.addWeighted(overlay, alpha, result_frame, 1 - alpha, 0, result_frame)
        
        return result_frame
    
    def _draw_target_angle_line(self, frame: np.ndarray, point_a: Point, point_b: Point, 
                               target_angle: float, current_angle: float):
        """
        Draw a line showing the target angle.
        
        Args:
            frame: Frame to draw on
            point_a: First point
            point_b: Vertex point
            target_angle: Target angle in degrees
            current_angle: Current angle in degrees
        """
        # Convert points to numpy arrays
        a = np.array([point_a.x, point_a.y])
        b = np.array([point_b.x, point_b.y])
        
        # Calculate distance for line length
        dist = np.linalg.norm(a - b)
        line_length = min(100, dist)
        
        # Calculate direction vector from b to a
        dir_vector = a - b
        dir_vector = dir_vector / np.linalg.norm(dir_vector)
        
        # Calculate angle adjustment needed
        angle_diff = target_angle - current_angle
        
        # Rotate the direction vector by the angle difference
        angle_rad = np.radians(angle_diff)
        rotation_matrix = np.array([
            [np.cos(angle_rad), -np.sin(angle_rad)],
            [np.sin(angle_rad), np.cos(angle_rad)]
        ])
        
        rotated_vector = np.dot(rotation_matrix, dir_vector)
        
        # Calculate target point
        target_point = b + rotated_vector * line_length
        
        # Draw dashed line to show target position
        self._draw_dashed_line(
            frame, 
            (int(b[0]), int(b[1])), 
            (int(target_point[0]), int(target_point[1])),
            COLORS["highlight"],
            thickness=2,
            dash_length=self.line_dash_length,
            gap_length=self.line_gap_length
        )
    
    def _draw_dashed_line(self, frame: np.ndarray, pt1: Tuple[int, int], pt2: Tuple[int, int], 
                         color: Tuple[int, int, int], thickness: int = 1, 
                         dash_length: int = 10, gap_length: int = 5):
        """
        Draw a dashed line on the frame.
        
        Args:
            frame: Frame to draw on
            pt1: Start point
            pt2: End point
            color: Line color
            thickness: Line thickness
            dash_length: Length of each dash
            gap_length: Length of each gap
        """
        x1, y1 = pt1
        x2, y2 = pt2
        
        # Calculate line length and direction
        dx, dy = x2 - x1, y2 - y1
        dist = math.sqrt(dx * dx + dy * dy)
        
        # Normalize direction vector
        if dist > 0:
            dx, dy = dx / dist, dy / dist
        
        # Calculate number of segments
        segment_length = dash_length + gap_length
        num_segments = int(dist / segment_length)
        
        # Draw dashed line
        for i in range(num_segments):
            start_dist = i * segment_length
            end_dist = start_dist + dash_length
            
            start_x = int(x1 + dx * start_dist)
            start_y = int(y1 + dy * start_dist)
            
            end_x = int(x1 + dx * min(end_dist, dist))
            end_y = int(y1 + dy * min(end_dist, dist))
            
            cv2.line(frame, (start_x, start_y), (end_x, end_y), color, thickness)
    
    def draw_guidance_text(self, frame: np.ndarray, pose_data: PoseData, 
                          adjustments: List[AdjustmentRecommendation]) -> np.ndarray:
        """
        Draw guidance text on the frame.
        
        Args:
            frame: Input frame
            pose_data: Processed pose data
            adjustments: List of adjustment recommendations
            
        Returns:
            Frame with guidance text
        """
        if not adjustments:
            return frame
        
        result_frame = frame.copy()
        
        # Draw main guidance text in the corner
        y_offset = 30
        for i, adjustment in enumerate(adjustments[:3]):  # Show top 3 recommendations
            text = f"{i+1}. {adjustment.description}"
            cv2.putText(
                result_frame, 
                text, 
                (10, y_offset + i * 30), 
                FONT, 
                0.6, 
                COLORS["text_color"], 
                2
            )
        
        return result_frame
    
    def apply_all_guidance_cues(self, frame: np.ndarray, pose_data: PoseData, 
                              adjustments: List[AdjustmentRecommendation],
                              show_arrows: bool = True,
                              show_target_pose: bool = True,
                              show_text: bool = True) -> np.ndarray:
        """
        Apply all guidance cues to the frame.
        
        Args:
            frame: Input frame
            pose_data: Processed pose data
            adjustments: List of adjustment recommendations
            show_arrows: Whether to show adjustment arrows
            show_target_pose: Whether to show target pose overlay
            show_text: Whether to show guidance text
            
        Returns:
            Frame with all guidance cues
        """
        result_frame = frame.copy()
        
        # Apply each enabled cue type
        if show_target_pose:
            result_frame = self.draw_target_pose_overlay(result_frame, pose_data)
        
        if show_arrows:
            result_frame = self.draw_adjustment_arrows(result_frame, pose_data, adjustments)
        
        if show_text:
            result_frame = self.draw_guidance_text(result_frame, pose_data, adjustments)
        
        return result_frame
    
    def enhance_frame_visualization(self, frame: np.ndarray, pose_data: PoseData,
                                  view_mode: str = "normal") -> np.ndarray:
        """
        Enhance the frame visualization based on the selected view mode.
        
        Args:
            frame: Input frame
            pose_data: Processed pose data
            view_mode: Visualization mode (normal, skeleton, angles, guidance)
            
        Returns:
            Enhanced visualization frame
        """
        result_frame = frame.copy()
        
        if view_mode == "skeleton_only":
            # Create a black background
            result_frame = np.zeros_like(frame)
            
            # Draw only the skeleton with high contrast colors
            landmarks = pose_data.landmarks
            
            # Draw key points
            for point in landmarks.values():
                cv2.circle(
                    result_frame, 
                    point.as_tuple(), 
                    8, 
                    (0, 255, 255), 
                    -1
                )
            
            # Draw connections
            connections = [
                (landmarks["nose"], landmarks["shoulder"]),
                (landmarks["shoulder"], landmarks["elbow"]),
                (landmarks["elbow"], landmarks["wrist"]),
                (landmarks["shoulder"], landmarks["hip"]),
                (landmarks["hip"], landmarks["knee"]),
                (landmarks["knee"], landmarks["ankle"])
            ]
            
            for start_point, end_point in connections:
                cv2.line(
                    result_frame, 
                    start_point.as_tuple(), 
                    end_point.as_tuple(), 
                    (0, 255, 0), 
                    3
                )
        
        elif view_mode == "angles_only":
            # Create a dark background
            result_frame = np.zeros_like(frame)
            
            # Draw only the angles with high contrast
            for angle_type, angle in pose_data.angles.items():
                point_a = angle.point_a.as_tuple()
                point_b = angle.point_b.as_tuple()
                point_c = angle.point_c.as_tuple()
                
                # Draw lines
                cv2.line(result_frame, point_a, point_b, (0, 255, 0), 2)
                cv2.line(result_frame, point_b, point_c, (0, 255, 0), 2)
                
                # Calculate position for the angle text
                text_x = (point_a[0] + point_b[0] + point_c[0]) // 3
                text_y = (point_a[1] + point_b[1] + point_c[1]) // 3
                
                # Draw angle value
                cv2.putText(
                    result_frame, 
                    f"{angle_type}: {angle.value:.1f}deg", 
                    (text_x, text_y), 
                    FONT, 
                    0.8, 
                    (255, 255, 0), 
                    2
                )
        
        elif view_mode == "comparison_view":
            # Split the frame into before/after sections
            # For now, just draw a dividing line down the middle
            h, w = result_frame.shape[:2]
            cv2.line(result_frame, (w//2, 0), (w//2, h), (0, 255, 255), 2)
            
            # Add before/after labels
            cv2.putText(
                result_frame, 
                "Before", 
                (w//4, 30), 
                FONT, 
                1.0, 
                (255, 255, 255), 
                2
            )
            
            cv2.putText(
                result_frame, 
                "After (Target)", 
                (3*w//4, 30), 
                FONT, 
                1.0, 
                (255, 255, 255), 
                2
            )
        
        # For normal and guidance modes, the frame is returned as is
        return result_frame