"""
Setup wizard for the Bike Fit Analyzer.
Guides users through setup, calibration, and initial configuration.
"""
from typing import Dict, List, Optional, Tuple
from PyQt5.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, QCheckBox,
    QRadioButton, QButtonGroup, QPushButton, QGroupBox, QFormLayout
)
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont

from bike_fit_analyzer.models.user_profile import UserProfile
from bike_fit_analyzer.models.bike_config import BikeType


class IntroPage(QWizardPage):
    """Introduction page for the setup wizard."""
    
    def __init__(self):
        """Initialize the intro page."""
        super().__init__()
        self.setTitle("Welcome to Bike Fit Analyzer")
        self.setSubTitle("This wizard will guide you through the setup process.")
        
        layout = QVBoxLayout()
        
        intro_text = QLabel(
            "Proper bike fit is crucial for comfort, performance, and injury prevention. "
            "This application uses computer vision to analyze your riding position and "
            "provide recommendations for optimal bike setup.\n\n"
            "The wizard will guide you through:\n"
            "1. Camera setup and positioning\n"
            "2. User measurements input\n"
            "3. Bike configuration\n"
            "4. Calibration process\n\n"
            "Click 'Next' to begin."
        )
        intro_text.setWordWrap(True)
        
        layout.addWidget(intro_text)
        self.setLayout(layout)


class CameraSetupPage(QWizardPage):
    """Camera setup and positioning page."""
    
    def __init__(self):
        """Initialize the camera setup page."""
        super().__init__()
        self.setTitle("Camera Setup")
        self.setSubTitle("Position your camera for optimal pose detection.")
        
        layout = QVBoxLayout()
        
        # Camera position instructions
        instructions = QLabel(
            "Proper camera positioning is essential for accurate analysis:\n\n"
            "1. Place the camera at saddle height\n"
            "2. Position it perpendicular to the bike (side view)\n"
            "3. Ensure the entire bike and rider are visible\n"
            "4. Use good lighting conditions\n\n"
            "The best position is 3-4 meters away from the bike, directly from the side."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Camera preview would go here in a full implementation
        preview_placeholder = QLabel("Camera preview would appear here")
        preview_placeholder.setAlignment(Qt.AlignCenter)
        preview_placeholder.setStyleSheet("background-color: #222; padding: 40px;")
        layout.addWidget(preview_placeholder)
        
        # Camera selection
        camera_group = QGroupBox("Camera Selection")
        camera_layout = QFormLayout()
        
        self.camera_combo = QComboBox()
        self.camera_combo.addItem("Default Camera", 0)
        camera_layout.addRow("Select Camera:", self.camera_combo)
        
        camera_group.setLayout(camera_layout)
        layout.addWidget(camera_group)
        
        self.setLayout(layout)


class UserMeasurementsPage(QWizardPage):
    """User measurements input page."""
    
    def __init__(self):
        """Initialize the user measurements page."""
        super().__init__()
        self.setTitle("User Measurements")
        self.setSubTitle("Enter your body measurements for personalized fit recommendations.")
        
        layout = QVBoxLayout()
        
        # Form for measurements
        form_layout = QFormLayout()
        
        # Height
        self.height_spinner = QDoubleSpinBox()
        self.height_spinner.setRange(100, 220)
        self.height_spinner.setValue(175)
        self.height_spinner.setSuffix(" cm")
        form_layout.addRow("Height:", self.height_spinner)
        
        # Inseam
        self.inseam_spinner = QDoubleSpinBox()
        self.inseam_spinner.setRange(60, 120)
        self.inseam_spinner.setValue(80)
        self.inseam_spinner.setSuffix(" cm")
        form_layout.addRow("Inseam:", self.inseam_spinner)
        
        # Arm length
        self.arm_spinner = QDoubleSpinBox()
        self.arm_spinner.setRange(50, 100)
        self.arm_spinner.setValue(70)
        self.arm_spinner.setSuffix(" cm")
        form_layout.addRow("Arm Length:", self.arm_spinner)
        
        # Torso length
        self.torso_spinner = QDoubleSpinBox()
        self.torso_spinner.setRange(40, 80)
        self.torso_spinner.setValue(60)
        self.torso_spinner.setSuffix(" cm")
        form_layout.addRow("Torso Length:", self.torso_spinner)
        
        # Shoulder width
        self.shoulder_spinner = QDoubleSpinBox()
        self.shoulder_spinner.setRange(30, 60)
        self.shoulder_spinner.setValue(45)
        self.shoulder_spinner.setSuffix(" cm")
        form_layout.addRow("Shoulder Width:", self.shoulder_spinner)
        
        # Flexibility level
        self.flexibility_combo = QComboBox()
        self.flexibility_combo.addItems(["Low", "Medium", "High"])
        self.flexibility_combo.setCurrentIndex(1)  # Default to Medium
        form_layout.addRow("Flexibility Level:", self.flexibility_combo)
        
        # Experience level
        self.experience_combo = QComboBox()
        self.experience_combo.addItems(["Beginner", "Intermediate", "Advanced"])
        self.experience_combo.setCurrentIndex(1)  # Default to Intermediate
        form_layout.addRow("Riding Experience:", self.experience_combo)
        
        layout.addLayout(form_layout)
        
        # Note about measurements
        note = QLabel(
            "Note: Accurate measurements will result in better fit recommendations. "
            "If you're unsure about any measurement, use our measurement guide or "
            "leave it at the default value for now."
        )
        note.setWordWrap(True)
        note.setStyleSheet("font-style: italic; color: #666;")
        layout.addWidget(note)
        
        self.setLayout(layout)
    
    def validatePage(self):
        """Validate the page before proceeding."""
        # In a real implementation, we might validate that measurements are reasonable
        # For example, inseam should be less than height
        return True


class BikeConfigPage(QWizardPage):
    """Bike configuration page."""
    
    def __init__(self):
        """Initialize the bike configuration page."""
        super().__init__()
        self.setTitle("Bike Configuration")
        self.setSubTitle("Tell us about your bike for more accurate analysis.")
        
        layout = QVBoxLayout()
        
        # Bike type selection
        bike_group = QGroupBox("Bike Type")
        bike_layout = QVBoxLayout()
        
        self.bike_type_combo = QComboBox()
        self.bike_type_combo.addItems([
            "Road Bike",
            "Mountain Bike",
            "Hybrid/City Bike",
            "Time Trial/Triathlon Bike",
            "Gravel Bike",
            "Touring Bike"
        ])
        bike_layout.addWidget(self.bike_type_combo)
        
        bike_group.setLayout(bike_layout)
        layout.addWidget(bike_group)
        
        # Bike measurements
        measurements_group = QGroupBox("Current Bike Measurements (if known)")
        measurements_layout = QFormLayout()
        
        # Saddle height
        self.saddle_height_spinner = QDoubleSpinBox()
        self.saddle_height_spinner.setRange(60, 100)
        self.saddle_height_spinner.setValue(72)
        self.saddle_height_spinner.setSuffix(" cm")
        measurements_layout.addRow("Saddle Height:", self.saddle_height_spinner)
        
        # Saddle setback
        self.saddle_setback_spinner = QDoubleSpinBox()
        self.saddle_setback_spinner.setRange(-5, 15)
        self.saddle_setback_spinner.setValue(5)
        self.saddle_setback_spinner.setSuffix(" cm")
        measurements_layout.addRow("Saddle Setback:", self.saddle_setback_spinner)
        
        # Reach
        self.reach_spinner = QDoubleSpinBox()
        self.reach_spinner.setRange(30, 60)
        self.reach_spinner.setValue(45)
        self.reach_spinner.setSuffix(" cm")
        measurements_layout.addRow("Reach:", self.reach_spinner)
        
        # Stack
        self.stack_spinner = QDoubleSpinBox()
        self.stack_spinner.setRange(50, 70)
        self.stack_spinner.setValue(55)
        self.stack_spinner.setSuffix(" cm")
        measurements_layout.addRow("Stack:", self.stack_spinner)
        
        measurements_group.setLayout(measurements_layout)
        layout.addWidget(measurements_group)
        
        # Bike fit goals
        goals_group = QGroupBox("Bike Fit Goals")
        goals_layout = QVBoxLayout()
        
        self.comfort_check = QCheckBox("Comfort: Reduce strain on back and neck")
        self.comfort_check.setChecked(True)
        
        self.performance_check = QCheckBox("Performance: Maximize power output")
        self.performance_check.setChecked(False)
        
        self.aero_check = QCheckBox("Aerodynamics: Reduce drag")
        self.aero_check.setChecked(False)
        
        self.endurance_check = QCheckBox("Endurance: Long-distance comfort")
        self.endurance_check.setChecked(True)
        
        goals_layout.addWidget(self.comfort_check)
        goals_layout.addWidget(self.performance_check)
        goals_layout.addWidget(self.aero_check)
        goals_layout.addWidget(self.endurance_check)
        
        goals_group.setLayout(goals_layout)
        layout.addWidget(goals_group)
        
        self.setLayout(layout)


class CalibrationPage(QWizardPage):
    """Camera and analysis calibration page."""
    
    def __init__(self):
        """Initialize the calibration page."""
        super().__init__()
        self.setTitle("Calibration")
        self.setSubTitle("Let's calibrate the system for accurate measurements.")
        
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "Follow these steps to calibrate the system:\n\n"
            "1. Sit on your bike in your normal riding position\n"
            "2. Ensure your entire body and bike are visible\n"
            "3. Make sure the camera can see your side profile clearly\n"
            "4. Click 'Start Calibration' and hold your position for 5 seconds"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Calibration preview
        preview_group = QGroupBox("Calibration Preview")
        preview_layout = QVBoxLayout()
        
        preview_placeholder = QLabel("Camera preview would appear here")
        preview_placeholder.setAlignment(Qt.AlignCenter)
        preview_placeholder.setStyleSheet("background-color: #222; padding: 100px;")
        
        preview_layout.addWidget(preview_placeholder)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Calibration controls
        controls_layout = QHBoxLayout()
        
        self.start_calibration_btn = QPushButton("Start Calibration")
        self.cancel_calibration_btn = QPushButton("Cancel")
        self.cancel_calibration_btn.setEnabled(False)
        
        controls_layout.addWidget(self.start_calibration_btn)
        controls_layout.addWidget(self.cancel_calibration_btn)
        
        layout.addLayout(controls_layout)
        
        # Calibration status
        self.status_label = QLabel("Ready to calibrate")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # Connect signals
        self.start_calibration_btn.clicked.connect(self.start_calibration)
        self.cancel_calibration_btn.clicked.connect(self.cancel_calibration)
    
    @pyqtSlot()
    def start_calibration(self):
        """Start the calibration process."""
        # In a full implementation, this would initiate a real calibration
        self.status_label.setText("Calibrating... Please hold your position.")
        self.start_calibration_btn.setEnabled(False)
        self.cancel_calibration_btn.setEnabled(True)
        
        # Simulate a successful calibration after a short delay
        # In a real app, this would be handled by actual calibration logic
        QTimer.singleShot(3000, self.calibration_complete)
    
    @pyqtSlot()
    def calibration_complete(self):
        """Handle calibration completion."""
        self.status_label.setText("Calibration complete! You can proceed to the next step.")
        self.start_calibration_btn.setText("Recalibrate")
        self.start_calibration_btn.setEnabled(True)
        self.cancel_calibration_btn.setEnabled(False)
    
    @pyqtSlot()
    def cancel_calibration(self):
        """Cancel the calibration process."""
        self.status_label.setText("Calibration cancelled. Click 'Start Calibration' to try again.")
        self.start_calibration_btn.setEnabled(True)
        self.cancel_calibration_btn.setEnabled(False)


class CompletionPage(QWizardPage):
    """Wizard completion page."""
    
    def __init__(self):
        """Initialize the completion page."""
        super().__init__()
        self.setTitle("Setup Complete")
        self.setSubTitle("You're all set to start analyzing your bike fit!")
        
        layout = QVBoxLayout()
        
        # Completion message
        completion_text = QLabel(
            "Congratulations! You've successfully set up the Bike Fit Analyzer.\n\n"
            "Here's what you can do next:\n\n"
            "1. Start the analysis by clicking 'Start Analysis' in the main window\n"
            "2. Follow the guidance to adjust your bike fit\n"
            "3. Save your profile for future sessions\n"
            "4. Experiment with different positions to find your optimal fit\n\n"
            "Click 'Finish' to return to the main application."
        )
        completion_text.setWordWrap(True)
        
        layout.addWidget(completion_text)
        
        # Quick start options
        options_group = QGroupBox("Quick Start Options")
        options_layout = QVBoxLayout()
        
        self.start_analysis_check = QCheckBox("Start analysis immediately")
        self.start_analysis_check.setChecked(True)
        
        self.save_profile_check = QCheckBox("Save user profile")
        self.save_profile_check.setChecked(True)
        
        options_layout.addWidget(self.start_analysis_check)
        options_layout.addWidget(self.save_profile_check)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        self.setLayout(layout)


class SetupWizard(QWizard):
    """Setup wizard for the Bike Fit Analyzer."""
    
    def __init__(self, parent=None):
        """Initialize the setup wizard."""
        super().__init__(parent)
        
        self.setWindowTitle("Bike Fit Analyzer Setup")
        self.setWizardStyle(QWizard.ModernStyle)
        
        # Set window size
        self.resize(800, 600)
        
        # Add pages
        self.addPage(IntroPage())
        self.addPage(CameraSetupPage())
        self.addPage(UserMeasurementsPage())
        self.addPage(BikeConfigPage())
        self.addPage(CalibrationPage())
        self.addPage(CompletionPage())
        
        # Connect signals
        self.finished.connect(self.on_wizard_finished)
    
    @pyqtSlot(int)
    def on_wizard_finished(self, result):
        """
        Handle wizard completion.
        
        Args:
            result: Wizard result code
        """
        if result == QWizard.Accepted:
            # In a full implementation, this would apply all the settings
            # and potentially start the analysis if requested
            print("Wizard completed successfully")
