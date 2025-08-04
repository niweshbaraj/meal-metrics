from fastapi import APIRouter, HTTPException, status
from typing import Optional
from datetime import datetime
from api.schemas.user import User, UserCreate
from api.db.models import users_db, user_lookup
from api.utils.utils import calculate_bmr

router = APIRouter()

@router.post(
    "/register",
    summary="Register a new user",
    description="Register a new user with profile data (public endpoint, no authentication required)",
    responses={
        200: {"description": "User registered successfully."},
        400: {"description": "Invalid user data."},
        500: {"description": "Server error."}
    }
)
def register_user(user_data: UserCreate):
    """
    Register a new user with profile data.

    Request Body:
    - **name**: User's full name.
    - **email**: User's email address (optional).
    - **age**: User's age in years.
    - **weight**: User's weight in kg.
    - **height**: User's height in cm.
    - **gender**: User's gender (male/female/other).
    - **activity_level**: User's activity level (optional, default: moderate).
    - **goal**: User's fitness goal (optional, default: maintain).

    Returns:
    - **message**: A success message.
    - **userId**: The unique identifier of the registered user.
    - **name**: The name of the registered user.
    - **user**: The full profile of the registered user.
    """
    try:
        # Generate userId
        user_id = f"user_{len(users_db) + 1}"
        
        # Store user data with all fields from schema
        user_record = {
            "name": user_data.name,
            "email": user_data.email,
            "height": user_data.height,
            "weight": user_data.weight,
            "age": user_data.age,
            "gender": user_data.gender,
            "activity_level": user_data.activity_level,
            "goal": user_data.goal,
            "registeredAt": datetime.now().isoformat()
        }
        
        users_db[user_id] = user_record
        
        # Update lookup table by name for easier searching
        user_lookup[user_data.name] = user_id
        
        return {
            "message": "User registered successfully",
            "userId": user_id,
            "name": user_data.name,
            "user": user_record
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to register user: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error registering user: {str(e)}"
        )

@router.get(
    "/bmr/{userId}",
    summary="Get user's BMR",
    description="Retrieve the Basal Metabolic Rate (BMR) for a user by their userId.",
    responses={
        200: {"description": "BMR details retrieved successfully."},
        404: {"description": "User not found."},
        500: {"description": "Error calculating BMR."}
    }
)
def get_bmr(
    userId: str
):
    """
    Retrieve the Basal Metabolic Rate (BMR) for a user by their userId.

    Path Parameters:
    - **userId**: The unique identifier of the user.

    Returns:
    - **userId**: The user's unique identifier.
    - **username**: The user's name.
    - **bmr**: The calculated BMR value.
    - **user_profile**: The user's profile details including height, weight, age, gender, activity level, and goal.
    """
    try:
        user = users_db.get(userId)
        if not user:
            raise HTTPException(
                status_code=404, 
                detail=f"User with ID '{userId}' not found"
            )

        # Calculate BMR (handle 'others' gender)
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
            "bmr": round(bmr, 2),
            "user_profile": {
                "height": user['height'],
                "weight": user['weight'],
                "age": user['age'],
                "gender": user['gender'],
                "activity_level": user['activity_level'],
                "goal": user['goal']
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating BMR: {str(e)}"
        )

@router.get(
    "/lookup/{username}",
    summary="Lookup user by name",
    description="Retrieve the userId and profile details for a user by their username.",
    responses={
        200: {"description": "User details retrieved successfully."},
        404: {"description": "User not found."},
        500: {"description": "Error looking up user."}
    }
)
def lookup_user(
    username: str
):
    """
    Retrieve the userId and profile details for a user by their username.

    Path Parameters:
    - **username**: The name of the user.

    Returns:
    - **username**: The user's name.
    - **userId**: The user's unique identifier.
    - **user_profile**: The user's profile details including email, height, weight, age, gender, activity level, and goal.
    """
    try:
        if username not in user_lookup:
            raise HTTPException(
                status_code=404, 
                detail=f"User '{username}' not found"
            )

        user_id = user_lookup[username]
        user = users_db.get(user_id)

        return {
            "username": username,
            "userId": user_id,
            "user_profile": {
                "email": user['email'],
                "height": user['height'],
                "weight": user['weight'],
                "age": user['age'],
                "gender": user['gender'],
                "activity_level": user['activity_level'],
                "goal": user['goal']
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error looking up user: {str(e)}"
        )

@router.get(
    "/",
    summary="List all users",
    description="Retrieve a list of all registered users.",
    responses={
        200: {"description": "List of users retrieved successfully."},
        500: {"description": "Error listing users."}
    }
)
def list_users():
    """
    Retrieve a list of all registered users.

    Returns:
    - **total_users**: The total number of registered users.
    - **users**: A list of user details including userId, name, email, and registration date.
    """
    try:
        user_list = []
        for user_id, user_data in users_db.items():
            user_list.append({
                "userId": user_id,
                "name": user_data['name'],
                "email": user_data.get('email'),
                "registeredAt": user_data.get('registeredAt')
            })

        return {
            "total_users": len(user_list),
            "users": user_list
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing users: {str(e)}"
        )

@router.get("/public")
def list_users_public():
    """
    Retrieve a public list of all registered users for login purposes.

    Returns:
    - **total_users**: The total number of registered users.
    - **users**: A list of user details including userId and name.
    """
    try:
        user_list = []
        for user_id, user_data in users_db.items():
            user_list.append({
                "userId": user_id,
                "name": user_data['name']
            })

        return {
            "total_users": len(user_list),
            "users": user_list
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing users: {str(e)}"
        )

@router.get("/{userId}")
def get_user_details(
    userId: str
):
    """
    Retrieve the details of a specific user by their userId.

    Path Parameters:
    - **userId**: The unique identifier of the user.

    Returns:
    - **userId**: The user's unique identifier.
    - **user_profile**: The user's profile details including name, email, height, weight, age, gender, activity level, and goal.
    """
    try:
        if userId not in users_db:
            raise HTTPException(
                status_code=404, 
                detail=f"User with ID '{userId}' not found"
            )

        user_data = users_db[userId]
        return {
            "userId": userId,
            **user_data
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving user: {str(e)}"
        )
