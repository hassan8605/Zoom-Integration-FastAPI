from fastapi import APIRouter

from src.zoom.router import router as zoom_router

api_router = APIRouter()
api_router.include_router(zoom_router)

