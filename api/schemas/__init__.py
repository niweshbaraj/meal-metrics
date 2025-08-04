"""
Schemas module for the BMR Tracker API

This module contains all Pydantic models used for request/response validation.
"""

from .user import User, UserCreate
from .meal import MealLog
from .webhook import WebhookMessage
from .responses import (
    UserRegistrationResponse,
    BMRResponse,
    MealLogResponse,
    NutritionData,
    NutritionStatusResponse,
    MealsResponse,
    FoodsResponse,
    WebhookResponse,
    APIInfoResponse
)

__all__ = [
    # Request schemas
    "User",
    "UserCreate",
    "MealLog", 
    "WebhookMessage",
    
    # Response schemas
    "UserRegistrationResponse",
    "BMRResponse",
    "MealLogResponse",
    "NutritionData",
    "NutritionStatusResponse",
    "MealsResponse",
    "FoodsResponse",
    "WebhookResponse",
    "APIInfoResponse"
]
