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

def seed_demo_cases():
    """Seeds initial demonstration cases into the database if the cases table is empty."""
    from backend.app.db import SessionLocal
    from backend.app.models import Case
    from backend.app.schemas import TransactionCreate
    from backend.app.api import score_single_transaction

    db = SessionLocal()
    try:
        if db.query(Case).count() == 0:
            print("[*] Seeding initial demonstration investigation cases into database...")
            demo_txs = [
                TransactionCreate(
                    amount=3850.00,
                    time=10800.0, # 3 AM
                    pca_features={"V14": -6.8, "V12": -4.2, "V10": -3.5},
                    is_synthetic=True,
                    ground_truth_label=1
                ),
                TransactionCreate(
                    amount=1290.00,
                    time=14400.0, # 4 AM
                    pca_features={"V14": -4.1, "V12": -3.0},
                    is_synthetic=True,
                    ground_truth_label=1
                ),
                TransactionCreate(
                    amount=2950.00,
                    time=54000.0,
                    pca_features={"V1": -1.5, "V2": 2.2},
                    is_synthetic=True,
                    ground_truth_label=0
                ),
                TransactionCreate(
                    amount=680.00,
                    time=7200.0,
                    pca_features={"V14": -5.2},
                    is_synthetic=True,
                    ground_truth_label=1
                )
            ]
            for tx in demo_txs:
                score_single_transaction(tx, db)
            print("[✓] Initial investigation queue seeded successfully!")
    except Exception as e:
        print(f"[!] Seeding skipped: {e}")
    finally:
        db.close()

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
    
    # Seed demo cases for immediate queue visibility
    seed_demo_cases()

@app.get("/")
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": f"{settings.API_PREFIX}/health"
    }
