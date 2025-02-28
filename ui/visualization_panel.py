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
    def update_frame(self, frame):
        """
        Update the displayed frame.
        
        Args:
            frame: New frame to display
        """
        if frame is None:
            return
        
        # Store the current frame
        self.current_frame = frame.copy()
        
        # Convert OpenCV BGR image to RGB for Qt
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
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
    
    def clear_display(self):
        """Clear the display."""
        self.image_label.clear()
        self.current_frame = None
    
    @pyqtSlot(int)
    def change_view_mode(self, index):
        """
        Change the visualization view mode.
        
        Args:
            index: Index of the selected view mode
        """
        # This will be implemented to change how the frame is visualized
        # For now, just update the UI
        mode = self.view_mode_combo.currentText()
        print(f"View mode changed to: {mode}")
    
    @pyqtSlot(int)
    def toggle_angles(self, state):
        """
        Toggle the display of angles.
        
        Args:
            state: Checkbox state
        """
        # This will be implemented to show/hide angles in the visualization
        show = state == Qt.Checked
        print(f"Show angles: {show}")
    
    @pyqtSlot(int)
    def toggle_guidance(self, state):
        """
        Toggle the display of guidance cues.
        
        Args:
            state: Checkbox state
        """
        # This will be implemented to show/hide guidance in the visualization
        show = state == Qt.Checked
        print(f"Show guidance: {show}")
    
    def update_guidance_text(self, guidance_text):
        """
        Update the guidance text.
        
        Args:
            guidance_text: New guidance text
        """
        self.guidance_label.setText(guidance_text)
