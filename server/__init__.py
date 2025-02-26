from .logger import logger
from .database import database
from fastapi import FastAPI, APIRouter

app = FastAPI(
    title="Cafe Dolce Goose API",
    version="0.0.1",
    
)

from .routes.v1 import router
app.include_router(router)