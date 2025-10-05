"""
Database configuration and models for ShepardOS
Uses SQLalchemy ORM with SQLite
"""
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Table, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./shepardos.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Association tables for many-to-many relationships
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id')),
    Column('permission_id', Integer, ForeignKey('permissions.id'))
)

user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

user_groups = Table(
    'user_groups',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('group_id', Integer, ForeignKey('groups.id'))
)

group_roles = Table(
    'group_roles',
    Base.metadata,
    Column('group_id', Integer, ForeignKey('groups.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

terminal_required_permissions = Table(
    'terminal_required_permissions',
    Base.metadata,
    Column('terminal_id', Integer, ForeignKey('terminals.id')),
    Column('permission_id', Integer, ForeignKey('permissions.id'))
)

class User(Base):
    """User model with identity information and barcode pass"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    barcode = Column(String, unique=True, index=True, nullable=False)
    account_number = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    date_of_birth = Column(String)
    photo_url = Column(String)
    pass_revoked = Column(Boolean, default=False)
    can_go_negative = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    groups = relationship("Group", secondary=user_groups, back_populates="users")
    transactions_from = relationship("Transaction", foreign_keys="Transaction.from_account_id", back_populates="from_account")
    transactions_to = relationship("Transaction", foreign_keys="Transaction.to_account_id", back_populates="to_account")
    audit_logs = relationship("AuditLog", back_populates="user")

class Permission(Base):
    """Permission model - named permissions without inherent meaning"""
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    is_system = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
    terminals = relationship("Terminal", secondary=terminal_required_permissions, back_populates="required_permissions")

class Role(Base):
    """Role model - groups of permissions"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    users = relationship("User", secondary=user_roles, back_populates="roles")
    groups = relationship("Group", secondary=group_roles, back_populates="roles")

class Group(Base):
    """Group model - groups of users"""
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    users = relationship("User", secondary=user_groups, back_populates="groups")
    roles = relationship("Role", secondary=group_roles, back_populates="groups")

class Terminal(Base):
    """Terminal model - configuration for each terminal with key-based auth"""
    __tablename__ = "terminals"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    location = Column(String)
    terminal_type = Column(String)  # checkpoint, currency, combined
    key_hash = Column(String, unique=True, nullable=False)
    currency_enabled = Column(Boolean, default=False)
    currency_amount = Column(Float, default=0.0)
    gatekeeping_enabled = Column(Boolean, default=True)
    require_permission_check = Column(Boolean, default=True)
    require_currency_debit = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    required_permissions = relationship("Permission", secondary=terminal_required_permissions, back_populates="terminals")
    audit_logs = relationship("AuditLog", back_populates="terminal")

class Transaction(Base):
    """Transaction model - insert-only ledger for currency"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    from_account_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    to_account_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(Text)
    terminal_id = Column(Integer, ForeignKey('terminals.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    from_account = relationship("User", foreign_keys=[from_account_id], back_populates="transactions_from")
    to_account = relationship("User", foreign_keys=[to_account_id], back_populates="transactions_to")

class AuditLog(Base):
    """Audit log for tracking user actions at terminals"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    terminal_id = Column(Integer, ForeignKey('terminals.id'), nullable=False)
    action = Column(String, nullable=False)
    success = Column(Boolean, nullable=False)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    terminal = relationship("Terminal", back_populates="audit_logs")

def init_db():
    """Initialize database and create all tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
