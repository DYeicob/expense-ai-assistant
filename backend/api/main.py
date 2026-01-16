from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from backend.config.settings import settings
from backend.models.database import engine, get_db, init_db, Base
from backend.models import tables
from backend.api.routes import expenses, upload, analytics, predictions

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API for intelligent personal expense management",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Event handlers
@app.on_event("startup")
async def startup_event():
    """Execute on application startup"""
    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Database: {settings.database_url}")
    
    # Initialize database
    try:
        init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
    
    # Populate categories if they don't exist
    from backend.config.constants import EXPENSE_CATEGORIES
    db = next(get_db())
    try:
        for slug, info in EXPENSE_CATEGORIES.items():
            existing = db.query(tables.Category).filter(
                tables.Category.slug == slug
            ).first()
            
            if not existing:
                category = tables.Category(
                    name=info["name"],
                    slug=slug,
                    color=info["color"],
                    icon=info["icon"],
                    keywords=info["keywords"]
                )
                db.add(category)
        
        db.commit()
        logger.info("✅ Categories initialized")
    except Exception as e:
        logger.error(f"Error initializing categories: {e}")
        db.rollback()
    finally:
        db.close()


@app.on_event("shutdown")
async def shutdown_event():
    """Execute on application shutdown"""
    logger.info("👋 Shutting down application...")


# Main routes
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Check database connection
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    }


# Include routers
app.include_router(
    expenses.router,
    prefix="/api/expenses",
    tags=["expenses"]
)

app.include_router(
    upload.router,
    prefix="/api/upload",
    tags=["upload"]
)

app.include_router(
    analytics.router,
    prefix="/api/analytics",
    tags=["analytics"]
)

app.include_router(
    predictions.router,
    prefix="/api/predictions",
    tags=["predictions"]
)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "detail": str(exc) if settings.debug else None
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
