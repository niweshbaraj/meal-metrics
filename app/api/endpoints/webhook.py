from fastapi import APIRouter, Depends, HTTPException, Header
from datetime import date
from typing import Optional
import re
from app.schemas import WebhookMessage, MealLog, WebhookResponse
from app.db.food_data import food_db
from app.db.models import users_db, meals_db, get_user_by_identifier, update_user_activity
from app.core.auth import get_current_user, AuthUser

router = APIRouter()

@router.post("/", 
          response_model=WebhookResponse,
          summary="Process webhook for meal logging",
          description="Process a webhook message for meal logging from external sources")
def webhook_meal_logging(
    msg: WebhookMessage,
    current_user: AuthUser = Depends(get_current_user)
):
    """
    Process a webhook message to log meals from external sources (e.g., chat apps).
    
    Request Body:
    - **message**: The text message containing meal information (required)
    - **userId**: User ID to associate the meal with (optional)
    
    Authentication:
    - Requires API key in X-API-Key header
    - Requires user ID in X-User-Id header
    - Regular users can only log meals for themselves
    - Admin users can log meals for any user
    
    The system will parse the message to detect food items and meal type.
    Example message: "log lunch: pasta, rice"
    """
    try:
        # Find user by identifier (use userId from webhook message)
        user_identifier = msg.userId if msg.userId else "unknown"
        user_record = get_user_by_identifier(user_identifier)
        
        if not user_record:
            return WebhookResponse(
                success=False,
                message=f"User not found with identifier: {user_identifier}. Please register first.",
                userId=None,
                username=None
            )
        
        user_id, user_data = user_record
        
        # Check if current user has access to log meals for this user
        from app.core.auth import check_user_access
        if not check_user_access(user_id, current_user):
            return WebhookResponse(
                success=False,
                message="You don't have permission to log meals for this user.",
                userId=None,
                username=None
            )
        
        # Parse the message to extract food items
        message_text = msg.message.lower().strip()
        
        # Simple food parsing logic
        detected_foods = []
        for food_name in food_db.keys():
            if food_name.lower() in message_text:
                detected_foods.append(food_name)
        
        if not detected_foods:
            return WebhookResponse(
                success=False,
                message=f"No recognizable food items found in message: '{msg.message}'. Try mentioning specific food names.",
                userId=user_id,
                username=user_data['name']
            )
        
        # Create meal log
        meal_log = MealLog(
            userId=user_id,
            items=detected_foods,
            meal_type=msg.meal_type or "snack",
            loggedAt=date.today()
        )
        
        # Calculate nutrition for this meal
        meal_nutrition = {"calories": 0, "protein": 0, "carbs": 0, "fiber": 0}
        for item in detected_foods:
            if item in food_db:
                for nutrient in meal_nutrition:
                    meal_nutrition[nutrient] += food_db[item][nutrient]
        
        # Store meal log
        meal_entry = meal_log.model_dump()
        meal_entry['nutrition'] = meal_nutrition
        meal_entry['source'] = 'webhook'
        meals_db.append(meal_entry)
        
        # Update user activity
        update_user_activity(user_id, "meal")
        
        return WebhookResponse(
            success=True,
            message=f"Meal logged successfully! Detected foods: {', '.join(detected_foods)}",
            userId=user_id,
            username=user_data['name'],
            meal_details=meal_entry
        )
        
    except Exception as e:
        return WebhookResponse(
            success=False,
            message=f"Error processing webhook: {str(e)}",
            userId=None,
            username=None
        )
