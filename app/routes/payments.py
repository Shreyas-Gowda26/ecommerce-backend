import razorpay
from fastapi import APIRouter, HTTPException, Depends
from app.db.database import db,orders_collection
from app.core.dependencies import get_current_user
from bson import ObjectId
from datetime import datetime
import os

router = APIRouter(prefix="/payments", tags=["Payments"])

# Razorpay client
razorpay_client = razorpay.Client(
    auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET"))
)


@router.post("/create-order")
def create_payment_order(user: dict = Depends(get_current_user)):
    """Create a Razorpay order for the user's latest pending order"""
    latest_order = db.orders.find_one({"user_id": user["sub"], "status": "pending"})
    if not latest_order:
        raise HTTPException(status_code=404, detail="No pending order found")

    amount_in_paise = int(latest_order["total_amount"] * 100)  # Razorpay expects paise

    # Create Razorpay order
    payment_order = razorpay_client.order.create({
        "amount": amount_in_paise,
        "currency": "INR",
        "payment_capture": 1  # auto capture
    })

    # Save Razorpay order ID to DB
    db.orders.update_one(
        {"_id": latest_order["_id"]},
        {"$set": {"razorpay_order_id": payment_order["id"], "payment_status": "created"}}
    )

    return {
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
