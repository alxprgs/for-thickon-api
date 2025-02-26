import bcrypt

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
