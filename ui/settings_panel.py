"""
Settings panel for the Bike Fit Analyzer.
Provides controls for camera, analysis, and visualization settings.
"""
from typing import Optional, Dict, List, Any
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSlider, QSpinBox, QDoubleSpinBox, QCheckBox,
    QGroupBox, QFormLayout, QTabWidget, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal

from bike_fit_analyzer.utils.camera import CameraManager
from bike_fit_analyzer.config.settings import IDEAL_ANGLES


class SettingsPanel(QWidget):
    """Panel for configuring settings and controls."""
    
    def __init__(self, camera_manager: CameraManager):
        """
        Initialize the settings panel.
        
        Args:
            camera_manager: Camera manager for accessing camera list
        """
        super().__init__()
        
        self.camera_manager = camera_manager
        self._analysis_active = False
        
        # Initialize UI
        self.init_ui()
        
        # Populate camera list
        self.refresh_camera_list()
    
    def init_ui(self):
        """Initialize the UI components."""
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Create a tab widget
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # Create tabs
        self.camera_tab = QWidget()
        self.analysis_tab = QWidget()
        self.angles_tab = QWidget()
        self.guidance_tab = QWidget()
        
        self.tabs.addTab(self.camera_tab, "Camera")
        self.tabs.addTab(self.analysis_tab, "Analysis")
        self.tabs.addTab(self.angles_tab, "Angles")
        self.tabs.addTab(self.guidance_tab, "Guidance")
        
        # Setup each tab
        self.setup_camera_tab()
        self.setup_analysis_tab()
        self.setup_angles_tab()
        self.setup_guidance_tab()
        
        # Set fixed width for the panel
        self.setMinimumWidth(300)
        self.setMaximumWidth(400)
        self.advanced_tab = QWidget()
        self.tabs.addTab(self.advanced_tab, "Advanced")
        self.setup_advanced_tab()
    
    def setup_camera_tab(self):
        """Setup the camera settings tab."""
        layout = QVBoxLayout(self.camera_tab)
        
        # Camera selection
        camera_group = QGroupBox("Camera Selection")
        camera_layout = QVBoxLayout()
        
        # Camera dropdown and refresh button
        camera_dropdown_layout = QHBoxLayout()
        
        self.camera_label = QLabel("Camera:")
        self.camera_combo = QComboBox()
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_camera_list)
        
        camera_dropdown_layout.addWidget(self.camera_label)
        camera_dropdown_layout.addWidget(self.camera_combo, 1)
        camera_dropdown_layout.addWidget(self.refresh_btn)
        
        camera_layout.addLayout(camera_dropdown_layout)
        
        # Mirror mode toggle
        self.mirror_toggle_btn = QPushButton("Toggle Mirror Mode")
        self.mirror_toggle_btn.setCheckable(True)
        self.mirror_toggle_btn.setChecked(True)
        camera_layout.addWidget(self.mirror_toggle_btn)
        
        camera_group.setLayout(camera_layout)
        layout.addWidget(camera_group)
        
        # Camera controls
        controls_group = QGroupBox("Camera Controls")
        controls_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Camera")
        self.stop_btn = QPushButton("Stop Camera")
        self.stop_btn.setEnabled(False)
        
        controls_layout.addWidget(self.start_btn)
        controls_layout.addWidget(self.stop_btn)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        # Resolution settings
        resolution_group = QGroupBox("Resolution")
        resolution_layout = QFormLayout()
        
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            "640x480", "800x600", "1280x720", "1920x1080"
        ])
        self.resolution_combo.setCurrentIndex(2)  # Default to 1280x720
        
        resolution_layout.addRow("Resolution:", self.resolution_combo)
        
        resolution_group.setLayout(resolution_layout)
        layout.addWidget(resolution_group)
        
        # Add stretch to push everything to the top
        layout.addStretch()
    
    def setup_analysis_tab(self):
        """Setup the analysis settings tab."""
        layout = QVBoxLayout(self.analysis_tab)
        
        # Analysis controls
        analysis_group = QGroupBox("Analysis Controls")
        analysis_layout = QHBoxLayout()
        
        self.start_analysis_btn = QPushButton("Start Analysis")
        self.stop_analysis_btn = QPushButton("Stop Analysis")
        self.stop_analysis_btn.setEnabled(False)
        
        analysis_layout.addWidget(self.start_analysis_btn)
        analysis_layout.addWidget(self.stop_analysis_btn)
        
        analysis_group.setLayout(analysis_layout)
        layout.addWidget(analysis_group)
        
        # Detection settings
        detection_group = QGroupBox("Detection Settings")
        detection_layout = QFormLayout()
        
        self.detection_conf_slider = QSlider(Qt.Horizontal)
        self.detection_conf_slider.setMinimum(1)
        self.detection_conf_slider.setMaximum(10)
        self.detection_conf_slider.setValue(5)  # Default 0.5
        self.detection_conf_label = QLabel("0.5")
        self.detection_conf_slider.valueChanged.connect(
            lambda v: self.detection_conf_label.setText(f"{v/10:.1f}")
        )
        
        detection_conf_layout = QHBoxLayout()
        detection_conf_layout.addWidget(self.detection_conf_slider)
        detection_conf_layout.addWidget(self.detection_conf_label)
        
        self.tracking_conf_slider = QSlider(Qt.Horizontal)
        self.tracking_conf_slider.setMinimum(1)
        self.tracking_conf_slider.setMaximum(10)
        self.tracking_conf_slider.setValue(5)  # Default 0.5
        self.tracking_conf_label = QLabel("0.5")
        self.tracking_conf_slider.valueChanged.connect(
            lambda v: self.tracking_conf_label.setText(f"{v/10:.1f}")
        )
        
        tracking_conf_layout = QHBoxLayout()
        tracking_conf_layout.addWidget(self.tracking_conf_slider)
        tracking_conf_layout.addWidget(self.tracking_conf_label)
        
        self.model_complexity_combo = QComboBox()
        self.model_complexity_combo.addItems(["0 (Fastest)", "1 (Medium)", "2 (Most Accurate)"])
        self.model_complexity_combo.setCurrentIndex(2)  # Default to most accurate
        
        detection_layout.addRow("Detection Confidence:", detection_conf_layout)
        detection_layout.addRow("Tracking Confidence:", tracking_conf_layout)
        detection_layout.addRow("Model Complexity:", self.model_complexity_combo)
        
        detection_group.setLayout(detection_layout)
        layout.addWidget(detection_group)
        
        # Visualization options
        vis_group = QGroupBox("Visualization Options")
        vis_layout = QVBoxLayout()
        
        self.show_skeleton_check = QCheckBox("Show Skeleton")
        self.show_skeleton_check.setChecked(True)
        
        self.show_landmarks_check = QCheckBox("Show Landmarks")
        self.show_landmarks_check.setChecked(True)
        
        self.show_angles_check = QCheckBox("Show Angles")
        self.show_angles_check.setChecked(True)
        
        self.show_guidance_check = QCheckBox("Show Guidance")
        self.show_guidance_check.setChecked(True)
        
        vis_layout.addWidget(self.show_skeleton_check)
        vis_layout.addWidget(self.show_landmarks_check)
        vis_layout.addWidget(self.show_angles_check)
        vis_layout.addWidget(self.show_guidance_check)
        
        vis_group.setLayout(vis_layout)
        layout.addWidget(vis_group)
        
        # Add stretch
        layout.addStretch()
    
    def setup_angles_tab(self):
        """Setup the angles settings tab."""
        # Create a scroll area for the angles tab
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        angles_widget = QWidget()
        layout = QVBoxLayout(angles_widget)
        
        # Angle ranges settings
        for angle_name, (min_val, max_val) in IDEAL_ANGLES.items():
            angle_group = QGroupBox(angle_name.replace('_', ' ').title())
            angle_layout = QFormLayout()
            
            # Min value
            min_spinner = QSpinBox()
            min_spinner.setMinimum(0)
            min_spinner.setMaximum(180)
            min_spinner.setValue(min_val)
            angle_layout.addRow("Min:", min_spinner)
            
            # Max value
            max_spinner = QSpinBox()
            max_spinner.setMinimum(0)
            max_spinner.setMaximum(180)
            max_spinner.setValue(max_val)
            angle_layout.addRow("Max:", max_spinner)
            
            # Enable checkbox
            enable_check = QCheckBox("Enable")
            enable_check.setChecked(True)
            angle_layout.addRow("", enable_check)
            
            angle_group.setLayout(angle_layout)
            layout.addWidget(angle_group)
        
        # Reset button
        reset_btn = QPushButton("Reset to Defaults")
        layout.addWidget(reset_btn)
        
        # Add stretch
        layout.addStretch()
        
        scroll_area.setWidget(angles_widget)
        
        # Add scroll area to tab layout
        tab_layout = QVBoxLayout(self.angles_tab)
        tab_layout.addWidget(scroll_area)
    
    def setup_guidance_tab(self):
        """Setup the guidance settings tab."""
        layout = QVBoxLayout(self.guidance_tab)
        
        # Guidance mode
        guidance_mode_group = QGroupBox("Guidance Mode")
        guidance_mode_layout = QVBoxLayout()
        
        self.real_time_radio = QCheckBox("Real-time Guidance")
        self.real_time_radio.setChecked(True)
        
        self.summary_radio = QCheckBox("Summary After Analysis")
        self.summary_radio.setChecked(False)
        
        self.save_report_check = QCheckBox("Save Guidance Report")
        self.save_report_check.setChecked(False)
        
        guidance_mode_layout.addWidget(self.real_time_radio)
        guidance_mode_layout.addWidget(self.summary_radio)
        guidance_mode_layout.addWidget(self.save_report_check)
        
        guidance_mode_group.setLayout(guidance_mode_layout)
        layout.addWidget(guidance_mode_group)
        
        # Visual cues
        visual_cues_group = QGroupBox("Visual Cues")
        visual_cues_layout = QVBoxLayout()
        
        self.show_arrows_check = QCheckBox("Show Directional Arrows")
        self.show_arrows_check.setChecked(True)
        
        self.show_color_coding_check = QCheckBox("Show Color Coding")
        self.show_color_coding_check.setChecked(True)
        
        self.show_text_cues_check = QCheckBox("Show Text Cues")
        self.show_text_cues_check.setChecked(True)
        
        self.show_target_pose_check = QCheckBox("Show Target Pose Overlay")
        self.show_target_pose_check.setChecked(False)
        
        visual_cues_layout.addWidget(self.show_arrows_check)
        visual_cues_layout.addWidget(self.show_color_coding_check)
        visual_cues_layout.addWidget(self.show_text_cues_check)
        visual_cues_layout.addWidget(self.show_target_pose_check)
        
        visual_cues_group.setLayout(visual_cues_layout)
        layout.addWidget(visual_cues_group)
        
        # Sensitivity
        sensitivity_group = QGroupBox("Adjustment Sensitivity")
        sensitivity_layout = QFormLayout()
        
        self.sensitivity_slider = QSlider(Qt.Horizontal)
        self.sensitivity_slider.setMinimum(1)
        self.sensitivity_slider.setMaximum(10)
        self.sensitivity_slider.setValue(5)
        
        self.tolerance_slider = QSlider(Qt.Horizontal)
        self.tolerance_slider.setMinimum(1)
        self.tolerance_slider.setMaximum(10)
        self.tolerance_slider.setValue(3)
        
        sensitivity_layout.addRow("Guidance Sensitivity:", self.sensitivity_slider)
        sensitivity_layout.addRow("Adjustment Tolerance:", self.tolerance_slider)
        
        sensitivity_group.setLayout(sensitivity_layout)
        layout.addWidget(sensitivity_group)
        
        # Add stretch
        layout.addStretch()
    
    def refresh_camera_list(self):
        """Refresh the list of available cameras."""
        self.camera_combo.clear()
        
        available_cameras = self.camera_manager.available_cameras
        if not available_cameras:
            self.camera_combo.addItem("No cameras found")
            self.start_btn.setEnabled(False)
            return
        
        for cam_id, cam_name in available_cameras.items():
            self.camera_combo.addItem(f"{cam_name}", cam_id)
        
        self.start_btn.setEnabled(True)
    
    def get_selected_camera_id(self) -> int:
        """Get the ID of the currently selected camera."""
        if self.camera_combo.count() == 0:
            return 0
        
        return self.camera_combo.currentData()
    
    def update_button_states(self, camera_running: bool):
        """
        Update button states based on camera state.
        
        Args:
            camera_running: Whether the camera is currently running
        """
        self.start_btn.setEnabled(not camera_running)
        self.stop_btn.setEnabled(camera_running)
        self.start_analysis_btn.setEnabled(camera_running and not self._analysis_active)
        self.stop_analysis_btn.setEnabled(camera_running and self._analysis_active)
    
    def update_mirror_button(self, mirror_enabled: bool):
        """
        Update the mirror button state.
        
        Args:
            mirror_enabled: Whether mirror mode is enabled
        """
        self.mirror_toggle_btn.setChecked(mirror_enabled)
    
    def is_analysis_active(self) -> bool:
        """Check if analysis is active."""
        return self._analysis_active
    
    def set_analysis_active(self, active: bool):
        """
        Set the analysis active state.
        
        Args:
            active: Whether analysis should be active
        """
        self._analysis_active = active
        self.start_analysis_btn.setEnabled(not active)
        self.stop_analysis_btn.setEnabled(active)

    def setup_advanced_tab(self):
        """Setup the advanced measurements tab."""
        layout = QVBoxLayout(self.advanced_tab)
        
        # KOPS section
        kops_group = QGroupBox("Knee Over Pedal Spindle (KOPS)")
        kops_layout = QVBoxLayout()
        
        self.enable_kops_check = QCheckBox("Enable KOPS Analysis")
        self.enable_kops_check.setChecked(True)
        
        self.kops_tolerance_spin = QDoubleSpinBox()
        self.kops_tolerance_spin.setRange(0.1, 5.0)
        self.kops_tolerance_spin.setValue(1.0)
        self.kops_tolerance_spin.setSuffix(" cm")
        
        kops_tolerance_layout = QHBoxLayout()
        kops_tolerance_layout.addWidget(QLabel("Tolerance:"))
        kops_tolerance_layout.addWidget(self.kops_tolerance_spin)
        
        kops_layout.addWidget(self.enable_kops_check)
        kops_layout.addLayout(kops_tolerance_layout)
        kops_group.setLayout(kops_layout)
        layout.addWidget(kops_group)
        
        # Saddle setback section
        saddle_group = QGroupBox("Saddle Setback")
        saddle_layout = QVBoxLayout()
        
        self.enable_setback_check = QCheckBox("Enable Setback Analysis")
        self.enable_setback_check.setChecked(True)
        
        saddle_layout.addWidget(self.enable_setback_check)
        saddle_group.setLayout(saddle_layout)
        layout.addWidget(saddle_group)
        
        # Cleat positioning section
        cleat_group = QGroupBox("Cleat Positioning")
        cleat_layout = QVBoxLayout()
        
        self.enable_cleat_check = QCheckBox("Enable Cleat Analysis")
        self.enable_cleat_check.setChecked(True)
        
        self.cleat_position_spin = QSpinBox()
        self.cleat_position_spin.setRange(50, 80)
        self.cleat_position_spin.setValue(65)
        self.cleat_position_spin.setSuffix("%")
        
        cleat_position_layout = QHBoxLayout()
        cleat_position_layout.addWidget(QLabel("Ideal Position:"))
        cleat_position_layout.addWidget(self.cleat_position_spin)
        
        cleat_layout.addWidget(self.enable_cleat_check)
        cleat_layout.addLayout(cleat_position_layout)
        cleat_group.setLayout(cleat_layout)
        layout.addWidget(cleat_group)
        
        # Stack and reach section
        geometry_group = QGroupBox("Stack and Reach")
        geometry_layout = QVBoxLayout()
        
        self.enable_geometry_check = QCheckBox("Enable Stack/Reach Analysis")
        self.enable_geometry_check.setChecked(True)
        
        geometry_layout.addWidget(self.enable_geometry_check)
        geometry_group.setLayout(geometry_layout)
        layout.addWidget(geometry_group)
        
        # Add stretch to push everything to the top
        layout.addStretch()
