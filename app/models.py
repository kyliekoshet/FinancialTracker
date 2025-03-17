from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.sql import func
import enum
from .database import Base

class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"

class CategoryType(str, enum.Enum):
    SALARY = "salary"
    INVESTMENT = "investment"
    FOOD = "food"
    RENT = "rent"
    UTILITIES = "utilities"
    GIFT = "gift"
    TRAVEL = "travel"
    SHOPPING = "shopping"
    ENTERTAINMENT = "entertainment"
    ACCOMMODATION = "accommodation"
    HEALTH = "health"
    GROCERIES = "groceries"
    SUBSCRIPTIONS = "subscriptions"
    CAR = "car"
    TRANSPORT = "transport"
    OTHER = "other"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    category = Column(Enum(CategoryType), nullable=False, default=CategoryType.OTHER)
    description = Column(String, nullable=True)
    date = Column(DateTime, default=func.now(), nullable=False) 