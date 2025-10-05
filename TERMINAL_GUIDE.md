# ShepardOS Terminal User Guide

## Quick Start

### First Time Login

1. **Start the terminal** - You'll see the login screen
2. **Press 'l'** to begin login
3. **Enter your barcode** (scan or type)
4. **Enter your password** when prompted
5. **Access granted!** - You'll see the main menu

### Test Credentials

All test users have the password: `password123`

| User | Barcode | Role | Permissions |
|------|---------|------|-------------|
| John Admin | 100000000001 | Administrator | Full system access |
| Jane Guard | 100000000002 | Security Guard | Checkpoint access |
| Bob Employee | 100000000003 | Employee | Basic facility access |

## Main Features

### Navigation

- **Arrow Keys (↑/↓)**: Navigate menu options
- **Enter**: Select highlighted option
- **Esc**: Return to main menu
- **q**: Quit (press twice to confirm)

### Menu Options

Your menu will show only the features you have permission to use:

#### Available to All Users:
1. **Gatekeeping - Verify Access** (Read Only)
   - Check if someone can pass without making changes
   - Press 's' to scan barcode
   - View user info and permission status

2. **Gatekeeping - Process Access** (Execute)
   - Verify AND execute access (including currency deduction)
   - Press 's' to scan barcode
   - Deducts currency if terminal configured for it

3. **Currency Transfer**
   - Transfer money between accounts
   - Press 't' to start transfer
   - Follow prompts for account numbers and amount

4. **User Search**
   - Search for any user in the system
   - Press 's' to search
   - Type name, barcode, or account number
   - Navigate results with arrow keys

#### Admin Only (requires `system.manage_users`):
5. **User Management**
   - Create new users: Press 'c'
   - List all users: Press 'l'
   - Search users: Press 's'

#### Admin Only (requires `system.admin`):
6. **Permission Tree**
   - View entire permission hierarchy
   - See all roles and permissions

#### Admin Only (requires `system.manage_terminals`):
7. **Terminal Management**
   - Create new terminals: Press 'c'
   - Configure terminal settings

#### Available to All:
8. **Configuration**
   - Set terminal authentication key: Press 'k'

9. **Lock Terminal**
   - Locks screen without logging out
   - Preserves your session
   - Unlock with your password

10. **Logout**
    - Returns to login screen
    - Clears all session data

## Common Workflows

### Checkpoint Verification (Read-Only)

Use this to check if someone can pass without actually letting them through:

1. Select "Gatekeeping - Verify Access"
2. Press 's' to scan
3. Enter user's barcode
4. Review results:
   - ✓ Access Granted = They have required permissions
   - ✗ Access Denied = Missing permissions or revoked pass
5. Press Enter to continue

### Processing Access (Execute)

Use this when actually allowing someone through:

1. Select "Gatekeeping - Process Access"
2. Press 's' to scan
3. Enter user's barcode
4. System will:
   - Verify permissions
   - Check balance (if currency required)
   - Deduct currency (if configured)
   - Log the transaction
5. User granted/denied based on results

### Currency Transfer

1. Select "Currency Transfer"
2. Press 't' to start
3. Enter source account number
4. Enter destination account number
5. Enter amount
6. Enter description (optional)
7. Confirm with 'y'

### Creating a New User (Admin Only)

1. Select "User Management"
2. Press 'c' for create
3. Press 'n' to start new user flow
4. Follow prompts for:
   - First name
   - Last name
   - Email
   - (System auto-generates barcode and account number)
5. Set password via separate endpoint

### Searching for Users

1. Select "User Search" or "User Management"
2. Press 's' to search
3. Start typing - results appear in real-time
4. Use arrow keys to navigate results
5. Press Enter to view full user details

## Terminal Locking

### Why Lock?

- Step away briefly without logging out
- Prevents unauthorized access
- Maintains your session

### How to Lock:

1. From main menu, select "Lock Terminal"
2. Screen shows locked message
3. Press 'u' to unlock
4. Enter your password
5. Back to menu where you left off

## Security Notes

### Password Policy

- Passwords are hashed with SHA-256
- Never shared between users
- Change default password after first login
- Don't share your credentials

### Permission System

- **system.admin**: Full system access, see everything
- **system.manage_users**: Create, modify, delete users
- **system.manage_terminals**: Configure terminals
- **checkpoint.*.access**: Access specific checkpoints
- **store.purchase**: Make purchases
- **facility.entry**: Enter facility

### Best Practices

1. **Always lock** when stepping away
2. **Logout** at end of shift
3. **Don't share** your barcode or password
4. **Report** any unauthorized access attempts
5. **Check permissions** before granting access

## Troubleshooting

### "Invalid credentials"
- Double-check barcode number
- Verify password is correct
- Ensure pass hasn't been revoked

### "Access denied" during gatekeeping
- User may not have required permissions
- Pass may be revoked
- Check balance if currency required

### "Terminal key not configured"
- Press 'k' in Configuration
- Enter the terminal authentication key
- Provided by system administrator

### Menu options missing
- You may not have required permissions
- Contact administrator for access
- Logout and login again to refresh

## Features by Permission

| Permission | Features Unlocked |
|-----------|-------------------|
| (None - All Users) | Gatekeeping, Currency, Search, Configuration |
| `system.manage_users` | User Management, Create Users |
| `system.admin` | Permission Tree, Full Admin Access |
| `system.manage_terminals` | Terminal Management, Create Terminals |

## Advanced Features

### Real-Time Search

User search shows results as you type:
- No need to press Enter
- Instant feedback
- Navigate with arrow keys
- Clear, Google-style interface

### Permission Tree

Shows complete hierarchy:
```
System Permissions:
├─ system.admin
├─ system.manage_users
└─ system.manage_terminals

Custom Permissions:
├─ checkpoint.a.access
├─ checkpoint.b.access
├─ store.purchase
└─ facility.entry
```

### Dynamic Menus

Your menu adapts to your permissions:
- Admin sees all options
- Guard sees checkpoint options
- Employee sees basic options
- Clean, uncluttered interface

## Getting Help

### Terminal Keys

- **l**: Login
- **u**: Unlock (when locked)
- **s**: Scan/Search
- **k**: Configure key
- **c**: Create new
- **t**: Transfer
- **ESC**: Back/Menu
- **q**: Quit (twice)

### Status Messages

- **Green**: Success, action completed
- **Red**: Error, action failed
- **Yellow**: Warning, needs attention
- **Gray**: Information, help text

### User Display

Top of menu shows:
```
| Logged in as: John Admin
```

Always know who's using the terminal!

## Quick Reference Card

```
┌─────────────────────────────────────────┐
│         SHEPARDOS QUICK REFERENCE        │
├─────────────────────────────────────────┤
│ LOGIN       │ l = Login                 │
│             │ Barcode → Password        │
├─────────────────────────────────────────┤
│ NAVIGATION  │ ↑↓ = Move selection       │
│             │ Enter = Select            │
│             │ ESC = Back to menu        │
├─────────────────────────────────────────┤
│ GATEKEEPING │ s = Scan barcode          │
│             │ k = Set terminal key      │
├─────────────────────────────────────────┤
│ CURRENCY    │ t = Transfer money        │
├─────────────────────────────────────────┤
│ USERS       │ s = Search users          │
│             │ c = Create user (admin)   │
│             │ l = List all (admin)      │
├─────────────────────────────────────────┤
│ SECURITY    │ Lock = Secure terminal    │
│             │ u = Unlock with password  │
│             │ Logout = End session      │
├─────────────────────────────────────────┤
│ QUIT        │ q = Quit (press twice)    │
└─────────────────────────────────────────┘
```

## Support

For technical support or issues:
1. Contact your system administrator
2. Check the main README.md
3. Review API documentation at `/docs`
4. Report security issues immediately
