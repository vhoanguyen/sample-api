import jwt
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from enum import Enum
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta

JWT_ALGORITHM = "HS256"
JWT_SECRET = "password"


class ExpiryTime(int, Enum):
    ONE_MINUTE = 60
    FIVE_MINUTES = 5 * 60
    FIFTEEN_MINUTES = 15 * 60
    THIRTY_MINUTES = 30 * 60
    ONE_HOUR = 60 * 60


def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return {}
    except jwt.InvalidTokenError:
        print("Invalid token")
        return {}


def sign_jwt(
    user_name: str, email: str, role: str, expiration: int = ExpiryTime.FIFTEEN_MINUTES
) -> dict:

    now_timestamp = datetime.now(timezone.utc).timestamp()
    expiry_time = now_timestamp + ExpiryTime.ONE_MINUTE
    payload = {
        "user_name": user_name,
        "email": email,
        "role": role,
        "exp": expiry_time,
        "iat": datetime.now(timezone.utc).timestamp(),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return {
        "user_name": user_name,
        "email": email,
        "role": role,
        "access_token": token,
        "refresh_token": token,
        "expiry_time": datetime.fromtimestamp(expiry_time),
        "issued_at": datetime.fromtimestamp(now_timestamp),
    }


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token."
                )
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decode_jwt(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True

        return isTokenValid


def get_current_user(token: str = Depends(JWTBearer())) -> dict:
    return decode_jwt(token)
