"""
Camera handling utilities for the Bike Fit Analyzer.
"""
import os
import cv2
from typing import Dict, List, Optional, Tuple


class CameraManager:
    """Handles camera detection, selection, and management."""
    
    def __init__(self):
        """Initialize the camera manager."""
        self.available_cameras = self.find_available_cameras()
    
    def find_available_cameras(self) -> Dict[int, str]:
        """Find all available camera devices."""
        available_cameras = {}
        
        # On macOS, check for specific camera devices
        if os.name == 'posix' and os.uname().sysname == 'Darwin':  # Check if running on macOS
            # Check for common macOS camera paths
            for i in range(10):  # Check devices 0-9
                # Check potential FaceTime HD Camera
                facetime_path = f"/dev/video{i}"
                if os.path.exists(facetime_path):
                    available_cameras[i] = f"Camera at {facetime_path}"
                
                # Also try to open the camera to verify it works
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        available_cameras[i] = f"Camera #{i}"
                    cap.release()
        else:
            # Generic approach for other platforms
            for i in range(10):  # Check devices 0-9
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        # Try to get camera name
                        camera_name = f"Camera #{i}"
                        # On some systems, we can get the camera name
                        try:
                            camera_name = cap.getBackendName() + f" #{i}"
                        except:
                            pass
                        available_cameras[i] = camera_name
                    cap.release()
        
        # Special handling for MacBook - if no cameras found via indices,
        # try using cv2.CAP_AVFOUNDATION explicitly for macOS
        if os.name == 'posix' and os.uname().sysname == 'Darwin' and len(available_cameras) == 0:
            for i in range(10):
                cap = cv2.VideoCapture(i, cv2.CAP_AVFOUNDATION)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        available_cameras[i] = f"AVFoundation Camera #{i}"
                    cap.release()
        
        return available_cameras

    def list_cameras(self) -> Optional[List[int]]:
        """List all available cameras."""
        if not self.available_cameras:
            print("No cameras detected. Please check your camera connections.")
            return None
        
        print("\nAvailable Cameras:")
        print("-----------------")
        for cam_id, cam_name in self.available_cameras.items():
            print(f"{cam_id}: {cam_name}")
        print()
        
        return list(self.available_cameras.keys())

    def select_camera(self) -> int:
        """Prompt user to select a camera."""
        camera_ids = self.list_cameras()
        
        if not camera_ids:
            print("No cameras available to select. Using default (0).")
            return 0
        
        while True:
            try:
                selection = input(f"Select camera ID (0-{max(camera_ids)}), or press Enter for default (0): ")
                
                if selection == "":
                    return 0
                
                selection = int(selection)
                if selection in camera_ids:
                    return selection
                else:
                    print(f"Invalid selection. Please choose from: {camera_ids}")
            except ValueError:
                print("Please enter a valid number.")

    def open_camera(self, camera_id: int) -> Optional[cv2.VideoCapture]:
        """Open the camera with the specified ID."""
        print(f"Opening camera {camera_id}...")
        
        # Try standard method first
        cap = cv2.VideoCapture(camera_id)
        
        # If that doesn't work and we're on macOS, try AVFoundation backend
        if not cap.isOpened() and os.name == 'posix' and os.uname().sysname == 'Darwin':
            print("Trying AVFoundation backend for macOS...")
            cap = cv2.VideoCapture(camera_id, cv2.CAP_AVFOUNDATION)
        
        # Check if camera opened successfully
        if not cap.isOpened():
            print(f"Failed to open camera {camera_id}. Please try another camera.")
            return None
        
        # Set camera resolution
        from bike_fit_analyzer.config.settings import CAMERA_WIDTH, CAMERA_HEIGHT
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        
        return cap
