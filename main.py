# main.py
from fastapi import FastAPI, Response, Header, Request, status
import uuid, json
from model import LoginInfo, PartInfo, Role
from typing import Annotated

####### Global Variables ########
app = FastAPI()
user_db_conn = open("user_db.json", "r+")
user_db = json.loads(user_db_conn.read())
parts_db_conn = open("parts_db.json", "r+")
parts_db = json.loads(parts_db_conn.read())


# Login API
@app.post("/login", status_code=200)
async def login(login_info: LoginInfo, response: Response):
    for user in user_db:
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
@app.get("/parts", status_code=200)
async def get_parts(response: Response, request: Request):
    bearer_token = request.headers.get("Authorization")
    if not bearer_token:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Unauthorized"}
    session_token = bearer_token.split(" ")[1]
    for user in user_db:
        if user.get("session_token") == session_token:
            return parts_db
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {"message": "Unauthorized"}


# Get book by ISBN API
@app.get("/part/{id}", status_code=200)
async def get_part(id: str, response: Response, request: Request):
    bearer_token = request.headers.get("Authorization")
    if not bearer_token:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Unauthorized"}
    session_token = bearer_token.split(" ")[1]
    for user in user_db:
        if user.get("session_token") == session_token:
            if id in parts_db:
                return parts_db[id]
            response.status_code = status.HTTP_404_NOT_FOUND
            return {"message": "Part not found"}
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {"message": "Unauthorized"}


# Add book API
@app.put("/part/{id}", status_code=201)
async def add_part(id: str, part_info: PartInfo,  request: Request, response: Response):
    bearer_token = request.headers.get("Authorization")
    if not bearer_token:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Unauthorized"}
    session_token = bearer_token.split(" ")[1]
    for user in user_db:
        if user.get("session_token") == session_token and user["role"] == Role.ADMIN:
            if id in parts_db:
                response.status_code = status.HTTP_409_CONFLICT
                return {"message": "Book already exists"}
            part_info = await request.json()
            parts_db[id] = part_info
            return {"message": "Part added successfully"}
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {"message": "Unauthorized"}


# Update book API
@app.patch("/part/{id}", status_code=200)
async def update_part(id: str, part_info: PartInfo, request: Request, response: Response):
    bearer_token = request.headers.get("Authorization")
    if not bearer_token:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Unauthorized"}
    session_token = bearer_token.split(" ")[1]
    for user in user_db:
        if user.get("session_token") == session_token and user["role"] == Role.ADMIN:
            if id not in parts_db:
                response.status_code = status.HTTP_404_NOT_FOUND
                return {"message": "Book not found"}
            part_info = await request.json()
            parts_db[id] = part_info
            return {"message": "Part updated successfully"}
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {"message": "Unauthorized"}


# SHUTDOWN EVENT
@app.on_event("shutdown")
def shutdown_event():
    print("Shutting down the server")
    print("Saving userdb")
    user_db_conn.seek(0)
    print("clearing session tokens")
    for user in user_db:
        if user.get("session_token"):
            print(f"Clearing session token for {user['username']}")
            del user["session_token"]
    user_db_conn.write(json.dumps(user_db, indent=4))
    user_db_conn.truncate()
    user_db_conn.close()

    print("Saving partsdb")
    parts_db_conn.seek(0)
    parts_db_conn.write(json.dumps(parts_db, indent=4))
    parts_db_conn.truncate()
    parts_db_conn.close()

