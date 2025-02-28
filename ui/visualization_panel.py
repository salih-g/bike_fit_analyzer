"""
Enhanced visualization panel for the Bike Fit Analyzer.
Displays camera output and visualization overlays.
"""
import cv2
import numpy as np
from typing import Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QCheckBox,
    QGroupBox, QHBoxLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QPixmap, QImage


class VisualizationPanel(QWidget):
    """Panel for displaying camera feed and analysis visualizations."""
    
    def __init__(self):
        """Initialize the visualization panel."""
        super().__init__()
        
        # Store the current frame
        self.current_frame = None
        self.processed_frame = None
        self.pose_data = None
        self.adjustments = None
        
        # Store visualization options
        self.current_view_mode = "Normal View"
        self.show_angles = True
        self.show_guidance = True
        
        # Initialize UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Display options
        self.options_group = QGroupBox("Display Options")
        options_layout = QHBoxLayout()
        
        # View mode selector
        self.view_mode_label = QLabel("View Mode:")
        self.view_mode_combo = QComboBox()
        self.view_mode_combo.addItems([
            "Normal View", 
            "Skeleton Only", 
            "Angles Only",
            "Guidance View",
            "Comparison View"
        ])
        self.view_mode_combo.currentIndexChanged.connect(self.change_view_mode)
        
        options_layout.addWidget(self.view_mode_label)
        options_layout.addWidget(self.view_mode_combo)
        options_layout.addStretch()
        
        # Show angles checkbox
        self.show_angles_check = QCheckBox("Show Angles")
        self.show_angles_check.setChecked(True)
        self.show_angles_check.stateChanged.connect(self.toggle_angles)
        
        # Show guidance checkbox
        self.show_guidance_check = QCheckBox("Show Guidance")
        self.show_guidance_check.setChecked(True)
        self.show_guidance_check.stateChanged.connect(self.toggle_guidance)
        
        options_layout.addWidget(self.show_angles_check)
        options_layout.addWidget(self.show_guidance_check)
        
        self.options_group.setLayout(options_layout)
        self.layout.addWidget(self.options_group)
        
        # Image display
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setStyleSheet("background-color: #222; border: 1px solid #444;")
        self.layout.addWidget(self.image_label)
        
        # Add guidance information panel
        self.guidance_group = QGroupBox("Fit Guidance")
        guidance_layout = QVBoxLayout()
        
        self.guidance_label = QLabel("Fit analysis will appear here when analysis is started.")
        self.guidance_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.guidance_label.setWordWrap(True)
        self.guidance_label.setStyleSheet("padding: 10px;")
        
        guidance_layout.addWidget(self.guidance_label)
        self.guidance_group.setLayout(guidance_layout)
        self.layout.addWidget(self.guidance_group)
        
        # Set initial size
        self.setMinimumWidth(640)
    
    @pyqtSlot(np.ndarray)
    def update_frame(self, frame, pose_data=None, adjustments=None):
        """
        Update the displayed frame.
        
        Args:
            frame: New frame to display
            pose_data: Optional pose data for visualization
            adjustments: Optional adjustment recommendations
        """
        if frame is None:
            return
        
        # Store the current frame and pose data
        self.current_frame = frame.copy()
        self.pose_data = pose_data
        self.adjustments = adjustments
        
        try:
            # Process frame based on visualization options
            self.processed_frame = self._process_frame_with_options(frame)
            
            # Convert OpenCV BGR image to RGB for Qt
            rgb_frame = cv2.cvtColor(self.processed_frame, cv2.COLOR_BGR2RGB)
            
            # Convert numpy array to QImage
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # Create pixmap and set to label
            pixmap = QPixmap.fromImage(qt_image)
            
            # Scale pixmap to fit the label while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.image_label.width(),
                self.image_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            self.image_label.setPixmap(scaled_pixmap)
            
            # Update guidance text if adjustments are available
            if adjustments:
                self._update_guidance_display(adjustments)
        except Exception as e:
            print(f"Error updating frame: {e}")
            # In case of error, just display the original frame
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(
                self.image_label.width(),
                self.image_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
    
    def _process_frame_with_options(self, frame):
        """
        Process the frame with current visualization options.
        
        Args:
            frame: Frame to process
            
        Returns:
            Processed frame
        """
        # Import visualization classes only when needed
        from bike_fit_analyzer.utils.visualization import Visualizer
        
        if not hasattr(self, 'visualizer'):
            self.visualizer = Visualizer()
        
        processed_frame = frame.copy()
        
        # Apply base visualization first
        if self.pose_data is not None:
            # Draw the pose with or without angles
            processed_frame = self.visualizer.draw_pose(processed_frame, self.pose_data, 
                                                       show_angles=self.show_angles)
            
            # Get the view mode key (convert "Normal View" to "normal_view")
            view_mode_key = self.current_view_mode.lower().replace(' ', '_')
            
            # Apply special view modes
            if view_mode_key != "normal_view":
                processed_frame = self._apply_special_view_mode(processed_frame, view_mode_key)
            
            # Apply guidance if enabled and we have adjustments
            if self.show_guidance and self.adjustments:
                processed_frame = self._apply_guidance_cues(processed_frame)
        
        # Add reference info regardless of pose data
        processed_frame = self.visualizer.add_reference_info(processed_frame)
        
        return processed_frame
    
    def _apply_special_view_mode(self, frame, view_mode_key):
        """
        Apply special view mode visualization.
        
        Args:
            frame: Frame to process
            view_mode_key: View mode key string
            
        Returns:
            Processed frame
        """
        result_frame = frame.copy()
        
        # Import necessary classes
        import cv2
        import numpy as np
        from bike_fit_analyzer.config.settings import FONT, COLORS
        
        if view_mode_key == "skeleton_only":
            # Create a black background
            result_frame = np.zeros_like(frame)
            
            # Draw only the skeleton with high contrast colors
            landmarks = self.pose_data.landmarks
            
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
        
        elif view_mode_key == "angles_only":
            # Create a dark background
            result_frame = np.zeros_like(frame)
            
            # Draw only the angles with high contrast
            for angle_type, angle in self.pose_data.angles.items():
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
        
        elif view_mode_key == "comparison_view":
            # Split the frame into before/after sections
            h, w = result_frame.shape[:2]
            
            # Draw dividing line
            cv2.line(result_frame, (w//2, 0), (w//2, h), (0, 255, 255), 2)
            
            # Add before/after labels
            cv2.putText(
                result_frame, 
                "Current", 
                (w//4, 30), 
                FONT, 
                1.0, 
                (255, 255, 255), 
                2
            )
            
            cv2.putText(
                result_frame, 
                "Ideal Target", 
                (3*w//4, 30), 
                FONT, 
                1.0, 
                (255, 255, 255), 
                2
            )
        
        return result_frame
    
    def _apply_guidance_cues(self, frame):
        """
        Apply guidance cues to the frame.
        
        Args:
            frame: Frame to process
            
        Returns:
            Processed frame with guidance cues
        """
        if not self.adjustments or not self.pose_data:
            return frame
        
        result_frame = frame.copy()
        
        # Draw adjustment arrows
        result_frame = self._draw_adjustment_arrows(result_frame)
        
        # Draw target pose overlay if in guidance view
        if self.current_view_mode.lower() == "guidance view":
            result_frame = self._draw_target_pose_overlay(result_frame)
        
        # Draw guidance text
        result_frame = self._draw_guidance_text(result_frame)
        
        return result_frame
    
    def _draw_adjustment_arrows(self, frame):
        """Draw directional arrows for suggested adjustments."""
        import cv2
        from bike_fit_analyzer.config.settings import COLORS, FONT
        
        result_frame = frame.copy()
        
        # Group adjustments by component
        component_adjustments = {}
        for adjustment in self.adjustments:
            component = adjustment.component
            if component not in component_adjustments:
                component_adjustments[component] = []
            component_adjustments[component].append(adjustment)
        
        # Draw arrows for each component
        landmarks = self.pose_data.landmarks
        arrow_length = 40
        arrow_thickness = 2
        font_scale = 0.7
        text_thickness = 2
        
        for component, adj_list in component_adjustments.items():
            # Get highest priority adjustment for this component
            adjustment = min(adj_list, key=lambda x: x.priority)
            
            # Determine arrow position based on component
            if component == "saddle":
                # Position arrow near hip
                position = (landmarks["hip"].x, landmarks["hip"].y - 50)
                direction = adjustment.direction
                
                # Draw vertical arrow
                x, y = position
                if direction in ["up", "raise"]:
                    pt1 = (x, y + arrow_length // 2)
                    pt2 = (x, y - arrow_length // 2)
                else:  # down, lower
                    pt1 = (x, y - arrow_length // 2)
                    pt2 = (x, y + arrow_length // 2)
                
                cv2.arrowedLine(
                    result_frame, pt1, pt2, 
                    COLORS["highlight"], 
                    thickness=arrow_thickness,
                    tipLength=0.3
                )
                
                # Add text label
                text_position = (x + 10, y)
                cv2.putText(
                    result_frame, 
                    direction.title(), 
                    text_position, 
                    FONT, 
                    font_scale, 
                    COLORS["text_color"], 
                    text_thickness
                )
                
            elif component == "handlebar":
                # Position arrow near hands/elbow
                position = (landmarks["elbow"].x + 50, landmarks["elbow"].y)
                direction = adjustment.direction
                
                # Draw arrow
                x, y = position
                if direction in ["up", "raise", "down", "lower"]:
                    # Vertical arrow
                    if direction in ["up", "raise"]:
                        pt1 = (x, y + arrow_length // 2)
                        pt2 = (x, y - arrow_length // 2)
                    else:
                        pt1 = (x, y - arrow_length // 2)
                        pt2 = (x, y + arrow_length // 2)
                else:
                    # Horizontal arrow
                    if direction in ["left", "shorten", "back"]:
                        pt1 = (x + arrow_length // 2, y)
                        pt2 = (x - arrow_length // 2, y)
                    else:
                        pt1 = (x - arrow_length // 2, y)
                        pt2 = (x + arrow_length // 2, y)
                
                cv2.arrowedLine(
                    result_frame, pt1, pt2, 
                    COLORS["highlight"], 
                    thickness=arrow_thickness,
                    tipLength=0.3
                )
                
                # Add text label
                text_position = (x + 10, y - 10)
                cv2.putText(
                    result_frame, 
                    direction.title(), 
                    text_position, 
                    FONT, 
                    font_scale, 
                    COLORS["text_color"], 
                    text_thickness
                )
        
        return result_frame
    
    def _draw_target_pose_overlay(self, frame):
        """Draw target pose overlay showing ideal positions."""
        import cv2
        import numpy as np
        import math
        from bike_fit_analyzer.config.settings import IDEAL_ANGLES, COLORS
        
        result_frame = frame.copy()
        
        # Create a transparent overlay
        overlay = result_frame.copy()
        
        # Draw target pose
        landmarks = self.pose_data.landmarks
        angles = self.pose_data.angles
        
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
    
    def _draw_target_angle_line(self, frame, point_a, point_b, target_angle, current_angle):
        """Draw a line showing the target angle."""
        import cv2
        import numpy as np
        import math
        from bike_fit_analyzer.config.settings import COLORS
        
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
            dash_length=10,
            gap_length=5
        )
    
    def _draw_dashed_line(self, frame, pt1, pt2, color, thickness=1, dash_length=10, gap_length=5):
        """Draw a dashed line on the frame."""
        import cv2
        import math
        
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
    
    def _draw_guidance_text(self, frame):
        """Draw guidance text on the frame."""
        import cv2
        from bike_fit_analyzer.config.settings import FONT, COLORS
        
        result_frame = frame.copy()
        
        # Draw main guidance text in the corner
        y_offset = 30
        for i, adjustment in enumerate(self.adjustments[:3]):  # Show top 3 recommendations
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
    
    def _update_guidance_display(self, adjustments):
        """Update the guidance text display."""
        if not adjustments:
            return
        
        # Generate feedback text
        guidance_text = "<b>Bike Fit Guidance:</b><br><br>"
        
        for i, adjustment in enumerate(adjustments[:5]):  # Show top 5 items
            priority_color = "#FF6347" if adjustment.priority == 1 else "#FFC107" if adjustment.priority == 2 else "#4CAF50"
            guidance_text += f"<span style='color:{priority_color};'>• {adjustment.description}</span><br><br>"
        
        self.guidance_label.setText(guidance_text)
    
    def clear_display(self):
        """Clear the display."""
        self.image_label.clear()
        self.current_frame = None
        self.processed_frame = None
        self.pose_data = None
        self.adjustments = None
        self.guidance_label.setText("Fit analysis will appear here when analysis is started.")
    
    @pyqtSlot(int)
    def change_view_mode(self, index):
        """
        Change the visualization view mode.
        
        Args:
            index: Index of the selected view mode
        """
        self.current_view_mode = self.view_mode_combo.currentText()
        print(f"View mode changed to: {self.current_view_mode}")
        
        # Update frame with new view mode if we have a current frame
        if self.current_frame is not None:
            try:
                processed_frame = self._process_frame_with_options(self.current_frame)
                
                # Update display
                rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qt_image)
                scaled_pixmap = pixmap.scaled(
                    self.image_label.width(),
                    self.image_label.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
            except Exception as e:
                print(f"Error updating view mode: {e}")
    
    @pyqtSlot(int)
    def toggle_angles(self, state):
        """
        Toggle the display of angles.
        
        Args:
            state: Checkbox state
        """
        self.show_angles = state == Qt.Checked
        print(f"Show angles: {self.show_angles}")
        
        # Update frame with new angle visibility if we have a current frame
        if self.current_frame is not None:
            try:
                processed_frame = self._process_frame_with_options(self.current_frame)
                
                # Update display
                rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qt_image)
                scaled_pixmap = pixmap.scaled(
                    self.image_label.width(),
                    self.image_label.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
            except Exception as e:
                print(f"Error toggling angles: {e}")
    
    @pyqtSlot(int)
    def toggle_guidance(self, state):
        """
        Toggle the display of guidance cues.
        
        Args:
            state: Checkbox state
        """
        self.show_guidance = state == Qt.Checked
        print(f"Show guidance: {self.show_guidance}")
        
        # Update frame with new guidance visibility if we have a current frame
        if self.current_frame is not None:
            try:
                processed_frame = self._process_frame_with_options(self.current_frame)
                
                # Update display
                rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qt_image)
                scaled_pixmap = pixmap.scaled(
                    self.image_label.width(),
                    self.image_label.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
            except Exception as e:
                print(f"Error toggling guidance: {e}")
    
    def update_guidance_text(self, guidance_text):
        """
        Update the guidance text.
        
        Args:
            guidance_text: New guidance text
        """
        self.guidance_label.setText(guidance_text)