from fastapi import FastAPI
from app.routes import auth, products, cart, orders, payments

app = FastAPI(title="Ecommerce Backend")

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(payments.router)