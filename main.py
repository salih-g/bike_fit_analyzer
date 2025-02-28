"""
Main entry point for the Bike Fit Analyzer application.
Launches the GUI interface for the application.
"""
import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from bike_fit_analyzer.ui.main_window import MainWindow


def check_dependencies():
    """Check that all required dependencies are installed."""
    try:
        import cv2
        import mediapipe
        import numpy as np
        from PyQt5.QtWidgets import QApplication
    except ImportError as e:
        print(f"Error: Missing required dependency - {e}")
        print("Please install all dependencies with: pip install -r requirements.txt")
        return False
    
    return True


def main():
    """Main entry point for the application."""
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Create and start the application
    app = QApplication(sys.argv)
    app.setApplicationName("Bike Fit Analyzer")
    
    # Set app icon if available
    icon_path = os.path.join(os.path.dirname(__file__), "ui", "resources", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Start the event loop
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())