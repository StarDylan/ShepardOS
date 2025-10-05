"""
Seed database with initial data for testing
"""
from database import SessionLocal, init_db
from database import User, Permission, Role, Group, Terminal
from routers.terminals import hash_key
import secrets

def seed_database():
    """Seed the database with initial data"""
    db = SessionLocal()
    
    try:
        print("Seeding database...")
        
        # Create system permissions
        permissions = [
            Permission(name="system.admin", description="Full system administration", is_system=True),
            Permission(name="system.manage_users", description="Manage users", is_system=True),
            Permission(name="system.manage_terminals", description="Manage terminals", is_system=True),
            Permission(name="checkpoint.a.access", description="Access Checkpoint A", is_system=False),
            Permission(name="checkpoint.a.login", description="Login at Checkpoint A", is_system=False),
            Permission(name="checkpoint.b.access", description="Access Checkpoint B", is_system=False),
            Permission(name="store.purchase", description="Make purchases at store", is_system=False),
            Permission(name="facility.entry", description="Enter facility", is_system=False),
        ]
        
        for perm in permissions:
            existing = db.query(Permission).filter(Permission.name == perm.name).first()
            if not existing:
                db.add(perm)
        db.commit()
        print(f"Created {len(permissions)} permissions")
        
        # Create roles
        admin_role = Role(name="Administrator", description="Full system access")
        admin_role.permissions = db.query(Permission).filter(Permission.is_system == True).all()
        
        guard_role = Role(name="Security Guard", description="Checkpoint access")
        guard_role.permissions = db.query(Permission).filter(
            Permission.name.in_(["checkpoint.a.access", "checkpoint.a.login", "checkpoint.b.access"])
        ).all()
        
        employee_role = Role(name="Employee", description="Basic facility access")
        employee_role.permissions = db.query(Permission).filter(
            Permission.name.in_(["facility.entry", "store.purchase"])
        ).all()
        
        roles = [admin_role, guard_role, employee_role]
        for role in roles:
            existing = db.query(Role).filter(Role.name == role.name).first()
            if not existing:
                db.add(role)
        db.commit()
        print(f"Created {len(roles)} roles")
        
        # Create groups
        security_group = Group(name="Security Team", description="Security personnel")
        security_group.roles = [guard_role]
        
        staff_group = Group(name="Staff", description="General staff members")
        staff_group.roles = [employee_role]
        
        groups = [security_group, staff_group]
        for group in groups:
            existing = db.query(Group).filter(Group.name == group.name).first()
            if not existing:
                db.add(group)
        db.commit()
        print(f"Created {len(groups)} groups")
        
        # Create sample users
        users = [
            User(
                barcode="100000000001",
                account_number="1000000000000001",
                first_name="John",
                last_name="Admin",
                email="admin@shepardos.local",
                can_go_negative=False
            ),
            User(
                barcode="100000000002",
                account_number="1000000000000002",
                first_name="Jane",
                last_name="Guard",
                email="guard@shepardos.local",
                can_go_negative=False
            ),
            User(
                barcode="100000000003",
                account_number="1000000000000003",
                first_name="Bob",
                last_name="Employee",
                email="employee@shepardos.local",
                can_go_negative=False
            ),
        ]
        
        for user in users:
            existing = db.query(User).filter(User.barcode == user.barcode).first()
            if not existing:
                db.add(user)
        db.commit()
        
        # Assign roles to users
        admin_user = db.query(User).filter(User.barcode == "100000000001").first()
        admin_user.roles = [admin_role]
        
        guard_user = db.query(User).filter(User.barcode == "100000000002").first()
        guard_user.roles = [guard_role]
        guard_user.groups = [security_group]
        
        employee_user = db.query(User).filter(User.barcode == "100000000003").first()
        employee_user.roles = [employee_role]
        employee_user.groups = [staff_group]
        
        db.commit()
        print(f"Created {len(users)} users")
        
        # Create sample terminals
        checkpoint_a_key = "checkpoint_a_test_key_12345"
        checkpoint_a = Terminal(
            name="Checkpoint A",
            location="Main Entrance",
            terminal_type="checkpoint",
            key_hash=hash_key(checkpoint_a_key),
            currency_enabled=False,
            gatekeeping_enabled=True,
            require_permission_check=True,
            require_currency_debit=False
        )
        checkpoint_a.required_permissions = db.query(Permission).filter(
            Permission.name == "checkpoint.a.access"
        ).all()
        
        store_key = "store_terminal_test_key_67890"
        store_terminal = Terminal(
            name="Store Terminal",
            location="Main Store",
            terminal_type="combined",
            key_hash=hash_key(store_key),
            currency_enabled=True,
            currency_amount=10.0,
            gatekeeping_enabled=True,
            require_permission_check=True,
            require_currency_debit=True
        )
        store_terminal.required_permissions = db.query(Permission).filter(
            Permission.name == "store.purchase"
        ).all()
        
        terminals = [checkpoint_a, store_terminal]
        for terminal in terminals:
            existing = db.query(Terminal).filter(Terminal.name == terminal.name).first()
            if not existing:
                db.add(terminal)
        db.commit()
        print(f"Created {len(terminals)} terminals")
        
        print("\n" + "="*60)
        print("Sample Terminal Keys (save these for testing):")
        print("="*60)
        print(f"Checkpoint A Key: {checkpoint_a_key}")
        print(f"Store Terminal Key: {store_key}")
        print("="*60)
        
        # Create system account for terminal collections
        system_account = User(
            barcode="SYSTEM000000",
            account_number="SYSTEM_TERMINAL",
            first_name="System",
            last_name="Terminal",
            can_go_negative=True
        )
        existing = db.query(User).filter(User.account_number == "SYSTEM_TERMINAL").first()
        if not existing:
            db.add(system_account)
            db.commit()
            print("Created system account")
        
        # Seed some initial currency for users
        from database import Transaction
        transactions = [
            Transaction(
                from_account_id=system_account.id,
                to_account_id=admin_user.id,
                amount=1000.0,
                description="Initial balance"
            ),
            Transaction(
                from_account_id=system_account.id,
                to_account_id=guard_user.id,
                amount=500.0,
                description="Initial balance"
            ),
            Transaction(
                from_account_id=system_account.id,
                to_account_id=employee_user.id,
                amount=250.0,
                description="Initial balance"
            ),
        ]
        
        for trans in transactions:
            db.add(trans)
        db.commit()
        print(f"Created {len(transactions)} initial transactions")
        
        print("\nDatabase seeded successfully!")
        
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    seed_database()
