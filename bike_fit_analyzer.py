import cv2
import mediapipe as mp
import numpy as np
import time
import os

class BikeFitAnalyzer:
    def __init__(self):
        # Initialize MediaPipe Pose model
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Define ideal angle ranges from the diagram
        self.ideal_angles = {
            "neck_angle": (65, 75),      # 65°-75°
            "shoulder_angle": (60, 110), # 60°-110°
            "hip_angle": (65, 145),      # 65°-145°
            "knee_angle": (115, 180),    # 115°-180°
            "elbow_angle": (150, 160)    # 150°-160°
        }
        
        # Colors for visualization
        self.colors = {
            "in_range": (0, 255, 0),       # Green
            "out_of_range": (0, 0, 255),   # Red
            "text_color": (255, 255, 0),   # Yellow
            "line_color": (255, 0, 0),     # Red
            "highlight": (0, 255, 255)     # Cyan
        }
        
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.line_thickness = 2
        self.point_radius = 5
        
        # For FPS calculation
        self.prev_time = 0
        self.current_time = 0
        
        # Available cameras
        self.available_cameras = self.find_available_cameras()

    def find_available_cameras(self):
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

    def list_cameras(self):
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

    def select_camera(self):
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

    def calculate_angle(self, a, b, c):
        """Calculate the angle between three points."""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle

    def is_in_range(self, angle, angle_type):
        """Check if an angle is within the ideal range."""
        if angle_type in self.ideal_angles:
            min_val, max_val = self.ideal_angles[angle_type]
            return min_val <= angle <= max_val
        return False

    def get_color(self, angle, angle_type):
        """Get color based on whether angle is in ideal range."""
        if self.is_in_range(angle, angle_type):
            return self.colors["in_range"]
        return self.colors["out_of_range"]

    def draw_angle_arc(self, image, point_a, point_b, point_c, angle, angle_type):
        """Draw an arc to visualize the angle."""
        # Calculate midpoint between points a and c
        radius = int(np.linalg.norm(np.array(point_b) - np.array(point_a)) * 0.3)
        
        # Calculate angles for arc
        vector1 = np.array([point_a[0] - point_b[0], point_a[1] - point_b[1]])
        vector2 = np.array([point_c[0] - point_b[0], point_c[1] - point_b[1]])
        
        angle1 = np.arctan2(vector1[1], vector1[0]) * 180 / np.pi
        angle2 = np.arctan2(vector2[1], vector2[0]) * 180 / np.pi
        
        # Ensure angles are in the proper range
        start_angle = (min(angle1, angle2) + 360) % 360
        end_angle = (max(angle1, angle2) + 360) % 360
        
        # Swap if we need to draw the minor arc
        if end_angle - start_angle > 180:
            start_angle, end_angle = end_angle, start_angle + 360
            
        color = self.get_color(angle, angle_type)
            
        # Draw the arc
        cv2.ellipse(image, point_b, (radius, radius), 0, start_angle, end_angle, color, 2)
        
        # Position for the text
        text_offset_x = radius * np.cos(np.radians((start_angle + end_angle) / 2))
        text_offset_y = radius * np.sin(np.radians((start_angle + end_angle) / 2))
        text_position = (
            int(point_b[0] + 1.2 * text_offset_x), 
            int(point_b[1] + 1.2 * text_offset_y)
        )
        
        # Add the angle text
        cv2.putText(image, f"{angle:.1f}°", text_position, 
                   self.font, 0.6, self.colors["text_color"], 2)

    def process_frame(self, frame):
        """Process a single frame and calculate bike fit metrics."""
        # Convert the BGR image to RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the image and detect pose
        results = self.pose.process(image_rgb)
        
        # Draw pose landmarks
        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame, 
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2)
            )
            
            # Extract landmarks
            landmarks = results.pose_landmarks.landmark
            
            # Define landmark indices for each joint
            # For the right side of the body (assuming side view)
            nose = (int(landmarks[self.mp_pose.PoseLandmark.NOSE].x * frame.shape[1]),
                   int(landmarks[self.mp_pose.PoseLandmark.NOSE].y * frame.shape[0]))
            
            right_shoulder = (int(landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].x * frame.shape[1]),
                             int(landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].y * frame.shape[0]))
            
            right_elbow = (int(landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW].x * frame.shape[1]),
                          int(landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW].y * frame.shape[0]))
            
            right_wrist = (int(landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST].x * frame.shape[1]),
                          int(landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST].y * frame.shape[0]))
            
            right_hip = (int(landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP].x * frame.shape[1]),
                        int(landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP].y * frame.shape[0]))
            
            right_knee = (int(landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE].x * frame.shape[1]),
                         int(landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE].y * frame.shape[0]))
            
            right_ankle = (int(landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE].x * frame.shape[1]),
                          int(landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE].y * frame.shape[0]))
            
            # Left side landmarks as fallback
            left_shoulder = (int(landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER].x * frame.shape[1]),
                            int(landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER].y * frame.shape[0]))
            
            left_elbow = (int(landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW].x * frame.shape[1]),
                         int(landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW].y * frame.shape[0]))
            
            left_wrist = (int(landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST].x * frame.shape[1]),
                         int(landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST].y * frame.shape[0]))
            
            left_hip = (int(landmarks[self.mp_pose.PoseLandmark.LEFT_HIP].x * frame.shape[1]),
                       int(landmarks[self.mp_pose.PoseLandmark.LEFT_HIP].y * frame.shape[0]))
            
            left_knee = (int(landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE].x * frame.shape[1]),
                        int(landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE].y * frame.shape[0]))
            
            left_ankle = (int(landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE].x * frame.shape[1]),
                         int(landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE].y * frame.shape[0]))
            
            # Determine which side is more visible (for side view analysis)
            right_visibility = (landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].visibility +
                               landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP].visibility +
                               landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE].visibility)
            
            left_visibility = (landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER].visibility +
                              landmarks[self.mp_pose.PoseLandmark.LEFT_HIP].visibility +
                              landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE].visibility)
            
            # Use the more visible side
            if right_visibility > left_visibility:
                shoulder = right_shoulder
                elbow = right_elbow
                wrist = right_wrist
                hip = right_hip
                knee = right_knee
                ankle = right_ankle
            else:
                shoulder = left_shoulder
                elbow = left_elbow
                wrist = left_wrist
                hip = left_hip
                knee = left_knee
                ankle = left_ankle
            
            # Calculate angles
            # Neck angle (between nose, shoulder, and hip)
            neck_angle = self.calculate_angle(nose, shoulder, hip)
            
            # Shoulder angle (between hip, shoulder, and elbow)
            shoulder_angle = self.calculate_angle(hip, shoulder, elbow)
            
            # Elbow angle (between shoulder, elbow, and wrist)
            elbow_angle = self.calculate_angle(shoulder, elbow, wrist)
            
            # Hip angle (between shoulder, hip, and knee)
            hip_angle = self.calculate_angle(shoulder, hip, knee)
            
            # Knee angle (between hip, knee, and ankle)
            knee_angle = self.calculate_angle(hip, knee, ankle)
            
            # Draw key points
            key_points = [nose, shoulder, elbow, wrist, hip, knee, ankle]
            for point in key_points:
                cv2.circle(frame, point, self.point_radius, self.colors["highlight"], -1)
            
            # Draw connecting lines
            connections = [(nose, shoulder), (shoulder, elbow), (elbow, wrist), 
                          (shoulder, hip), (hip, knee), (knee, ankle)]
            for connection in connections:
                cv2.line(frame, connection[0], connection[1], self.colors["line_color"], self.line_thickness)
            
            # Draw angles with arcs
            self.draw_angle_arc(frame, nose, shoulder, hip, neck_angle, "neck_angle")
            self.draw_angle_arc(frame, hip, shoulder, elbow, shoulder_angle, "shoulder_angle")
            self.draw_angle_arc(frame, shoulder, elbow, wrist, elbow_angle, "elbow_angle")
            self.draw_angle_arc(frame, shoulder, hip, knee, hip_angle, "hip_angle")
            self.draw_angle_arc(frame, hip, knee, ankle, knee_angle, "knee_angle")
            
            # Add ideal angle ranges as reference
            y_offset = 30
            for i, (angle_type, (min_val, max_val)) in enumerate(self.ideal_angles.items()):
                text = f"{angle_type.replace('_', ' ').title()}: {min_val}°-{max_val}°"
                cv2.putText(frame, text, (10, y_offset + i * 30), 
                           self.font, 0.6, self.colors["text_color"], 2)
        
        # Calculate and display FPS
        self.current_time = time.time()
        fps = 1 / (self.current_time - self.prev_time) if (self.current_time - self.prev_time) > 0 else 0
        self.prev_time = self.current_time
        
        cv2.putText(frame, f"FPS: {int(fps)}", (10, frame.shape[0] - 10), 
                   self.font, 0.7, self.colors["text_color"], 2)
        
        return frame

    def run(self, camera_id=None, mirror=True):
        """Run the bike fit analyzer using the specified camera."""
        # If no camera_id provided, prompt for selection
        if camera_id is None:
            camera_id = self.select_camera()
        
        print(f"Opening camera {camera_id}...")
        
        # Try different methods to open the camera (especially for macOS)
        cap = None
        
        # Try standard method first
        cap = cv2.VideoCapture(camera_id)
        
        # If that doesn't work and we're on macOS, try AVFoundation backend
        if not cap.isOpened() and os.name == 'posix' and os.uname().sysname == 'Darwin':
            print("Trying AVFoundation backend for macOS...")
            cap = cv2.VideoCapture(camera_id, cv2.CAP_AVFOUNDATION)
        
        # Check if camera opened successfully
        if not cap.isOpened():
            print(f"Failed to open camera {camera_id}. Please try another camera.")
            return
        
        # Set camera resolution (adjust as needed)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # Create window
        window_name = "Bike Fit Analyzer"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        print("\nControls:")
        print("- Press 'q' to quit")
        print("- Press 'm' to toggle mirror mode")
        print("- Press 'c' to change camera\n")
        
        current_mirror = mirror
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to receive frame from camera.")
                break
            
            # Mirror the image if requested
            if current_mirror:
                frame = cv2.flip(frame, 1)
            
            # Process the frame
            output_frame = self.process_frame(frame)
            
            # Show the result
            cv2.imshow(window_name, output_frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('m'):
                current_mirror = not current_mirror
                print(f"Mirror mode: {'On' if current_mirror else 'Off'}")
            elif key == ord('c'):
                # Clean up current camera
                cap.release()
                
                # Select a new camera
                new_camera_id = self.select_camera()
                
                # Try to open the new camera
                cap = cv2.VideoCapture(new_camera_id)
                if not cap.isOpened() and os.name == 'posix' and os.uname().sysname == 'Darwin':
                    cap = cv2.VideoCapture(new_camera_id, cv2.CAP_AVFOUNDATION)
                
                if not cap.isOpened():
                    print(f"Failed to open camera {new_camera_id}. Trying to revert to camera {camera_id}.")
                    cap = cv2.VideoCapture(camera_id)
                    if not cap.isOpened() and os.name == 'posix' and os.uname().sysname == 'Darwin':
                        cap = cv2.VideoCapture(camera_id, cv2.CAP_AVFOUNDATION)
                else:
                    camera_id = new_camera_id
                    print(f"Switched to camera {camera_id}")
                
                # Set camera resolution
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # Clean up
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    analyzer = BikeFitAnalyzer()
    # No camera_id is provided, so it will prompt for selection
    analyzer.run(mirror=True)