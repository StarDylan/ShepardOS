"""
Permission management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db, Permission as DBPermission
from schemas import Permission, PermissionCreate

router = APIRouter()

@router.post("/", response_model=Permission, status_code=status.HTTP_201_CREATED)
async def create_permission(permission: PermissionCreate, db: Session = Depends(get_db)):
    """Create a new permission"""
    existing = db.query(DBPermission).filter(DBPermission.name == permission.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission already exists"
        )
    
    db_permission = DBPermission(**permission.model_dump())
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

@router.get("/", response_model=List[Permission])
async def list_permissions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all permissions"""
    permissions = db.query(DBPermission).offset(skip).limit(limit).all()
    return permissions

@router.get("/{permission_id}", response_model=Permission)
async def get_permission(permission_id: int, db: Session = Depends(get_db)):
    """Get permission by ID"""
    permission = db.query(DBPermission).filter(DBPermission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    return permission

@router.delete("/{permission_id}")
async def delete_permission(permission_id: int, db: Session = Depends(get_db)):
    """Delete a permission (only if not a system permission)"""
    permission = db.query(DBPermission).filter(DBPermission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    
    if permission.is_system:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete system permission"
        )
    
    db.delete(permission)
    db.commit()
    return {"message": "Permission deleted"}
