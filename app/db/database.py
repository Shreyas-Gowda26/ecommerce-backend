from pymongo import MongoClient

MONGO_URL = "mongodb://localhost:27017"
client = MongoClient(MONGO_URL)
db = client["payment_db"]

users_collection = db["users"]
carts_collection = db["carts"]
orders_collection = db["orders"]
products_collection = db["products"]
payments_collection = db["payments"]
