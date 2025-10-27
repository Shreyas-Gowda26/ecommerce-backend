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

    class Config:
        orm_mode = True


class ProductBase(BaseModel):
    name:str
    description:Optional[str]=None
    price:float
    stock:int
    category:Optional[str]=None
    image_url:Optional[str]=None

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    _id:str
    created_at:datetime

    class Config:
        orm_mode = True


class CartItem(BaseModel):
    product_id:str
    quantity:int 
    price:float

class Cart(BaseModel):
    user_id:str
    items:List[CartItem]

    class Config:
        orm_mode = True

class OrderItem(BaseModel):
    product_id :str
    quantity:int
    price:float

class OrderCreate(BaseModel):
    user_id:str
    items:List[OrderItem]
    total_amount:float
    payment_method:str

class OrderResponse(OrderCreate):
    id:str
    status:str="pending"
    created_at:datetime

    class Config:
        orm_mode = True

class PaymentResponse(BaseModel):
    order_id:str
    payment_id:str
    amount:float
    status:str
    timestamp:datetime

    class Config:
        orm_mode = True
