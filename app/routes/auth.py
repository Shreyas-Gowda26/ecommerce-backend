from fastapi import APIRouter, HTTPException, Depends
from app.db.database import db,users_collection
from app.db.schemas import UserCreate, UserLogin, UserResponse
from app.core.security import hash_password, verify_password, create_access_token
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate):
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(user.password)
    new_user = {
        "name": user.name,
        "email": user.email,
        "password": hashed_pw,
        "role": user.role,
        "created_at": datetime.utcnow()
    }
    result = users_collection.insert_one(new_user)
    created_user = users_collection.find_one({"_id": result.inserted_id})

    # Convert ObjectId to string
    created_user["id"] = str(created_user["_id"])
    del created_user["_id"]
    del created_user["password"]

    return created_user


@router.post("/login")
def login_user(user: UserLogin):
    db_user = users_collection.find_one({"email": user.email})
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect password")

    token = create_access_token({"sub": str(db_user["_id"]), "role": db_user["role"]})
    return {"access_token": token, "token_type": "bearer"}
