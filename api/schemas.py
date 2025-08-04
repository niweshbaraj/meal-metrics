# Re-export all schemas from subdirectories for backward compatibility
from api.schemas.user import User, UserCreate
from api.schemas.meal import MealLog
from api.schemas.webhook import WebhookMessage, WebhookResponse
from api.schemas.responses import *

# Keep the old schemas that are still being used
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import date

class APIInfoResponse(BaseModel):
    message: str
    version: str
    docs: str
    endpoints: List[str]

class NutritionStatusResponse(BaseModel):
    userId: str
    userName: str
    date: str
    bmr: float
    totalCalories: float
    remainingCalories: float
    macros: dict
    status: str
