# main.py
from fastapi import FastAPI, Response, Request, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from fastapi.middleware.cors import CORSMiddleware
from lib.app_jwt import JWTBearer, sign_jwt, ExpiryTime, get_current_user

import uuid, json
from datetime import datetime, timedelta
import schemas
import jmespath


####### Global Variables ########
app = FastAPI()
users_db_conn = open("users_db.json", "r")
users_db = json.loads(users_db_conn.read())
parts_db_conn = open("parts_db.json", "r+")
parts_db = json.loads(parts_db_conn.read())
# carts_db_conn = open("carts_db.json", "r+")
# carts_db = json.loads(carts_db_conn.read())
products_db_conn = open("products_db.json", "r")
products_db = json.loads(products_db_conn.read())

origins = [
    "http://localhost",
    "http://localhost:9000",
    "http://localhost:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Login API
@app.post("/login", status_code=200)
async def login(login_info: schemas.LoginInfo, response: Response):
    for user in users_db:
        if (
            user["username"] == login_info.username
            and user["password"] == login_info.password
        ):
            _user_response = sign_jwt(
                user_name=user["username"],
                email=user["email"],
                role=user["role"],
                expiration=ExpiryTime.ONE_MINUTE
                )
            return _user_response
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
    user = jmespath.search(f"[?access_token=='{session_token}']", users_db)
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
@app.get("/parts", status_code=200, dependencies=[Depends(JWTBearer())])
async def get_parts(response: Response, request: Request):
    return parts_db

# Get part API
@app.get("/part/{part_id}", status_code=200, dependencies=[Depends(JWTBearer())])
async def get_part(part_id: str, response: Response, request: Request):
    part = parts_db.get(part_id, None)
    return part if part else {"message": "Part not found"}

# Add part API
@app.put("/part/{part_id}", status_code=201, dependencies=[Depends(JWTBearer())])
async def add_part(
    part_id: str, part_info: schemas.PartInfo, response: Response, request: Request,
    current_user=Depends(get_current_user)
):
    user_name = current_user.get("user_name", None)
    current_role = jmespath.search(f"[?username=='{user_name}'].role", users_db)
    if current_role and current_role[0] == schemas.Role.ADMIN:
        if part_id not in parts_db:
            parts_db[part_id] = part_info.model_dump()
            return {"message": "Part added successfully"}
        else:
            response.status_code = status.HTTP_409_CONFLICT
            return {"message": "Part already exists"}
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Unauthorized"}
    return {"message": "Part added successfully"}



# Update part API
@app.patch("/part/{part_id}", status_code=200, dependencies=[Depends(JWTBearer())])
async def update_part(
    part_id: str, part_info: schemas.PartInfo, response: Response, request: Request,
    current_user=Depends(get_current_user)
):
    user_name = current_user.get("user_name", None)
    current_role = jmespath.search(f"[?username=='{user_name}'].role", users_db)
    if current_role and current_role[0] == schemas.Role.ADMIN:
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


# Search products API
# Search products by title and description
@app.post("/search/{keyword}", status_code=200, dependencies=[Depends(JWTBearer())])
async def search_products(keyword: str, response: Response, request: Request):
    search_results = jmespath.search(
        f"[?contains(title, '{keyword}') || contains(description, '{keyword}')]",
        products_db,
    )
    return search_results

# SHUTDOWN EVENT
@app.on_event("shutdown")
def shutdown_event():
    print("Shutting down the server")

    print("Saving partsdb")
    parts_db_conn.seek(0)
    parts_db_conn.write(json.dumps(parts_db, indent=4))
    parts_db_conn.truncate()
    parts_db_conn.close()

    # print("Saving cartsdb")
    # carts_db_conn.seek(0)
    # carts_db_conn.write(json.dumps(carts_db, indent=4))
    # carts_db_conn.truncate()
    # carts_db_conn.close()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, ssl_certfile="server.crt", ssl_keyfile="server.key")