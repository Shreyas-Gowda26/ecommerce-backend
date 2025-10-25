from pydantic import BaseModel,EmailStr
from typing import Optional,List 
from datetime import datetime

class UserBase(BaseModel):
    name:str
    email:EmailStr
    role:str = "user"

class UserCreate(UserBase):
    password:str

class UserLogin(BaseModel):
    email:EmailStr
    password:str

class UserResponse(UserBase):
    id:str
    created_at:datetime