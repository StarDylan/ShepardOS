"""
Role management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db, Role as DBRole, Permission as DBPermission
from schemas import Role, RoleCreate, RoleUpdate, RoleWithPermissions

router = APIRouter()

@router.post("/", response_model=Role, status_code=status.HTTP_201_CREATED)
async def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    """Create a new role with permissions"""
    existing = db.query(DBRole).filter(DBRole.name == role.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role already exists"
        )
    
    db_role = DBRole(name=role.name, description=role.description)
    
    # Add permissions
    for perm_id in role.permission_ids:
        permission = db.query(DBPermission).filter(DBPermission.id == perm_id).first()
        if permission:
            db_role.permissions.append(permission)
    
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

@router.get("/", response_model=List[Role])
async def list_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all roles"""
    roles = db.query(DBRole).offset(skip).limit(limit).all()
    return roles

@router.get("/{role_id}", response_model=RoleWithPermissions)
async def get_role(role_id: int, db: Session = Depends(get_db)):
    """Get role by ID with permissions"""
    role = db.query(DBRole).filter(DBRole.id == role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return role

@router.put("/{role_id}", response_model=Role)
async def update_role(role_id: int, role_update: RoleUpdate, db: Session = Depends(get_db)):
    """Update role information and permissions"""
    db_role = db.query(DBRole).filter(DBRole.id == role_id).first()
    if not db_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    
    if role_update.name is not None:
        db_role.name = role_update.name
    if role_update.description is not None:
        db_role.description = role_update.description
    
    if role_update.permission_ids is not None:
        db_role.permissions.clear()
        for perm_id in role_update.permission_ids:
            permission = db.query(DBPermission).filter(DBPermission.id == perm_id).first()
            if permission:
                db_role.permissions.append(permission)
    
    db.commit()
    db.refresh(db_role)
    return db_role

@router.delete("/{role_id}")
async def delete_role(role_id: int, db: Session = Depends(get_db)):
    """Delete a role"""
    role = db.query(DBRole).filter(DBRole.id == role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    
    db.delete(role)
    db.commit()
    return {"message": "Role deleted"}
