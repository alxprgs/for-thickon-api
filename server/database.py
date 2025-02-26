import os
from motor.motor_asyncio import AsyncIOMotorClient
from server import logger

try:
    client = AsyncIOMotorClient(
        os.getenv("MONGO_URL"),
        serverSelectionTimeoutMS=5000,
        socketTimeoutMS=5000
    )
    database = client["CDG"]
    logger.info("Подключение к MongoDB установлено")
except Exception as e:
    logger.critical(f"Ошибка подключения к MongoDB: {e}")
    raise