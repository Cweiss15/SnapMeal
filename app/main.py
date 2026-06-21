from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import upload
from app.routers.auth import router as auth_router
from app.routers.preferences import router as preferences_router
from app.routers.favorites import router as favorites_router
from app.database import engine, Base
from app.models import *  # noqa: F401, F403 — ensure models are registered

app = FastAPI(title="SnapMeal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(upload.router)
app.include_router(preferences_router)
app.include_router(favorites_router)
