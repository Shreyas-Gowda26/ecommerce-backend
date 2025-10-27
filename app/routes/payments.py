import razorpay
from fastapi import HTTPException,Depends,APIRouter
from app.db.database import orders_collection
from app.core.dependencies import get_current_user
from datetime import datetime
from bson import ObjectId
import os

router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)

razorpay_client = razorpay.Client(
    auth=(os.getenv("RAZORPAY_KEY_ID"),os.getenv("RAZORPAY_KEY_SECRET"))
)

@router.post("/create_order")
def create_payment_order(user: dict=Depends(get_current_user)):
    latest_order = orders_collection.find_one({"user_id":user["sub"],"status":"pending"})
    if not latest_order:
        raise HTTPException(status_code=404,detail="No pending order found")
    
    amount_in_paise = int(latest_order["total_amount"]*100)

    payment_order = razorpay_client.order.create({
        "amount": amount_in_paise,
        "currency": "INR",
        "payment_capture": 1  # auto capture
    })

    orders_collection.update_one(
        {"_id":latest_order["_id"]},
         {"$set":{"razorpay_order_id":payment_order["id"],"payment_status":"created"}}
    )

    return{
         "order_id": str(latest_order["_id"]),
        "razorpay_order_id": payment_order["id"],
        "amount": latest_order["total_amount"],
        "currency": "INR",
        "key_id": os.getenv("RAZORPAY_KEY_ID")
    }

@router.post("/verify")
def verify_payment(payment_id: str, razorpay_order_id: str, signature: str):
    """Verify payment signature and update order status"""
    try:
        # Verify signature
        razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature
        })
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Payment verification failed")

    # Update order status
    orders_collection.update_one(
        {"razorpay_order_id": razorpay_order_id},
        {"$set": {"status": "paid", "payment_id": payment_id, "paid_at": datetime.utcnow()}}
    )

    return {"detail": "Payment verified successfully"}