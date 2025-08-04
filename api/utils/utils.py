import os
from typing import Dict, Any

def calculate_bmr(gender: str, weight: float, height: float, age: int) -> float:
    """
    Calculate BMR using Mifflin-St Jeor Equation
    
    Args:
        gender: 'male', 'female', or 'other'
        weight: Weight in kg
        height: Height in cm
        age: Age in years
    
    Returns:
        BMR in calories per day
    """
    if gender.lower() == "male":
        return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    elif gender.lower() == "female":
        return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    elif gender.lower() == "other":
        # Use average of male and female formulas for "other" gender
        male_bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        female_bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
        return (male_bmr + female_bmr) / 2
    else:
        raise ValueError("Gender must be 'male', 'female', or 'other'")

def calculate_tdee(bmr: float, activity_level: str = "sedentary") -> float:
    """
    Calculate Total Daily Energy Expenditure (TDEE) based on BMR and activity level
    
    Args:
        bmr: Basal Metabolic Rate
        activity_level: sedentary, light, moderate, active, very_active
    
    Returns:
        TDEE in calories per day
    """
    activity_multipliers = {
        "sedentary": 1.2,      # Little or no exercise
        "light": 1.375,        # Light exercise/sports 1-3 days/week
        "moderate": 1.55,      # Moderate exercise/sports 3-5 days/week
        "active": 1.725,       # Hard exercise/sports 6-7 days a week
        "very_active": 1.9     # Very hard exercise/physical job
    }
    
    multiplier = activity_multipliers.get(activity_level.lower(), 1.2)
    return bmr * multiplier

def verify_token(token: str) -> bool:
    """
    Verify API token - in production, use proper JWT or OAuth
    """
    # Get from environment variable or use default for demo
    valid_token = os.getenv("API_KEY", "SECRET_API_KEY")
    return token == valid_token

def get_nutrition_recommendations(age: int, gender: str, goal: str) -> Dict[str, Any]:
    """
    Get basic nutrition recommendations based on user profile
    
    Args:
        age: User's age
        gender: User's gender
        goal: User's fitness goal
    
    Returns:
        Dictionary with nutrition recommendations
    """
    base_recommendations = {
        "protein_grams_per_kg": 0.8,  # WHO recommendation
        "carbs_percentage": 50,       # % of total calories
        "fat_percentage": 30,         # % of total calories
        "fiber_grams": 25             # Daily fiber intake
    }
    
    # Adjust based on goal
    if goal == "build_muscle":
        base_recommendations["protein_grams_per_kg"] = 1.6
    elif goal == "lose_weight":
        base_recommendations["carbs_percentage"] = 40
        base_recommendations["protein_grams_per_kg"] = 1.2
    
    # Adjust based on gender and age
    if gender.lower() == "female":
        base_recommendations["fiber_grams"] = 21
    
    if age > 50:
        base_recommendations["protein_grams_per_kg"] = 1.0
    
    return base_recommendations

def format_nutrition_summary(nutrition_data: Dict[str, float]) -> str:
    """
    Format nutrition data into a readable summary
    """
    return f"""
    Calories: {nutrition_data.get('calories', 0):.0f} kcal
    Protein: {nutrition_data.get('protein', 0):.1f}g
    Carbohydrates: {nutrition_data.get('carbs', 0):.1f}g
    Fiber: {nutrition_data.get('fiber', 0):.1f}g
    """.strip()

def verify_token(token: str) -> bool:
    """
    Verify JWT token or API token
    
    This is a placeholder function for the JWT verification that would be 
    implemented in a production environment.
    
    Args:
        token: The token to verify
        
    Returns:
        True if the token is valid, False otherwise
    """
    # In a real application, this would verify a JWT token
    # For now, just check if it's one of our test API keys
    from api.core.auth import SECRET_API_KEY, ADMIN_API_KEY
    
    return token in [SECRET_API_KEY, ADMIN_API_KEY]
