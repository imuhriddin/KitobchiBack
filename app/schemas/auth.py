from pydantic import BaseModel, EmailStr, Field, constr
from typing import Optional


class RegisterRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=64)
    
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None

