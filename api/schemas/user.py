from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import uuid

class UserCreate(BaseModel):
    """Schema for creating a new user (without userId)"""
    name: str = Field(..., min_length=2, max_length=50, description="User's full name")
    email: Optional[str] = Field(None, description="User's email address")
    age: int = Field(..., gt=0, le=120, description="Age in years")
    weight: float = Field(..., gt=0, le=500, description="Weight in kg")
    height: float = Field(..., gt=0, le=300, description="Height in cm")
    gender: str = Field(..., description="Gender (male/female/other)")
    activity_level: Optional[str] = Field(default="moderate", description="Activity level")
    goal: Optional[str] = Field(default="maintain", description="Fitness goal")
    
    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v):
        if v.lower() not in ['male', 'female', 'other']:
            raise ValueError('Gender must be either "male", "female", or "other"')
        return v.lower()
    
    @field_validator('activity_level')
    @classmethod
    def validate_activity_level(cls, v):
        valid_levels = ['sedentary', 'light', 'moderate', 'active', 'very_active']
        if v and v.lower() not in valid_levels:
            raise ValueError(f'Activity level must be one of: {valid_levels}')
        return v.lower() if v else 'moderate'
    
    @field_validator('goal')
    @classmethod
    def validate_goal(cls, v):
        valid_goals = ['lose_weight', 'gain_weight', 'maintain', 'build_muscle']
        if v and v.lower() not in valid_goals:
            raise ValueError(f'Goal must be one of: {valid_goals}')
        return v.lower() if v else 'maintain'

class User(UserCreate):
    """Complete user schema with userId and timestamps"""
    userId: str = Field(..., description="Unique user identifier")
    registeredAt: datetime = Field(default_factory=datetime.now, description="Registration timestamp")
    
    @classmethod
    def create_from_user_data(cls, user_data: UserCreate) -> "User":
        """Create a User instance with auto-generated userId from UserCreate data"""
        return cls(
            userId=str(uuid.uuid4()),
            **user_data.model_dump()
        )
