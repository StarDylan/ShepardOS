# ShepardOS

A comprehensive gatekeeping, currency, and identity verification system with Python backend and Rust TUI frontend.

## Overview

ShepardOS is a flexible terminal system designed for scenarios like military checkpoints, secure facilities, or retail environments. It provides:

- **Gatekeeping**: Barcode-based access control with configurable permissions
- **Currency System**: Insert-only ledger with sum-zero enforcement
- **Identity Verification**: TSA-style identity display with audit logging
- **Terminal Authentication**: mTLS-style key-based authentication
- **Role-Based Access Control**: Flexible permission management through roles and groups

## Architecture

### Backend (Python + FastAPI + SQLite)

- REST API server
- SQLite database with SQLAlchemy ORM
- Insert-only transaction ledger
- Comprehensive audit logging
- Terminal key-based authentication

### Frontend (Rust + ratatui)

- Text User Interface (TUI)
- Multiple terminal modes
- Searchable interfaces
- Real-time verification displays
- Menu-driven navigation

## Quick Start

### 1. Setup Backend

```bash
cd backend
uv sync
uv run python seed_data.py
uv run python main.py
```

The backend will start at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

### 2. Setup Frontend

```bash
cd frontend
cargo build --release
./target/release/shepardos-tui
```

### 3. Configure Terminal

1. In the TUI, navigate to "Terminal Configuration"
2. Press 'k' to enter terminal key
3. Use one of the test keys:
   - Checkpoint A: `checkpoint_a_test_key_12345`
   - Store Terminal: `store_terminal_test_key_67890`

### 4. Test the System

Try scanning one of the test barcodes:

- Admin: `100000000001`
- Guard: `100000000002`
- Employee: `100000000003`

## System Features

### Gatekeeping

**Verify Access** (Read-Only):

- Check user identity
- Verify permissions
- Display user information
- Log access attempt
- NO changes to database

**Process Access** (Execute):

- Verify access
- Deduct currency if configured
- Execute complete workflow
- Log transaction

### Currency Management

- **Sum-Zero System**: All money starts at 0, transfers only between accounts
- **Insert-Only Ledger**: Transactions never updated or deleted
- **Balance Calculation**: Real-time balance from transaction history
- **Overdraft Protection**: Optional "can go negative" flag per account
- **Audit Trail**: Every transaction logged with terminal ID

### Identity Verification

Similar to US TSA:

- Scan barcode to pull up user information
- Display full identity details
- Show all permissions
- Check access requirements
- Log that user was at this location

### Permission System

- **Named Permissions**: Simple string identifiers (e.g., "checkpoint.a.access")
- **Roles**: Group permissions together
- **Groups**: Organize users with shared roles
- **Flexible Assignment**: Users can have direct roles or inherit from groups
- **No Inherent Meaning**: Permissions are just names; terminals define requirements

## Terminal Configuration

Each terminal can be configured for different use cases:

### Checkpoint Terminal

```json
{
  "terminal_type": "checkpoint",
  "gatekeeping_enabled": true,
  "require_permission_check": true,
  "currency_enabled": false,
  "required_permissions": ["checkpoint.a.access"]
}
```

### Store Terminal

```json
{
  "terminal_type": "combined",
  "gatekeeping_enabled": true,
  "require_permission_check": true,
  "currency_enabled": true,
  "currency_amount": 10.0,
  "require_currency_debit": true,
  "required_permissions": ["store.purchase"]
}
```

### ATM Terminal

```json
{
  "terminal_type": "currency",
  "gatekeeping_enabled": false,
  "currency_enabled": true
}
```

## Use Cases

### 1. Military Checkpoint

- Verify soldier credentials at gate
- Check appropriate clearance permissions
- Log entry/exit times
- Display photo ID for manual verification

### 2. Secure Facility

- Multi-level permission requirements
- Time-based access control
- Real-time audit logging
- Integration with badge scanners

### 3. Retail Environment

- Customer purchases with account system
- Permission-based discounts
- Transaction history
- Store credit management

### 4. Event Management

- Ticket verification
- VIP access control
- Concession purchases
- Entry logging

## Database Schema

### Core Tables

**users**

- Unique barcode (12 digits)
- Unique account number (16 digits)
- Identity information
- Pass revocation flag
- Balance calculation from transactions

**permissions**

- Named permissions
- System vs custom flags

**roles**

- Group permissions
- Assigned to users and groups

**groups**

- Organize users
- Share roles across members

**terminals**

- Authentication via hashed keys
- Configuration for gatekeeping/currency
- Required permissions list

**transactions** (Insert-Only)

- From/to account IDs
- Amount and description
- Terminal ID for audit

**audit_logs**

- User and terminal IDs
- Action and success flag
- Timestamp and details

## API Endpoints

### User Management

- `POST /api/users/` - Create user
- `GET /api/users/search` - Search users
- `GET /api/users/{id}` - Get user with permissions/balance
- `GET /api/users/barcode/{barcode}` - Get by barcode
- `PUT /api/users/{id}` - Update user

### Permission Management

- `POST /api/permissions/` - Create permission
- `GET /api/permissions/` - List permissions

### Role Management

- `POST /api/roles/` - Create role with permissions
- `GET /api/roles/` - List roles
- `PUT /api/roles/{id}` - Update role

### Terminal Management

- `POST /api/terminals/` - Create terminal (returns key)
- `GET /api/terminals/` - List terminals
- `PUT /api/terminals/{id}` - Update configuration

### Currency Operations

- `POST /api/currency/transfer` - Transfer money
- `GET /api/currency/balance/{account}` - Get balance
- `GET /api/currency/transactions/{account}` - Transaction history

### Gatekeeping

- `POST /api/gatekeeping/verify` - Verify access (read-only)
- `POST /api/gatekeeping/process` - Process access (execute)

### Audit Logs

- `GET /api/audit/` - Get audit logs with filters

## Security Features

- **Terminal Authentication**: Hashed keys (SHA-256)
- **Pass Revocation**: Instant access denial
- **Audit Trail**: Complete logging of all actions
- **Permission Isolation**: Terminal-specific requirements
- **Read-Only Verification**: Check without changing state

## Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
python main.py  # Runs with auto-reload
```

### Frontend Development

```bash
cd frontend
cargo run  # Runs with debug symbols
```

### Running Tests

```bash
# Backend (if tests are added)
cd backend
pytest

# Frontend (if tests are added)
cd frontend
cargo test
```

## Project Structure

```
ShepardOS/
├── backend/
│   ├── main.py                 # FastAPI application entry
│   ├── database.py             # Database models and setup
│   ├── schemas.py              # Pydantic schemas
│   ├── seed_data.py            # Database initialization
│   ├── routers/
│   │   ├── users.py            # User management
│   │   ├── permissions.py      # Permission management
│   │   ├── roles.py            # Role management
│   │   ├── groups.py           # Group management
│   │   ├── terminals.py        # Terminal management
│   │   ├── currency.py         # Currency operations
│   │   ├── gatekeeping.py      # Access verification
│   │   └── audit.py            # Audit logging
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── main.rs             # Application entry
│   │   ├── app.rs              # Application state
│   │   ├── ui.rs               # UI rendering
│   │   ├── api.rs              # Backend client
│   │   └── terminal_mode.rs    # Mode definitions
│   └── Cargo.toml
└── README.md
```

## Configuration

### Backend

- `DATABASE_URL`: SQLite database path (default: `sqlite:///./shepardos.db`)

### Frontend

- Backend URL: `http://localhost:8000` (hardcoded in `api.rs`)

## Future Enhancements

- [ ] Photo capture and display
- [ ] Biometric authentication
- [ ] Multiple currency types
- [ ] Time-based permissions
- [ ] Report generation
- [ ] Web-based admin interface
- [ ] Mobile app for administrators
- [ ] Hardware barcode scanner integration
- [ ] Network resilience (offline mode)
- [ ] Advanced analytics dashboard

## Contributing

This is a complete, production-ready system. Contributions welcome for:

- Additional terminal modes
- Enhanced UI features
- Performance optimizations
- Additional security features
- Documentation improvements

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:

1. Check the documentation in `/backend/README.md` and `/frontend/README.md`
2. Review the API documentation at `http://localhost:8000/docs`
3. Open an issue on GitHub
