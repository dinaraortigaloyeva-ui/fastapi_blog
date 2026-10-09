from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import posts, users, auth
from .config import settings

# Production da docs o'chirish (ixtiyoriy)
app = FastAPI(
    title="Blog API",
    version="5.0.0",
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {
        "xabar": "Blog API",
        "version": "5.0.0",
        "environment": settings.environment
    }

# Health check — deploy platformalar uchun
@app.get("/health")
def health_check():
    return {"status": "ok"}