from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# User schema => collection: user
class User(BaseModel):
    phone: str = Field(..., description="E.164 phone number")
    name: Optional[str] = Field(None, description="Display name")
    avatar_url: Optional[str] = Field(None, description="Profile photo URL")
    created_at: Optional[datetime] = None

# Vehicle schema => collection: vehicle
class Vehicle(BaseModel):
    owner_id: str = Field(..., description="User id of owner")
    type: str = Field(..., description="bike or car")
    title: str = Field(..., description="Listing title")
    description: Optional[str] = None
    photos: List[str] = Field(default_factory=list)
    has_insurance: bool = False
    location: Optional[str] = None
    price_per_day: float = Field(..., ge=0)
    created_at: Optional[datetime] = None

# Booking schema => collection: booking
class Booking(BaseModel):
    user_id: str
    vehicle_id: str
    start_date: str  # ISO date string (YYYY-MM-DD)
    end_date: str    # ISO date string (YYYY-MM-DD)
    instant_delivery: bool = False
    subscription: Optional[str] = Field(None, description="e.g., Weekly, Monthly")
    created_at: Optional[datetime] = None

# OTP schema => collection: otp
class Otp(BaseModel):
    phone: str
    code: str
    created_at: Optional[datetime] = None

# Support message schema => collection: supportmessage
class SupportMessage(BaseModel):
    user_id: str
    role: str = Field(..., description="user or bot")
    message: str
    created_at: Optional[datetime] = None
