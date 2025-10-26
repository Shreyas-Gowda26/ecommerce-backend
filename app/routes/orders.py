from fastapi import APIRouter, HTTPException, Depends
from app.db.database import db,orders_collection,products_collection
from app.db.schemas import OrderCreate, OrderResponse
from app.core.dependencies import get_current_user
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse)
def place_order(order: OrderCreate, user: dict = Depends(get_current_user)):
    user_id = user["sub"]

    # Validate all product IDs and check stock
    for item in order.items:
        product = products_collection.find_one({"_id": ObjectId(item.product_id)})
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        if product["stock"] < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for {product['name']}")

    # Reduce stock
    for item in order.items:
        products_collection.update_one(
            {"_id": ObjectId(item.product_id)},
            {"$inc": {"stock": -item.quantity}}
        )

    # Create order
    order_doc = {
        "user_id": user_id,
        "items": [item.dict() for item in order.items],
        "total_amount": order.total_amount,
        "payment_method": order.payment_method,
        "status": "pending",
        "created_at": datetime.utcnow()
    }

    result = orders_collection.insert_one(order_doc)
    created_order = orders_collection.find_one({"_id": result.inserted_id})

    created_order["id"] = str(created_order["_id"])
    del created_order["_id"]
    return created_order


@router.get("/", response_model=list[OrderResponse])
def list_orders(user: dict = Depends(get_current_user)):
    orders = []
    for o in orders_collection.find({"user_id": user["sub"]}):
        o["id"] = str(o["_id"])
        del o["_id"]
        orders.append(o)
    return orders
