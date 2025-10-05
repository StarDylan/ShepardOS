# ShepardOS Backend

Python FastAPI backend server for ShepardOS - a comprehensive gatekeeping, currency, and identity verification system.

## Features

- **User Management**: Barcode-based user identification with account numbers
- **Permission System**: Named permissions without inherent meaning
- **Role-Based Access Control**: Group permissions into roles
- **Group Management**: Organize users into groups with shared roles
- **Terminal Authentication**: mTLS-style key-based terminal authentication
- **Gatekeeping**: Verify user access with configurable permission checks
- **Currency System**: Insert-only ledger with sum-zero enforcement
- **Identity Verification**: TSA-style identity display with audit logging
- **Audit Trail**: Complete logging of all access attempts

## Setup

### Install Dependencies

This project uses [uv](https://github.com/astral-sh/uv) for fast Python package management.

```bash
cd backend

# Install uv if not already installed
pip install uv

# Install dependencies
uv sync
```

### Initialize Database

```bash
uv run python seed_data.py
```

This will:
- Create all database tables
- Seed sample permissions, roles, groups, users, and terminals
- Display test terminal keys
- Script is idempotent (safe to run multiple times)

### Run the Server

```bash
uv run python main.py
```

Or with uvicorn directly:

```bash
uv run uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## API Endpoints

### Users
- `POST /api/users/` - Create new user
- `GET /api/users/search?query=` - Search users
- `GET /api/users/{user_id}` - Get user with permissions and balance
- `GET /api/users/barcode/{barcode}` - Get user by barcode
- `GET /api/users/account/{account_number}` - Get user by account number
- `PUT /api/users/{user_id}` - Update user
- `POST /api/users/{user_id}/roles/{role_id}` - Add role to user
- `DELETE /api/users/{user_id}/roles/{role_id}` - Remove role from user
- `POST /api/users/generate` - Generate unique barcode and account number

### Permissions
- `POST /api/permissions/` - Create permission
- `GET /api/permissions/` - List permissions
- `GET /api/permissions/{permission_id}` - Get permission

### Roles
- `POST /api/roles/` - Create role with permissions
- `GET /api/roles/` - List roles
- `GET /api/roles/{role_id}` - Get role with permissions
- `PUT /api/roles/{role_id}` - Update role

### Groups
- `POST /api/groups/` - Create group with roles and users
- `GET /api/groups/` - List groups
- `GET /api/groups/{group_id}` - Get group details
- `PUT /api/groups/{group_id}` - Update group

### Terminals
- `POST /api/terminals/` - Create terminal (returns auth key)
- `GET /api/terminals/` - List terminals
- `GET /api/terminals/{terminal_id}` - Get terminal configuration
- `PUT /api/terminals/{terminal_id}` - Update terminal configuration
- `POST /api/terminals/{terminal_id}/regenerate-key` - Regenerate terminal key

### Currency
- `POST /api/currency/transfer` - Transfer money between accounts
- `GET /api/currency/balance/{account_number}` - Get account balance
- `GET /api/currency/transactions/{account_number}` - Get transaction history
- `GET /api/currency/all-transactions` - Get all transactions (admin)

### Gatekeeping
- `POST /api/gatekeeping/verify` - Verify user access (read-only check)
- `POST /api/gatekeeping/process` - Process access (execute currency debit if configured)

### Audit Logs
- `GET /api/audit/` - Get audit logs with filters
- `GET /api/audit/{log_id}` - Get specific audit log

## Database Schema

### Users
- Unique barcode (12 digits)
- Unique account number (16 digits)
- Identity information (name, DOB, photo, etc.)
- Pass revocation flag
- Can go negative flag for accounts

### Permissions
- Named permissions (e.g., "checkpoint.a.access")
- System permissions for administrative functions

### Roles
- Named groups of permissions
- Can be assigned to users and groups

### Groups
- Named groups of users
- Can have multiple roles

### Terminals
- Unique name and location
- Authentication via hashed keys
- Configurable for gatekeeping, currency, or both
- Required permissions list
- Currency amount for transactions

### Transactions
- Insert-only ledger
- From/to account IDs
- Amount and description
- Terminal ID for audit trail

### Audit Logs
- User and terminal IDs
- Action type and success flag
- Timestamp and details

## Terminal Configuration Examples

### Checkpoint Terminal (Gatekeeping Only)
```json
{
  "name": "Checkpoint A",
  "terminal_type": "checkpoint",
  "gatekeeping_enabled": true,
  "require_permission_check": true,
  "currency_enabled": false,
  "required_permission_ids": [4]
}
```

### Store Terminal (Gatekeeping + Currency)
```json
{
  "name": "Store Terminal",
  "terminal_type": "combined",
  "gatekeeping_enabled": true,
  "require_permission_check": true,
  "currency_enabled": true,
  "currency_amount": 10.0,
  "require_currency_debit": true,
  "required_permission_ids": [7]
}
```

### Currency Terminal (Currency Only)
```json
{
  "name": "ATM Terminal",
  "terminal_type": "currency",
  "gatekeeping_enabled": false,
  "currency_enabled": true
}
```

## Sample Data

After running `seed_data.py`, you'll have:

**Users:**
- John Admin (barcode: 100000000001, account: 1000000000000001) - Administrator
- Jane Guard (barcode: 100000000002, account: 1000000000000002) - Security Guard
- Bob Employee (barcode: 100000000003, account: 1000000000000003) - Employee

**Terminals:**
- Checkpoint A (key provided in seed output)
- Store Terminal (key provided in seed output)

All users start with initial currency balances.

## Development

The system uses:
- FastAPI for REST API
- SQLAlchemy ORM for database access
- Pydantic for request/response validation
- SQLite for data storage (configurable via DATABASE_URL env var)

## Security

- Terminal keys are hashed before storage (SHA-256)
- Keys should be stored securely by terminal clients
- All access attempts are logged in audit trail
- System permissions protect administrative functions
