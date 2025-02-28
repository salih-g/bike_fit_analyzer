"""
UI rendering for the Bike Fit Analyzer.
"""
import cv2


class UIRenderer:
    """Handles UI rendering and user interaction."""
    
    def __init__(self, window_name="Bike Fit Analyzer"):
        """Initialize the UI renderer."""
        self.window_name = window_name
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        self._print_controls()
    
    def _print_controls(self):
        """Print control instructions to the console."""
        print("\nControls:")
        print("- Press 'q' to quit")
        print("- Press 'm' to toggle mirror mode")
        print("- Press 'c' to change camera\n")
    
    def show_frame(self, frame):
        """Show a frame in the window."""
        cv2.imshow(self.window_name, frame)
    
    def get_key_press(self):
        """Get key press from the user."""
        return cv2.waitKey(1) & 0xFF
    
    def cleanup(self):
        """Clean up resources."""
        cv2.destroyAllWindows()

