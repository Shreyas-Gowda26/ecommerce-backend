from pymongo import MongoClient

MONGO_URL = "mongodb://localhost:27017"
client = MongoClient(MONGO_URL)
db = client["payment_db"]

users_collection = db["USERS"]
carts_collection = db["CARTS"]
orders_collection = db["ORDERS"]
products_collection = db["PRODUCTS"]
payments_collection = db["PAYMENTS"]