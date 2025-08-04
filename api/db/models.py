# Database Models and Storage for BMR Tracker
from datetime import datetime, date
from typing import Dict, List, Optional

# User Storage
users_db: Dict[str, dict] = {}  # userId -> user_data
user_lookup: Dict[str, str] = {}  # username -> userId

# Meal Storage
meals_db: List[dict] = []  # List of all meal entries

# Activity Tracking
def update_user_activity(user_id: str, activity_type: str = "activity"):
    """Update user activity timestamp and nutrient intake"""
    if user_id in users_db:
        users_db[user_id][f"last_{activity_type}"] = datetime.now().isoformat()

        # Update nutrient intake if activity is meal
        if activity_type == "meal":
            nutrient_intake = {"calories": 0, "protein": 0, "carbs": 0, "fiber": 0}
            for meal in meals_db:
                if meal["userId"] == user_id and meal["loggedAt"] == date.today():
                    for nutrient in nutrient_intake:
                        nutrient_intake[nutrient] += meal["nutrition"][nutrient]

            # Update user's nutrient intake
            users_db[user_id]["nutrient_intake"] = nutrient_intake

# User Lookup Function
def get_user_by_identifier(identifier: str) -> Optional[tuple]:
    """Get user by userId, username, or email"""
    # Check if it's a direct userId
    if identifier in users_db:
        return (identifier, users_db[identifier])
    
    # Check username lookup
    if identifier in user_lookup:
        user_id = user_lookup[identifier]
        return (user_id, users_db[user_id])
    
    # Check email in user data
    for user_id, user_data in users_db.items():
        if user_data.get('email', '').lower() == identifier.lower():
            return (user_id, user_data)
    
    return None
