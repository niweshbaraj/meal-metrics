from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from typing import Optional
from datetime import date
from api.schemas import MealLog
from api.db.models import users_db, meals_db, update_user_activity
from api.db.food_data import food_db
from api.core.auth import get_current_user, check_user_access, AuthUser

router = APIRouter()

@router.post("/log",
          response_model=dict,
          summary="Log a user's meal",
          description="Record a meal with specified food items for a user.",
          responses={
              200: {"description": "Meal logged successfully."},
              400: {"description": "Invalid food items."},
              404: {"description": "User not found."},
              500: {"description": "Error logging meal."}
          })
def log_meal(
    log: MealLog
):
    """
    Record a meal with specified food items for a user.

    Request Body:
    - **userId**: The unique identifier of the user.
    - **meal**: The type of meal (e.g., breakfast, lunch, dinner, snack).
    - **items**: A list of food items included in the meal.
    - **loggedAt**: The date the meal was consumed (optional, defaults to today).

    Returns:
    - **message**: A success message.
    - **meal_details**: The details of the logged meal including nutrition information.
    - **username**: The name of the user.
    """
    try:
        if log.userId not in users_db:
            raise HTTPException(
                status_code=404, 
                detail=f"User with ID '{log.userId}' not found. Please register first."
            )
        
        # Set default date if not provided
        if not log.loggedAt:
            log.loggedAt = date.today()
        
        # Validate food items exist in database (case-insensitive)
        normalized_food_db = {k.lower(): k for k in food_db.keys()}
        normalized_items = []
        unknown_items = []
        
        for item in log.items:
            item_lower = item.strip().lower()
            if item_lower in normalized_food_db:
                normalized_items.append(normalized_food_db[item_lower])
            else:
                unknown_items.append(item)
        
        if unknown_items:
            available_foods = list(food_db.keys())
            raise HTTPException(
                status_code=400,
                detail=f"Unknown food items: {unknown_items}. Available foods: {available_foods[:10]}... (use GET /nutrition/foods for full list)"
            )
        
        # Calculate nutrition for this meal using normalized food names
        meal_nutrition = {"calories": 0, "protein": 0, "carbs": 0, "fiber": 0}
        for item in normalized_items:
            if item in food_db:
                for nutrient in meal_nutrition:
                    meal_nutrition[nutrient] += food_db[item][nutrient]
        
        # Store meal log with normalized food names
        meal_entry = log.model_dump()
        meal_entry['items'] = normalized_items  # Store normalized food names
        meal_entry['nutrition'] = meal_nutrition
        meals_db.append(meal_entry)
        
        # Update user activity
        update_user_activity(log.userId, "meal")
        
        # Get username for response
        user = users_db.get(log.userId)
        username = user['name'] if user else "Unknown"
        
        return {
            "message": "Meal logged successfully",
            "meal_details": meal_entry,
            "username": username
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle any unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Error logging meal: {str(e)}"
        )

@router.get("/{userId}",
          response_model=dict,
          summary="Get user's meals",
          description="Retrieve meals logged by a user, with optional date filtering.",
          responses={
              200: {"description": "Meals retrieved successfully."},
              404: {"description": "User not found."},
              500: {"description": "Error retrieving meals."}
          })
def get_meals(
    userId: str, 
    on_date: Optional[date] = Query(None, description="Filter meals by date (YYYY-MM-DD)")
):
    """
    Retrieve meals logged by a user, with optional date filtering.

    Path Parameters:
    - **userId**: The unique identifier of the user.

    Query Parameters:
    - **on_date**: The date to filter meals by (optional).

    Returns:
    - **userId**: The user's unique identifier.
    - **meals**: A list of meals logged by the user.
    """
    try:
        if userId not in users_db:
            raise HTTPException(
                status_code=404, 
                detail=f"User with ID '{userId}' not found"
            )
        
        # Filter meals by userId
        user_meals = [m for m in meals_db if m["userId"] == userId]
        if on_date:
            user_meals = [m for m in user_meals if str(m["loggedAt"]) == str(on_date)]
        
        return {
            "userId": userId,
            "meals": user_meals
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle any unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving meals: {str(e)}"
        )
