"""
Pose detection logic for the Bike Fit Analyzer.
"""
import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, Tuple, Optional, List

from bike_fit_analyzer.models.angles import Point, Angle, PoseData
from bike_fit_analyzer.core.angle_calculator import create_angle
from bike_fit_analyzer.config.settings import (
    POSE_MODEL_COMPLEXITY,
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE
)


class PoseDetector:
    """Handles pose detection and landmark processing."""
    
    def __init__(self):
        """Initialize the pose detector."""
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=POSE_MODEL_COMPLEXITY,
            smooth_landmarks=True,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE
        )
    
    def detect_pose(self, frame: np.ndarray) -> Tuple[np.ndarray, Optional[PoseData]]:
        """
        Detect pose in the given frame.
        
        Args:
            frame: Input frame
            
        Returns:
            Tuple of (processed frame with landmarks drawn, pose data)
        """
        # Convert the BGR image to RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the image and detect pose
        results = self.pose.process(image_rgb)
        
        # Draw pose landmarks on the frame
        processed_frame = frame.copy()
        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                processed_frame, 
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2)
            )
            
            # Extract landmarks and calculate angles
            pose_data = self._process_landmarks(results.pose_landmarks, frame.shape)
            return processed_frame, pose_data
        
        return processed_frame, None
    
    def _process_landmarks(self, pose_landmarks, frame_shape: Tuple[int, int, int]) -> PoseData:
        """
        Process the pose landmarks and calculate angles.
        
        Args:
            pose_landmarks: MediaPipe pose landmarks
            frame_shape: Shape of the frame (height, width, channels)
            
        Returns:
            PoseData object containing landmarks and angles
        """
        landmarks = pose_landmarks.landmark
        height, width, _ = frame_shape
        
        # Extract key points
        points = {
            "nose": Point(
                x=int(landmarks[self.mp_pose.PoseLandmark.NOSE].x * width),
                y=int(landmarks[self.mp_pose.PoseLandmark.NOSE].y * height)
            ),
            "right_shoulder": Point(
                x=int(landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].x * width),
                y=int(landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].y * height)
            ),
            "right_elbow": Point(
                x=int(landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW].x * width),
                y=int(landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW].y * height)
            ),
            "right_wrist": Point(
                x=int(landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST].x * width),
                y=int(landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST].y * height)
            ),
            "right_hip": Point(
                x=int(landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP].x * width),
                y=int(landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP].y * height)
            ),
            "right_knee": Point(
                x=int(landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE].x * width),
                y=int(landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE].y * height)
            ),
            "right_ankle": Point(
                x=int(landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE].x * width),
                y=int(landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE].y * height)
            ),
            "left_shoulder": Point(
                x=int(landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER].x * width),
                y=int(landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER].y * height)
            ),
            "left_elbow": Point(
                x=int(landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW].x * width),
                y=int(landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW].y * height)
            ),
            "left_wrist": Point(
                x=int(landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST].x * width),
                y=int(landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST].y * height)
            ),
            "left_hip": Point(
                x=int(landmarks[self.mp_pose.PoseLandmark.LEFT_HIP].x * width),
                y=int(landmarks[self.mp_pose.PoseLandmark.LEFT_HIP].y * height)
            ),
            "left_knee": Point(
                x=int(landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE].x * width),
                y=int(landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE].y * height)
            ),
            "left_ankle": Point(
                x=int(landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE].x * width),
                y=int(landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE].y * height)
            )
        }
        
        # Determine which side is more visible (for side view analysis)
        right_visibility = (
            landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].visibility +
            landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP].visibility +
            landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE].visibility
        )
        
        left_visibility = (
            landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER].visibility +
            landmarks[self.mp_pose.PoseLandmark.LEFT_HIP].visibility +
            landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE].visibility
        )
        
        # Select the more visible side
        if right_visibility > left_visibility:
            shoulder = points["right_shoulder"]
            elbow = points["right_elbow"]
            wrist = points["right_wrist"]
            hip = points["right_hip"]
            knee = points["right_knee"]
            ankle = points["right_ankle"]
        else:
            shoulder = points["left_shoulder"]
            elbow = points["left_elbow"]
            wrist = points["left_wrist"]
            hip = points["left_hip"]
            knee = points["left_knee"]
            ankle = points["left_ankle"]
        
        # Calculate angles
        angles = {
            "neck_angle": create_angle(points["nose"], shoulder, hip, "neck_angle"),
            "shoulder_angle": create_angle(hip, shoulder, elbow, "shoulder_angle"),
            "elbow_angle": create_angle(shoulder, elbow, wrist, "elbow_angle"),
            "hip_angle": create_angle(shoulder, hip, knee, "hip_angle"),
            "knee_angle": create_angle(hip, knee, ankle, "knee_angle")
        }
        
        # Create selected points dictionary for visualization
        selected_points = {
            "nose": points["nose"],
            "shoulder": shoulder,
            "elbow": elbow,
            "wrist": wrist,
            "hip": hip,
            "knee": knee,
            "ankle": ankle
        }
        
        return PoseData(landmarks=selected_points, angles=angles)

