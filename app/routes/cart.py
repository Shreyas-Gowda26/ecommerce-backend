from fastapi import APIRouter,HTTPException,Depends
from app.db.database import db,carts_collection,products_collection
from app.db.schemas import Cart,CartItem
from typing import List
from app.core.dependencies import get_current_user
from bson import ObjectId

router = APIRouter(
    prefix="/cart",
    tags=["CART"]
)

@router.post("/add")
def create_order(item : CartItem, user: dict = Depends(get_current_user)):
    user_id = user["sub"]
    product = products_collection.find_one({"_id":ObjectId(item.product_id)})
    if not product:
        raise HTTPException(status_code=404,detail="Product not found")
    
    cart = carts_collection.find_one({"user_id":user_id})

    if not cart: 
        carts_collection.find_one({
            "user_id": user_id,
            "items": [{"product_id": item.product_id, "quantity": item.quantity}]
        })
    else: 
        found = False
        for i in cart["items"]:
            if i["product_id"] == item.product_id:
                i["quantity"]+=item.quantity
                found = True
        if not found:
             cart["items"].append({"product_id": item.product_id, "quantity": item.quantity})
        carts_collection.update_one({"user_id": user_id}, {"$set": {"items": cart["items"]}})

    return {"detail": "Item added to cart"}

@router.get("/")
def get_cart(user: dict = Depends(get_current_user)):
    cart = carts_collection.find_one({"user_id": user["sub"]})
    if not cart:
        return {"items": []}
    for item in cart["items"]:
        product = products_collection.find_one({"_id": ObjectId(item["product_id"])})
        item["product_name"] = product["name"]
        item["price"] = product["price"]
    return cart


@router.delete("/remove/{product_id}")
def remove_from_cart(product_id: str, user: dict = Depends(get_current_user)):
    cart = carts_collection.find_one({"user_id": user["sub"]})
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    new_items = [i for i in cart["items"] if i["product_id"] != product_id]
    carts_collection.update_one({"user_id": user["sub"]}, {"$set": {"items": new_items}})
    return {"detail": "Item removed from cart"}