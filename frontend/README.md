# ShepardOS Terminal Frontend

Rust-based Text User Interface (TUI) for ShepardOS terminals using ratatui.

## Features

- **Main Menu**: Navigate between different terminal modes
- **Gatekeeping Verification**: Read-only access verification
- **Gatekeeping Processing**: Access verification with currency deduction
- **Currency Transfer**: Transfer money between accounts
- **User Search**: Searchable user database
- **User Information**: View detailed user info with permissions
- **Terminal Configuration**: Configure terminal key

## Building

```bash
cd frontend
cargo build --release
```

## Running

Make sure the backend server is running first:

```bash
cd ../backend
python main.py &
```

Then run the frontend:

```bash
cd frontend
cargo run
```

Or use the compiled binary:

```bash
./target/release/shepardos-tui
```

## Usage

### Navigation

- **Arrow Keys**: Navigate menu items and search results
- **Enter**: Select menu item or confirm action
- **Esc**: Go back to main menu
- **q**: Quit application (press twice to confirm)

### Main Menu Options

1. **Gatekeeping - Verify Access (Read Only)**
   - Verify user access without making changes
   - Check permissions and currency requirements
   - Display user information
   
2. **Gatekeeping - Process Access (Execute)**
   - Verify user access and execute currency deduction if configured
   - Process complete gatekeeping workflow
   
3. **Currency Transfer**
   - Transfer money between accounts
   - Guided multi-step input process
   
4. **User Search**
   - Search users by name, barcode, or account number
   - Navigate results with arrow keys
   - View detailed user information
   
5. **User Information**
   - View detailed user profile
   - See all permissions
   - Check account balance
   
6. **Terminal Configuration**
   - Set terminal authentication key

### Gatekeeping Workflow

1. Select gatekeeping mode from main menu
2. Press 'k' to configure terminal key (first time only)
3. Press 's' to scan barcode
4. Enter or scan user barcode
5. View verification result with:
   - Access status (granted/denied)
   - User identity information
   - Permission check results
   - Currency balance and deductions

### Currency Transfer Workflow

1. Select "Currency Transfer" from main menu
2. Press 't' to start transfer
3. Enter source account number
4. Enter destination account number
5. Enter amount
6. Enter description (optional)
7. Confirm transfer

### User Search Workflow

1. Select "User Search" from main menu
2. Press 's' to start search
3. Enter search query (name, barcode, or account number)
4. Use arrow keys to navigate results
5. Press Enter to view user details

## Configuration

The terminal connects to the backend API at `http://localhost:8000` by default.

Each terminal needs a unique authentication key provided by the backend. To get a terminal key:

1. Create a terminal via the backend API
2. Save the returned key
3. Configure the key in the TUI using the Configuration menu

## Terminal Keys for Testing

When using the seeded database, you can use these test keys:

- **Checkpoint A**: `checkpoint_a_test_key_12345`
- **Store Terminal**: `store_terminal_test_key_67890`

## User Interface Design

The TUI follows a menu-driven design with searchable interfaces:

- **No long lists**: Use search to find specific items
- **Clear navigation**: Always show available keys
- **Status feedback**: Clear success/error messages
- **Confirmation prompts**: Confirm destructive actions
- **Real-time validation**: Check inputs before submission

## Architecture

- `main.rs`: Application entry point and event loop
- `app.rs`: Application state and business logic
- `ui.rs`: UI rendering with ratatui
- `api.rs`: Backend API client
- `terminal_mode.rs`: Terminal mode definitions

## Dependencies

- **ratatui**: TUI framework
- **crossterm**: Terminal manipulation
- **reqwest**: HTTP client
- **serde**: JSON serialization
- **tokio**: Async runtime
- **tui-input**: Text input widget
- **anyhow**: Error handling
- **chrono**: Date/time handling
