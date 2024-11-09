# main.py

from fastapi import FastAPI, Response, Header, Request, status
import uuid
from model import LoginInfo
from typing import Annotated

app = FastAPI()
userdb = [
    {
        "username": "admin",
        "password": "admin",
        "email": "admin@localhost.localdomain",
        "role": "admin",
    }
]
bookdb = {
    "1234-567-890": {"name": "BookA", "price": 100, "quantity": 10},
    "2345-678-901": {"name": "BookB", "price": 200, "quantity": 20},
    "3456-789-012": {"name": "BookC", "price": 300, "quantity": 30},
}



@app.post("/login", status_code=200)
async def login(login_info: LoginInfo, response: Response):
    for user in userdb:
        if (
            user["username"] == login_info.username
            and user["password"] == login_info.password
        ):
            session_token = str(uuid.uuid4())
            user["session_token"] = session_token
            return {
                "message": "Login successful",
                "role": user["role"],
                "session_token": session_token,
            }
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {"message": "Login failed"}


@app.get("/books", status_code=200)
async def get_books(response: Response, request: Request):
    bearer_token = request.headers.get("Authorization")
    if not bearer_token:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Unauthorized"}
    session_token = bearer_token.split(" ")[1]
    for user in userdb:
        if user.get("session_token") == session_token:
            return bookdb
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {"message": "Unauthorized"}


@app.get("/book/{isbn}", status_code=200)
async def get_book(isbn: str, response: Response, request: Request):
    bearer_token = request.headers.get("Authorization")
    if not bearer_token:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Unauthorized"}
    session_token = bearer_token.split(" ")[1]
    for user in userdb:
        if user.get("session_token") == session_token:
            if isbn in bookdb:
                return bookdb[isbn]
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Book not found"}
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {"message": "Unauthorized"}
