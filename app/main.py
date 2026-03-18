from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import auth, accounts, transactions, budgets, bills, rewards, alerts, insights, categories
from app.services.reminder_service import start_scheduler
from app.routes import currency

app = FastAPI(
    title="Digital Banking API",
    description="Modern Banking Application API",
    version="1.0.0"
)

# ---------------- CORS Middleware ----------------A
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
app.include_router(insights.router, prefix="/insights", tags=["Insights"])
app.include_router(categories.router, prefix="", tags=["Categories"])
app.include_router(currency.router, prefix="/currency", tags=["Currency"])
# ---------------- Start Scheduler ----------------
@app.on_event("startup")
def start_background_tasks():
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