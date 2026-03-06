"""
Nova AI Service - FastAPI Application (V2)
Entry point for the application. Configures app, middleware, and routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.config import get_settings
from routers import verification, ideas, assets, universal_validation, scoring_v2, comparison, chat, grounded
import logging

# Configure logging globally (Python Pro best practice)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings = get_settings()
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} Starting...")
    logger.info(f"Mode: {'DEBUG' if settings.DEBUG else 'PRODUCTION'}")
    yield
    # Shutdown
    logger.info(f"{settings.APP_NAME} Shutting down...")

def create_app() -> FastAPI:
    settings = get_settings()
    
    app = FastAPI(
        title=settings.APP_NAME,
        description="AI-powered idea generation and validation service",
        version=settings.APP_VERSION,
        lifespan=lifespan
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include Routers
    app.include_router(verification.router)
    app.include_router(ideas.router)
    app.include_router(assets.router)
    app.include_router(universal_validation.router)  # Universal validation
    app.include_router(scoring_v2.router)  # Deterministic Scoring V2
    app.include_router(comparison.router)  # Smart Comparison Search
    app.include_router(chat.router)  # Conversational Orchestrator
    app.include_router(grounded.router)  # Grounded Generators (Zero Hallucination)

    return app

app = create_app()

@app.get("/")
async def root():
    return {"message": "Nova AI Service V2 (FastAPI)", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

