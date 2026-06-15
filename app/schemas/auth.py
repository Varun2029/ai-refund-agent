"""Pydantic schemas for authentication endpoints."""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "agent"

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
