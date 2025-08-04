from fastapi import APIRouter, Depends, HTTPException, Query, Header
from typing import Optional
from datetime import date
from app.schemas import NutritionStatusResponse
from app.db.models import users_db, meals_db
from app.db.food_data import food_db
from app.utils import calculate_bmr
from app.core.auth import get_current_user, check_user_access, AuthUser

router = APIRouter()

@router.get("/status/{userId}",
          response_model=NutritionStatusResponse,
          summary="Get user's nutrition status",
          description="Get detailed nutritional status and intake summary for a user")
def get_status(
    userId: str, 
    current_user: AuthUser = Depends(get_current_user),
    on_date: Optional[date] = Query(None, description="Get status for specific date (YYYY-MM-DD)")
):
    """
    Get a user's nutritional status, intake summary, and recommendations.
    
    Path Parameters:
    - **userId**: User ID to retrieve nutrition status for (required)
    
    Query Parameters:
    - **on_date**: Date to retrieve nutrition for (optional, format: YYYY-MM-DD)
    
    Authentication:
    - Requires API key in X-API-Key header
    - Requires user ID in X-User-Id header
    - Regular users can only access their own data
    - Admin users can access any user's data
    
    Returns comprehensive nutrition data including calories consumed, macro breakdown,
    meal distribution, and personalized recommendations based on the user's BMR.
    """
    try:
        # Check if user can access this data
        check_user_access(userId, current_user)
        if userId not in users_db:
            raise HTTPException(
                status_code=404, 
                detail=f"User with ID '{userId}' not found"
            )
        
        user = users_db[userId]
        
        # Filter meals by userId
        user_meals = [m for m in meals_db if m["userId"] == userId]
        if on_date:
            user_meals = [m for m in user_meals if str(m["loggedAt"]) == str(on_date)]
        
        # Calculate total nutrition consumed
        totals = {"calories": 0, "protein": 0, "carbs": 0, "fiber": 0}
        meal_breakdown = {"breakfast": 0, "lunch": 0, "dinner": 0, "snack": 0}
        
        for meal in user_meals:
            meal_type = meal.get("meal", "").lower()
            if meal_type in meal_breakdown:
                meal_breakdown[meal_type] += 1
                
            for item in meal["items"]:
                if item in food_db:
                    for key in totals:
                        totals[key] += food_db[item][key]
        
        # Calculate BMR for reference (handle 'others' gender)
        if user['gender'].lower() in ['male', 'female']:
            bmr = calculate_bmr(user['gender'], user['weight'], user['height'], user['age'])
        else:
            # For 'others' gender, use average of male/female BMR
            bmr_male = calculate_bmr('male', user['weight'], user['height'], user['age'])
            bmr_female = calculate_bmr('female', user['weight'], user['height'], user['age'])
            bmr = (bmr_male + bmr_female) / 2
        
        return {
            "userId": userId,
            "username": user['name'],
            "date": str(on_date) if on_date else "All time",
            "bmr": round(bmr, 2),
            "nutrient_intake": totals,
            "meals_logged": {
                "total": len(user_meals),
                "breakdown": meal_breakdown
            },
            "recommendations": {
                "calories_vs_bmr": f"{totals['calories']} consumed vs {round(bmr, 2)} BMR",
                "protein_percentage": f"{round((totals['protein'] * 4 / max(totals['calories'], 1)) * 100, 1)}% of calories from protein" if totals['calories'] > 0 else "No calories logged"
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle any unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Error getting nutrition status: {str(e)}"
        )

@router.get("/foods")
def list_foods():
    """Get list of all available foods in the database (No authentication required)"""
    try:
        foods_with_nutrition = {}
        for food, nutrition in food_db.items():
            foods_with_nutrition[food] = nutrition
        
        return {
            "total_foods": len(food_db),
            "foods": foods_with_nutrition,
            "categories": {
                "grains": [f for f in food_db if any(grain in f.lower() for grain in ['rice', 'roti', 'chapati', 'naan', 'paratha'])],
                "proteins": [f for f in food_db if any(protein in f.lower() for protein in ['dal', 'chicken', 'fish', 'paneer', 'egg'])],
                "vegetables": [f for f in food_db if any(veg in f.lower() for veg in ['cucumber', 'tomato', 'onion', 'potato', 'carrot', 'spinach'])],
                "fruits": [f for f in food_db if any(fruit in f.lower() for fruit in ['apple', 'banana', 'orange'])]
            }
        }
    except Exception as e:
        # Handle any unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Error listing foods: {str(e)}"
        )
