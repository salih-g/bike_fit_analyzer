"""
Bike adjustment recommendations based on pose analysis.
"""
from typing import Dict, List, Tuple, Optional
import numpy as np
from dataclasses import dataclass

from bike_fit_analyzer.models.angles import PoseData
from bike_fit_analyzer.models.bike_config import BikeConfig
from bike_fit_analyzer.models.user_profile import UserProfile
from bike_fit_analyzer.config.settings import IDEAL_ANGLES


@dataclass
class AdjustmentRecommendation:
    """Represents a bike adjustment recommendation."""
    component: str
    direction: str
    amount: float
    priority: int  # 1 (highest) to 5 (lowest)
    description: str
    angles_affected: List[str]


class BikeAdjustmentAnalyzer:
    """Analyzes pose data and provides bike adjustment recommendations."""
    
    def __init__(self, bike_config: Optional[BikeConfig] = None, user_profile: Optional[UserProfile] = None):
        """
        Initialize the bike adjustment analyzer.
        
        Args:
            bike_config: Bike configuration data
            user_profile: User profile data
        """
        self.bike_config = bike_config
        self.user_profile = user_profile
        
        # Define adjustment thresholds (in degrees)
        self.minor_threshold = 5.0
        self.moderate_threshold = 10.0
        self.major_threshold = 15.0
    
    def analyze_pose(self, pose_data: PoseData) -> List[AdjustmentRecommendation]:
        """
        Analyze pose data and generate adjustment recommendations.
        
        Args:
            pose_data: Processed pose data
            
        Returns:
            List of adjustment recommendations
        """
        recommendations = []
        
        # Extract angle values
        angles = pose_data.angle_values
        
        # Check each angle against ideal ranges
        for angle_type, angle_value in angles.items():
            if angle_type in IDEAL_ANGLES:
                min_val, max_val = IDEAL_ANGLES[angle_type]
                
                # Check if angle is outside ideal range
                if angle_value < min_val:
                    deviation = min_val - angle_value
                    recommendations.extend(self._generate_recommendations_for_low_angle(angle_type, deviation))
                elif angle_value > max_val:
                    deviation = angle_value - max_val
                    recommendations.extend(self._generate_recommendations_for_high_angle(angle_type, deviation))
        
        # Sort recommendations by priority
        recommendations.sort(key=lambda r: r.priority)
        
        return recommendations
    
    def _generate_recommendations_for_low_angle(self, angle_type: str, deviation: float) -> List[AdjustmentRecommendation]:
        """
        Generate recommendations for an angle that's too low.
        
        Args:
            angle_type: Type of angle
            deviation: Degrees below minimum ideal value
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Set priority based on deviation
        if deviation < self.minor_threshold:
            priority = 3
            amount_text = "slightly"
        elif deviation < self.moderate_threshold:
            priority = 2
            amount_text = "moderately"
        else:
            priority = 1
            amount_text = "significantly"
        
        # Generate recommendations based on angle type
        if angle_type == "neck_angle":
            recommendations.append(AdjustmentRecommendation(
                component="handlebar",
                direction="raise",
                amount=deviation,
                priority=priority,
                description=f"Raise handlebars {amount_text} to reduce neck flexion",
                angles_affected=["neck_angle", "shoulder_angle"]
            ))
            
            if priority < 3:  # Only suggest for moderate/major issues
                recommendations.append(AdjustmentRecommendation(
                    component="stem",
                    direction="shorten",
                    amount=deviation * 0.5,
                    priority=priority + 1,
                    description=f"Consider a shorter stem to bring handlebars closer",
                    angles_affected=["neck_angle", "shoulder_angle"]
                ))
        
        elif angle_type == "hip_angle":
            recommendations.append(AdjustmentRecommendation(
                component="saddle",
                direction="back",
                amount=deviation * 0.3,
                priority=priority,
                description=f"Move saddle {amount_text} backward to open hip angle",
                angles_affected=["hip_angle"]
            ))
            
            recommendations.append(AdjustmentRecommendation(
                component="handlebar",
                direction="raise",
                amount=deviation * 0.5,
                priority=priority,
                description=f"Raise handlebars {amount_text} to open hip angle",
                angles_affected=["hip_angle", "shoulder_angle"]
            ))
        
        elif angle_type == "knee_angle":
            recommendations.append(AdjustmentRecommendation(
                component="saddle",
                direction="raise",
                amount=deviation * 0.3,
                priority=priority,
                description=f"Raise saddle {amount_text} to increase knee extension",
                angles_affected=["knee_angle", "hip_angle"]
            ))
        
        elif angle_type == "shoulder_angle":
            recommendations.append(AdjustmentRecommendation(
                component="handlebar",
                direction="raise",
                amount=deviation * 0.5,
                priority=priority,
                description=f"Raise handlebars {amount_text} to open shoulder angle",
                angles_affected=["shoulder_angle", "neck_angle"]
            ))
        
        elif angle_type == "elbow_angle":
            recommendations.append(AdjustmentRecommendation(
                component="stem",
                direction="extend",
                amount=deviation * 0.3,
                priority=priority,
                description=f"Consider a longer stem to increase elbow extension",
                angles_affected=["elbow_angle", "shoulder_angle"]
            ))
        
        return recommendations
    
    def _generate_recommendations_for_high_angle(self, angle_type: str, deviation: float) -> List[AdjustmentRecommendation]:
        """
        Generate recommendations for an angle that's too high.
        
        Args:
            angle_type: Type of angle
            deviation: Degrees above maximum ideal value
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Set priority based on deviation
        if deviation < self.minor_threshold:
            priority = 3
            amount_text = "slightly"
        elif deviation < self.moderate_threshold:
            priority = 2
            amount_text = "moderately"
        else:
            priority = 1
            amount_text = "significantly"
        
        # Generate recommendations based on angle type
        if angle_type == "neck_angle":
            recommendations.append(AdjustmentRecommendation(
                component="handlebar",
                direction="lower",
                amount=deviation,
                priority=priority,
                description=f"Lower handlebars {amount_text} to increase neck flexion",
                angles_affected=["neck_angle", "shoulder_angle"]
            ))
        
        elif angle_type == "hip_angle":
            recommendations.append(AdjustmentRecommendation(
                component="saddle",
                direction="forward",
                amount=deviation * 0.3,
                priority=priority,
                description=f"Move saddle {amount_text} forward to close hip angle",
                angles_affected=["hip_angle"]
            ))
            
            if priority < 3:  # Only suggest for moderate/major issues
                recommendations.append(AdjustmentRecommendation(
                    component="handlebar",
                    direction="lower",
                    amount=deviation * 0.5,
                    priority=priority,
                    description=f"Lower handlebars {amount_text} to close hip angle",
                    angles_affected=["hip_angle", "shoulder_angle"]
                ))
        
        elif angle_type == "knee_angle":
            recommendations.append(AdjustmentRecommendation(
                component="saddle",
                direction="lower",
                amount=deviation * 0.3,
                priority=priority,
                description=f"Lower saddle {amount_text} to reduce knee extension",
                angles_affected=["knee_angle", "hip_angle"]
            ))
        
        elif angle_type == "shoulder_angle":
            recommendations.append(AdjustmentRecommendation(
                component="handlebar",
                direction="lower",
                amount=deviation * 0.5,
                priority=priority,
                description=f"Lower handlebars {amount_text} to close shoulder angle",
                angles_affected=["shoulder_angle", "neck_angle"]
            ))
            
            if priority < 3:  # Only suggest for moderate/major issues
                recommendations.append(AdjustmentRecommendation(
                    component="stem",
                    direction="extend",
                    amount=deviation * 0.3,
                    priority=priority + 1,
                    description=f"Consider a longer stem to increase reach",
                    angles_affected=["shoulder_angle"]
                ))
        
        elif angle_type == "elbow_angle":
            recommendations.append(AdjustmentRecommendation(
                component="stem",
                direction="shorten",
                amount=deviation * 0.3,
                priority=priority,
                description=f"Consider a shorter stem to decrease elbow extension",
                angles_affected=["elbow_angle", "shoulder_angle"]
            ))
        
        return recommendations

