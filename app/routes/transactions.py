from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models import TransactionType, CategoryType, Transaction
from ..schemas import Transaction as TransactionSchema
from ..schemas import TransactionCreate, TransactionUpdate

# Create router instance
router = APIRouter(prefix="/transactions")

# Database Operations
def get_transaction(db: Session, transaction_id: int) -> Optional[Transaction]:
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()

def get_transactions(db: Session, skip: int = 0, limit: int = 100) -> List[Transaction]:
    return db.query(Transaction).offset(skip).limit(limit).all()

def create_transaction(db: Session, transaction: TransactionCreate) -> Transaction:
    db_transaction = Transaction(
        amount=transaction.amount,
        type=transaction.type,
        category=transaction.category
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def update_transaction(
    db: Session, 
    transaction_id: int, 
    transaction_update: TransactionUpdate
) -> Optional[Transaction]:
    db_transaction = get_transaction(db, transaction_id)
    if db_transaction is None:
        return None
        
    update_data = transaction_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_transaction, key, value)
    
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def delete_transaction(db: Session, transaction_id: int) -> bool:
    db_transaction = get_transaction(db, transaction_id)
    if db_transaction is None:
        return False
        
    db.delete(db_transaction)
    db.commit()
    return True

# API Routes
@router.post("/", response_model=TransactionSchema, status_code=status.HTTP_201_CREATED)
def create_transaction_route(
    amount: float,
    type: str,
    category: str = "OTHER",
    db: Session = Depends(get_db)
):
    try:
        # Convert string inputs to proper enums
        try:
            transaction_type = TransactionType(type.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid transaction type. Must be one of: {[t.value for t in TransactionType]}"
            )

        try:
            category_type = CategoryType(category.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category. Must be one of: {[c.value for c in CategoryType]}"
            )

        transaction_data = TransactionCreate(
            amount=amount,
            type=transaction_type,
            category=category_type
        )
        return create_transaction(db=db, transaction=transaction_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=List[TransactionSchema])
def read_transactions_route(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        return get_transactions(db, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch transactions")

@router.get("/{transaction_id}", response_model=TransactionSchema)
def read_transaction_route(transaction_id: int, db: Session = Depends(get_db)):
    transaction = get_transaction(db, transaction_id=transaction_id)
    if transaction is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Transaction with id {transaction_id} not found"
        )
    return transaction

@router.put("/{transaction_id}", response_model=TransactionSchema)
def update_transaction_route(
    transaction_id: int,
    transaction: TransactionUpdate,
    db: Session = Depends(get_db)
):
    updated_transaction = update_transaction(
        db, 
        transaction_id=transaction_id, 
        transaction_update=transaction
    )
    if updated_transaction is None:
        raise HTTPException(
            status_code=404,
            detail=f"Transaction with id {transaction_id} not found"
        )
    return updated_transaction

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction_route(transaction_id: int, db: Session = Depends(get_db)):
    if not delete_transaction(db, transaction_id=transaction_id):
        raise HTTPException(
            status_code=404,
            detail=f"Transaction with id {transaction_id} not found"
        )
    return None
