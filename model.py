from pydantic import BaseModel


class LoginInfo(BaseModel):
    username: str
    password: str

class BookInfo(BaseModel):
    name: str
    price: int
    quantity: int