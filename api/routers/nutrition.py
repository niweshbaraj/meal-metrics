from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from datetime import date
from api.schemas import NutritionStatusResponse
from api.db.models import users_db, meals_db
from api.db.food_data import food_db
from api.utils.utils import calculate_bmr
from api.core.auth import get_current_user, check_user_access, AuthUser

router = APIRouter()

@router.get("/status/{userId}")
def get_status(
    userId: str, 
    on_date: Optional[date] = Query(None, description="Get status for specific date (YYYY-MM-DD)")
):
    """
    Retrieve the nutritional status and intake summary for a user by their userId.

    Path Parameters:
    - **userId**: The unique identifier of the user.

    Query Parameters:
    - **on_date**: The date to filter meals by (optional).

    Returns:
    - **userId**: The user's unique identifier.
    - **username**: The user's name.
    - **date**: The date of the status (or "All time" if not specified).
    - **bmr**: The user's Basal Metabolic Rate (BMR).
    - **nutrient_intake**: The total nutrients consumed (calories, protein, carbs, fiber).
    - **meals_logged**: The total number of meals logged and their breakdown by type.
    - **recommendations**: Nutritional recommendations based on the user's intake.
    """
    try:
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

            # Use pre-calculated nutrition from the meal log
            for key in totals:
                totals[key] += meal["nutrition"].get(key, 0)

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
                "protein_percentage": f"{round((totals['protein'] * 4 / max(totals['calories'], 1)) * 100, 2)}% protein intake"
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
    """
    Retrieve a list of all available foods in the database.

    Returns:
    - **total_foods**: The total number of foods in the database.
    - **foods**: A dictionary of food items and their nutritional information.
    - **categories**: Food categories including grains, proteins, vegetables, and fruits.
    """
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
