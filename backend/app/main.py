from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .routes import auth, intake, dashboard, teacher, survey, debug, profile

settings = get_settings()

app = FastAPI(
    title="HI FI Financial Literacy Guide API",
    description="API for student financial literacy guidance with ML risk prediction and AI teaching",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,  # type: ignore[arg-type]
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(intake.router, prefix="/api", tags=["Intake"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(teacher.router, prefix="/api/teacher", tags=["Teacher"])
app.include_router(survey.router, prefix="/api/survey", tags=["Survey"])
app.include_router(debug.router, prefix="/api/debug", tags=["Debug"])
app.include_router(profile.router, prefix="/api", tags=["Profile"])


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/")
async def root():
    """Root endpoint redirect to docs."""
    return {"message": "Student Finance Coach API", "docs": "/api/docs"}
