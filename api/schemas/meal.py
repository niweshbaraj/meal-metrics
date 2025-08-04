from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import date

class MealLog(BaseModel):
    userId: str = Field(..., description="User ID")
    meal: str = Field(..., description="Meal type")
    items: List[str] = Field(..., min_items=1, description="List of food items")
    loggedAt: Optional[date] = Field(default=None, description="Date of meal (YYYY-MM-DD)")

    @field_validator('meal')
    @classmethod
    def validate_meal(cls, v):
        valid_meals = ['breakfast', 'lunch', 'dinner', 'snack']
        if v.lower() not in valid_meals:
            raise ValueError(f'Meal type must be one of: {valid_meals}')
        return v.lower()

    @field_validator('items')
    @classmethod
    def validate_items(cls, v):
        return [item.strip().title() for item in v if item.strip()]
