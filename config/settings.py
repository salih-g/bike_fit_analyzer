# bike_fit_analyzer/config/settings.py
"""
Configuration settings for the Bike Fit Analyzer application.
"""
import cv2
from typing import Dict, Tuple, List, Any

# Ideal angle ranges
IDEAL_ANGLES = {
    "neck_angle": (65, 75),      # 65°-75°
    "shoulder_angle": (60, 110), # 60°-110°
    "hip_angle": (65, 145),      # 65°-145°
    "knee_angle": (115, 180),    # 115°-180°
    "elbow_angle": (150, 160)    # 150°-160°
}

# Colors for visualization
COLORS = {
    "in_range": (0, 255, 0),       # Green
    "out_of_range": (0, 0, 255),   # Red
    "text_color": (255, 255, 0),   # Yellow
    "line_color": (255, 0, 0),     # Red
    "highlight": (0, 255, 255),    # Cyan
    "warning": (0, 165, 255),      # Orange
    "background": (45, 45, 45),    # Dark Gray
    "success": (0, 255, 0),        # Green
    "info": (255, 255, 0),         # Yellow
    "overlay": (180, 180, 180)     # Light Gray
}

# Font and drawing settings
FONT = cv2.FONT_HERSHEY_SIMPLEX
LINE_THICKNESS = 2
POINT_RADIUS = 5

# Camera settings
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
DEFAULT_FPS = 30
DEFAULT_MIRROR = True

# MediaPipe Pose settings
POSE_MODEL_COMPLEXITY = 2
MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5

# GUI settings
GUI_SETTINGS = {
    "window_title": "Bike Fit Analyzer",
    "default_window_width": 1200,
    "default_window_height": 800,
    "min_window_width": 800,
    "min_window_height": 600,
    "settings_panel_width": 350,
    "visualization_panel_min_width": 640,
    "visualization_panel_min_height": 480,
    "status_bar_timeout": 5000,  # ms
    "icon_size": (32, 32)
}

# View modes
VIEW_MODES = [
    "Normal View", 
    "Skeleton Only", 
    "Angles Only",
    "Guidance View",
    "Comparison View"
]

# Recording settings
RECORDING_SETTINGS = {
    "default_duration": 10,  # seconds
    "default_fps": 30,
    "default_format": "mp4",
    "default_resolution": (1280, 720)
}

# Visual guidance settings
GUIDANCE_SETTINGS = {
    "arrow_length": 40,
    "arrow_thickness": 2,
    "arrow_head_length": 10,
    "text_offset": 30,
    "font_scale": 0.7,
    "text_thickness": 2,
    "line_dash_length": 10,
    "line_gap_length": 5,
    "overlay_alpha": 0.4,
    "max_recommendations": 3,
    "target_line_color": (0, 255, 255),  # Cyan
    "arrow_head_size": 15
}

# Adjustment thresholds (in degrees)
ADJUSTMENT_THRESHOLDS = {
    "minor": 5.0,       # Small adjustments for minor deviations
    "moderate": 10.0,   # Medium adjustments for moderate deviations
    "major": 15.0       # Significant adjustments for major deviations
}

# Bike component adjustment ranges (in cm or degrees)
ADJUSTMENT_RANGES = {
    "saddle_height": (0, 15),       # cm
    "saddle_fore_aft": (-5, 5),     # cm
    "handlebar_height": (0, 10),    # cm
    "handlebar_reach": (-5, 5),     # cm
    "stem_length": (6, 14),         # cm
    "stem_angle": (-45, 45)         # degrees
}

# Wizard settings
WIZARD_SETTINGS = {
    "window_title": "Bike Fit Analyzer Setup",
    "window_width": 800,
    "window_height": 600,
    "calibration_duration": 5,      # seconds
    "calibration_countdown": 3,     # seconds
    "calibration_frames": 15,       # frames to average for calibration
    "show_help_on_first_run": True
}

# File paths for saved settings and profiles
DEFAULT_PATHS = {
    "user_profiles": "user_profiles/",
    "bike_configs": "bike_configs/",
    "reports": "reports/",
    "recordings": "recordings/",
    "log_files": "logs/",
    "default_profile": "default_profile.json",
    "default_config": "default_config.json"
}

# Supported bike types with their default settings
BIKE_TYPES = {
    "road": {
        "name": "Road Bike",
        "default_angles": {
            "neck_angle": (65, 75),
            "shoulder_angle": (70, 90),
            "hip_angle": (65, 75),
            "knee_angle": (145, 155),
            "elbow_angle": (155, 165)
        },
        "description": "Performance-oriented road cycling position."
    },
    "mtb": {
        "name": "Mountain Bike",
        "default_angles": {
            "neck_angle": (70, 80),
            "shoulder_angle": (80, 100),
            "hip_angle": (75, 85),
            "knee_angle": (135, 145),
            "elbow_angle": (145, 155)
        },
        "description": "More upright position for off-road control."
    },
    "hybrid": {
        "name": "Hybrid/City Bike",
        "default_angles": {
            "neck_angle": (75, 85),
            "shoulder_angle": (90, 110),
            "hip_angle": (80, 100),
            "knee_angle": (135, 145),
            "elbow_angle": (145, 155)
        },
        "description": "Comfortable upright position for city riding."
    },
    "tt": {
        "name": "Time Trial/Triathlon Bike",
        "default_angles": {
            "neck_angle": (55, 65),
            "shoulder_angle": (60, 80),
            "hip_angle": (55, 65),
            "knee_angle": (145, 155),
            "elbow_angle": (155, 165)
        },
        "description": "Aggressive aerodynamic position for time trials."
    },
    "gravel": {
        "name": "Gravel Bike",
        "default_angles": {
            "neck_angle": (68, 78),
            "shoulder_angle": (75, 95),
            "hip_angle": (70, 80),
            "knee_angle": (140, 150),
            "elbow_angle": (150, 160)
        },
        "description": "Balanced position for mixed-terrain riding."
    }
}

# Default camera positions for different bike types
CAMERA_POSITIONS = {
    "road": "Place camera at saddle height, 3-4 meters to the side",
    "mtb": "Place camera at saddle height, 3-4 meters to the side",
    "hybrid": "Place camera at saddle height, 3-4 meters to the side",
    "tt": "Place camera at saddle height, 3-4 meters to the side, ensure aero position is visible",
    "gravel": "Place camera at saddle height, 3-4 meters to the side"
}

# Body measurement defaults (in cm)
DEFAULT_MEASUREMENTS = {
    "height": 175.0,
    "inseam": 80.0,
    "arm_length": 70.0,
    "torso_length": 60.0,
    "shoulder_width": 45.0
}

KOPS_SETTINGS = {
    "ideal_range": (-0.5, 0.5),  # cm forward/backward from pedal spindle
    "tolerance": 1.0,  # cm
    "visualization_color": (255, 0, 255)  # Magenta
}

SADDLE_SETBACK_SETTINGS = {
    "ideal_range_ratio": (5, 8),  # Percentage of saddle height
    "tolerance": 1.0,  # cm
    "visualization_color": (255, 165, 0)  # Orange
}

CLEAT_POSITION_SETTINGS = {
    "ideal_position_percent": (60, 70),  # Percentage from heel
    "tolerance": 2.0,  # percentage points
    "visualization_color": (0, 128, 255)  # Light blue
}

STACK_REACH_SETTINGS = {
    "visualization_colors": {
        "stack": (0, 255, 0),  # Green
        "reach": (255, 0, 0)   # Red
    }
}