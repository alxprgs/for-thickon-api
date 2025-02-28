import bcrypt
from fastapi import Request, HTTPException, status, Depends
import uuid
from uuid import UUID

def create_hash(text: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(text.encode(), salt).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

async def check_auth_us(request, database) -> bool:
    token = request.cookies.get('token')
    if token:
        user = await database["users"].find_one({"session": token})
        return True if user else False
    return False 

async def get_authenticated_user(request: Request, database):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация"
        )
    
    user = await database["users"].find_one({"session": token})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные"
        )
    return user

def generate_cart_id() -> str:
    return str(uuid.uuid4())

def validate_cart_id(cart_id: str):
    try:
        UUID(cart_id, version=4)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректный ID корзины"
        )

async def verify_csrf_token(request: Request):
    from server import database
    csrf_cookie = request.cookies.get("csrf_token")
    csrf_header = request.headers.get("X-CSRF-Token")
    
    if not csrf_cookie or not csrf_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token is missing"
        )
    
    if csrf_cookie != csrf_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token"
        )
    
    user = await get_authenticated_user(request, database)
    if user.get("csrf_token") != csrf_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token mismatch"
        )
    
    return csrf_header