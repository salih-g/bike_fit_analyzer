import json
import os
from typing import Dict, Any, Callable, List
from bike_fit_analyzer.config.settings import *
from bike_fit_analyzer.config.settings import CAMERA_HEIGHT, CAMERA_WIDTH, DEFAULT_MIRROR, IDEAL_ANGLES, MIN_DETECTION_CONFIDENCE, MIN_TRACKING_CONFIDENCE, POSE_MODEL_COMPLEXITY

class SettingsManager:
    """Central manager for all application settings."""
    
    def __init__(self):
        """Initialize the settings manager with default values."""
        # Store current settings
        self.settings = {
            # Camera settings
            "camera_id": 0,
            "mirror_enabled": DEFAULT_MIRROR,
            "camera_width": CAMERA_WIDTH,
            "camera_height": CAMERA_HEIGHT,
            
            # Analysis settings
            "pose_model_complexity": POSE_MODEL_COMPLEXITY,
            "min_detection_confidence": MIN_DETECTION_CONFIDENCE,
            "min_tracking_confidence": MIN_TRACKING_CONFIDENCE,
            
            # Visualization settings
            "show_skeleton": True,
            "show_landmarks": True,
            "show_angles": True,
            "show_guidance": True,
            "view_mode": "Normal View",
            
            # Angle settings
            "angles": IDEAL_ANGLES.copy(),
            "angles_enabled": {k: True for k in IDEAL_ANGLES},
            
            # Guidance settings
            "real_time_guidance": True,
            "summary_after_analysis": False,
            "save_report": False,
            "show_arrows": True,
            "show_color_coding": True,
            "show_text_cues": True,
            "show_target_pose": False,
            "guidance_sensitivity": 5,
            "adjustment_tolerance": 3,
            
            # Advanced settings
            "enable_kops": True,
            "kops_tolerance": 1.0,
            "enable_setback": True,
            "enable_cleat": True,
            "cleat_position": 65,
            "enable_geometry": True
        }
        
        # Store observers that need to be notified of changes
        self.observers: List[Callable[[str, Any], None]] = []
    
    def get(self, key: str, default=None) -> Any:
        """Get a setting value."""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a setting value and notify observers."""
        if key in self.settings and self.settings[key] != value:
            self.settings[key] = value
            self._notify_observers(key, value)
    
    def add_observer(self, observer: Callable[[str, Any], None]) -> None:
        """Add an observer to be notified of setting changes."""
        if observer not in self.observers:
            self.observers.append(observer)
    
    def remove_observer(self, observer: Callable[[str, Any], None]) -> None:
        """Remove an observer."""
        if observer in self.observers:
            self.observers.remove(observer)
    
    def _notify_observers(self, key: str, value: Any) -> None:
        """Notify all observers of a setting change."""
        for observer in self.observers:
            observer(key, value)
    
    def save_to_file(self, file_path: str) -> None:
        """Save settings to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(self.settings, f, indent=2)
    
    def load_from_file(self, file_path: str) -> bool:
        """Load settings from a JSON file."""
        if not os.path.exists(file_path):
            return False
        
        try:
            with open(file_path, 'r') as f:
                new_settings = json.load(f)
                
                # Update settings and notify observers
                for key, value in new_settings.items():
                    if key in self.settings:
                        self.set(key, value)
                
                return True
        except Exception as e:
            print(f"Error loading settings: {e}")
            return False

# Create a global instance
settings_manager = SettingsManager()