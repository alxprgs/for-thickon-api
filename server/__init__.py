from .logger import logger
from .database import database
from fastapi import FastAPI, APIRouter, status
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Cafe Dolce Goose API",
    version="0.0.1",
    docs_url="/"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from .routes.v1 import router
app.include_router(router)