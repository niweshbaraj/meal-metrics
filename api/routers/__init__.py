"""
API Routers module for the BMR Tracker API

This module contains all the FastAPI routers organized by functionality.
"""

from .users import router as users_router
from .meals import router as meals_router
from .nutrition import router as nutrition_router
from .webhook import router as webhook_router

__all__ = [
    "users_router",
    "meals_router",
    "nutrition_router",
    "webhook_router"
]
