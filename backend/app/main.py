from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.api import router as api_router
from backend.app.model import global_risk_engine
from backend.app.ingestion import load_and_validate_dataset

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="SentinelRisk Transaction Risk & Fraud Decision Intelligence Platform API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.on_event("startup")
def startup_event():
    """On startup, load model artifact or perform training if model file does not exist."""
    print("[*] Starting SentinelRisk Backend Engine...")
    if not global_risk_engine.load_model():
        print("[*] No pre-trained model artifact found. Initiating model training pipeline on real dataset...")
        try:
            df, _ = load_and_validate_dataset()
            global_risk_engine.train_pipeline(df)
        except Exception as e:
            print(f"[!] Warning: Model initial training skipped on startup: {e}")

@app.get("/")
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": f"{settings.API_PREFIX}/health"
    }
