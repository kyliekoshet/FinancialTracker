from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List
from datetime import datetime, timedelta

from ..database import get_db
from ..models import Transaction, TransactionType, CategoryType

router = APIRouter(prefix="/insights")

# Database Operations
def get_total_by_type(db: Session, type: TransactionType) -> float:
    """Calculate total amount for a specific transaction type"""
    total = db.query(func.sum(Transaction.amount))\
        .filter(Transaction.type == type)\
        .scalar()
    return float(total) if total is not None else 0.0

def get_spending_by_category(db: Session) -> Dict[str, float]:
    """Calculate total spending by category"""
    results = db.query(
        Transaction.category,
        func.sum(Transaction.amount)
    ).filter(
        Transaction.type == TransactionType.EXPENSE
    ).group_by(
        Transaction.category
    ).all()
    
    return {
        category.value: float(total) 
        for category, total in results
    }

def get_recent_transactions(
    db: Session,
    days: int = 30,
    type: TransactionType = None
) -> List[Transaction]:
    """Get transactions from the last N days, optionally filtered by type"""
    query = db.query(Transaction)\
        .filter(Transaction.date >= datetime.now() - timedelta(days=days))
    
    if type:
        query = query.filter(Transaction.type == type)
    
    return query.all()

def get_monthly_summary(db: Session) -> Dict[str, float]:
    """Calculate financial summary for the current month"""
    start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    income = db.query(func.sum(Transaction.amount))\
        .filter(
            Transaction.type == TransactionType.INCOME,
            Transaction.date >= start_of_month
        ).scalar()
    
    expenses = db.query(func.sum(Transaction.amount))\
        .filter(
            Transaction.type == TransactionType.EXPENSE,
            Transaction.date >= start_of_month
        ).scalar()
    
    return {
        "income": float(income) if income else 0.0,
        "expenses": float(expenses) if expenses else 0.0,
        "balance": float(income if income else 0) - float(expenses if expenses else 0)
    }

# API Routes
@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    """Get overall financial summary"""
    try:
        total_income = get_total_by_type(db, TransactionType.INCOME)
        total_expenses = get_total_by_type(db, TransactionType.EXPENSE)
        
        return {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_balance": total_income - total_expenses,
            "monthly_summary": get_monthly_summary(db)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate financial summary: {str(e)}"
        )

@router.get("/spending-by-category")
def get_category_spending(db: Session = Depends(get_db)):
    """Get breakdown of spending by category"""
    try:
        spending = get_spending_by_category(db)
        return {
            "categories": spending,
            "total": sum(spending.values())
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to calculate spending by category"
        )

@router.get("/recent-activity")
def get_activity(
    days: int = 30,
    type: str = None,
    db: Session = Depends(get_db)
):
    """Get recent transaction activity"""
    try:
        # Convert type string to enum if provided
        transaction_type = None
        if type:
            try:
                transaction_type = TransactionType(type.lower())
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid transaction type. Must be one of: {[t.value for t in TransactionType]}"
                )
        
        transactions = get_recent_transactions(db, days, transaction_type)
        
        return {
            "period_days": days,
            "transaction_type": type,
            "count": len(transactions),
            "transactions": transactions
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch recent activity"
        )

@router.get("/monthly")
def get_month_summary(db: Session = Depends(get_db)):
    """Get current month's financial summary"""
    try:
        summary = get_monthly_summary(db)
        return {
            "month": datetime.now().strftime("%B %Y"),
            "income": summary["income"],
            "expenses": summary["expenses"],
            "balance": summary["balance"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate monthly summary"
        ) 