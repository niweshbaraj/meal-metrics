from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class WebhookMessage(BaseModel):
    message: str = Field(..., min_length=1, description="Webhook message")

class WebhookResponse(BaseModel):
    success: bool = Field(..., description="Whether the webhook processing was successful")
    message: str = Field(..., description="Response message")
    userId: Optional[str] = Field(default=None, description="User ID processed")
    username: Optional[str] = Field(default=None, description="Username processed")
    meal_details: Optional[Dict[str, Any]] = Field(default=None, description="Details of logged meal if successful")
