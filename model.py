from pydantic import BaseModel
from enum import Enum

class LoginInfo(BaseModel):
    username: str
    password: str

class PartInfo(BaseModel):
    name: str
    price: int
    quantity: int

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"