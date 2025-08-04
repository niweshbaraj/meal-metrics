"""
Enhanced authentication for BMR Tracker with user-specific access control
"""
from fastapi import HTTPException, Header, Depends, Security, status
from fastapi.security import APIKeyHeader
from typing import Optional
from pydantic import BaseModel

# Security scheme definitions
API_KEY_NAME = "X-API-Key"
USER_ID_NAME = "X-User-Id"
# Define API key header for authentication
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)
# Define User ID header - keep auto_error=False so it doesn't require it globally
user_id_header = APIKeyHeader(name=USER_ID_NAME, auto_error=False)

# API keys for different roles
# In a production environment, these would be stored securely in environment variables
# For demonstration purposes, we're using the actual string values
SECRET_API_KEY = "SECRET_API_KEY"  # For regular users - Use this exact string in X-API-Key header
ADMIN_API_KEY = "ADMIN_API_KEY"    # For admin access - Use this exact string in X-API-Key header

class AuthUser(BaseModel):
    """Authentication user model with role-based access control"""
    user_id: str
    role: str = "user"  # "user" or "admin"

# Authentication dependency
def get_current_user(
    api_key: str = Security(api_key_header),
    user_id: Optional[str] = Security(user_id_header)
) -> AuthUser:
    """
    Authenticate user based on API key and return AuthUser object
    
    For non-admin users, X-User-Id must be provided
    For admin users, X-User-Id is optional
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": f"APIKey {API_KEY_NAME}"}
        )

    if api_key == ADMIN_API_KEY:
        # Admin can access any resource
        return AuthUser(user_id=user_id or "admin", role="admin")

    elif api_key == SECRET_API_KEY:
        # Regular users need to provide their user_id
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID required for non-admin access",
                headers={"WWW-Authenticate": f"APIKey {USER_ID_NAME}"}
            )
        return AuthUser(user_id=user_id, role="user")

    # Invalid API key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key",
        headers={"WWW-Authenticate": f"APIKey {API_KEY_NAME}"}
    )

# Check if user has access to a specific user_id
def check_user_access(auth_user: AuthUser, user_id: str) -> bool:
    """Check if authenticated user has access to a specific user_id"""
    # Admins can access any user
    if auth_user.role == "admin":
        return True
    
    # Regular users can only access their own resources
    return auth_user.user_id == user_id

# Admin-only dependency
def require_admin(auth_user: AuthUser = Depends(get_current_user)) -> AuthUser:
    """Require admin role for this endpoint"""
    if auth_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return auth_user
