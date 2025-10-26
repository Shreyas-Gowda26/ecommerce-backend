from fastapi import APIRouter,HTTPException,Depends,status
from app.db.database import db,products_collection
from app.db.schemas import ProductCreate,ProductResponse
from app.core.dependencies import admin_required
from datetime import datetime
from bson import ObjectId
from typing import List
router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.post("/",response_model=ProductResponse,dependencies=[Depends(admin_required)])
def create_product(product:ProductCreate):
    new_product = product.model_dump()
    new_product["created_at"]= datetime.utcnow()
    result = products_collection.insert_one(new_product)
    create_product = products_collection.find_one({"_id":result.inserted_id})
    create_product["id"]= str(create_product["_id"])
    del create_product["_id"]
    return create_product

@router.get("/",response_model=List[ProductResponse])
def list_products():
    products = []
    product = products_collection.find()
    for item in product:
        data = {k: item[k] for k in item if k != "_id"}
        products.append(data)
    return products

@router.get("/{product_id}",response_model=ProductResponse)
def get_product(product_id:str):
    product = products_collection.find_one({"_id":ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404,detail="Product not found")
    product["_id"]=str(product["_id"])
    return product

@router.put("/{product_id}",response_model=ProductResponse,dependencies=[Depends(admin_required)])
def update_product(product_id:str,product:ProductCreate):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400,detail="Invalid product ID")
    update_result = products_collection.update_one(
        {"_id":ObjectId(product_id)},
        {"$set":product.model_dump()}
    )
    if update_result.matched_count ==0:
        raise HTTPException(status_code=404,detail="Product not found")
    update_product = products_collection.find_one({"_id":ObjectId(product_id)})
    update_product["_id"]= str(update_product["_id"])
    del update_product["_id"]
    return update_product

@router.delete("/{product_id}",response_model=ProductResponse,dependencies=[Depends(admin_required)])
def delete_product(product_id:str):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400,detail="Invalid product ID")
    delete_result = products_collection.delete_one({"_id":ObjectId(product_id)})
    if delete_result.deleted_count==0:
        raise HTTPException(status_code=404,detail="Product not found")
    return {"detail":"Product deleted successfully"}