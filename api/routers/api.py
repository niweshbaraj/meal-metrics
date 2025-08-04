"""
API Router aggregator for BMR Tracker
"""
from fastapi import APIRouter
from api.routers import users, meals, nutrition, webhook

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(meals.router, prefix="/meals", tags=["meals"])
api_router.include_router(nutrition.router, prefix="/nutrition", tags=["nutrition"])
api_router.include_router(webhook.router, prefix="/webhook", tags=["webhook"])
