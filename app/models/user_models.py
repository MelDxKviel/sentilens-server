from typing import Optional
from datetime import datetime

from pydantic import EmailStr
from sqlmodel import SQLModel, Field, AutoString


class UserBase(SQLModel):
    username: str = Field(index=True, unique=True,
                          max_length=255, min_length=3)
    email: EmailStr = Field(unique=True, index=True, sa_type=AutoString)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_superuser: bool = Field(default=False)


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password: str


class UserRead(UserBase):
    id: int


class UserRegister(SQLModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(SQLModel):
    username: str
    password: str


class UserCreate(UserBase):
    password: str
    access_token: str = None


class UserUpdate(SQLModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None


class PasswordChange(SQLModel):
    old_password: str
    new_password: str


class PasswordResetEmail(SQLModel):
    email: EmailStr


class PasswordResetConfirm(SQLModel):
    reset_code: str
    new_password: str
