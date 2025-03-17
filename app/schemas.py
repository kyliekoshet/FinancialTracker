from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from .models import TransactionType, CategoryType

class TransactionBase(BaseModel):
    amount: float = Field(..., gt=0)
    type: TransactionType
    category: CategoryType = CategoryType.OTHER
    description: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    type: Optional[TransactionType] = None
    category: Optional[CategoryType] = None
    description: Optional[str] = None

class Transaction(TransactionBase):
    id: int
    date: datetime

    class Config:
        from_attributes = True 