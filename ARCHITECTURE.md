# ShepardOS Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         ShepardOS System                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐           ┌──────────────────┐
│  Terminal Client │           │  Terminal Client │
│   (Rust TUI)     │           │   (Rust TUI)     │
│                  │           │                  │
│  - Checkpoint A  │           │  - Store POS     │
│  - Gatekeeping   │           │  - Combined      │
└────────┬─────────┘           └────────┬─────────┘
         │                              │
         │   HTTP/REST (Terminal Key)   │
         │                              │
         └──────────────┬───────────────┘
                        │
         ┌──────────────▼────────────────┐
         │    FastAPI Backend Server     │
         │                               │
         │  - REST API Endpoints         │
         │  - Terminal Authentication    │
         │  - Business Logic             │
         └──────────────┬────────────────┘
                        │
         ┌──────────────▼────────────────┐
         │      SQLite Database          │
         │                               │
         │  - Users & Permissions        │
         │  - Terminals & Config         │
         │  - Transactions (Insert-Only) │
         │  - Audit Logs                 │
         └───────────────────────────────┘
```

## Component Architecture

### Frontend (Rust TUI)

```
┌─────────────────────────────────────────────────────┐
│                   Terminal Client                    │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │  Main    │  │  Event   │  │   Application     │ │
│  │  Loop    │──▶  Handler │──▶   State           │ │
│  └──────────┘  └──────────┘  └──────────────────┘ │
│                                         │           │
│  ┌──────────┐  ┌──────────┐  ┌─────────▼────────┐ │
│  │   UI     │◀─│  Render  │◀─│   Mode Manager   │ │
│  │  Layer   │  │  Engine  │  │  (6 Modes)       │ │
│  └──────────┘  └──────────┘  └──────────────────┘ │
│                                         │           │
│                               ┌─────────▼────────┐ │
│                               │   API Client     │ │
│                               │  (HTTP/JSON)     │ │
│                               └──────────────────┘ │
└─────────────────────────────────────────────────────┘
```

#### Terminal Modes

1. **Menu Mode**: Navigate between features
2. **Gatekeeping Verify**: Read-only access checks
3. **Gatekeeping Process**: Execute access with currency
4. **Currency Transfer**: Move money between accounts
5. **User Search**: Find and view users
6. **Configuration**: Set terminal key

### Backend (Python FastAPI)

```
┌─────────────────────────────────────────────────────┐
│                  FastAPI Backend                     │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │           REST API Endpoints                  │  │
│  │                                               │  │
│  │  /api/users          /api/permissions        │  │
│  │  /api/roles          /api/groups             │  │
│  │  /api/terminals      /api/currency           │  │
│  │  /api/gatekeeping    /api/audit              │  │
│  └────────────────────┬─────────────────────────┘  │
│                       │                             │
│  ┌────────────────────▼─────────────────────────┐  │
│  │         Business Logic Layer                  │  │
│  │                                               │  │
│  │  - Permission Resolution                      │  │
│  │  - Balance Calculation                        │  │
│  │  - Terminal Authentication                    │  │
│  │  - Audit Logging                              │  │
│  └────────────────────┬─────────────────────────┘  │
│                       │                             │
│  ┌────────────────────▼─────────────────────────┐  │
│  │         SQLAlchemy ORM Layer                  │  │
│  │                                               │  │
│  │  - Model Definitions                          │  │
│  │  - Relationship Management                    │  │
│  │  - Query Building                             │  │
│  └────────────────────┬─────────────────────────┘  │
│                       │                             │
│  ┌────────────────────▼─────────────────────────┐  │
│  │            SQLite Database                    │  │
│  │                                               │  │
│  │  - Persistent Storage                         │  │
│  │  - Transaction Management                     │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

## Data Flow

### Gatekeeping Verification Flow

```
User Scans Barcode
        │
        ▼
┌───────────────────┐
│  Terminal Client  │
└─────────┬─────────┘
          │ POST /api/gatekeeping/verify
          │ {barcode, terminal_key}
          ▼
┌───────────────────────────┐
│  Backend: Verify Terminal │
│  - Check key hash         │
│  - Verify terminal active │
└─────────┬─────────────────┘
          │
          ▼
┌───────────────────────────┐
│  Backend: Find User       │
│  - Lookup by barcode      │
│  - Check pass not revoked │
└─────────┬─────────────────┘
          │
          ▼
┌───────────────────────────┐
│  Backend: Check Access    │
│  - Get user permissions   │
│  - Check required perms   │
│  - Calculate balance      │
└─────────┬─────────────────┘
          │
          ▼
┌───────────────────────────┐
│  Backend: Create Log      │
│  - Record attempt         │
│  - Save details           │
└─────────┬─────────────────┘
          │
          ▼
┌───────────────────────────┐
│  Return Result to Client  │
│  - Success/failure        │
│  - User information       │
│  - Permission status      │
│  - Balance info           │
└───────────────────────────┘
```

### Currency Transfer Flow

```
Initiate Transfer
        │
        ▼
┌───────────────────────────┐
│  Validate Accounts        │
│  - Find source account    │
│  - Find dest account      │
└─────────┬─────────────────┘
          │
          ▼
┌───────────────────────────┐
│  Calculate Balance        │
│  - Sum incoming trans     │
│  - Sum outgoing trans     │
│  - Check sufficient funds │
└─────────┬─────────────────┘
          │
          ▼
┌───────────────────────────┐
│  Create Transaction       │
│  - INSERT new record      │
│  - Never UPDATE/DELETE    │
│  - Preserve audit trail   │
└─────────┬─────────────────┘
          │
          ▼
┌───────────────────────────┐
│  Return Confirmation      │
│  - Transaction ID         │
│  - New balance            │
└───────────────────────────┘
```

## Database Schema

### Entity Relationship Diagram

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│    Users     │────┬────│   Roles      │────┬────│  Permissions │
│              │    │    │              │    │    │              │
│ - barcode    │    │    │ - name       │    │    │ - name       │
│ - account_no │    │    │ - desc       │    │    │ - desc       │
│ - name       │    │    └──────────────┘    │    │ - is_system  │
│ - email      │    │                        │    └──────────────┘
│ - pass_revok │    │    ┌──────────────┐    │
│ - can_go_neg │    └────│   Groups     │────┘
└──────┬───────┘         │              │
       │                 │ - name       │
       │                 │ - desc       │
       │                 └──────────────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌──────────────┐   ┌──────────────┐
│ Transactions │   │  Audit Logs  │
│              │   │              │
│ - from_id    │   │ - user_id    │
│ - to_id      │   │ - terminal_id│
│ - amount     │   │ - action     │
│ - desc       │   │ - success    │
│ - terminal_id│   │ - details    │
│ - timestamp  │   │ - timestamp  │
└──────────────┘   └──────────────┘
       │                 │
       │                 │
       └────────┬────────┘
                │
                ▼
         ┌──────────────┐
         │  Terminals   │
         │              │
         │ - name       │
         │ - location   │
         │ - key_hash   │
         │ - type       │
         │ - config     │
         │ - active     │
         └──────────────┘
```

## Security Architecture

### Terminal Authentication

```
Terminal Key (Plain Text)
        │
        ▼
    SHA-256 Hash
        │
        ▼
Store in Database
        │
        ▼
On Authentication:
  Input Key → Hash → Compare with Stored Hash
```

### Permission Resolution

```
User
  │
  ├─▶ Direct Roles ─▶ Permissions ─┐
  │                                 │
  └─▶ Groups ─▶ Group Roles ──────▶ Merge ──▶ Final Permission Set
                   │                  │
                   └─▶ Permissions ───┘
```

## Scalability Considerations

### Current Architecture (Single Instance)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Terminal 1  │────▶│   Backend    │────▶│   SQLite DB  │
├──────────────┤     │   Server     │     └──────────────┘
│  Terminal 2  │────▶│  (Single)    │
├──────────────┤     │              │
│  Terminal N  │────▶│              │
└──────────────┘     └──────────────┘
```

### Future Scaling Options

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Terminal 1  │────▶│   Backend    │────▶│  PostgreSQL  │
├──────────────┤     │  Instance 1  │     │    Cluster   │
│  Terminal 2  │────▶│              │     └──────────────┘
└──────────────┘     └──────────────┘
                            │
┌──────────────┐     ┌──────┴───────┐     ┌──────────────┐
│  Terminal 3  │────▶│ Load         │────▶│    Redis     │
├──────────────┤     │ Balancer     │     │    Cache     │
│  Terminal N  │────▶│              │     └──────────────┘
└──────────────┘     └──────┬───────┘
                            │
                     ┌──────▼───────┐
                     │   Backend    │
                     │  Instance 2  │
                     └──────────────┘
```

## Deployment Patterns

### Standalone Deployment

```
Single Machine
├── Backend (Port 8000)
├── SQLite Database
└── Terminal Clients (Local Network)
```

### Distributed Deployment

```
Server Infrastructure
├── Application Server
│   └── Backend API
├── Database Server
│   └── PostgreSQL
└── Terminal Network
    ├── Checkpoint Terminals
    ├── Currency Terminals
    └── Admin Terminals
```

### Cloud Deployment

```
Cloud Environment
├── Container Orchestration (K8s)
│   ├── Backend Pods (N replicas)
│   └── Load Balancer
├── Managed Database (RDS/Cloud SQL)
└── Edge Terminals
    └── VPN/Secure Connection
```

## Integration Points

### External Systems

```
┌──────────────────┐
│   ShepardOS      │
└────────┬─────────┘
         │
         ├─────▶ Badge/ID Scanner Hardware
         │       (Barcode readers, RFID)
         │
         ├─────▶ Photo Capture System
         │       (Cameras, ID verification)
         │
         ├─────▶ Access Control Hardware
         │       (Door locks, gates)
         │
         ├─────▶ Financial Systems
         │       (Accounting, payroll)
         │
         └─────▶ HR/Identity Management
                 (User provisioning)
```

## Performance Characteristics

### Database Operations

- **User Lookup**: O(1) via indexed barcode/account
- **Permission Resolution**: O(roles × permissions)
- **Balance Calculation**: O(transactions) - cached in practice
- **Audit Logging**: O(1) insert-only operations

### API Response Times

- Simple queries: < 50ms
- Complex permission checks: < 100ms
- Currency transfers: < 200ms (with transaction)
- Search operations: < 150ms (with LIKE queries)

## Development Workflow

```
Local Development
├── Backend Development
│   ├── Edit Python files
│   ├── Auto-reload (uvicorn)
│   └── Test via /docs
│
└── Frontend Development
    ├── Edit Rust files
    ├── cargo run (rebuild)
    └── Test against local backend
```

## Testing Strategy

### Backend Testing

```
├── Unit Tests
│   ├── Model validation
│   ├── Business logic
│   └── Permission resolution
│
├── Integration Tests
│   ├── API endpoints
│   ├── Database operations
│   └── Authentication
│
└── End-to-End Tests
    ├── Complete workflows
    └── Multi-step operations
```

### Frontend Testing

```
├── Unit Tests
│   ├── State management
│   └── Input handling
│
└── Integration Tests
    ├── API client
    └── UI rendering
```

## Monitoring & Observability

### Audit Trail

All operations logged with:
- Timestamp
- User ID
- Terminal ID
- Action type
- Success/failure
- Detailed context

### Metrics to Track

- Access attempts (success/failure rate)
- Transaction volume
- Response times
- Terminal activity
- User activity patterns
- System errors

## Maintenance

### Regular Tasks

- Database backups
- Log rotation
- Terminal key rotation
- User account review
- Permission audit
- System health checks

### Upgrade Path

1. Backup database
2. Update backend code
3. Run migrations
4. Deploy new frontend
5. Test critical paths
6. Monitor logs
