"""
Main application window for the Bike Fit Analyzer.
Implements a PyQt-based GUI that integrates all components.
"""
import sys
import cv2
import numpy as np
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QStatusBar, QAction, QToolBar,
    QDockWidget, QTabWidget, QMessageBox, QFileDialog, QSplitter
)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QImage, QIcon

from bike_fit_analyzer.ui.settings_panel import SettingsPanel
from bike_fit_analyzer.ui.visualization_panel import VisualizationPanel
from bike_fit_analyzer.core.analyzer import BikeFitAnalyzer
from bike_fit_analyzer.utils.camera import CameraManager
from bike_fit_analyzer.wizard.setup_wizard import SetupWizard
from bike_fit_analyzer.models.user_profile import UserProfile


class MainWindow(QMainWindow):
    """Main application window for the Bike Fit Analyzer."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        # Initialize application components
        self.analyzer = BikeFitAnalyzer()
        self.camera_manager = CameraManager()
        self.user_profile = UserProfile()
        
        # Camera and video processing variables
        self.camera = None
        self.camera_id = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.mirror_enabled = True
        
        # Setup the UI
        self.init_ui()
        
        # Connect signals and slots
        self.connect_signals()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle("Bike Fit Analyzer")
        self.setMinimumSize(1200, 800)
        
        # Create central widget with main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        
        # Create splitter for resizable panels
        self.splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.splitter)
        
        # Create visualization panel (left side)
        self.visualization_panel = VisualizationPanel()
        self.splitter.addWidget(self.visualization_panel)
        
        # Create settings panel (right side)
        self.settings_panel = SettingsPanel(self.camera_manager)
        self.splitter.addWidget(self.settings_panel)
        
        # Set initial splitter sizes (70% visualization, 30% settings)
        self.splitter.setSizes([700, 300])
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
    
    def create_menu_bar(self):
        """Create the application menu bar."""
        # File menu
        file_menu = self.menuBar().addMenu("&File")
        
        new_profile_action = QAction("New Profile", self)
        new_profile_action.triggered.connect(self.new_profile)
        file_menu.addAction(new_profile_action)
        
        open_profile_action = QAction("Open Profile", self)
        open_profile_action.triggered.connect(self.open_profile)
        file_menu.addAction(open_profile_action)
        
        save_profile_action = QAction("Save Profile", self)
        save_profile_action.triggered.connect(self.save_profile)
        file_menu.addAction(save_profile_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Camera menu
        camera_menu = self.menuBar().addMenu("&Camera")
        
        start_camera_action = QAction("Start Camera", self)
        start_camera_action.triggered.connect(self.start_camera)
        camera_menu.addAction(start_camera_action)
        
        stop_camera_action = QAction("Stop Camera", self)
        stop_camera_action.triggered.connect(self.stop_camera)
        camera_menu.addAction(stop_camera_action)
        
        camera_menu.addSeparator()
        
        mirror_action = QAction("Toggle Mirror", self)
        mirror_action.setCheckable(True)
        mirror_action.setChecked(self.mirror_enabled)
        mirror_action.triggered.connect(self.toggle_mirror)
        camera_menu.addAction(mirror_action)
        
        # Analysis menu
        analysis_menu = self.menuBar().addMenu("&Analysis")
        
        start_analysis_action = QAction("Start Analysis", self)
        start_analysis_action.triggered.connect(self.start_analysis)
        analysis_menu.addAction(start_analysis_action)
        
        stop_analysis_action = QAction("Stop Analysis", self)
        stop_analysis_action.triggered.connect(self.stop_analysis)
        analysis_menu.addAction(stop_analysis_action)
        
        analysis_menu.addSeparator()
        
        capture_frame_action = QAction("Capture Frame", self)
        capture_frame_action.triggered.connect(self.capture_frame)
        analysis_menu.addAction(capture_frame_action)
        
        # Wizard menu
        wizard_menu = self.menuBar().addMenu("&Wizard")
        
        setup_wizard_action = QAction("Setup Wizard", self)
        setup_wizard_action.triggered.connect(self.run_setup_wizard)
        wizard_menu.addAction(setup_wizard_action)
        
        calibration_action = QAction("Calibration", self)
        calibration_action.triggered.connect(self.run_calibration)
        wizard_menu.addAction(calibration_action)
        
        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Create the main toolbar."""
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(self.toolbar)
        
        # Add camera controls to toolbar
        self.toolbar.addAction(QAction("Start Camera", self, triggered=self.start_camera))
        self.toolbar.addAction(QAction("Stop Camera", self, triggered=self.stop_camera))
        self.toolbar.addSeparator()
        
        # Add analysis controls to toolbar
        self.toolbar.addAction(QAction("Start Analysis", self, triggered=self.start_analysis))
        self.toolbar.addAction(QAction("Stop Analysis", self, triggered=self.stop_analysis))
        self.toolbar.addSeparator()
        
        # Add wizard access to toolbar
        self.toolbar.addAction(QAction("Setup Wizard", self, triggered=self.run_setup_wizard))
    
    def connect_signals(self):
        """Connect signal and slots for UI components."""
        # Connect camera selection combobox
        self.settings_panel.camera_combo.currentIndexChanged.connect(self.change_camera)
        
        # Connect mirror toggle button
        self.settings_panel.mirror_toggle_btn.clicked.connect(self.toggle_mirror)
        
        # Connect start/stop buttons
        self.settings_panel.start_btn.clicked.connect(self.start_camera)
        self.settings_panel.stop_btn.clicked.connect(self.stop_camera)
        
        # Connect analysis buttons
        self.settings_panel.start_analysis_btn.clicked.connect(self.start_analysis)
        self.settings_panel.stop_analysis_btn.clicked.connect(self.stop_analysis)
    
    @pyqtSlot()
    def start_camera(self):
        """Start the camera capture."""
        if self.timer.isActive():
            return
        
        # Get selected camera ID from settings panel
        self.camera_id = self.settings_panel.get_selected_camera_id()
        
        # Open the camera
        self.camera = self.camera_manager.open_camera(self.camera_id)
        if self.camera is None:
            QMessageBox.critical(self, "Error", f"Failed to open camera {self.camera_id}")
            return
        
        # Start the timer for frame updates
        self.timer.start(30)  # Update every 30ms (approx. 33 FPS)
        self.status_bar.showMessage(f"Camera {self.camera_id} started")
        
        # Update button states
        self.settings_panel.update_button_states(camera_running=True)
    
    @pyqtSlot()
    def stop_camera(self):
        """Stop the camera capture."""
        if not self.timer.isActive():
            return
        
        # Stop the timer
        self.timer.stop()
        
        # Release the camera
        if self.camera is not None:
            self.camera.release()
            self.camera = None
        
        # Clear the display
        self.visualization_panel.clear_display()
        
        self.status_bar.showMessage("Camera stopped")
        
        # Update button states
        self.settings_panel.update_button_states(camera_running=False)
    
    @pyqtSlot(int)
    def change_camera(self, index):
        """Change the camera source."""
        if index < 0:
            return
        
        # Get the camera ID from the combobox
        self.camera_id = self.settings_panel.get_selected_camera_id()
        
        # If camera is running, restart it with the new ID
        if self.timer.isActive():
            self.stop_camera()
            self.start_camera()
    
    @pyqtSlot()
    def toggle_mirror(self):
        """Toggle mirror mode for the camera view."""
        self.mirror_enabled = not self.mirror_enabled
        self.settings_panel.update_mirror_button(self.mirror_enabled)
        self.status_bar.showMessage(f"Mirror mode: {'On' if self.mirror_enabled else 'Off'}")
    
    @pyqtSlot()
    def update_frame(self):
        """Update the video frame from the camera."""
        if self.camera is None or not self.camera.isOpened():
            self.stop_camera()
            return
        
        # Read a frame from the camera
        ret, frame = self.camera.read()
        if not ret:
            self.status_bar.showMessage("Failed to capture frame")
            return
        
        # Process the frame if analysis is active
        if self.settings_panel.is_analysis_active():
            frame = self.analyzer.process_frame(frame, self.mirror_enabled)
        elif self.mirror_enabled:
            frame = cv2.flip(frame, 1)
        
        # Update the visualization panel with the new frame
        self.visualization_panel.update_frame(frame)
    
    @pyqtSlot()
    def start_analysis(self):
        """Start the pose analysis."""
        self.settings_panel.set_analysis_active(True)
        self.status_bar.showMessage("Analysis started")
    
    @pyqtSlot()
    def stop_analysis(self):
        """Stop the pose analysis."""
        self.settings_panel.set_analysis_active(False)
        self.status_bar.showMessage("Analysis stopped")
    
    @pyqtSlot()
    def capture_frame(self):
        """Capture the current frame and save it."""
        if self.visualization_panel.current_frame is None:
            QMessageBox.warning(self, "Warning", "No frame to capture")
            return
        
        # Prompt for save location
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Frame", "", "Images (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            # Save the current frame
            cv2.imwrite(file_path, self.visualization_panel.current_frame)
            self.status_bar.showMessage(f"Frame saved to {file_path}")
    
    @pyqtSlot()
    def run_setup_wizard(self):
        """Launch the setup wizard."""
        wizard = SetupWizard(self)
        if wizard.exec_():
            # Apply settings from wizard
            self.status_bar.showMessage("Setup complete")
    
    @pyqtSlot()
    def run_calibration(self):
        """Launch the calibration wizard."""
        # This could be a specific page in the setup wizard or a separate dialog
        self.status_bar.showMessage("Calibration complete")
    
    @pyqtSlot()
    def new_profile(self):
        """Create a new user profile."""
        # Reset user profile data
        self.user_profile = UserProfile()
        self.status_bar.showMessage("New profile created")
    
    @pyqtSlot()
    def open_profile(self):
        """Open an existing user profile."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Profile", "", "Profile Files (*.json)"
        )
        
        if file_path:
            try:
                self.user_profile.load_from_file(file_path)
                self.status_bar.showMessage(f"Profile loaded from {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load profile: {str(e)}")
    
    @pyqtSlot()
    def save_profile(self):
        """Save the current user profile."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Profile", "", "Profile Files (*.json)"
        )
        
        if file_path:
            try:
                self.user_profile.save_to_file(file_path)
                self.status_bar.showMessage(f"Profile saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save profile: {str(e)}")
    
    @pyqtSlot()
    def show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About Bike Fit Analyzer",
            "Bike Fit Analyzer v1.0\n\n"
            "A tool for analyzing and optimizing bike fit using computer vision.\n\n"
            "© 2025 Bike Fit Team"
        )
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Stop the camera if it's running
        if self.timer.isActive():
            self.stop_camera()
        
        # Accept the close event
        event.accept()

