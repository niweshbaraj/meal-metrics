from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.staticfiles import StaticFiles
from api.routers.api import api_router
from api.schemas import APIInfoResponse, UserCreate
from api.core.auth import API_KEY_NAME, USER_ID_NAME
from fastapi.openapi.utils import get_openapi
import os

app = FastAPI(
    title="BMR Tracker API",
    description="""
    A comprehensive nutrition tracking backend built using FastAPI
    
    ## Authentication
    
    Authentication requires two parts:
    
    1. **API Key** (set via the "Authorize" button at the top):
       - Use **SECRET_API_KEY** for regular users
       - Use **ADMIN_API_KEY** for admin access
    
    2. **User ID** (must be provided as a separate header for each endpoint):
       - For regular users: Required as X-User-Id header (e.g., **user_1**)
       - For admin access: Not required
    
    After clicking Authorize to set your API key, you'll still need to manually add 
    the X-User-Id header when testing endpoints that require regular user access.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "users", "description": "User management operations"},
        {"name": "meals", "description": "Meal logging operations"},
        {"name": "nutrition", "description": "Nutrition tracking and analysis"},
        {"name": "webhook", "description": "Webhook integration for external apps"}
    ]
)

# Remove the OpenAPI components and security requirements
app.openapi_components = {}
app.openapi_security = []

# For demonstration purposes, remember to use these values:
# - Regular user API Key: SECRET_API_KEY
# - Admin API Key: ADMIN_API_KEY
# - User ID: Required for regular users (e.g., user_1)

# Add middleware to log all incoming requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    print(f"Response status: {response.status_code}")
    return response

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Mount static files for frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_path):
    app.mount("/frontend", StaticFiles(directory=frontend_path), name="frontend")

@app.get("/", response_model=APIInfoResponse)
def root():
    """Root endpoint with API information"""
    return APIInfoResponse(
        message="BMR Tracker API",
        version="1.0.0",
        docs="/docs",
        endpoints=[
            "POST /api/v1/users/register - Register a new user",
            "GET /api/v1/users/bmr/{userId} - Get user's BMR by userId",
            "GET /api/v1/users/lookup/{username} - Get userId by username",
            "GET /api/v1/users/ - List all users",
            "POST /api/v1/meals/log - Log a meal using userId",
            "GET /api/v1/meals/{userId} - Get user's meals by userId",
            "GET /api/v1/nutrition/status/{userId} - Get nutrient status by userId",
            "GET /api/v1/nutrition/foods - List available foods",
            "POST /api/v1/webhook/ - Webhook for meal logging with userId"
        ]
    )

# Override the OpenAPI schema generation to include all models explicitly
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    # Explicitly include UserCreate and HTTPValidationError in the schema
    openapi_schema["components"]["schemas"].update({
        "UserCreate": UserCreate.schema(),
        "HTTPValidationError": {
            "title": "HTTPValidationError",
            "type": "object",
            "properties": {
                "detail": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/ValidationError"}
                }
            }
        },
        "ValidationError": {
            "title": "ValidationError",
            "type": "object",
            "properties": {
                "loc": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "msg": {"type": "string"},
                "type": {"type": "string"}
            }
        }
    })
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
