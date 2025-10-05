"""
User management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import or_, func

from database import get_db, User as DBUser
from schemas import User, UserCreate, UserUpdate, UserWithPermissions, SearchQuery, SearchResult
import secrets

router = APIRouter()

def generate_barcode() -> str:
    """Generate a unique 12-digit barcode"""
    return ''.join([str(secrets.randbelow(10)) for _ in range(12)])

def generate_account_number() -> str:
    """Generate a unique 16-digit account number"""
    return ''.join([str(secrets.randbelow(10)) for _ in range(16)])

def calculate_balance(db: Session, user_id: int) -> float:
    """Calculate user's current balance from transaction history"""
    from database import Transaction as DBTransaction
    
    incoming = db.query(func.sum(DBTransaction.amount)).filter(
        DBTransaction.to_account_id == user_id
    ).scalar() or 0.0
    
    outgoing = db.query(func.sum(DBTransaction.amount)).filter(
        DBTransaction.from_account_id == user_id
    ).scalar() or 0.0
    
    return incoming - outgoing

def get_user_permissions(db: Session, user_id: int) -> List[str]:
    """Get all permissions for a user from roles and groups"""
    from database import Permission as DBPermission
    
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        return []
    
    permissions = set()
    
    # Get permissions from user's roles
    for role in user.roles:
        for perm in role.permissions:
            permissions.add(perm.name)
    
    # Get permissions from user's groups' roles
    for group in user.groups:
        for role in group.roles:
            for perm in role.permissions:
                permissions.add(perm.name)
    
    return list(permissions)

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user with barcode and account number"""
    # Check if barcode or account number already exists
    existing = db.query(DBUser).filter(
        or_(DBUser.barcode == user.barcode, DBUser.account_number == user.account_number)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Barcode or account number already exists"
        )
    
    db_user = DBUser(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/search", response_model=SearchResult)
async def search_users(query: str, limit: int = 20, db: Session = Depends(get_db)):
    """Search users by name, barcode, or account number"""
    search_pattern = f"%{query}%"
    users = db.query(DBUser).filter(
        or_(
            DBUser.first_name.ilike(search_pattern),
            DBUser.last_name.ilike(search_pattern),
            DBUser.barcode.ilike(search_pattern),
            DBUser.account_number.ilike(search_pattern),
            DBUser.email.ilike(search_pattern)
        )
    ).limit(limit).all()
    
    total = db.query(func.count(DBUser.id)).filter(
        or_(
            DBUser.first_name.ilike(search_pattern),
            DBUser.last_name.ilike(search_pattern),
            DBUser.barcode.ilike(search_pattern),
            DBUser.account_number.ilike(search_pattern),
            DBUser.email.ilike(search_pattern)
        )
    ).scalar()
    
    return {"users": users, "total": total}

@router.get("/{user_id}", response_model=UserWithPermissions)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID with permissions and balance"""
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user_dict = User.model_validate(user).model_dump()
    user_dict["permissions"] = get_user_permissions(db, user_id)
    user_dict["balance"] = calculate_balance(db, user_id)
    
    return user_dict

@router.get("/barcode/{barcode}", response_model=UserWithPermissions)
async def get_user_by_barcode(barcode: str, db: Session = Depends(get_db)):
    """Get user by barcode with permissions and balance"""
    user = db.query(DBUser).filter(DBUser.barcode == barcode).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user_dict = User.model_validate(user).model_dump()
    user_dict["permissions"] = get_user_permissions(db, user.id)
    user_dict["balance"] = calculate_balance(db, user.id)
    
    return user_dict

@router.get("/account/{account_number}", response_model=UserWithPermissions)
async def get_user_by_account(account_number: str, db: Session = Depends(get_db)):
    """Get user by account number with permissions and balance"""
    user = db.query(DBUser).filter(DBUser.account_number == account_number).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user_dict = User.model_validate(user).model_dump()
    user_dict["permissions"] = get_user_permissions(db, user.id)
    user_dict["balance"] = calculate_balance(db, user.id)
    
    return user_dict

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """Update user information"""
    db_user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/{user_id}/roles/{role_id}")
async def add_role_to_user(user_id: int, role_id: int, db: Session = Depends(get_db)):
    """Add a role to a user"""
    from database import Role as DBRole
    
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    role = db.query(DBRole).filter(DBRole.id == role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    
    if role not in user.roles:
        user.roles.append(role)
        db.commit()
    
    return {"message": "Role added to user"}

@router.delete("/{user_id}/roles/{role_id}")
async def remove_role_from_user(user_id: int, role_id: int, db: Session = Depends(get_db)):
    """Remove a role from a user"""
    from database import Role as DBRole
    
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    role = db.query(DBRole).filter(DBRole.id == role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    
    if role in user.roles:
        user.roles.remove(role)
        db.commit()
    
    return {"message": "Role removed from user"}

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete a user"""
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}

@router.post("/generate", response_model=dict)
async def generate_credentials(db: Session = Depends(get_db)):
    """Generate unique barcode and account number for a new user"""
    # Generate unique barcode
    barcode = generate_barcode()
    while db.query(DBUser).filter(DBUser.barcode == barcode).first():
        barcode = generate_barcode()
    
    # Generate unique account number
    account_number = generate_account_number()
    while db.query(DBUser).filter(DBUser.account_number == account_number).first():
        account_number = generate_account_number()
    
    return {"barcode": barcode, "account_number": account_number}
