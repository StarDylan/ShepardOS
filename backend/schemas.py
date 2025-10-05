"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    photo_url: Optional[str] = None
    can_go_negative: bool = False

class UserCreate(UserBase):
    barcode: str
    account_number: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    photo_url: Optional[str] = None
    pass_revoked: Optional[bool] = None
    can_go_negative: Optional[bool] = None

class User(UserBase):
    id: int
    barcode: str
    account_number: str
    pass_revoked: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserWithPermissions(User):
    permissions: List[str] = []
    balance: float = 0.0

# Permission schemas
class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None

class PermissionCreate(PermissionBase):
    is_system: bool = False

class Permission(PermissionBase):
    id: int
    is_system: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Role schemas
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    permission_ids: List[int] = []

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permission_ids: Optional[List[int]] = None

class Role(RoleBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class RoleWithPermissions(Role):
    permissions: List[Permission] = []

# Group schemas
class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None

class GroupCreate(GroupBase):
    role_ids: List[int] = []
    user_ids: List[int] = []

class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    role_ids: Optional[List[int]] = None
    user_ids: Optional[List[int]] = None

class Group(GroupBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class GroupWithDetails(Group):
    roles: List[Role] = []
    user_count: int = 0

# Terminal schemas
class TerminalBase(BaseModel):
    name: str
    location: Optional[str] = None
    terminal_type: str = "checkpoint"
    currency_enabled: bool = False
    currency_amount: float = 0.0
    gatekeeping_enabled: bool = True
    require_permission_check: bool = True
    require_currency_debit: bool = False

class TerminalCreate(TerminalBase):
    required_permission_ids: List[int] = []

class TerminalUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    terminal_type: Optional[str] = None
    currency_enabled: Optional[bool] = None
    currency_amount: Optional[float] = None
    gatekeeping_enabled: Optional[bool] = None
    require_permission_check: Optional[bool] = None
    require_currency_debit: Optional[bool] = None
    active: Optional[bool] = None
    required_permission_ids: Optional[List[int]] = None

class Terminal(TerminalBase):
    id: int
    active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class TerminalWithDetails(Terminal):
    required_permissions: List[Permission] = []

class TerminalAuth(BaseModel):
    terminal_id: int
    key: str

class TerminalKeyResponse(BaseModel):
    terminal_id: int
    key: str
    message: str

# Transaction schemas
class TransactionCreate(BaseModel):
    from_account_number: str
    to_account_number: str
    amount: float = Field(gt=0)
    description: Optional[str] = None
    terminal_key: Optional[str] = None

class Transaction(BaseModel):
    id: int
    from_account_id: int
    to_account_id: int
    amount: float
    description: Optional[str] = None
    terminal_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class TransactionWithDetails(Transaction):
    from_account_name: str
    to_account_name: str

class Balance(BaseModel):
    account_number: str
    balance: float
    transaction_count: int

# Gatekeeping schemas
class GatekeepingCheck(BaseModel):
    barcode: str
    terminal_key: str

class GatekeepingResponse(BaseModel):
    success: bool
    user: Optional[UserWithPermissions] = None
    message: str
    required_permissions: List[str] = []
    user_permissions: List[str] = []
    missing_permissions: List[str] = []
    currency_required: bool = False
    currency_amount: float = 0.0
    current_balance: float = 0.0

# Audit log schemas
class AuditLog(BaseModel):
    id: int
    user_id: int
    terminal_id: int
    action: str
    success: bool
    details: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class AuditLogWithDetails(AuditLog):
    user_name: str
    terminal_name: str

# Search schemas
class SearchQuery(BaseModel):
    query: str
    limit: int = Field(default=20, le=100)

class SearchResult(BaseModel):
    users: List[User] = []
    total: int = 0
