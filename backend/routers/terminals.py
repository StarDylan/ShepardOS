"""
Terminal management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import hashlib
import secrets

from database import get_db, Terminal as DBTerminal, Permission as DBPermission
from schemas import Terminal, TerminalCreate, TerminalUpdate, TerminalWithDetails, TerminalKeyResponse

router = APIRouter()

def generate_terminal_key() -> str:
    """Generate a secure random key for terminal authentication"""
    return secrets.token_urlsafe(32)

def hash_key(key: str) -> str:
    """Hash a terminal key for storage"""
    return hashlib.sha256(key.encode()).hexdigest()

@router.post("/", response_model=TerminalKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_terminal(terminal: TerminalCreate, db: Session = Depends(get_db)):
    """Create a new terminal and return its authentication key"""
    existing = db.query(DBTerminal).filter(DBTerminal.name == terminal.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Terminal already exists"
        )
    
    # Generate and hash key
    key = generate_terminal_key()
    key_hash = hash_key(key)
    
    db_terminal = DBTerminal(
        name=terminal.name,
        location=terminal.location,
        terminal_type=terminal.terminal_type,
        key_hash=key_hash,
        currency_enabled=terminal.currency_enabled,
        currency_amount=terminal.currency_amount,
        gatekeeping_enabled=terminal.gatekeeping_enabled,
        require_permission_check=terminal.require_permission_check,
        require_currency_debit=terminal.require_currency_debit
    )
    
    # Add required permissions
    for perm_id in terminal.required_permission_ids:
        permission = db.query(DBPermission).filter(DBPermission.id == perm_id).first()
        if permission:
            db_terminal.required_permissions.append(permission)
    
    db.add(db_terminal)
    db.commit()
    db.refresh(db_terminal)
    
    return {
        "terminal_id": db_terminal.id,
        "key": key,
        "message": "Save this key securely. It cannot be recovered."
    }

@router.get("/", response_model=List[Terminal])
async def list_terminals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all terminals"""
    terminals = db.query(DBTerminal).offset(skip).limit(limit).all()
    return terminals

@router.get("/{terminal_id}", response_model=TerminalWithDetails)
async def get_terminal(terminal_id: int, db: Session = Depends(get_db)):
    """Get terminal by ID with details"""
    terminal = db.query(DBTerminal).filter(DBTerminal.id == terminal_id).first()
    if not terminal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Terminal not found")
    return terminal

@router.put("/{terminal_id}", response_model=Terminal)
async def update_terminal(terminal_id: int, terminal_update: TerminalUpdate, db: Session = Depends(get_db)):
    """Update terminal configuration"""
    db_terminal = db.query(DBTerminal).filter(DBTerminal.id == terminal_id).first()
    if not db_terminal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Terminal not found")
    
    update_data = terminal_update.model_dump(exclude_unset=True, exclude={"required_permission_ids"})
    for field, value in update_data.items():
        setattr(db_terminal, field, value)
    
    if terminal_update.required_permission_ids is not None:
        db_terminal.required_permissions.clear()
        for perm_id in terminal_update.required_permission_ids:
            permission = db.query(DBPermission).filter(DBPermission.id == perm_id).first()
            if permission:
                db_terminal.required_permissions.append(permission)
    
    db.commit()
    db.refresh(db_terminal)
    return db_terminal

@router.post("/{terminal_id}/regenerate-key", response_model=TerminalKeyResponse)
async def regenerate_terminal_key(terminal_id: int, db: Session = Depends(get_db)):
    """Regenerate authentication key for a terminal"""
    terminal = db.query(DBTerminal).filter(DBTerminal.id == terminal_id).first()
    if not terminal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Terminal not found")
    
    # Generate new key
    key = generate_terminal_key()
    key_hash = hash_key(key)
    
    terminal.key_hash = key_hash
    db.commit()
    
    return {
        "terminal_id": terminal.id,
        "key": key,
        "message": "Save this key securely. It cannot be recovered."
    }

@router.delete("/{terminal_id}")
async def delete_terminal(terminal_id: int, db: Session = Depends(get_db)):
    """Delete a terminal"""
    terminal = db.query(DBTerminal).filter(DBTerminal.id == terminal_id).first()
    if not terminal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Terminal not found")
    
    db.delete(terminal)
    db.commit()
    return {"message": "Terminal deleted"}

def verify_terminal_key(db: Session, terminal_id: int, key: str) -> bool:
    """Verify a terminal's authentication key"""
    terminal = db.query(DBTerminal).filter(DBTerminal.id == terminal_id).first()
    if not terminal or not terminal.active:
        return False
    
    return terminal.key_hash == hash_key(key)
