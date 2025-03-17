from fastapi import FastAPI
from .database import engine, Base
from .routes import transactions, insights

# Create tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Finance Tracker",
    description="A basic API for tracking income and expenses",
)

# Include routers
app.include_router(transactions.router)
app.include_router(insights.router)

# Root endpoint showing API information
@app.get("/")
def root():
    return {
        "message": "Welcome to the Simple Finance Tracker API",
        "documentation": "/docs",
        "endpoints": {
            "transactions": {
                "POST /transactions/": "Create a new transaction",
                "GET /transactions/": "List all transactions",
                "GET /transactions/{id}": "Get a specific transaction",
                "PUT /transactions/{id}": "Update a transaction",
                "DELETE /transactions/{id}": "Delete a transaction",
            },
            "insights": {
                "GET /insights/summary": "Get overall financial summary",
                "GET /insights/spending-by-category": "Get spending breakdown by category",
                "GET /insights/recent-activity": "Get recent transaction activity",
                "GET /insights/monthly": "Get current month's summary"
            }
        }
    }