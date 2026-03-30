from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, constr, field_validator
import re


EMAIL_REGEX = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"


class UserBase(BaseModel):
    email: constr(strip_whitespace=True, min_length=1, max_length=255)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if not re.match(EMAIL_REGEX, v):
            raise ValueError("Email must be valid, e.g. 'test@test.com'.")
        return v.lower()


class UserCreate(UserBase):
    password: constr(min_length=1, max_length=255)


class UserUpdate(BaseModel):
    email: Optional[constr(strip_whitespace=True, min_length=1, max_length=255)] = None
    password: Optional[constr(min_length=1, max_length=255)] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if v is None:
            return v
        if not re.match(EMAIL_REGEX, v):
            raise ValueError("Email must be valid, e.g. 'test@test.com'.")
        return v.lower()


class UserRead(UserBase):
    userID: int
    createdAt: datetime
    lastUpdated: datetime

    model_config = {"from_attributes": True}


class LoginPayload(BaseModel):
    email: constr(strip_whitespace=True, min_length=1, max_length=255)
    password: constr(min_length=1, max_length=255)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v):
        return v.strip().lower()