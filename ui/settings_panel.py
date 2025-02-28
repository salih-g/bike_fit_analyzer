# bike_fit_analyzer/ui/settings_panel.py
"""
Settings panel for the Bike Fit Analyzer.
Provides controls for camera, analysis, and visualization settings.
"""
from typing import Optional, Dict, List, Any, Tuple
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSlider, QSpinBox, QDoubleSpinBox, QCheckBox,
    QGroupBox, QFormLayout, QTabWidget, QScrollArea, QRadioButton,
    QButtonGroup
)
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal

from bike_fit_analyzer.utils.camera import CameraManager
from bike_fit_analyzer.config.settings import IDEAL_ANGLES, VIEW_MODES, BIKE_TYPES
from bike_fit_analyzer.config.settings_manager import settings_manager


class SettingsPanel(QWidget):
    """Panel for configuring settings and controls."""
    
    # Signal emitted when settings change that require camera restart
    camera_settings_changed = pyqtSignal()
    
    def __init__(self, camera_manager: CameraManager):
        """
        Initialize the settings panel.
        
        Args:
            camera_manager: Camera manager for accessing camera list
        """
        super().__init__()
        
        self.camera_manager = camera_manager
        self._analysis_active = False
        
        # Store references to angle spinners for updates
        self.angle_spinners = {}
        self.angle_enable_checks = {}
        
        # Initialize UI
        self.init_ui()
        
        # Populate camera list
        self.refresh_camera_list()
        
        # Connect signals
        self.connect_signals()
        
        # Register as observer for settings changes
        settings_manager.add_observer(self._on_settings_changed)
    
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
        self.advanced_tab = QWidget()
        
        self.tabs.addTab(self.camera_tab, "Camera")
        self.tabs.addTab(self.analysis_tab, "Analysis")
        self.tabs.addTab(self.angles_tab, "Angles")
        self.tabs.addTab(self.guidance_tab, "Guidance")
        self.tabs.addTab(self.advanced_tab, "Advanced")
        
        # Setup each tab
        self.setup_camera_tab()
        self.setup_analysis_tab()
        self.setup_angles_tab()
        self.setup_guidance_tab()
        self.setup_advanced_tab()
        
        # Set fixed width for the panel
        self.setMinimumWidth(300)
        self.setMaximumWidth(400)
    
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
        self.mirror_toggle_btn.setChecked(settings_manager.get("mirror_enabled", True))
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
        
        # Set default resolution based on settings
        default_width = settings_manager.get("camera_width", 1280)
        default_height = settings_manager.get("camera_height", 720)
        default_resolution = f"{default_width}x{default_height}"
        
        # Find index of default resolution in combo box
        index = self.resolution_combo.findText(default_resolution)
        if index >= 0:
            self.resolution_combo.setCurrentIndex(index)
        else:
            # Default to 1280x720 if not found
            index = self.resolution_combo.findText("1280x720")
            if index >= 0:
                self.resolution_combo.setCurrentIndex(index)
        
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
        
        # Get current settings
        detection_conf = settings_manager.get("min_detection_confidence", 0.5)
        tracking_conf = settings_manager.get("min_tracking_confidence", 0.5)
        model_complexity = settings_manager.get("pose_model_complexity", 2)
        
        # Detection confidence slider
        self.detection_conf_slider = QSlider(Qt.Horizontal)
        self.detection_conf_slider.setMinimum(1)
        self.detection_conf_slider.setMaximum(10)
        self.detection_conf_slider.setValue(int(detection_conf * 10))
        self.detection_conf_label = QLabel(f"{detection_conf:.1f}")
        
        detection_conf_layout = QHBoxLayout()
        detection_conf_layout.addWidget(self.detection_conf_slider)
        detection_conf_layout.addWidget(self.detection_conf_label)
        
        # Tracking confidence slider
        self.tracking_conf_slider = QSlider(Qt.Horizontal)
        self.tracking_conf_slider.setMinimum(1)
        self.tracking_conf_slider.setMaximum(10)
        self.tracking_conf_slider.setValue(int(tracking_conf * 10))
        self.tracking_conf_label = QLabel(f"{tracking_conf:.1f}")
        
        tracking_conf_layout = QHBoxLayout()
        tracking_conf_layout.addWidget(self.tracking_conf_slider)
        tracking_conf_layout.addWidget(self.tracking_conf_label)
        
        # Model complexity combo
        self.model_complexity_combo = QComboBox()
        self.model_complexity_combo.addItems(["0 (Fastest)", "1 (Medium)", "2 (Most Accurate)"])
        self.model_complexity_combo.setCurrentIndex(model_complexity)
        
        detection_layout.addRow("Detection Confidence:", detection_conf_layout)
        detection_layout.addRow("Tracking Confidence:", tracking_conf_layout)
        detection_layout.addRow("Model Complexity:", self.model_complexity_combo)
        
        detection_group.setLayout(detection_layout)
        layout.addWidget(detection_group)
        
        # Visualization options
        vis_group = QGroupBox("Visualization Options")
        vis_layout = QVBoxLayout()
        
        # Get current settings
        show_skeleton = settings_manager.get("show_skeleton", True)
        show_landmarks = settings_manager.get("show_landmarks", True)
        show_angles = settings_manager.get("show_angles", True)
        show_guidance = settings_manager.get("show_guidance", True)
        
        self.show_skeleton_check = QCheckBox("Show Skeleton")
        self.show_skeleton_check.setChecked(show_skeleton)
        
        self.show_landmarks_check = QCheckBox("Show Landmarks")
        self.show_landmarks_check.setChecked(show_landmarks)
        
        self.show_angles_check = QCheckBox("Show Angles")
        self.show_angles_check.setChecked(show_angles)
        
        self.show_guidance_check = QCheckBox("Show Guidance")
        self.show_guidance_check.setChecked(show_guidance)
        
        vis_layout.addWidget(self.show_skeleton_check)
        vis_layout.addWidget(self.show_landmarks_check)
        vis_layout.addWidget(self.show_angles_check)
        vis_layout.addWidget(self.show_guidance_check)
        
        # View mode selection
        view_mode_layout = QFormLayout()
        self.view_mode_combo = QComboBox()
        self.view_mode_combo.addItems(VIEW_MODES)
        
        # Set current view mode from settings
        current_view_mode = settings_manager.get("view_mode", "Normal View")
        index = self.view_mode_combo.findText(current_view_mode)
        if index >= 0:
            self.view_mode_combo.setCurrentIndex(index)
        
        view_mode_layout.addRow("View Mode:", self.view_mode_combo)
        vis_layout.addLayout(view_mode_layout)
        
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
        
        # Get current angle settings
        current_angles = settings_manager.get("angles", IDEAL_ANGLES.copy())
        angles_enabled = settings_manager.get("angles_enabled", {k: True for k in IDEAL_ANGLES})
        
        # Bike type selection
        bike_type_group = QGroupBox("Bike Type Presets")
        bike_type_layout = QVBoxLayout()
        
        self.bike_type_combo = QComboBox()
        for bike_id, bike_data in BIKE_TYPES.items():
            self.bike_type_combo.addItem(bike_data['name'], bike_id)
        
        bike_type_layout.addWidget(QLabel("Select Bike Type:"))
        bike_type_layout.addWidget(self.bike_type_combo)
        
        self.apply_preset_btn = QPushButton("Apply Preset Angles")
        bike_type_layout.addWidget(self.apply_preset_btn)
        
        bike_type_group.setLayout(bike_type_layout)
        layout.addWidget(bike_type_group)
        
        # Angle ranges settings
        for angle_name, (min_val, max_val) in IDEAL_ANGLES.items():
            # Get current values from settings
            if angle_name in current_angles:
                min_val, max_val = current_angles[angle_name]
            
            enabled = angles_enabled.get(angle_name, True)
            
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
            enable_check.setChecked(enabled)
            angle_layout.addRow("", enable_check)
            
            # Store references to spinners and checkboxes for later updates
            self.angle_spinners[angle_name] = (min_spinner, max_spinner)
            self.angle_enable_checks[angle_name] = enable_check
            
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
        
        # Get current guidance settings
        real_time_guidance = settings_manager.get("real_time_guidance", True)
        summary_after_analysis = settings_manager.get("summary_after_analysis", False)
        save_report = settings_manager.get("save_report", False)
        show_arrows = settings_manager.get("show_arrows", True)
        show_color_coding = settings_manager.get("show_color_coding", True)
        show_text_cues = settings_manager.get("show_text_cues", True)
        show_target_pose = settings_manager.get("show_target_pose", False)
        guidance_sensitivity = settings_manager.get("guidance_sensitivity", 5)
        adjustment_tolerance = settings_manager.get("adjustment_tolerance", 3)
        
        # Guidance mode
        guidance_mode_group = QGroupBox("Guidance Mode")
        guidance_mode_layout = QVBoxLayout()
        
        self.real_time_check = QCheckBox("Real-time Guidance")
        self.real_time_check.setChecked(real_time_guidance)
        
        self.summary_check = QCheckBox("Summary After Analysis")
        self.summary_check.setChecked(summary_after_analysis)
        
        self.save_report_check = QCheckBox("Save Guidance Report")
        self.save_report_check.setChecked(save_report)
        
        guidance_mode_layout.addWidget(self.real_time_check)
        guidance_mode_layout.addWidget(self.summary_check)
        guidance_mode_layout.addWidget(self.save_report_check)
        
        guidance_mode_group.setLayout(guidance_mode_layout)
        layout.addWidget(guidance_mode_group)
        
        # Visual cues
        visual_cues_group = QGroupBox("Visual Cues")
        visual_cues_layout = QVBoxLayout()
        
        self.show_arrows_check = QCheckBox("Show Directional Arrows")
        self.show_arrows_check.setChecked(show_arrows)
        
        self.show_color_coding_check = QCheckBox("Show Color Coding")
        self.show_color_coding_check.setChecked(show_color_coding)
        
        self.show_text_cues_check = QCheckBox("Show Text Cues")
        self.show_text_cues_check.setChecked(show_text_cues)
        
        self.show_target_pose_check = QCheckBox("Show Target Pose Overlay")
        self.show_target_pose_check.setChecked(show_target_pose)
        
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
        self.sensitivity_slider.setValue(guidance_sensitivity)
        self.sensitivity_label = QLabel(f"{guidance_sensitivity}")
        
        sensitivity_slider_layout = QHBoxLayout()
        sensitivity_slider_layout.addWidget(self.sensitivity_slider)
        sensitivity_slider_layout.addWidget(self.sensitivity_label)
        
        self.tolerance_slider = QSlider(Qt.Horizontal)
        self.tolerance_slider.setMinimum(1)
        self.tolerance_slider.setMaximum(10)
        self.tolerance_slider.setValue(adjustment_tolerance)
        self.tolerance_label = QLabel(f"{adjustment_tolerance}")
        
        tolerance_slider_layout = QHBoxLayout()
        tolerance_slider_layout.addWidget(self.tolerance_slider)
        tolerance_slider_layout.addWidget(self.tolerance_label)
        
        sensitivity_layout.addRow("Guidance Sensitivity:", sensitivity_slider_layout)
        sensitivity_layout.addRow("Adjustment Tolerance:", tolerance_slider_layout)
        
        sensitivity_group.setLayout(sensitivity_layout)
        layout.addWidget(sensitivity_group)
        
        # Add stretch
        layout.addStretch()
    
    def setup_advanced_tab(self):
        """Setup the advanced measurements tab."""
        layout = QVBoxLayout(self.advanced_tab)
        
        # Get current advanced settings
        enable_kops = settings_manager.get("enable_kops", True)
        kops_tolerance = settings_manager.get("kops_tolerance", 1.0)
        enable_setback = settings_manager.get("enable_setback", True)
        enable_cleat = settings_manager.get("enable_cleat", True)
        cleat_position = settings_manager.get("cleat_position", 65)
        enable_geometry = settings_manager.get("enable_geometry", True)
        
        # KOPS section
        kops_group = QGroupBox("Knee Over Pedal Spindle (KOPS)")
        kops_layout = QVBoxLayout()
        
        self.enable_kops_check = QCheckBox("Enable KOPS Analysis")
        self.enable_kops_check.setChecked(enable_kops)
        
        self.kops_tolerance_spin = QDoubleSpinBox()
        self.kops_tolerance_spin.setRange(0.1, 5.0)
        self.kops_tolerance_spin.setValue(kops_tolerance)
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
        self.enable_setback_check.setChecked(enable_setback)
        
        saddle_layout.addWidget(self.enable_setback_check)
        saddle_group.setLayout(saddle_layout)
        layout.addWidget(saddle_group)
        
        # Cleat positioning section
        cleat_group = QGroupBox("Cleat Positioning")
        cleat_layout = QVBoxLayout()
        
        self.enable_cleat_check = QCheckBox("Enable Cleat Analysis")
        self.enable_cleat_check.setChecked(enable_cleat)
        
        self.cleat_position_spin = QSpinBox()
        self.cleat_position_spin.setRange(50, 80)
        self.cleat_position_spin.setValue(cleat_position)
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
        self.enable_geometry_check.setChecked(enable_geometry)
        
        geometry_layout.addWidget(self.enable_geometry_check)
        geometry_group.setLayout(geometry_layout)
        layout.addWidget(geometry_group)
        
        # Add stretch to push everything to the top
        layout.addStretch()
    
    def connect_signals(self):
        """Connect signals from UI elements to settings manager."""
        # Camera tab signals
        self.camera_combo.currentIndexChanged.connect(self._on_camera_changed)
        self.mirror_toggle_btn.clicked.connect(self._on_mirror_toggled)
        self.resolution_combo.currentIndexChanged.connect(self._on_resolution_changed)
        
        # Analysis tab signals
        self.detection_conf_slider.valueChanged.connect(self._on_detection_conf_changed)
        self.tracking_conf_slider.valueChanged.connect(self._on_tracking_conf_changed)
        self.model_complexity_combo.currentIndexChanged.connect(self._on_model_complexity_changed)
        self.show_skeleton_check.stateChanged.connect(self._on_show_skeleton_changed)
        self.show_landmarks_check.stateChanged.connect(self._on_show_landmarks_changed)
        self.show_angles_check.stateChanged.connect(self._on_show_angles_changed)
        self.show_guidance_check.stateChanged.connect(self._on_show_guidance_changed)
        self.view_mode_combo.currentIndexChanged.connect(self._on_view_mode_changed)
        
        # Angles tab signals
        self.apply_preset_btn.clicked.connect(self._on_apply_preset)
        
        # Connect each angle spinner and checkbox
        for angle_name, (min_spinner, max_spinner) in self.angle_spinners.items():
            min_spinner.valueChanged.connect(
                lambda value, angle=angle_name: self._on_angle_min_changed(angle, value))
            max_spinner.valueChanged.connect(
                lambda value, angle=angle_name: self._on_angle_max_changed(angle, value))
        
        for angle_name, enable_check in self.angle_enable_checks.items():
            enable_check.stateChanged.connect(
                lambda state, angle=angle_name: self._on_angle_enabled_changed(angle, state))
        
        # Guidance tab signals
        self.real_time_check.stateChanged.connect(self._on_real_time_guidance_changed)
        self.summary_check.stateChanged.connect(self._on_summary_after_analysis_changed)
        self.save_report_check.stateChanged.connect(self._on_save_report_changed)
        self.show_arrows_check.stateChanged.connect(self._on_show_arrows_changed)
        self.show_color_coding_check.stateChanged.connect(self._on_show_color_coding_changed)
        self.show_text_cues_check.stateChanged.connect(self._on_show_text_cues_changed)
        self.show_target_pose_check.stateChanged.connect(self._on_show_target_pose_changed)
        self.sensitivity_slider.valueChanged.connect(self._on_sensitivity_changed)
        self.tolerance_slider.valueChanged.connect(self._on_tolerance_changed)
        
        # Advanced tab signals
        self.enable_kops_check.stateChanged.connect(self._on_enable_kops_changed)
        self.kops_tolerance_spin.valueChanged.connect(self._on_kops_tolerance_changed)
        self.enable_setback_check.stateChanged.connect(self._on_enable_setback_changed)
        self.enable_cleat_check.stateChanged.connect(self._on_enable_cleat_changed)
        self.cleat_position_spin.valueChanged.connect(self._on_cleat_position_changed)
        self.enable_geometry_check.stateChanged.connect(self._on_enable_geometry_changed)
    
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
        
        # Select the camera ID from settings
        camera_id = settings_manager.get("camera_id", 0)
        for i in range(self.camera_combo.count()):
            if self.camera_combo.itemData(i) == camera_id:
                self.camera_combo.setCurrentIndex(i)
                break
    
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
    
    def _on_settings_changed(self, key: str, value: Any):
        """
        Handle settings changes from other parts of the application.
        
        Args:
            key: Setting key
            value: New value
        """
        # Update UI elements based on settings changes
        if key == "mirror_enabled":
            self.mirror_toggle_btn.setChecked(value)
        elif key == "show_skeleton":
            self.show_skeleton_check.setChecked(value)
        elif key == "show_landmarks":
            self.show_landmarks_check.setChecked(value)
        elif key == "show_angles":
            self.show_angles_check.setChecked(value)
        elif key == "show_guidance":
            self.show_guidance_check.setChecked(value)
        elif key == "view_mode":
            index = self.view_mode_combo.findText(value)
            if index >= 0:
                self.view_mode_combo.setCurrentIndex(index)
        elif key == "min_detection_confidence":
            self.detection_conf_slider.setValue(int(value * 10))
            self.detection_conf_label.setText(f"{value:.1f}")
        elif key == "min_tracking_confidence":
            self.tracking_conf_slider.setValue(int(value * 10))
            self.tracking_conf_label.setText(f"{value:.1f}")
        elif key == "pose_model_complexity":
            self.model_complexity_combo.setCurrentIndex(value)
        elif key == "real_time_guidance":
            self.real_time_check.setChecked(value)
        elif key == "summary_after_analysis":
            self.summary_check.setChecked(value)
        elif key == "save_report":
            self.save_report_check.setChecked(value)
        elif key == "show_arrows":
            self.show_arrows_check.setChecked(value)
        elif key == "show_color_coding":
            self.show_color_coding_check.setChecked(value)
        elif key == "show_text_cues":
            self.show_text_cues_check.setChecked(value)
        elif key == "show_target_pose":
            self.show_target_pose_check.setChecked(value)
        elif key == "guidance_sensitivity":
            self.sensitivity_slider.setValue(value)
            self.sensitivity_label.setText(str(value))
        elif key == "adjustment_tolerance":
            self.tolerance_slider.setValue(value)
            self.tolerance_label.setText(str(value))
        elif key == "angles":
            self._update_angle_spinners(value)
        elif key == "angles_enabled":
            self._update_angle_checkboxes(value)
        elif key == "enable_kops":
            self.enable_kops_check.setChecked(value)
        elif key == "kops_tolerance":
            self.kops_tolerance_spin.setValue(value)
        elif key == "enable_setback":
            self.enable_setback_check.setChecked(value)
        elif key == "enable_cleat":
            self.enable_cleat_check.setChecked(value)
        elif key == "cleat_position":
            self.cleat_position_spin.setValue(value)
        elif key == "enable_geometry":
            self.enable_geometry_check.setChecked(value)
    
    def _update_angle_spinners(self, angles: Dict[str, Tuple[int, int]]):
        """
        Update angle spinners based on new angles dictionary.
        
        Args:
            angles: Dictionary of angle ranges
        """
        for angle_name, (min_val, max_val) in angles.items():
            if angle_name in self.angle_spinners:
                min_spinner, max_spinner = self.angle_spinners[angle_name]
                # Block signals to prevent recursion
                min_spinner.blockSignals(True)
                max_spinner.blockSignals(True)
                
                min_spinner.setValue(min_val)
                max_spinner.setValue(max_val)
                
                min_spinner.blockSignals(False)
                max_spinner.blockSignals(False)
    
    def _update_angle_checkboxes(self, angles_enabled: Dict[str, bool]):
        """
        Update angle checkboxes based on new enabled states.
        
        Args:
            angles_enabled: Dictionary of angle enabled states
        """
        for angle_name, enabled in angles_enabled.items():
            if angle_name in self.angle_enable_checks:
                check = self.angle_enable_checks[angle_name]
                # Block signals to prevent recursion
                check.blockSignals(True)
                check.setChecked(enabled)
                check.blockSignals(False)
    
    # Handler methods for camera tab
    def _on_camera_changed(self, index):
        """Handle camera selection change."""
        if index < 0:
            return
        
        camera_id = self.camera_combo.currentData()
        settings_manager.set("camera_id", camera_id)
    
    def _on_mirror_toggled(self, checked):
        """Handle mirror mode toggle."""
        settings_manager.set("mirror_enabled", checked)
    
    def _on_resolution_changed(self, index):
        """Handle resolution change."""
        resolution_text = self.resolution_combo.currentText()
        try:
            width, height = map(int, resolution_text.split('x'))
            settings_manager.set("camera_width", width)
            settings_manager.set("camera_height", height)
        except ValueError:
            # Invalid resolution format
            pass
    
    # Handler methods for analysis tab
    def _on_detection_conf_changed(self, value):
        """Handle detection confidence change."""
        conf = value / 10.0  # Convert from 1-10 to 0.1-1.0
        self.detection_conf_label.setText(f"{conf:.1f}")
        settings_manager.set("min_detection_confidence", conf)
    
    def _on_tracking_conf_changed(self, value):
        """Handle tracking confidence change."""
        conf = value / 10.0  # Convert from 1-10 to 0.1-1.0
        self.tracking_conf_label.setText(f"{conf:.1f}")
        settings_manager.set("min_tracking_confidence", conf)
    
    def _on_model_complexity_changed(self, index):
        """Handle model complexity change."""
        settings_manager.set("pose_model_complexity", index)
    
    def _on_show_skeleton_changed(self, state):
        """Handle show skeleton toggle."""
        settings_manager.set("show_skeleton", state == Qt.Checked)
    
    def _on_show_landmarks_changed(self, state):
        """Handle show landmarks toggle."""
        settings_manager.set("show_landmarks", state == Qt.Checked)
    
    def _on_show_angles_changed(self, state):
        """Handle show angles toggle."""
        settings_manager.set("show_angles", state == Qt.Checked)
    
    def _on_show_guidance_changed(self, state):
        """Handle show guidance toggle."""
        settings_manager.set("show_guidance", state == Qt.Checked)
    
    def _on_view_mode_changed(self, index):
        """Handle view mode change."""
        view_mode = self.view_mode_combo.currentText()
        settings_manager.set("view_mode", view_mode)
    
    # Handler methods for angles tab
    def _on_apply_preset(self):
        """Apply angle presets based on selected bike type."""
        bike_id = self.bike_type_combo.currentData()
        
        if bike_id in BIKE_TYPES:
            bike_data = BIKE_TYPES[bike_id]
            if 'default_angles' in bike_data:
                # Update settings
                settings_manager.set("angles", bike_data['default_angles'].copy())
                
                # Update UI
                self._update_angle_spinners(bike_data['default_angles'])
    
    def _on_angle_min_changed(self, angle_name, value):
        """
        Handle angle minimum value change.
        
        Args:
            angle_name: Name of the angle
            value: New minimum value
        """
        current_angles = settings_manager.get("angles", IDEAL_ANGLES.copy())
        current_min, current_max = current_angles[angle_name]
        
        # Ensure min <= max
        value = min(value, current_max)
        
        # Update settings
        current_angles[angle_name] = (value, current_max)
        settings_manager.set("angles", current_angles)
    
    def _on_angle_max_changed(self, angle_name, value):
        """
        Handle angle maximum value change.
        
        Args:
            angle_name: Name of the angle
            value: New maximum value
        """
        current_angles = settings_manager.get("angles", IDEAL_ANGLES.copy())
        current_min, current_max = current_angles[angle_name]
        
        # Ensure max >= min
        value = max(value, current_min)
        
        # Update settings
        current_angles[angle_name] = (current_min, value)
        settings_manager.set("angles", current_angles)
    
    def _on_angle_enabled_changed(self, angle_name, state):
        """
        Handle angle enabled state change.
        
        Args:
            angle_name: Name of the angle
            state: New checkbox state
        """
        enabled = (state == Qt.Checked)
        angles_enabled = settings_manager.get("angles_enabled", {k: True for k in IDEAL_ANGLES})
        angles_enabled[angle_name] = enabled
        settings_manager.set("angles_enabled", angles_enabled)
    
    # Handler methods for guidance tab
    def _on_real_time_guidance_changed(self, state):
        """Handle real-time guidance toggle."""
        settings_manager.set("real_time_guidance", state == Qt.Checked)
    
    def _on_summary_after_analysis_changed(self, state):
        """Handle summary after analysis toggle."""
        settings_manager.set("summary_after_analysis", state == Qt.Checked)
    
    def _on_save_report_changed(self, state):
        """Handle save report toggle."""
        settings_manager.set("save_report", state == Qt.Checked)
    
    def _on_show_arrows_changed(self, state):
        """Handle show arrows toggle."""
        settings_manager.set("show_arrows", state == Qt.Checked)
    
    def _on_show_color_coding_changed(self, state):
        """Handle show color coding toggle."""
        settings_manager.set("show_color_coding", state == Qt.Checked)
    
    def _on_show_text_cues_changed(self, state):
        """Handle show text cues toggle."""
        settings_manager.set("show_text_cues", state == Qt.Checked)
    
    def _on_show_target_pose_changed(self, state):
        """Handle show target pose toggle."""
        settings_manager.set("show_target_pose", state == Qt.Checked)
    
    def _on_sensitivity_changed(self, value):
        """Handle sensitivity slider change."""
        self.sensitivity_label.setText(str(value))
        settings_manager.set("guidance_sensitivity", value)
    
    def _on_tolerance_changed(self, value):
        """Handle tolerance slider change."""
        self.tolerance_label.setText(str(value))
        settings_manager.set("adjustment_tolerance", value)
    
    # Handler methods for advanced tab
    def _on_enable_kops_changed(self, state):
        """Handle enable KOPS toggle."""
        settings_manager.set("enable_kops", state == Qt.Checked)
    
    def _on_kops_tolerance_changed(self, value):
        """Handle KOPS tolerance change."""
        settings_manager.set("kops_tolerance", value)
    
    def _on_enable_setback_changed(self, state):
        """Handle enable setback toggle."""
        settings_manager.set("enable_setback", state == Qt.Checked)
    
    def _on_enable_cleat_changed(self, state):
        """Handle enable cleat toggle."""
        settings_manager.set("enable_cleat", state == Qt.Checked)
    
    def _on_cleat_position_changed(self, value):
        """Handle cleat position change."""
        settings_manager.set("cleat_position", value)
    
    def _on_enable_geometry_changed(self, state):
        """Handle enable geometry toggle."""
        settings_manager.set("enable_geometry", state == Qt.Checked)