from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import date

class UserRegistrationResponse(BaseModel):
    message: str
    bmr: float
    user_data: Dict[str, Any]

class BMRResponse(BaseModel):
    username: str
    bmr: float
    formula: str
    user_profile: Dict[str, Any]

class MealLogResponse(BaseModel):
    message: str
    meal_details: Dict[str, Any]

class NutritionData(BaseModel):
    calories: float
    protein: float
    carbs: float
    fiber: float

class MealBreakdown(BaseModel):
    breakfast: int
    lunch: int
    dinner: int
    snack: int

class MealsLoggedInfo(BaseModel):
    total: int
    breakdown: MealBreakdown

class Recommendations(BaseModel):
    calories_vs_bmr: str
    protein_percentage: str

class NutritionStatusResponse(BaseModel):
    username: str
    date: str
    bmr: float
    nutrient_intake: NutritionData
    meals_logged: MealsLoggedInfo
    recommendations: Recommendations

class MealsResponse(BaseModel):
    username: str
    date_filter: str
    total_meals: int
    meals: List[Dict[str, Any]]
    total_nutrition: NutritionData

class FoodCategory(BaseModel):
    grains: List[str]
    proteins: List[str]
    vegetables: List[str]
    fruits: List[str]

class FoodsResponse(BaseModel):
    total_foods: int
    foods: Dict[str, NutritionData]
    categories: FoodCategory

class WebhookResponse(BaseModel):
    status: str
    message: str
    webhook_data: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None

class APIInfoResponse(BaseModel):
    message: str
    version: str
    docs: str
    endpoints: List[str]
