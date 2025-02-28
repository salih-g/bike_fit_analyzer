"""
Data models for angle-related data structures.
"""
from dataclasses import dataclass
from typing import Tuple, Dict, List


@dataclass
class Point:
    """Represents a 2D point with x, y coordinates."""
    x: int
    y: int
    
    def as_tuple(self) -> Tuple[int, int]:
        """Return the point as a tuple."""
        return (self.x, self.y)


@dataclass
class Angle:
    """Represents an angle with value and type."""
    value: float
    angle_type: str
    point_a: Point
    point_b: Point
    point_c: Point
    
    def is_in_range(self, ideal_ranges: Dict[str, Tuple[float, float]]) -> bool:
        """Check if the angle is within the ideal range."""
        if self.angle_type in ideal_ranges:
            min_val, max_val = ideal_ranges[self.angle_type]
            return min_val <= self.value <= max_val
        return False


@dataclass
class PoseData:
    """Represents processed pose data with landmarks and angles."""
    landmarks: Dict[str, Point]
    angles: Dict[str, Angle]
    
    @property
    def angle_values(self) -> Dict[str, float]:
        """Get a dictionary of angle values."""
        return {angle_type: angle.value for angle_type, angle in self.angles.items()}

