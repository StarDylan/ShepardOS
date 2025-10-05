# Getting Started with ShepardOS

This guide will help you get ShepardOS up and running quickly.

## Prerequisites

- Python 3.8 or higher
- Rust 1.70 or higher (install from https://rustup.rs)
- pip (Python package manager)

## Quick Setup

### Automatic Setup (Recommended)

Run the setup script:

```bash
./setup.sh
```

This will:
1. Install Python dependencies
2. Initialize and seed the database
3. Build the Rust frontend

### Manual Setup

If the automatic setup doesn't work, follow these steps:

#### 1. Setup Backend

```bash
cd backend
# Install uv if needed
pip install uv
# Install dependencies and seed database
uv sync
uv run python seed_data.py
```

#### 2. Build Frontend

```bash
cd frontend
cargo build --release
```

## Running ShepardOS

### Option 1: Run Script (Recommended)

```bash
./run.sh
```

This starts both backend and frontend together.

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
uv run python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
cargo run --release
```

## First Time Usage

### 1. Configure Terminal Key

When you first start the TUI:
1. Navigate to "Terminal Configuration" (option 6)
2. Press 'k' to enter terminal key
3. Enter one of the test keys:
   - `checkpoint_a_test_key_12345` (for Checkpoint A)
   - `store_terminal_test_key_67890` (for Store Terminal)

### 2. Test Gatekeeping

1. Return to main menu (press Esc)
2. Select "Gatekeeping - Verify Access"
3. Press 's' to scan barcode
4. Enter test barcode: `100000000001` (Admin user)
5. View the verification result

The system will show:
- User identity information
- Permission check results
- Current balance
- Access status

### 3. Try User Search

1. Go to main menu
2. Select "User Search"
3. Press 's' to search
4. Enter: `John` or `Admin`
5. Navigate results with arrow keys
6. Press Enter to view detailed user info

### 4. Test Currency Transfer

1. Go to main menu
2. Select "Currency Transfer"
3. Press 't' to start transfer
4. Follow the prompts:
   - From account: `1000000000000001` (Admin)
   - To account: `1000000000000002` (Guard)
   - Amount: `50`
   - Description: `Test transfer`
5. Confirm with 'y'

## Test Data

The seeded database includes:

### Users

| Name | Barcode | Account | Role | Balance |
|------|---------|---------|------|---------|
| John Admin | 100000000001 | 1000000000000001 | Administrator | $1000 |
| Jane Guard | 100000000002 | 1000000000000002 | Security Guard | $500 |
| Bob Employee | 100000000003 | 1000000000000003 | Employee | $250 |

### Terminals

| Name | Type | Key | Features |
|------|------|-----|----------|
| Checkpoint A | checkpoint | checkpoint_a_test_key_12345 | Gatekeeping only |
| Store Terminal | combined | store_terminal_test_key_67890 | Gatekeeping + Currency |

### Permissions

- `system.admin` - Full system administration
- `system.manage_users` - Manage users
- `system.manage_terminals` - Manage terminals
- `checkpoint.a.access` - Access Checkpoint A
- `checkpoint.a.login` - Login at Checkpoint A
- `checkpoint.b.access` - Access Checkpoint B
- `store.purchase` - Make purchases at store
- `facility.entry` - Enter facility

## Common Tasks

### Adding a New User

Use the backend API:

```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "barcode": "100000000004",
    "account_number": "1000000000000004",
    "first_name": "Alice",
    "last_name": "Contractor",
    "email": "alice@example.com",
    "can_go_negative": false
  }'
```

Or generate credentials first:

```bash
curl http://localhost:8000/api/users/generate
```

### Creating a New Terminal

```bash
curl -X POST http://localhost:8000/api/terminals/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gate B",
    "location": "North Entrance",
    "terminal_type": "checkpoint",
    "gatekeeping_enabled": true,
    "require_permission_check": true,
    "currency_enabled": false,
    "required_permission_ids": [4]
  }'
```

Save the returned key securely - it cannot be recovered!

### Viewing Audit Logs

Check the audit trail via the API:

```bash
curl http://localhost:8000/api/audit/
```

Or with filters:

```bash
# Failed access attempts
curl "http://localhost:8000/api/audit/?success=false"

# User-specific logs
curl "http://localhost:8000/api/audit/?user_id=1"

# Terminal-specific logs
curl "http://localhost:8000/api/audit/?terminal_id=1"
```

## Keyboard Shortcuts

### Global
- `q` - Quit (press twice to confirm)
- `Esc` - Back to main menu

### Main Menu
- `↑/↓` - Navigate options
- `Enter` - Select option

### Gatekeeping
- `s` - Scan barcode
- `k` - Configure terminal key

### User Search
- `s` - Start search
- `↑/↓` - Navigate results
- `Enter` - View user details

### Currency Transfer
- `t` - Start transfer
- `Enter` - Confirm each field
- `y/n` - Confirm/cancel transfer

## Troubleshooting

### Backend won't start

**Error: Address already in use**
- Another process is using port 8000
- Solution: Kill the process or change the port

```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or run on different port
cd backend
uvicorn main:app --port 8001
```

### Frontend build fails

**Error: Cargo not found**
- Rust is not installed
- Solution: Install from https://rustup.rs

**Error: Cannot find crate**
- Dependencies not downloaded
- Solution:
```bash
cd frontend
cargo clean
cargo build
```

### Database is empty

**No users found**
- Database wasn't seeded
- Solution:
```bash
cd backend
python seed_data.py
```

### Terminal key not working

**Invalid terminal key error**
- Wrong key entered
- Terminal doesn't exist
- Solution: Use exact test key from seed_data.py output

## API Documentation

Full API documentation is available at:
```
http://localhost:8000/docs
```

This provides:
- Interactive API testing
- Request/response schemas
- Authentication details

## Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Create custom terminals**: Add terminals for your use case
3. **Define permissions**: Create application-specific permissions
4. **Add users**: Build your user database
5. **Configure terminals**: Set up checkpoints, stores, etc.

## Support

- Check the main README.md for detailed documentation
- Review backend/README.md for API details
- Review frontend/README.md for TUI usage
- View API docs at http://localhost:8000/docs

## Security Notes

- Terminal keys are hashed (SHA-256) before storage
- Keys cannot be recovered after creation
- All access attempts are logged
- Pass revocation is instant across all terminals
- Transactions are insert-only (audit trail preserved)
