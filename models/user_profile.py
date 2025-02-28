"""
User profile data model for storing user measurements and preferences.
"""
import json
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any


@dataclass
class UserProfile:
    """User profile data for bike fit analysis."""
    
    # User information
    name: str = ""
    age: int = 0
    gender: str = ""
    
    # Body measurements (in cm)
    height: float = 0.0
    weight: float = 0.0
    inseam: float = 0.0
    arm_length: float = 0.0
    torso_length: float = 0.0
    shoulder_width: float = 0.0
    
    # Flexibility and experience
    flexibility: str = "medium"  # low, medium, high
    experience_level: str = "intermediate"  # beginner, intermediate, advanced
    
    # Riding preferences
    ride_type: List[str] = field(default_factory=lambda: ["recreational"])
    goals: List[str] = field(default_factory=lambda: ["comfort", "endurance"])
    
    # History of issues
    reported_issues: List[str] = field(default_factory=list)
    
    # Fit history
    fit_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def save_to_file(self, file_path: str):
        """
        Save user profile to a JSON file.
        
        Args:
            file_path: Path to save the file
        """
        with open(file_path, 'w') as f:
            json.dump(asdict(self), f, indent=2)
    
    def load_from_file(self, file_path: str):
        """
        Load user profile from a JSON file.
        
        Args:
            file_path: Path to the file to load
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
            
            # Update instance attributes
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
    
    def add_fit_session(self, session_data: Dict[str, Any]):
        """
        Add a fit session to the history.
        
        Args:
            session_data: Data from a fit session
        """
        # Add timestamp if not present
        if "timestamp" not in session_data:
            from datetime import datetime
            session_data["timestamp"] = datetime.now().isoformat()
            
        self.fit_history.append(session_data)
