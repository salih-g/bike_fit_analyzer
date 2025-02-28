"""
Core analyzer functionality for the Bike Fit Analyzer.
"""
import cv2
from typing import Optional

from bike_fit_analyzer.core.pose_detector import PoseDetector
from bike_fit_analyzer.utils.camera import CameraManager
from bike_fit_analyzer.utils.visualization import Visualizer
from bike_fit_analyzer.ui.renderer import UIRenderer


class BikeFitAnalyzer:
    """Main class for the Bike Fit Analyzer application."""
    
    def __init__(self):
        """Initialize the Bike Fit Analyzer."""
        self.camera_manager = CameraManager()
        self.pose_detector = PoseDetector()
        self.visualizer = Visualizer()
        self.ui_renderer = UIRenderer()
    
    def process_frame(self, frame, mirror=False):
        """
        Process a single frame.
        
        Args:
            frame: Input frame
            mirror: Whether to mirror the frame
            
        Returns:
            Processed frame
        """
        # Mirror the image if requested
        if mirror:
            frame = cv2.flip(frame, 1)
        
        # Detect pose
        processed_frame, pose_data = self.pose_detector.detect_pose(frame)
        
        # Visualize the frame
        output_frame = self.visualizer.visualize_frame(processed_frame, pose_data)
        
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

