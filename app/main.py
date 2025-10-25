from fastapi import FastAPI
from app.routes import auth

app = FastAPI(title="Payment Processing API")

app.include_router(auth.router)