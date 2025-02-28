"""
Bike configuration data model.
"""
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any
import json


@dataclass
class BikeType:
    """Represents a type of bike with default fit parameters."""
    
    name: str
    default_angles: Dict[str, tuple]
    description: str
    
    @classmethod
    def get_bike_types(cls) -> Dict[str, 'BikeType']:
        """Get a dictionary of available bike types."""
        return {
            "road": cls(
                name="Road Bike",
                default_angles={
                    "neck_angle": (65, 75),
                    "shoulder_angle": (70, 90),
                    "hip_angle": (65, 75),
                    "knee_angle": (145, 155),
                    "elbow_angle": (155, 165)
                },
                description="Performance-oriented road cycling position."
            ),
            "mtb": cls(
                name="Mountain Bike",
                default_angles={
                    "neck_angle": (70, 80),
                    "shoulder_angle": (80, 100),
                    "hip_angle": (75, 85),
                    "knee_angle": (135, 145),
                    "elbow_angle": (145, 155)
                },
                description="More upright position for off-road control."
            ),
            "hybrid": cls(
                name="Hybrid/City Bike",
                default_angles={
                    "neck_angle": (75, 85),
                    "shoulder_angle": (90, 110),
                    "hip_angle": (80, 100),
                    "knee_angle": (135, 145),
                    "elbow_angle": (145, 155)
                },
                description="Comfortable upright position for city riding."
            ),
            "tt": cls(
                name="Time Trial/Triathlon Bike",
                default_angles={
                    "neck_angle": (55, 65),
                    "shoulder_angle": (60, 80),
                    "hip_angle": (55, 65),
                    "knee_angle": (145, 155),
                    "elbow_angle": (155, 165)
                },
                description="Aggressive aerodynamic position for time trials."
            ),
            "gravel": cls(
                name="Gravel Bike",
                default_angles={
                    "neck_angle": (68, 78),
                    "shoulder_angle": (75, 95),
                    "hip_angle": (70, 80),
                    "knee_angle": (140, 150),
                    "elbow_angle": (150, 160)
                },
                description="Balanced position for mixed-terrain riding."
            )
        }


@dataclass
class BikeConfig:
    """Configuration data for a specific bike."""
    
    # Bike info
    bike_name: str = ""
    bike_type: str = "road"  # road, mtb, hybrid, tt, gravel
    
    # Bike measurements (in cm)
    saddle_height: float = 0.0
    saddle_setback: float = 0.0
    stack: float = 0.0
    reach: float = 0.0
    crank_length: float = 17.5
    stem_length: float = 10.0
    handlebar_width: float = 42.0
    
    # Customized angle preferences
    custom_angles: Dict[str, tuple] = field(default_factory=dict)
    
    # Notes and additional info
    notes: str = ""
    
    def save_to_file(self, file_path: str):
        """
        Save bike configuration to a JSON file.
        
        Args:
            file_path: Path to save the file
        """
        with open(file_path, 'w') as f:
            json.dump(asdict(self), f, indent=2)
    
    def load_from_file(self, file_path: str):
        """
        Load bike configuration from a JSON file.
        
        Args:
            file_path: Path to the file to load
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
            
            # Update instance attributes
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
    
    def get_angle_ranges(self) -> Dict[str, tuple]:
        """
        Get the angle ranges for this bike configuration.
        
        Returns:
            Dictionary of angle ranges
        """
        # Get default angles for the bike type
        bike_types = BikeType.get_bike_types()
        if self.bike_type in bike_types:
            default_angles = bike_types[self.bike_type].default_angles
        else:
            # Fallback to road bike defaults
            default_angles = bike_types["road"].default_angles
        
        # Override with custom angles
        angle_ranges = default_angles.copy()
        angle_ranges.update(self.custom_angles)
        
        return angle_ranges