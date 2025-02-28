"""
Core analyzer functionality for the Bike Fit Analyzer.
"""
import cv2
from typing import Optional, Tuple

from bike_fit_analyzer.core.pose_detector import PoseDetector
from bike_fit_analyzer.utils.camera import CameraManager
from bike_fit_analyzer.utils.visualization import Visualizer
from bike_fit_analyzer.ui.renderer import UIRenderer
from bike_fit_analyzer.guidance.bike_adjustments import BikeAdjustmentAnalyzer


class BikeFitAnalyzer:
    """Main class for the Bike Fit Analyzer application."""
    
    def __init__(self):
        """Initialize the Bike Fit Analyzer."""
        self.camera_manager = CameraManager()
        self.pose_detector = PoseDetector()
        self.visualizer = Visualizer()
        self.ui_renderer = UIRenderer()
        self.bike_adjustment_analyzer = BikeAdjustmentAnalyzer()
    
    def process_frame(self, frame, mirror=False, view_mode="Normal View", show_angles=True, show_guidance=True):
        """
        Process a single frame.
        
        Args:
            frame: Input frame
            mirror: Whether to mirror the frame
            view_mode: Visualization view mode
            show_angles: Whether to show angles
            show_guidance: Whether to show guidance
            
        Returns:
            Tuple of (processed frame, pose data, adjustments)
        """
        # Mirror the image if requested
        if mirror:
            frame = cv2.flip(frame, 1)
        
        # Detect pose
        processed_frame, pose_data = self.pose_detector.detect_pose(frame)
        
        # Generate adjustments if pose detected and guidance enabled
        adjustments = None
        if pose_data and show_guidance:
            adjustments = self.bike_adjustment_analyzer.analyze_pose(pose_data)
        
        # Visualize the frame (moved this to the visualization panel)
        # output_frame = self.visualizer.visualize_frame(
        #     processed_frame, 
        #     pose_data, 
        #     show_angles=show_angles
        # )
        
        return processed_frame, pose_data, adjustments
    
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
        current_view_mode = "Normal View"
        show_angles = True
        show_guidance = True
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Failed to receive frame from camera.")
                    break
                
                # Process the frame
                processed_frame, pose_data, adjustments = self.process_frame(
                    frame, 
                    current_mirror, 
                    current_view_mode, 
                    show_angles, 
                    show_guidance
                )
                
                # Use the visualizer to create the output
                output_frame = self.visualizer.visualize_frame(
                    processed_frame, 
                    pose_data, 
                    show_angles=show_angles
                )
                
                # Show the result
                self.ui_renderer.show_frame(output_frame)
                
                # Handle keyboard input
                key = self.ui_renderer.get_key_press()
                if key == ord('q'):
                    break
                elif key == ord('m'):
                    current_mirror = not current_mirror
                    print(f"Mirror mode: {'On' if current_mirror else 'Off'}")
                elif key == ord('a'):
                    show_angles = not show_angles
                    print(f"Show angles: {'On' if show_angles else 'Off'}")
                elif key == ord('g'):
                    show_guidance = not show_guidance
                    print(f"Show guidance: {'On' if show_guidance else 'Off'}")
                elif key == ord('v'):
                    # Cycle through view modes
                    view_modes = ["Normal View", "Skeleton Only", "Angles Only", "Guidance View", "Comparison View"]
                    current_idx = view_modes.index(current_view_mode)
                    current_idx = (current_idx + 1) % len(view_modes)
                    current_view_mode = view_modes[current_idx]
                    print(f"View mode: {current_view_mode}")
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