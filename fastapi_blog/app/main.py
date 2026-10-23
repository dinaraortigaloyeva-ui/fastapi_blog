
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from .routers import posts, users, auth
from .config import settings
from .database import get_db


# FastAPI ilovasi
app = FastAPI(
    title="Blog API",
    version="5.0.0",
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
)


# CORS sozlamalari
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routerlar
app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)


# Asosiy sahifa
@app.get("/", tags=["Health"])
def home():
    return {
        "xabar": "Blog API",
        "version": "5.0.0",
        "environment": settings.environment,
    }


# Health check — ilova va ma'lumotlar bazasini tekshirish
@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db.rollback()
        db_status = "error"

    response_data = {
        "status": "ok" if db_status == "ok" else "error",
        "database": db_status,
        "environment": settings.environment,
        "version": "5.0.0",
    }

    status_code = 200 if db_status == "ok" else 503

    return JSONResponse(
        status_code=status_code,
        content=response_data,
    )
