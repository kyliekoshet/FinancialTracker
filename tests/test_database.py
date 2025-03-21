import pytest
from sqlalchemy import text
from app.database import Base, engine, SessionLocal
from app.models import Transaction, TransactionType, CategoryType

@pytest.fixture
def db():
    """
    Test database fixture that provides a database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_database_connection(db):
    """Test that we can connect to the database"""
    result = db.execute(text("SELECT 1")).scalar()
    assert result == 1, "Database connection failed"

def test_create_tables():
    """Test that we can create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        assert True, "Tables created successfully"
    except Exception as e:
        pytest.fail(f"Failed to create tables: {str(e)}")

def test_transaction_enum_values():
    """Test that our enums have the correct values"""
    assert TransactionType.INCOME.value == "income"
    assert TransactionType.EXPENSE.value == "expense"
    
    # Test a few key category types
    assert CategoryType.SALARY.value == "salary"
    assert CategoryType.FOOD.value == "food"
    assert CategoryType.RENT.value == "rent"

def test_add_transaction(db):
    """Test that we can add a transaction to the database"""
    # Create a new transaction
    new_transaction = Transaction(
        amount=100.0,
        type=TransactionType.INCOME,
        category=CategoryType.SALARY,
        description="Test salary"
    )
    
    # Add it to the database
    db.add(new_transaction)
    db.commit()
    
    # Check that it was added correctly
    added_transaction = db.query(Transaction).filter(Transaction.description == "Test salary").first()
    assert added_transaction is not None
    assert added_transaction.amount == 100.0
    assert added_transaction.type == TransactionType.INCOME
    assert added_transaction.category == CategoryType.SALARY

def test_filter_transactions_by_type(db):
    """Test that we can filter transactions by their type"""
    # Clear existing data
    db.query(Transaction).delete()
    db.commit()
    
    # Add some test transactions
    transactions = [
        Transaction(amount=100.0, type=TransactionType.INCOME, category=CategoryType.SALARY),
        Transaction(amount=50.0, type=TransactionType.EXPENSE, category=CategoryType.FOOD),
        Transaction(amount=200.0, type=TransactionType.INCOME, category=CategoryType.INVESTMENT),
        Transaction(amount=75.0, type=TransactionType.EXPENSE, category=CategoryType.TRANSPORT)
    ]
    
    for t in transactions:
        db.add(t)
    db.commit()
    
    # Test filtering by income
    income_transactions = db.query(Transaction).filter(
        Transaction.type == TransactionType.INCOME
    ).all()
    
    assert len(income_transactions) == 2
    
    # Test filtering by expense
    expense_transactions = db.query(Transaction).filter(
        Transaction.type == TransactionType.EXPENSE
    ).all()
    
    assert len(expense_transactions) == 2

def test_update_transaction(db):
    """Test that we can update a transaction in the database"""
    # First add a transaction
    transaction = Transaction(
        amount=150.0,
        type=TransactionType.EXPENSE,
        category=CategoryType.ENTERTAINMENT,
        description="Concert tickets"
    )
    db.add(transaction)
    db.commit()
    
    # Get the transaction ID
    transaction_id = transaction.id
    
    # Update the transaction
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    db_transaction.amount = 175.0
    db_transaction.description = "Updated concert tickets"
    db.commit()
    
    # Verify the update
    updated_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    assert updated_transaction.amount == 175.0
    assert updated_transaction.description == "Updated concert tickets"
    # These should remain unchanged
    assert updated_transaction.type == TransactionType.EXPENSE
    assert updated_transaction.category == CategoryType.ENTERTAINMENT

def test_delete_transaction(db):
    """Test that we can delete a transaction from the database"""
    # First add a transaction
    transaction = Transaction(
        amount=75.0,
        type=TransactionType.EXPENSE,
        category=CategoryType.FOOD,
        description="Dinner at restaurant"
    )
    db.add(transaction)
    db.commit()
    
    # Get the transaction ID
    transaction_id = transaction.id
    
    # Verify it exists
    assert db.query(Transaction).filter(Transaction.id == transaction_id).first() is not None
    
    # Delete it
    db.query(Transaction).filter(Transaction.id == transaction_id).delete()
    db.commit()
    
    # Verify it's gone
    assert db.query(Transaction).filter(Transaction.id == transaction_id).first() is None

def test_filter_transactions_by_category(db):
    """Test that we can filter transactions by their category"""
    # Clear existing data
    db.query(Transaction).delete()
    db.commit()
    
    # Add transactions with different categories
    transactions = [
        Transaction(amount=1000.0, type=TransactionType.INCOME, category=CategoryType.SALARY),
        Transaction(amount=300.0, type=TransactionType.INCOME, category=CategoryType.INVESTMENT),
        Transaction(amount=50.0, type=TransactionType.EXPENSE, category=CategoryType.FOOD),
        Transaction(amount=30.0, type=TransactionType.EXPENSE, category=CategoryType.FOOD),
        Transaction(amount=200.0, type=TransactionType.EXPENSE, category=CategoryType.RENT),
        Transaction(amount=40.0, type=TransactionType.EXPENSE, category=CategoryType.TRANSPORT)
    ]
    
    for t in transactions:
        db.add(t)
    db.commit()
    
    # Test filtering by the FOOD category
    food_transactions = db.query(Transaction).filter(
        Transaction.category == CategoryType.FOOD
    ).all()
    
    assert len(food_transactions) == 2
    for t in food_transactions:
        assert t.category == CategoryType.FOOD
    
    # Test filtering by the SALARY category
    salary_transactions = db.query(Transaction).filter(
        Transaction.category == CategoryType.SALARY
    ).all()
    
    assert len(salary_transactions) == 1
    assert salary_transactions[0].amount == 1000.0 