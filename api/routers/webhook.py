from fastapi import APIRouter, Depends, HTTPException, Header
from datetime import date
from typing import Optional
import re
from api.schemas import WebhookMessage, MealLog
from api.schemas.responses import WebhookResponse
from api.db.food_data import food_db
from api.db.models import users_db, meals_db, get_user_by_identifier, update_user_activity
from api.core.auth import get_current_user, AuthUser

router = APIRouter()

@router.post("/", response_model=WebhookResponse)
def webhook_meal_logging(
    msg: WebhookMessage,
    user_id: str = Header(..., description="User ID sending the message")
):
    print(f"Received headers: user_id={user_id}")  # Debug log
    print(f"Received body: {msg}")  # Debug log
    """
    Log a meal via webhook (e.g., from WhatsApp/Google Chat).

    Request Body:
    - **userId**: The unique identifier of the user.
    - **meal**: The type of meal (e.g., breakfast, lunch, dinner, snack).
    - **items**: A list of food items included in the meal.
    - **loggedAt**: The date the meal was consumed (optional, defaults to today).

    Returns:
    - **status**: The status of the webhook (success or error).
    - **message**: A message describing the result.
    - **webhook_data**: The data received from the webhook.
    - **result**: The details of the logged meal (if successful).
    """
    try:
        # Parse message to extract meal type and items
        match = re.match(r"log (\w+): (.+)", msg.message)
        if match:
            meal = match.group(1)
            items = [item.strip() for item in match.group(2).split(",")]
        else:
            return WebhookResponse(
                status="error",
                message="Invalid message format. Expected format: 'log <meal>: <item1>, <item2>, ...'",
                webhook_data=msg.model_dump(),
                result=None
            )

        # Find user by identifier
        user_record = get_user_by_identifier(user_id)
        if not user_record:
            return WebhookResponse(
                status="error",
                message=f"User not found with identifier: {user_id}. Please register first.",
                webhook_data=None,
                result=None
            )

        user_id, user_data = user_record

        # Validate food items exist in database (case-insensitive)
        normalized_food_db = {k.lower(): k for k in food_db.keys()}
        normalized_items = []
        unknown_items = []

        for item in items:
            item_lower = item.strip().lower()
            if item_lower in normalized_food_db:
                normalized_items.append(normalized_food_db[item_lower])
            else:
                unknown_items.append(item)

        if unknown_items:
            available_foods = list(food_db.keys())
            return WebhookResponse(
                status="error",
                message=f"Unknown food items: {unknown_items}. Available foods: {available_foods[:10]}... (use GET /nutrition/foods for full list)",
                webhook_data=None,
                result=None
            )

        # Calculate nutrition for this meal using normalized food names
        meal_nutrition = {"calories": 0, "protein": 0, "carbs": 0, "fiber": 0}
        for item in normalized_items:
            if item in food_db:
                for nutrient in meal_nutrition:
                    meal_nutrition[nutrient] += food_db[item][nutrient]

        # Store meal log with normalized food names
        meal_entry = MealLog(
            userId=user_id,
            meal=meal,
            items=normalized_items,
            loggedAt=date.today()
        ).model_dump()
        meal_entry['nutrition'] = meal_nutrition
        meals_db.append(meal_entry)

        # Update user activity
        update_user_activity(user_id, "meal")

        return WebhookResponse(
            status="success",
            message="Meal logged successfully",
            webhook_data=msg.model_dump(),
            result=meal_entry
        )

    except Exception as e:
        return WebhookResponse(
            status="error",
            message=f"Error processing webhook: {str(e)}",
            webhook_data=msg.model_dump(),
            result=None
        )
