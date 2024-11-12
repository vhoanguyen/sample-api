from pydantic import BaseModel, Field, field_serializer
from enum import Enum
from datetime import datetime


class User(BaseModel):
    username: str
    password: str
    role_type: str
    email: str


class LoginInfo(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token_type: str = "bearer"
    access_token: str
    created_at: datetime = Field(default_factory=datetime.now)
    token_expiry: datetime

    @field_serializer("token_expiry")
    def token_expiry_serializer(self, v: datetime) -> str:
        return v.isoformat()

    @field_serializer("created_at")
    def created_at_serializer(self, v: datetime) -> str:
        return v.isoformat()


class PartInfo(BaseModel):
    name: str
    price: int
    quantity: int


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"


class ValidTime(int, Enum):
    ONE_MINUTE = 1
    THIRTY_MINUTES = 30
    ONE_HOUR = 60
    TWO_HOURS = 120
    THREE_HOURS = 180
    FOUR_HOURS = 240
