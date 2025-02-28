"""
User feedback system for bike fit adjustment guidance.
"""
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from bike_fit_analyzer.models.angles import PoseData
from bike_fit_analyzer.guidance.bike_adjustments import AdjustmentRecommendation


@dataclass
class FeedbackItem:
    """Represents a feedback item for the user."""
    message: str
    type: str  # 'info', 'warning', 'success', 'error'
    priority: int  # 1 (highest) to 5 (lowest)


class FeedbackGenerator:
    """Generates user feedback for bike fit adjustments."""
    
    def __init__(self):
        """Initialize the feedback generator."""
        pass
    
    def generate_feedback(self, pose_data: PoseData, 
                         adjustments: List[AdjustmentRecommendation]) -> List[FeedbackItem]:
        """
        Generate user feedback based on pose data and adjustment recommendations.
        
        Args:
            pose_data: Processed pose data
            adjustments: List of adjustment recommendations
            
        Returns:
            List of feedback items
        """
        feedback_items = []
        
        # If no adjustments needed, provide positive feedback
        if not adjustments:
            feedback_items.append(FeedbackItem(
                message="Great job! Your bike fit looks good. All angles are within ideal ranges.",
                type="success",
                priority=1
            ))
            return feedback_items
        
        # Check for high priority adjustments
        high_priority_adjustments = [adj for adj in adjustments if adj.priority == 1]
        if high_priority_adjustments:
            feedback_items.append(FeedbackItem(
                message="Your bike fit needs significant adjustment. Follow the recommendations to improve comfort and performance.",
                type="warning",
                priority=1
            ))
        else:
            feedback_items.append(FeedbackItem(
                message="Your bike fit is close to ideal. Some minor adjustments are recommended.",
                type="info",
                priority=1
            ))
        
        # Group adjustments by component
        component_adjustments = {}
        for adjustment in adjustments:
            component = adjustment.component
            if component not in component_adjustments:
                component_adjustments[component] = []
            component_adjustments[component].append(adjustment)
        
        # Generate feedback for each component
        for component, adj_list in component_adjustments.items():
            # Get highest priority adjustment for this component
            adjustment = min(adj_list, key=lambda x: x.priority)
            
            # Create feedback message
            message = f"{component.title()}: {adjustment.description}"
            
            # Determine message type based on priority
            if adjustment.priority == 1:
                msg_type = "warning"
            elif adjustment.priority == 2:
                msg_type = "warning"
            else:
                msg_type = "info"
            
            feedback_items.append(FeedbackItem(
                message=message,
                type=msg_type,
                priority=adjustment.priority
            ))
        
        # Add general feedback on posture
        angles = pose_data.angle_values
        
        # Check for specific postural issues
        if "neck_angle" in angles and angles["neck_angle"] < 65:
            feedback_items.append(FeedbackItem(
                message="Your neck is excessively flexed, which may cause neck strain. Try raising your handlebars.",
                type="warning",
                priority=2
            ))
        
        if "hip_angle" in angles and angles["hip_angle"] < 65:
            feedback_items.append(FeedbackItem(
                message="Your hip angle is very closed, which may reduce power. Try adjusting your saddle position.",
                type="warning",
                priority=2
            ))
        
        if "knee_angle" in angles and angles["knee_angle"] > 170:
            feedback_items.append(FeedbackItem(
                message="Your knee is nearly locked at full extension, which may cause knee pain. Lower your saddle slightly.",
                type="warning",
                priority=2
            ))
        
        # Add performance tips
        feedback_items.append(FeedbackItem(
            message="Tip: Remember to pedal with a smooth, circular motion and engage your core muscles.",
            type="info",
            priority=5
        ))
        
        # Sort feedback by priority
        feedback_items.sort(key=lambda item: item.priority)
        
        return feedback_items
    
    def generate_summary(self, pose_data: PoseData, 
                        adjustments: List[AdjustmentRecommendation]) -> str:
        """
        Generate a summary of bike fit analysis.
        
        Args:
            pose_data: Processed pose data
            adjustments: List of adjustment recommendations
            
        Returns:
            Summary text
        """
        # Get feedback items
        feedback_items = self.generate_feedback(pose_data, adjustments)
        
        # Create summary text
        summary = "Bike Fit Analysis Summary\n"
        summary += "========================\n\n"
        
        # Add overall assessment
        if not adjustments:
            summary += "Overall: Excellent bike fit! All angles are within ideal ranges.\n\n"
        elif any(adj.priority == 1 for adj in adjustments):
            summary += "Overall: Significant adjustments needed to optimize your bike fit.\n\n"
        else:
            summary += "Overall: Good bike fit with some minor adjustments recommended.\n\n"
        
        # Add angle measurements
        summary += "Angle Measurements:\n"
        summary += "------------------\n"
        
        angles = pose_data.angle_values
        from bike_fit_analyzer.config.settings import IDEAL_ANGLES
        
        for angle_type, angle_value in angles.items():
            if angle_type in IDEAL_ANGLES:
                min_val, max_val = IDEAL_ANGLES[angle_type]
                status = "✓" if min_val <= angle_value <= max_val else "✗"
                summary += f"{angle_type.replace('_', ' ').title()}: {angle_value:.1f}° {status} (Ideal: {min_val}°-{max_val}°)\n"
        
        summary += "\n"
        
        # Add recommendations
        if adjustments:
            summary += "Recommendations:\n"
            summary += "---------------\n"
            
            for i, adjustment in enumerate(adjustments[:5]):  # Top 5 recommendations
                summary += f"{i+1}. {adjustment.description}\n"
            
            summary += "\n"
        
        # Add general tips
        summary += "General Tips:\n"
        summary += "------------\n"
        summary += "1. Small adjustments can make a big difference in comfort and performance.\n"
        summary += "2. After making adjustments, ride for a short time to assess comfort before making further changes.\n"
        summary += "3. Consider a professional bike fit for precise measurements and personalized guidance.\n"
        
        return summary