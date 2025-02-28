"""
Configuration settings for the Bike Fit Analyzer application.
"""
import cv2

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
    "highlight": (0, 255, 255)     # Cyan
}

# Font and drawing settings
FONT = cv2.FONT_HERSHEY_SIMPLEX
LINE_THICKNESS = 2
POINT_RADIUS = 5

# Camera settings
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

# MediaPipe Pose settings
POSE_MODEL_COMPLEXITY = 2
MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5
