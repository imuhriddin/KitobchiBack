from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, books, users, likes, categories, languages
from app.database import engine, Base

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Kitobchi - Online marketplace for buying, selling, and giving away books",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(books.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(likes.router, prefix=settings.API_V1_PREFIX)
app.include_router(categories.router, prefix=settings.API_V1_PREFIX)
app.include_router(languages.router, prefix=settings.API_V1_PREFIX)


@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    # Note: In production, use Alembic migrations instead
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Kitobchi API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

