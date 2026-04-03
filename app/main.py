from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import (
    auth, accounts, transactions, budgets,
    bills, rewards, alerts, insights, categories, currency
)
import app.routes.export as export

# ✅ Scheduler
from app.services.scheduler import start_scheduler

# ✅ IMPORTANT: DB setup
from app.database import Base, engine


app = FastAPI(
    title="Digital Banking API",
    description="Modern Banking Application API",
    version="1.0.0"
)


# ---------------- CORS Middleware ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # ⚠️ restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- Register Routes ----------------
app.include_router(auth.router, prefix="", tags=["Auth"])
app.include_router(accounts.router, prefix="/accounts", tags=["Accounts"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(budgets.router, prefix="/budgets", tags=["Budgets"])
app.include_router(bills.router, prefix="/bills", tags=["Bills"])
app.include_router(rewards.router, prefix="/rewards", tags=["Rewards"])
app.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])

# ✅ Insights
app.include_router(insights.router, prefix="/insights", tags=["Insights"])

app.include_router(categories.router, prefix="", tags=["Categories"])
app.include_router(currency.router, prefix="/currency", tags=["Currency"])

# ✅ Export APIs
app.include_router(export.router)


# ---------------- Startup Event ----------------
@app.on_event("startup")
def start_background_tasks():
    print("🚀 Starting background scheduler...")

    # ✅ FIX: CREATE ALL TABLES (VERY IMPORTANT)
    Base.metadata.create_all(bind=engine)

    # ✅ Start scheduler
    start_scheduler()


# ---------------- Root Endpoint ----------------
@app.get("/")
def root():
    return {
        "message": "Digital Banking API is running",
        "version": "1.0.0"
    }


# ---------------- Health Check ----------------
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }