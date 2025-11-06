"""FastAPI application entry point"""

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings

# Initialize Sentry if DSN is provided
if settings.SENTRY_DSN:
    import sentry_sdk
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        traces_sample_rate=0.1,
    )
from app.routers import (
    auth,
    jobs,
    resume,
    cover_letter,
    outreach,
    health,
)

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

app = FastAPI(
    title="Smart Resume & Cover Letter Generator API",
    description="API for generating tailored resumes and cover letters",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(resume.router, prefix="/api/resume", tags=["resume"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(cover_letter.router, prefix="/api/cover-letter", tags=["cover-letter"])
app.include_router(outreach.router, prefix="/api/outreach", tags=["outreach"])


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """Global exception handler"""
    logger.error("Unhandled exception", exc_info=exc, path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("API server starting up", environment=settings.ENVIRONMENT)


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("API server shutting down")

