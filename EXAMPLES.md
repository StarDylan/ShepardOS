# ShepardOS API Examples

Real-world examples of using the ShepardOS API.

## Table of Contents

- [User Management](#user-management)
- [Permission & Role Setup](#permission--role-setup)
- [Terminal Configuration](#terminal-configuration)
- [Gatekeeping Workflows](#gatekeeping-workflows)
- [Currency Operations](#currency-operations)
- [Audit & Reporting](#audit--reporting)

## User Management

### Create a New User

```bash
# Generate unique credentials first
curl http://localhost:8000/api/users/generate

# Response: {"barcode": "123456789012", "account_number": "1234567890123456"}

# Create user with generated credentials
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "barcode": "123456789012",
    "account_number": "1234567890123456",
    "first_name": "Sarah",
    "last_name": "Connor",
    "email": "sconnor@example.com",
    "phone": "555-0123",
    "date_of_birth": "1965-11-13",
    "can_go_negative": false
  }'
```

### Search for Users

```bash
# Search by name
curl "http://localhost:8000/api/users/search?query=John"

# Search by barcode
curl "http://localhost:8000/api/users/search?query=100000000001"

# Search by email
curl "http://localhost:8000/api/users/search?query=admin@shepardos"
```

### Get User with Full Details

```bash
# By barcode (includes permissions and balance)
curl http://localhost:8000/api/users/barcode/100000000001

# By account number
curl http://localhost:8000/api/users/account/1000000000000001
```

### Update User Information

```bash
# Revoke user's pass
curl -X PUT http://localhost:8000/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{"pass_revoked": true}'

# Update contact info
curl -X PUT http://localhost:8000/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newemail@example.com",
    "phone": "555-9999"
  }'
```

## Permission & Role Setup

### Create Permissions

```bash
# Create custom permissions
curl -X POST http://localhost:8000/api/permissions/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "armory.access",
    "description": "Access to armory",
    "is_system": false
  }'

curl -X POST http://localhost:8000/api/permissions/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "commissary.purchase",
    "description": "Purchase from commissary"
  }'
```

### Create Roles

```bash
# Get permission IDs first
curl http://localhost:8000/api/permissions/

# Create role with permissions
curl -X POST http://localhost:8000/api/roles/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Infantry",
    "description": "Basic infantry soldier",
    "permission_ids": [4, 8]
  }'
```

### Assign Role to User

```bash
# Add role to user
curl -X POST http://localhost:8000/api/users/1/roles/1

# Remove role from user
curl -X DELETE http://localhost:8000/api/users/1/roles/1
```

### Create Groups

```bash
# Create group with roles and users
curl -X POST http://localhost:8000/api/groups/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alpha Squad",
    "description": "First squad, first platoon",
    "role_ids": [2],
    "user_ids": [1, 2, 3]
  }'
```

## Terminal Configuration

### Create Checkpoint Terminal

```bash
# Create gatekeeping-only terminal
curl -X POST http://localhost:8000/api/terminals/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Main Gate",
    "location": "Building 1 Entrance",
    "terminal_type": "checkpoint",
    "gatekeeping_enabled": true,
    "require_permission_check": true,
    "currency_enabled": false,
    "required_permission_ids": [8]
  }'

# Response includes terminal key - SAVE THIS!
# {
#   "terminal_id": 3,
#   "key": "abc123xyz789...",
#   "message": "Save this key securely. It cannot be recovered."
# }
```

### Create Store Terminal

```bash
# Create combined gatekeeping + currency terminal
curl -X POST http://localhost:8000/api/terminals/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "PX Terminal 1",
    "location": "Post Exchange",
    "terminal_type": "combined",
    "gatekeeping_enabled": true,
    "require_permission_check": true,
    "currency_enabled": true,
    "currency_amount": 5.0,
    "require_currency_debit": true,
    "required_permission_ids": [7]
  }'
```

### Update Terminal Configuration

```bash
# Change currency amount
curl -X PUT http://localhost:8000/api/terminals/1 \
  -H "Content-Type: application/json" \
  -d '{
    "currency_amount": 15.0
  }'

# Disable terminal
curl -X PUT http://localhost:8000/api/terminals/1 \
  -H "Content-Type: application/json" \
  -d '{
    "active": false
  }'
```

### Regenerate Terminal Key

```bash
# If key is compromised
curl -X POST http://localhost:8000/api/terminals/1/regenerate-key

# Response includes new key
```

## Gatekeeping Workflows

### Verify Access (Read-Only)

```bash
# Check if user has access without making changes
curl -X POST http://localhost:8000/api/gatekeeping/verify \
  -H "Content-Type: application/json" \
  -d '{
    "barcode": "100000000001",
    "terminal_key": "checkpoint_a_test_key_12345"
  }'

# Response shows:
# - Access granted/denied
# - User information
# - Permission check results
# - Current balance
# - Missing permissions if denied
```

### Process Access (Execute)

```bash
# Verify and execute (deduct currency if configured)
curl -X POST http://localhost:8000/api/gatekeeping/process \
  -H "Content-Type: application/json" \
  -d '{
    "barcode": "100000000002",
    "terminal_key": "store_terminal_test_key_67890"
  }'

# This will:
# 1. Verify access
# 2. Deduct currency if required and configured
# 3. Log the transaction
# 4. Return results
```

## Currency Operations

### Transfer Money

```bash
# Simple transfer
curl -X POST http://localhost:8000/api/currency/transfer \
  -H "Content-Type: application/json" \
  -d '{
    "from_account_number": "1000000000000001",
    "to_account_number": "1000000000000002",
    "amount": 100.0,
    "description": "Equipment purchase"
  }'
```

### Check Balance

```bash
# Get current balance
curl http://localhost:8000/api/currency/balance/1000000000000001

# Response: 
# {
#   "account_number": "1000000000000001",
#   "balance": 900.0,
#   "transaction_count": 4
# }
```

### View Transaction History

```bash
# Get user's transactions
curl http://localhost:8000/api/currency/transactions/1000000000000001

# With pagination
curl "http://localhost:8000/api/currency/transactions/1000000000000001?skip=0&limit=10"
```

### View All Transactions (Admin)

```bash
# Get all transactions
curl http://localhost:8000/api/currency/all-transactions

# With pagination
curl "http://localhost:8000/api/currency/all-transactions?skip=0&limit=50"
```

## Audit & Reporting

### View Recent Audit Logs

```bash
# All recent logs
curl http://localhost:8000/api/audit/

# Last 100 logs
curl "http://localhost:8000/api/audit/?limit=100"
```

### Filter Audit Logs

```bash
# Failed access attempts only
curl "http://localhost:8000/api/audit/?success=false"

# Specific user's activity
curl "http://localhost:8000/api/audit/?user_id=1"

# Specific terminal's logs
curl "http://localhost:8000/api/audit/?terminal_id=1"

# Combine filters
curl "http://localhost:8000/api/audit/?terminal_id=1&success=false"
```

### Get Specific Audit Log

```bash
# Detailed log entry
curl http://localhost:8000/api/audit/1
```

## Complete Workflows

### Workflow 1: New Employee Onboarding

```bash
# 1. Generate credentials
CREDS=$(curl -s http://localhost:8000/api/users/generate)
BARCODE=$(echo $CREDS | jq -r .barcode)
ACCOUNT=$(echo $CREDS | jq -r .account_number)

# 2. Create user
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d "{
    \"barcode\": \"$BARCODE\",
    \"account_number\": \"$ACCOUNT\",
    \"first_name\": \"New\",
    \"last_name\": \"Employee\",
    \"email\": \"newemployee@example.com\",
    \"can_go_negative\": false
  }"

# 3. Get user ID from response
USER_ID=4

# 4. Assign employee role
curl -X POST http://localhost:8000/api/users/$USER_ID/roles/3

# 5. Add to group
curl -X PUT http://localhost:8000/api/groups/2 \
  -H "Content-Type: application/json" \
  -d "{\"user_ids\": [1, 2, 3, $USER_ID]}"

# 6. Fund initial balance
curl -X POST http://localhost:8000/api/currency/transfer \
  -H "Content-Type: application/json" \
  -d "{
    \"from_account_number\": \"SYSTEM_TERMINAL\",
    \"to_account_number\": \"$ACCOUNT\",
    \"amount\": 500.0,
    \"description\": \"Initial balance\"
  }"
```

### Workflow 2: Setup New Checkpoint

```bash
# 1. Create checkpoint permission
curl -X POST http://localhost:8000/api/permissions/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "checkpoint.south.access",
    "description": "Access South Checkpoint"
  }'

# 2. Get permission ID (from response or list)
PERM_ID=9

# 3. Create terminal
TERMINAL=$(curl -X POST http://localhost:8000/api/terminals/ \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"South Gate\",
    \"location\": \"South Entrance\",
    \"terminal_type\": \"checkpoint\",
    \"gatekeeping_enabled\": true,
    \"require_permission_check\": true,
    \"currency_enabled\": false,
    \"required_permission_ids\": [$PERM_ID]
  }")

# 4. Save terminal key
echo "$TERMINAL" | jq -r .key > south_gate_key.txt
echo "Terminal key saved to south_gate_key.txt"

# 5. Add permission to existing roles
curl -X PUT http://localhost:8000/api/roles/2 \
  -H "Content-Type: application/json" \
  -d "{\"permission_ids\": [4, 5, 6, $PERM_ID]}"
```

### Workflow 3: Daily Access Report

```bash
# Get today's access attempts
TODAY=$(date -I)
curl "http://localhost:8000/api/audit/?skip=0&limit=1000" | \
  jq "[.[] | select(.created_at | startswith(\"$TODAY\"))]"

# Count successful vs failed
curl "http://localhost:8000/api/audit/" | \
  jq '[.[] | select(.created_at | startswith("'$TODAY'"))] | 
      group_by(.success) | 
      map({success: .[0].success, count: length})'

# Get failed attempts by user
curl "http://localhost:8000/api/audit/?success=false" | \
  jq 'group_by(.user_id) | 
      map({user_id: .[0].user_id, user_name: .[0].user_name, count: length}) | 
      sort_by(.count) | reverse'
```

## Python Client Example

```python
import requests

class ShepardOSClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def verify_access(self, barcode, terminal_key):
        """Verify user access at terminal"""
        response = requests.post(
            f"{self.base_url}/api/gatekeeping/verify",
            json={"barcode": barcode, "terminal_key": terminal_key}
        )
        return response.json()
    
    def process_access(self, barcode, terminal_key):
        """Process user access (execute)"""
        response = requests.post(
            f"{self.base_url}/api/gatekeeping/process",
            json={"barcode": barcode, "terminal_key": terminal_key}
        )
        return response.json()
    
    def search_users(self, query):
        """Search for users"""
        response = requests.get(
            f"{self.base_url}/api/users/search",
            params={"query": query}
        )
        return response.json()
    
    def get_balance(self, account_number):
        """Get account balance"""
        response = requests.get(
            f"{self.base_url}/api/currency/balance/{account_number}"
        )
        return response.json()

# Usage
client = ShepardOSClient()

# Verify access
result = client.verify_access(
    "100000000001", 
    "checkpoint_a_test_key_12345"
)
print(f"Access: {'GRANTED' if result['success'] else 'DENIED'}")
print(f"User: {result['user']['first_name']} {result['user']['last_name']}")

# Check balance
balance = client.get_balance("1000000000000001")
print(f"Balance: ${balance['balance']:.2f}")
```

## Error Handling

### Common Errors

```bash
# Invalid terminal key
curl -X POST http://localhost:8000/api/gatekeeping/verify \
  -H "Content-Type: application/json" \
  -d '{"barcode": "100000000001", "terminal_key": "wrong_key"}'
# Response: 401 Unauthorized

# User not found
curl http://localhost:8000/api/users/barcode/999999999999
# Response: 404 Not Found

# Insufficient funds
curl -X POST http://localhost:8000/api/currency/transfer \
  -H "Content-Type: application/json" \
  -d '{
    "from_account_number": "1000000000000003",
    "to_account_number": "1000000000000001",
    "amount": 10000.0
  }'
# Response: 400 Bad Request with balance info
```

## Tips

1. **Always save terminal keys** - They cannot be recovered
2. **Use search for large datasets** - Don't list all users
3. **Check audit logs regularly** - Monitor for unauthorized access
4. **Verify before process** - Test access without making changes
5. **Use descriptive names** - Make permissions and roles clear
6. **Group related users** - Simplify permission management
7. **Monitor balances** - Set up alerts for low balances
8. **Regular backups** - Database contains all transactions

## Interactive API Testing

Visit http://localhost:8000/docs for:
- Interactive API browser
- Try out endpoints directly
- View request/response schemas
- Authentication testing
