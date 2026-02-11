import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.api.auth import router as auth_router
from app.api.evolution import router as evolution_router
from app.core.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="No Lose SaaS",
    description="SaaS Application API",
    version="1.0.0"
)

# CORS middleware - configure origins based on environment
cors_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:80",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

# Add production domain if configured
domain = os.getenv("DOMAIN")
if domain:
    cors_origins.extend([
        f"http://{domain}",
        f"https://{domain}",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(evolution_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "No Lose SaaS API",
        "docs": "/docs",
        "health": "/api/health"
    }
