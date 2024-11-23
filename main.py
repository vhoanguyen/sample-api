# main.py
from fastapi import FastAPI, Response, Request, status
import uuid, json
from datetime import datetime, timedelta
import schemas
import jmespath

####### Global Variables ########
app = FastAPI()
user_db_conn = open("user_db.json", "r")
user_db = json.loads(user_db_conn.read())
parts_db_conn = open("parts_db.json", "r+")
parts_db = json.loads(parts_db_conn.read())


# Login API
@app.post("/login", status_code=200)
async def login(login_info: schemas.LoginInfo, response: Response):
    for user in user_db:
        if (
            user["username"] == login_info.username
            and user["password"] == login_info.password
        ):
            _user_response = schemas.LoginResponse(
                **{
                    "access_token": str(uuid.uuid4()),
                    "token_expiry": datetime.now()
                    + timedelta(minutes=schemas.ValidTime.THIRTY_MINUTES),
                }
            )
            user.update(_user_response)
            return _user_response.model_dump()
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {"message": "Login failed"}

# Refresh token API
@app.post("/login/refresh", status_code=200)
async def refresh_token(response: Response, request: Request):
    bearer_token = request.headers.get("Authorization")
    if not bearer_token:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Unauthorized"}
    session_token = bearer_token.split(" ")[1]
    now = datetime.now()
    user = jmespath.search(f"[?access_token=='{session_token}']", user_db)
    if user:
        print(user)
        user = user[0]
        token_expiry = user.get("token_expiry", None)
        if token_expiry:
            if token_expiry > now:
                _user_response = schemas.LoginResponse(
                    **{
                        "access_token": session_token,
                        "token_expiry": datetime.now() 
                        + timedelta(minutes=schemas.ValidTime.THIRTY_MINUTES),
                    }
                )
                user.update(_user_response)
                return _user_response.model_dump()
            else:
                response.status_code = status.HTTP_401_UNAUTHORIZED
                return {"message": "Token expired"}
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {"message": "Unauthorized"}

# Get all parts API
@app.get("/parts", status_code=200)
async def get_parts(response: Response, request: Request):
    bearer_token = request.headers.get("Authorization")
    if not bearer_token:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Unauthorized"}
    session_token = bearer_token.split(" ")[1]
    now = datetime.now()
    user = jmespath.search(f"[?access_token=='{session_token}']", user_db)
    if user:
        user = user[0]
        token_expiry = user.get("token_expiry", None)
        if token_expiry:
            if token_expiry > now:
                return parts_db
            else:
                response.status_code = status.HTTP_401_UNAUTHORIZED
                return {"message": "Token expired"}
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {"message": "Unauthorized"}


# Get part API
@app.get("/part/{part_id}", status_code=200)
async def get_part(part_id: str, response: Response, request: Request):
    bearer_token = request.headers.get("Authorization")
    if not bearer_token:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Unauthorized"}
    session_token = bearer_token.split(" ")[1]
    now = datetime.now()
    user = jmespath.search(f"[?access_token=='{session_token}']", user_db)
    if user:
        user = user[0]
        token_expiry = user.get("token_expiry", None)
        if token_expiry:
            if token_expiry > now:
                part = parts_db.get(part_id, None)
                return part if part else {"message": "Part not found"}
            else:
                response.status_code = status.HTTP_401_UNAUTHORIZED
                return {"message": "Token expired"}

    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {"message": "Unauthorized"}


# Add part API
@app.put("/part/{part_id}", status_code=201)
async def add_part(
    part_id: str, part_info: schemas.PartInfo, response: Response, request: Request
):
    bearer_token = request.headers.get("Authorization")
    if not bearer_token:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Unauthorized"}
    session_token = bearer_token.split(" ")[1]
    now = datetime.now()
    user = jmespath.search(f"[?access_token=='{session_token}']", user_db)
    if user:
        user = user[0]
        token_expiry = user.get("token_expiry", None)
        user_role = user.get("role", None)
        if token_expiry:
            if token_expiry > now:
                if user_role == schemas.Role.ADMIN:
                    parts_db[part_id] = part_info.model_dump()
                    return {"message": "Part added successfully"}
                else:
                    response.status_code = status.HTTP_401_UNAUTHORIZED
                    return {"message": "Unauthorized"}
            else:
                response.status_code = status.HTTP_401_UNAUTHORIZED
                return {"message": "Token expired"}

    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {"message": "Unauthorized"}


# Update part API
@app.patch("/part/{part_id}", status_code=200)
async def update_part(
    part_id: str, part_info: schemas.PartInfo, response: Response, request: Request
):
    bearer_token = request.headers.get("Authorization")
    if not bearer_token:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Unauthorized"}
    session_token = bearer_token.split(" ")[1]
    now = datetime.now()
    user = jmespath.search(f"[?access_token=='{session_token}']", user_db)
    if user:
        user = user[0]
        token_expiry = user.get("token_expiry", None)
        user_role = user.get("role", None)
        if token_expiry:
            if token_expiry > now:
                if user_role == schemas.Role.ADMIN:
                    part = parts_db.get(part_id, None)
                    if part:
                        parts_db[part_id] = part_info.model_dump()
                        return {"message": "Part updated successfully"}
                    else:
                        response.status_code = status.HTTP_404_NOT_FOUND
                        return {"message": "Part not found"}
                else:
                    response.status_code = status.HTTP_401_UNAUTHORIZED
                    return {"message": "Unauthorized"}
            else:
                response.status_code = status.HTTP_401_UNAUTHORIZED
                return {"message": "Token expired"}

    response.status_code = status.HTTP_401_UNAUTHORIZED
    return {"message": "Unauthorized"}


# SHUTDOWN EVENT
@app.on_event("shutdown")
def shutdown_event():
    print("Shutting down the server")

    print("Saving partsdb")
    parts_db_conn.seek(0)
    parts_db_conn.write(json.dumps(parts_db, indent=4))
    parts_db_conn.truncate()
    parts_db_conn.close()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, ssl_certfile="server.crt", ssl_keyfile="server.key")