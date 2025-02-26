from fastapi import APIRouter
from server.functions import check_auth_us
from fastapi import Request
from server import database

router = APIRouter()

@router.get("/check_auth")
async def check_auth(request: Request) -> bool:
    return await check_auth_us(request=request, database=database)
