"""
Currency management endpoints - insert-only ledger system
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func

from database import get_db, Transaction as DBTransaction, User as DBUser
from schemas import Transaction, TransactionCreate, TransactionWithDetails, Balance
from routers.terminals import verify_terminal_key

router = APIRouter()

def calculate_balance(db: Session, user_id: int) -> float:
    """Calculate user's current balance from transaction history"""
    incoming = db.query(func.sum(DBTransaction.amount)).filter(
        DBTransaction.to_account_id == user_id
    ).scalar() or 0.0
    
    outgoing = db.query(func.sum(DBTransaction.amount)).filter(
        DBTransaction.from_account_id == user_id
    ).scalar() or 0.0
    
    return incoming - outgoing

@router.post("/transfer", response_model=Transaction, status_code=status.HTTP_201_CREATED)
async def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    """
    Create a transaction (transfer money between accounts)
    This is an insert-only operation maintaining sum-zero currency system
    """
    # Find accounts
    from_account = db.query(DBUser).filter(
        DBUser.account_number == transaction.from_account_number
    ).first()
    if not from_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source account not found"
        )
    
    to_account = db.query(DBUser).filter(
        DBUser.account_number == transaction.to_account_number
    ).first()
    if not to_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination account not found"
        )
    
    # Verify terminal if key provided
    terminal_id = None
    if transaction.terminal_key:
        from database import Terminal as DBTerminal
        # Extract terminal_id from key or require it in request
        # For now, we'll skip terminal verification in basic transfer
        pass
    
    # Calculate current balance
    current_balance = calculate_balance(db, from_account.id)
    
    # Check if account can go negative
    if current_balance - transaction.amount < 0 and not from_account.can_go_negative:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient funds. Current balance: {current_balance}"
        )
    
    # Create transaction (insert only, never update)
    db_transaction = DBTransaction(
        from_account_id=from_account.id,
        to_account_id=to_account.id,
        amount=transaction.amount,
        description=transaction.description,
        terminal_id=terminal_id
    )
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction

@router.get("/balance/{account_number}", response_model=Balance)
async def get_balance(account_number: str, db: Session = Depends(get_db)):
    """Get current balance for an account"""
    account = db.query(DBUser).filter(DBUser.account_number == account_number).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    balance = calculate_balance(db, account.id)
    transaction_count = db.query(func.count(DBTransaction.id)).filter(
        (DBTransaction.from_account_id == account.id) | 
        (DBTransaction.to_account_id == account.id)
    ).scalar()
    
    return {
        "account_number": account_number,
        "balance": balance,
        "transaction_count": transaction_count
    }

@router.get("/transactions/{account_number}", response_model=List[TransactionWithDetails])
async def get_transactions(
    account_number: str, 
    skip: int = 0, 
    limit: int = 50, 
    db: Session = Depends(get_db)
):
    """Get transaction history for an account"""
    account = db.query(DBUser).filter(DBUser.account_number == account_number).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    transactions = db.query(DBTransaction).filter(
        (DBTransaction.from_account_id == account.id) | 
        (DBTransaction.to_account_id == account.id)
    ).order_by(DBTransaction.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for trans in transactions:
        trans_dict = Transaction.model_validate(trans).model_dump()
        trans_dict["from_account_name"] = f"{trans.from_account.first_name} {trans.from_account.last_name}"
        trans_dict["to_account_name"] = f"{trans.to_account.first_name} {trans.to_account.last_name}"
        result.append(trans_dict)
    
    return result

@router.get("/all-transactions", response_model=List[TransactionWithDetails])
async def get_all_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all transactions (admin view)"""
    transactions = db.query(DBTransaction).order_by(
        DBTransaction.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    result = []
    for trans in transactions:
        trans_dict = Transaction.model_validate(trans).model_dump()
        trans_dict["from_account_name"] = f"{trans.from_account.first_name} {trans.from_account.last_name}"
        trans_dict["to_account_name"] = f"{trans.to_account.first_name} {trans.to_account.last_name}"
        result.append(trans_dict)
    
    return result
