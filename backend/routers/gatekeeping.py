"""
Gatekeeping verification endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db, User as DBUser, Terminal as DBTerminal, AuditLog as DBAuditLog
from schemas import GatekeepingCheck, GatekeepingResponse, UserWithPermissions
from routers.terminals import verify_terminal_key, hash_key
from routers.users import get_user_permissions, calculate_balance

router = APIRouter()

@router.post("/verify", response_model=GatekeepingResponse)
async def verify_access(check: GatekeepingCheck, db: Session = Depends(get_db)):
    """
    Verify user access at a terminal
    Checks barcode, permissions, currency requirements, and logs the attempt
    """
    # Find terminal by key hash
    terminal = db.query(DBTerminal).filter(
        DBTerminal.key_hash == hash_key(check.terminal_key)
    ).first()
    
    if not terminal:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid terminal key"
        )
    
    if not terminal.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Terminal is not active"
        )
    
    # Find user by barcode
    user = db.query(DBUser).filter(DBUser.barcode == check.barcode).first()
    
    if not user:
        # Log failed attempt
        audit_log = DBAuditLog(
            user_id=0,  # Unknown user
            terminal_id=terminal.id,
            action="access_verification",
            success=False,
            details=f"Invalid barcode: {check.barcode}"
        )
        db.add(audit_log)
        db.commit()
        
        return GatekeepingResponse(
            success=False,
            message="Invalid barcode",
            required_permissions=[],
            user_permissions=[],
            missing_permissions=[]
        )
    
    # Check if pass is revoked
    if user.pass_revoked:
        audit_log = DBAuditLog(
            user_id=user.id,
            terminal_id=terminal.id,
            action="access_verification",
            success=False,
            details="Pass revoked"
        )
        db.add(audit_log)
        db.commit()
        
        return GatekeepingResponse(
            success=False,
            user=None,
            message="Pass has been revoked",
            required_permissions=[],
            user_permissions=[],
            missing_permissions=[]
        )
    
    # Get user permissions
    user_permissions = get_user_permissions(db, user.id)
    required_permissions = [p.name for p in terminal.required_permissions]
    
    # Check permissions if required
    permission_check_passed = True
    missing_permissions = []
    
    if terminal.require_permission_check and terminal.gatekeeping_enabled:
        missing_permissions = [p for p in required_permissions if p not in user_permissions]
        permission_check_passed = len(missing_permissions) == 0
    
    # Check currency if required
    currency_check_passed = True
    current_balance = calculate_balance(db, user.id)
    
    if terminal.require_currency_debit and terminal.currency_enabled:
        if current_balance - terminal.currency_amount < 0 and not user.can_go_negative:
            currency_check_passed = False
    
    # Determine overall success
    success = permission_check_passed and currency_check_passed
    
    # Prepare user info
    user_dict = {
        "id": user.id,
        "barcode": user.barcode,
        "account_number": user.account_number,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone": user.phone,
        "date_of_birth": user.date_of_birth,
        "photo_url": user.photo_url,
        "pass_revoked": user.pass_revoked,
        "can_go_negative": user.can_go_negative,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "permissions": user_permissions,
        "balance": current_balance
    }
    
    # Log the attempt
    details = []
    if not permission_check_passed:
        details.append(f"Missing permissions: {', '.join(missing_permissions)}")
    if not currency_check_passed:
        details.append(f"Insufficient funds: {current_balance} < {terminal.currency_amount}")
    
    audit_log = DBAuditLog(
        user_id=user.id,
        terminal_id=terminal.id,
        action="access_verification",
        success=success,
        details="; ".join(details) if details else "Access granted"
    )
    db.add(audit_log)
    db.commit()
    
    # Build response message
    message_parts = []
    if success:
        message_parts.append("Access granted")
    else:
        if not permission_check_passed:
            message_parts.append(f"Missing permissions: {', '.join(missing_permissions)}")
        if not currency_check_passed:
            message_parts.append(f"Insufficient funds (need {terminal.currency_amount}, have {current_balance})")
    
    return GatekeepingResponse(
        success=success,
        user=user_dict,
        message=" | ".join(message_parts) if message_parts else "Access granted",
        required_permissions=required_permissions,
        user_permissions=user_permissions,
        missing_permissions=missing_permissions,
        currency_required=terminal.require_currency_debit,
        currency_amount=terminal.currency_amount,
        current_balance=current_balance
    )

@router.post("/process", response_model=GatekeepingResponse)
async def process_access(check: GatekeepingCheck, db: Session = Depends(get_db)):
    """
    Process access at a terminal (verify and execute currency debit if configured)
    """
    # First verify access
    verification = await verify_access(check, db)
    
    if not verification.success:
        return verification
    
    # If currency debit is required and enabled, create transaction
    terminal = db.query(DBTerminal).filter(
        DBTerminal.key_hash == hash_key(check.terminal_key)
    ).first()
    
    if terminal.require_currency_debit and terminal.currency_enabled and terminal.currency_amount > 0:
        from database import Transaction as DBTransaction
        
        user = db.query(DBUser).filter(DBUser.barcode == check.barcode).first()
        
        # Find or create system account for terminal currency collection
        system_account = db.query(DBUser).filter(
            DBUser.account_number == "SYSTEM_TERMINAL"
        ).first()
        
        if not system_account:
            # Create system account
            system_account = DBUser(
                barcode="SYSTEM000000",
                account_number="SYSTEM_TERMINAL",
                first_name="System",
                last_name="Terminal",
                can_go_negative=True
            )
            db.add(system_account)
            db.commit()
            db.refresh(system_account)
        
        # Create transaction
        transaction = DBTransaction(
            from_account_id=user.id,
            to_account_id=system_account.id,
            amount=terminal.currency_amount,
            description=f"Terminal access fee - {terminal.name}",
            terminal_id=terminal.id
        )
        db.add(transaction)
        db.commit()
        
        # Update balance in response
        verification.current_balance = calculate_balance(db, user.id)
        verification.message += f" | Debited {terminal.currency_amount} from account"
    
    return verification
