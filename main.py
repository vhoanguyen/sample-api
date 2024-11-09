# main.py
from fastapi import FastAPI, Response, Header, Request, status
import uuid, json
from model import LoginInfo, BookInfo
from typing import Annotated

####### Global Variables ########
app = FastAPI()
userdb_conn = open("userdb.json", "r+")
userdb = json.loads(userdb_conn.read())
bookdb_conn = open("bookdb.json", "r+")
bookdb = json.loads(bookdb_conn.read())


# Login API
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


# Get all books API
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


# Get book by ISBN API
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


# Add book API
@app.put("/book/{isbn}", status_code=201)
async def add_book(isbn: str, book_info: BookInfo,  request: Request, response: Response):
    bearer_token = request.headers.get("Authorization")
    if not bearer_token:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Unauthorized"}
    session_token = bearer_token.split(" ")[1]
    for user in userdb:
        if user.get("session_token") == session_token and user["role"] == "admin":
            if isbn in bookdb:
                response.status_code = status.HTTP_409_CONFLICT
                return {"message": "Book already exists"}
            book_info = await request.json()
            bookdb[isbn] = book_info
            return {"message": "Book added successfully"}
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {"message": "Unauthorized"}

# SHUTDOWN EVENT
@app.on_event("shutdown")
def shutdown_event():
    print("Shutting down the server")
    print("Saving userdb")
    userdb_conn.seek(0)
    print("clearing session tokens")
    for user in userdb:
        if user.get("session_token"):
            print(f"Clearing session token for {user['username']}")
            del user["session_token"]
    userdb_conn.write(json.dumps(userdb, indent=4))
    userdb_conn.truncate()
    userdb_conn.close()

    print("Saving bookdb")
    bookdb_conn.seek(0)
    bookdb_conn.write(json.dumps(bookdb, indent=4))
    bookdb_conn.truncate()
    bookdb_conn.close()

