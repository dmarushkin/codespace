from pydantic import BaseModel
from .models import UserType
from datetime import datetime

class UserBase(BaseModel):
    email: str
    user_type: UserType = UserType.USER  # Default type is USER

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class TokenCreate(BaseModel):
    token_name: str

class Token(BaseModel):
    id: int
    token: str
    token_name: str
    expires_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

class Login(BaseModel):
    username: str
    password: str
