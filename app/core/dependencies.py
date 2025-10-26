from fastapi import HTTPException,Depends
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from app.core.security import decode_access_token

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return payload

def admin_required(user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user
