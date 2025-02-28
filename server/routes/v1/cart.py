from fastapi import APIRouter, Request, HTTPException, status, Depends
from pydantic import BaseModel, Field
from server import database
from typing import Dict
from fastapi.encoders import jsonable_encoder
from server.functions import get_authenticated_user, generate_cart_id, validate_cart_id, verify_csrf_token
import uuid

router = APIRouter(prefix="/cart")

class CartItemCreate(BaseModel):
    name: str
    price: float = Field(gt=0)
    quantity: int = Field(1, gt=0)

class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0)

class CartItemResponse(BaseModel):
    cart_id: str
    name: str
    price: float
    quantity: int

class OrderResponse(BaseModel):
    total_price: float
    status: bool
    payment_url: str


@router.post("/items", response_model=Dict)
async def add_to_cart(
    request: Request,
    item: CartItemCreate,
    csrf_token: str = Depends(verify_csrf_token)
):
    user = await get_authenticated_user(request, database)
    
    cart_id = generate_cart_id()
    update_data = {
        f"cart.{cart_id}": {
            "name": item.name,
            "price": item.price,
            "quantity": item.quantity
        }
    }

    result = await database["users"].update_one(
        {"_id": user["_id"]},
        {"$set": update_data}
    )

    if result.modified_count != 1:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось добавить товар в корзину"
        )

    return {
        "status": True,
        "cart_id": cart_id,
        "message": "Товар добавлен в корзину"
    }

@router.patch("/items/{cart_id}", response_model=Dict)
async def update_cart_item(
    request: Request,
    cart_id: str,
    update_data: CartItemUpdate,
    csrf_token: str = Depends(verify_csrf_token)
):
    validate_cart_id(cart_id)
    user = await get_authenticated_user(request, database)
    
    result = await database["users"].update_one(
        {
            "_id": user["_id"],
            f"cart.{cart_id}": {"$exists": True}
        },
        {"$set": {f"cart.{cart_id}.quantity": update_data.quantity}}
    )

    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Элемент корзины не найден"
        )

    return {
        "status": True,
        "message": "Элемент корзины обновлен"
    }

@router.delete("/items/{cart_id}", response_model=Dict)
async def delete_cart_item(
    request: Request,
    cart_id: str,
    csrf_token: str = Depends(verify_csrf_token)
):
    validate_cart_id(cart_id)
    user = await get_authenticated_user(request, database)
    
    result = await database["users"].update_one(
        {
            "_id": user["_id"],
            f"cart.{cart_id}": {"$exists": True}
        },
        {"$unset": {f"cart.{cart_id}": ""}}
    )

    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Элемент корзины не найден"
        )

    return {
        "status": True,
        "message": "Элемент корзины удален"
    }

@router.get("/items", response_model=Dict)
async def get_cart_items(request: Request):
    user = await get_authenticated_user(request, database)
    
    cart = user.get("cart", {})
    
    formatted_cart = [
        {
            "cart_id": cart_id,
            "name": item["name"],
            "price": float(item["price"]),
            "quantity": int(item["quantity"])
        }
        for cart_id, item in cart.items()
    ]
    return {
        "status": True,
        "cart": jsonable_encoder(formatted_cart)
    }

@router.post("/order", response_model=OrderResponse)
async def create_order(
    request: Request,
    csrf_token: str = Depends(verify_csrf_token)
):
    user = await get_authenticated_user(request, database)
    cart = user.get("cart", {})
    
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невозможно создать заказ: корзина пуста"
        )
    
    total_price = sum(item["price"] * item["quantity"] for item in cart.values())
    total_price = round(total_price, 2)
    
    order_id = str(uuid.uuid4())
    payment_url = f"https://payment.prghorse.ru/pay/{order_id}"
    
    await database["users"].update_one(
        {"_id": user["_id"]},
        {"$set": {"cart": {}}}
    )
    
    return {
        "total_price": total_price,
        "status": True,
        "payment_url": payment_url
    }