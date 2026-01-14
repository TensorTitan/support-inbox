import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict

from jose import jwt, JWTError

JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret_change_me")
JWT_ALG = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "120"))

USERS = {
    "operator1": {
        "username": "operator1",
        "display_name": "Operator 1",
        "password": "test123",
    },
    "operator2": {
        "username": "operator2",
        "display_name": "Operator 2",
        "password": "test123",
    },
}

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    user = USERS.get(username)
    if not user:
        return None
    if user["password"] != password:
        return None
    return user

def create_access_token(username: str, display_name: str) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=JWT_EXPIRE_MINUTES)

    payload = {
        "sub": username,
        "name": display_name,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def decode_token(token: str) -> Dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        username = payload.get("sub")
        name = payload.get("name")

        if not username or not name:
            raise JWTError("Missing claims")

        return {"username": username, "name": name}
    except JWTError as e:
        raise ValueError("Invalid token") from e