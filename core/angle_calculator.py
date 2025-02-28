"""
Angle calculation utilities for the Bike Fit Analyzer.
"""
import numpy as np
from typing import Tuple
from bike_fit_analyzer.models.angles import Point, Angle


def calculate_angle(a: Point, b: Point, c: Point) -> float:
    """
    Calculate the angle between three points.
    
    Args:
        a: First point
        b: Second point (vertex)
        c: Third point
        
    Returns:
        The angle in degrees
    """
    a_arr = np.array([a.x, a.y])
    b_arr = np.array([b.x, b.y])
    c_arr = np.array([c.x, c.y])
    
    radians = np.arctan2(c_arr[1] - b_arr[1], c_arr[0] - b_arr[0]) - np.arctan2(a_arr[1] - b_arr[1], a_arr[0] - b_arr[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle


def create_angle(a: Point, b: Point, c: Point, angle_type: str) -> Angle:
    """
    Create an Angle object from three points.
    
    Args:
        a: First point
        b: Second point (vertex)
        c: Third point
        angle_type: Type of angle (e.g., "neck_angle")
        
    Returns:
        An Angle object
    """
    angle_value = calculate_angle(a, b, c)
    return Angle(value=angle_value, angle_type=angle_type, point_a=a, point_b=b, point_c=c)
