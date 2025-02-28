"""
Core analyzer functionality for the Bike Fit Analyzer.
"""
import cv2
from typing import Optional

from bike_fit_analyzer.core.pose_detector import PoseDetector
from bike_fit_analyzer.utils.camera import CameraManager
from bike_fit_analyzer.utils.visualization import Visualizer
from bike_fit_analyzer.ui.renderer import UIRenderer
from bike_fit_analyzer.config.settings_manager import settings_manager


class BikeFitAnalyzer:
    """Main class for the Bike Fit Analyzer application."""
    
    def __init__(self):
        """Initialize the Bike Fit Analyzer."""
        self.camera_manager = CameraManager()
        self.pose_detector = PoseDetector()
        self.visualizer = Visualizer()
        self.ui_renderer = UIRenderer()
        
        # Register as an observer for settings changes
        settings_manager.add_observer(self._on_settings_changed)
    
    def _on_settings_changed(self, key, value):
        """Handle settings changes."""
        # Update pose detector parameters when they change
        if key == "pose_model_complexity":
            self.pose_detector.update_model_complexity(value)
        elif key == "min_detection_confidence" or key == "min_tracking_confidence":
            self.pose_detector.update_confidence_thresholds(
                settings_manager.get("min_detection_confidence"),
                settings_manager.get("min_tracking_confidence")
            )
    
    def process_frame(self, frame, mirror=None):
        """
        Process a single frame.
        
        Args:
            frame: Input frame
            mirror: Whether to mirror the frame (overrides settings if provided)
            
        Returns:
            Processed frame
        """
        # Use settings for mirror if not explicitly provided
        if mirror is None:
            mirror = settings_manager.get("mirror_enabled")
        
        # Mirror the image if requested
        if mirror:
            frame = cv2.flip(frame, 1)
        
        # Get visualization settings
        show_skeleton = settings_manager.get("show_skeleton")
        show_landmarks = settings_manager.get("show_landmarks")
        show_angles = settings_manager.get("show_angles")
        show_guidance = settings_manager.get("show_guidance")
        view_mode = settings_manager.get("view_mode")
        angles = settings_manager.get("angles")
        angles_enabled = settings_manager.get("angles_enabled")
        
        # Detect pose with current settings
        processed_frame, pose_data = self.pose_detector.detect_pose(frame)
        
        # Filter out disabled angles if we have pose data
        if pose_data:
            filtered_angles = {}
            for angle_name, angle in pose_data.angles.items():
                if angle_name in angles_enabled and angles_enabled[angle_name]:
                    # Update the ideal range based on current settings
                    if angle_name in angles:
                        angle.ideal_range = angles[angle_name]
                    filtered_angles[angle_name] = angle
            
            pose_data.angles = filtered_angles
        
        # Generate adjustments if we have pose data
        adjustments = []
        if pose_data and show_guidance:
            from bike_fit_analyzer.guidance.bike_adjustments import BikeAdjustmentAnalyzer
            adjuster = BikeAdjustmentAnalyzer()
            adjustments = adjuster.analyze_pose(pose_data)
        
        # Apply visualization based on current settings
        show_arrows = settings_manager.get("show_arrows")
        show_color_coding = settings_manager.get("show_color_coding")
        show_text_cues = settings_manager.get("show_text_cues")
        show_target_pose = settings_manager.get("show_target_pose")
        
        # Visualize the frame
        output_frame = self.visualizer.visualize_frame(
            processed_frame, 
            pose_data, 
            adjustments,
            show_skeleton=show_skeleton,
            show_landmarks=show_landmarks,
            show_angles=show_angles,
            show_guidance=show_guidance,
            show_arrows=show_arrows,
            show_color_coding=show_color_coding,
            show_text_cues=show_text_cues,
            show_target_pose=show_target_pose,
            view_mode=view_mode
        )
        
        return output_frame
    
    def run(self, camera_id=None, mirror=True):
        """
        Run the Bike Fit Analyzer.
        
        Args:
            camera_id: Optional camera ID to use
            mirror: Whether to mirror the camera view initially
        """
        # If no camera_id provided, prompt for selection
        if camera_id is None:
            camera_id = self.camera_manager.select_camera()
        
        # Open the camera
        cap = self.camera_manager.open_camera(camera_id)
        if cap is None:
            return
        
        current_mirror = mirror
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Failed to receive frame from camera.")
                    break
                
                # Process the frame
                output_frame = self.process_frame(frame, current_mirror)
                
                # Show the result
                self.ui_renderer.show_frame(output_frame)
                
                # Handle keyboard input
                key = self.ui_renderer.get_key_press()
                if key == ord('q'):
                    break
                elif key == ord('m'):
                    current_mirror = not current_mirror
                    print(f"Mirror mode: {'On' if current_mirror else 'Off'}")
                elif key == ord('c'):
                    # Clean up current camera
                    cap.release()
                    
                    # Select a new camera
                    new_camera_id = self.camera_manager.select_camera()
                    
                    # Try to open the new camera
                    cap = self.camera_manager.open_camera(new_camera_id)
                    if cap is None:
                        print(f"Failed to open camera {new_camera_id}. Trying to revert to camera {camera_id}.")
                        cap = self.camera_manager.open_camera(camera_id)
                    else:
                        camera_id = new_camera_id
                        print(f"Switched to camera {camera_id}")
        
        finally:
            # Clean up
            if cap is not None:
                cap.release()
            self.ui_renderer.cleanup()

