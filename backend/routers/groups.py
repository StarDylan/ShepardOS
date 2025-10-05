"""
Group management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db, Group as DBGroup, Role as DBRole, User as DBUser
from schemas import Group, GroupCreate, GroupUpdate, GroupWithDetails

router = APIRouter()

@router.post("/", response_model=Group, status_code=status.HTTP_201_CREATED)
async def create_group(group: GroupCreate, db: Session = Depends(get_db)):
    """Create a new group with roles and users"""
    existing = db.query(DBGroup).filter(DBGroup.name == group.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Group already exists"
        )
    
    db_group = DBGroup(name=group.name, description=group.description)
    
    # Add roles
    for role_id in group.role_ids:
        role = db.query(DBRole).filter(DBRole.id == role_id).first()
        if role:
            db_group.roles.append(role)
    
    # Add users
    for user_id in group.user_ids:
        user = db.query(DBUser).filter(DBUser.id == user_id).first()
        if user:
            db_group.users.append(user)
    
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

@router.get("/", response_model=List[GroupWithDetails])
async def list_groups(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all groups with details"""
    groups = db.query(DBGroup).offset(skip).limit(limit).all()
    result = []
    for group in groups:
        group_dict = Group.model_validate(group).model_dump()
        group_dict["roles"] = group.roles
        group_dict["user_count"] = len(group.users)
        result.append(group_dict)
    return result

@router.get("/{group_id}", response_model=GroupWithDetails)
async def get_group(group_id: int, db: Session = Depends(get_db)):
    """Get group by ID with details"""
    group = db.query(DBGroup).filter(DBGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    
    group_dict = Group.model_validate(group).model_dump()
    group_dict["roles"] = group.roles
    group_dict["user_count"] = len(group.users)
    return group_dict

@router.put("/{group_id}", response_model=Group)
async def update_group(group_id: int, group_update: GroupUpdate, db: Session = Depends(get_db)):
    """Update group information, roles, and users"""
    db_group = db.query(DBGroup).filter(DBGroup.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    
    if group_update.name is not None:
        db_group.name = group_update.name
    if group_update.description is not None:
        db_group.description = group_update.description
    
    if group_update.role_ids is not None:
        db_group.roles.clear()
        for role_id in group_update.role_ids:
            role = db.query(DBRole).filter(DBRole.id == role_id).first()
            if role:
                db_group.roles.append(role)
    
    if group_update.user_ids is not None:
        db_group.users.clear()
        for user_id in group_update.user_ids:
            user = db.query(DBUser).filter(DBUser.id == user_id).first()
            if user:
                db_group.users.append(user)
    
    db.commit()
    db.refresh(db_group)
    return db_group

@router.delete("/{group_id}")
async def delete_group(group_id: int, db: Session = Depends(get_db)):
    """Delete a group"""
    group = db.query(DBGroup).filter(DBGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    
    db.delete(group)
    db.commit()
    return {"message": "Group deleted"}
