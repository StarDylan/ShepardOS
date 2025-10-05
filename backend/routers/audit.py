"""
Audit log endpoints for tracking user actions
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db, AuditLog as DBAuditLog
from schemas import AuditLog, AuditLogWithDetails

router = APIRouter()

@router.get("/", response_model=List[AuditLogWithDetails])
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    terminal_id: Optional[int] = None,
    success: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get audit logs with optional filters"""
    query = db.query(DBAuditLog)
    
    if user_id is not None:
        query = query.filter(DBAuditLog.user_id == user_id)
    if terminal_id is not None:
        query = query.filter(DBAuditLog.terminal_id == terminal_id)
    if success is not None:
        query = query.filter(DBAuditLog.success == success)
    
    logs = query.order_by(DBAuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for log in logs:
        log_dict = AuditLog.model_validate(log).model_dump()
        
        if log.user_id > 0:
            log_dict["user_name"] = f"{log.user.first_name} {log.user.last_name}"
        else:
            log_dict["user_name"] = "Unknown"
        
        log_dict["terminal_name"] = log.terminal.name
        result.append(log_dict)
    
    return result

@router.get("/{log_id}", response_model=AuditLogWithDetails)
async def get_audit_log(log_id: int, db: Session = Depends(get_db)):
    """Get a specific audit log entry"""
    log = db.query(DBAuditLog).filter(DBAuditLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit log not found")
    
    log_dict = AuditLog.model_validate(log).model_dump()
    
    if log.user_id > 0:
        log_dict["user_name"] = f"{log.user.first_name} {log.user.last_name}"
    else:
        log_dict["user_name"] = "Unknown"
    
    log_dict["terminal_name"] = log.terminal.name
    return log_dict
