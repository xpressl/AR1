"""
AR Control Hub - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

from src.api.routes import customers, invoices, payments, notes, alerts, tasks, auth, dashboard, reports
from src.db.connection import init_db, close_db

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting AR Control Hub API...")
    await init_db()
    logger.info("Database connection initialized")
    yield
    # Shutdown
    logger.info("Shutting down AR Control Hub API...")
    await close_db()
    logger.info("Database connection closed")


# Create FastAPI application
app = FastAPI(
    title="AR Control Hub API",
    description="Accounts Receivable Management System for Building Supplies",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for container orchestration"""
    return {
        "status": "healthy",
        "service": "ar-control-hub-api",
        "version": "1.0.0"
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "AR Control Hub API",
        "docs": "/docs",
        "health": "/health"
    }


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(customers.router, prefix="/api/customers", tags=["Customers"])
app.include_router(invoices.router, prefix="/api/invoices", tags=["Invoices"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(notes.router, prefix="/api/notes", tags=["Notes"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("ENVIRONMENT") == "development"
    )
