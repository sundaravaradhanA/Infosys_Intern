from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import auth, accounts, transactions, budgets, bills, rewards, alerts, insights, categories, currency
from app.services.reminder_service import start_scheduler

app = FastAPI(
    title="Digital Banking API",
    description="Modern Banking Application API",
    version="1.0.0"
)

# ---------------- CORS Middleware ----------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Register Routes ----------------

app.include_router(auth.router)
app.include_router(accounts.router, prefix="/accounts")
app.include_router(transactions.router, prefix="/transactions")
app.include_router(budgets.router, prefix="/budgets")
app.include_router(bills.router, prefix="/bills")
app.include_router(rewards.router, prefix="/rewards")
app.include_router(alerts.router, prefix="/alerts")
app.include_router(insights.router, prefix="/insights")
app.include_router(categories.router)
app.include_router(currency.router, prefix="/currency")

# ---------------- Start Scheduler ----------------

@app.on_event("startup")
def start_background_tasks():
    start_scheduler()


# ---------------- Root ----------------

@app.get("/")
def root():
    return {
        "message": "Digital Banking API is running",
        "version": "1.0.0"
    }


# ---------------- Health ----------------

@app.get("/health")
def health_check():
    return {"status": "healthy"}