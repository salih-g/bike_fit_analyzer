# Bike Fit Analyzer

An advanced bicycle fit analysis and guidance system using computer vision to provide real-time feedback on cycling posture and bike adjustments.

## Features

- **Real-time Pose Analysis**: Analyzes the cyclist's body position using MediaPipe pose detection
- **Interactive GUI**: User-friendly interface with real-time visualization and controls
- **Guidance System**: Provides visual cues and adjustment recommendations
- **Setup Wizard**: Step-by-step guide for initial configuration and calibration
- **Multiple Bike Types**: Supports different bike types with appropriate fit parameters
- **User Profiles**: Save and load user measurements and preferences
- **Visual Guidance**: Directional arrows and target pose overlays to guide adjustments
- **Comprehensive Reporting**: Generates detailed fit reports with recommendations

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenCV
- MediaPipe
- PyQt5
- NumPy

### Install from source

```bash
# Clone the repository
git clone https://github.com/username/bike_fit_analyzer.git
cd bike_fit_analyzer

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Usage

### Running the application

```bash
# Run the application directly
python -m bike_fit_analyzer.main

# Or use the installed entry point
bike-fit-analyzer
```

### Setup Wizard

1. Launch the application
2. The setup wizard will guide you through the process:
   - Camera setup and positioning
   - User measurements input
   - Bike configuration
   - Calibration process

### Analyzing Your Bike Fit

1. Position your camera for a side view of your bike
2. Sit on your bike in your normal riding position
3. Start the camera and analysis
4. Follow the guidance for optimal adjustments

## Project Structure

```
bike_fit_analyzer/
├── __init__.py
├── main.py                  # Entry point
├── config/                  # Configuration settings
├── core/                    # Core analysis functionality
├── utils/                   # Utility functions
├── ui/                      # User interface components
├── wizard/                  # Setup wizard
├── guidance/                # Adjustment guidance system
└── models/                  # Data models
```

## Keyboard Controls

- Press `q` to quit
- Press `m` to toggle mirror mode
- Press `c` to change camera

## License

MIT License

## Acknowledgments

- MediaPipe for the pose detection framework
- OpenCV for computer vision capabilities
- PyQt5 for the graphical interface
