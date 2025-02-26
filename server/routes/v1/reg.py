from server import database
from fastapi import APIRouter
from server.functions import create_hash
from fastapi.responses import JSONResponse
from secrets import token_urlsafe
from pydantic_extra_types.phone_numbers import PhoneNumber
from pydantic import BaseModel, Field

class User_reg(BaseModel):
    login: PhoneNumber = Field(..., max_length=32, min_length=3)
    password: str = Field(..., min_length=8)
    repetition_password: str = Field(..., min_length=8)

router = APIRouter()

@router.post("/reg")
async def reg(user_data: User_reg) -> JSONResponse:
    db = database["users"]
    existing_user = await db.find_one({"login": user_data.login})
    if existing_user:
        return JSONResponse({"status": False,"error": "Аккаунт с таким номером телефона уже зарегистрирован."}, status_code=409)
    
    if user_data.password != user_data.repetition_password:
        return JSONResponse({"status": False,"error": "Пароль не соответствует повторению."}, status_code=422)
    
    if not any(char.isdigit() for char in user_data.password):
        return JSONResponse({"status": False,"error": "В пароле отсутствуют цифры."}, status_code=422)
    token = token_urlsafe(128)
    try:
        await database["users"].insert_one({
            "login": user_data.login,
            "password": create_hash(user_data.password),
            "session": token
        })
    except Exception as e:
       return JSONResponse({"status": False, "message": "server error"}, status_code=500)
    response = JSONResponse({"status": True}, status_code=200)
    response.set_cookie(key="token", value=token, httponly=True,secure=True,samesite="Strict")
    return response