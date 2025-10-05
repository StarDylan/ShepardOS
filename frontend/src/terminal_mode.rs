use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub enum TerminalMode {
    Login,
    Locked,
    Menu,
    GatekeepingVerify,
    GatekeepingProcess,
    CurrencyTransfer,
    UserSearch,
    UserInfo,
    UserManagement,
    CreateUser,
    DeleteUser,
    PermissionTree,
    TerminalManagement,
    CreateTerminal,
    Configuration,
}

impl TerminalMode {
    pub fn title(&self) -> &'static str {
        match self {
            TerminalMode::Login => "ShepardOS - Terminal Login",
            TerminalMode::Locked => "ShepardOS - Terminal Locked",
            TerminalMode::Menu => "ShepardOS Terminal - Main Menu",
            TerminalMode::GatekeepingVerify => "Gatekeeping - Verify Access",
            TerminalMode::GatekeepingProcess => "Gatekeeping - Process Access",
            TerminalMode::CurrencyTransfer => "Currency Transfer",
            TerminalMode::UserSearch => "User Search",
            TerminalMode::UserInfo => "User Information",
            TerminalMode::UserManagement => "User Management",
            TerminalMode::CreateUser => "Create New User",
            TerminalMode::DeleteUser => "Delete User",
            TerminalMode::PermissionTree => "Permission Tree",
            TerminalMode::TerminalManagement => "Terminal Management",
            TerminalMode::CreateTerminal => "Create New Terminal",
            TerminalMode::Configuration => "Terminal Configuration",
        }
    }

    pub fn description(&self) -> &'static str {
        match self {
            TerminalMode::Login => "Please authenticate to use this terminal",
            TerminalMode::Locked => "Terminal is locked - enter password to unlock",
            TerminalMode::Menu => "Select a mode to continue",
            TerminalMode::GatekeepingVerify => "Scan barcode to verify access permissions (read-only)",
            TerminalMode::GatekeepingProcess => "Scan barcode to process access and deduct currency",
            TerminalMode::CurrencyTransfer => "Transfer currency between accounts",
            TerminalMode::UserSearch => "Search for users by name, barcode, or account number",
            TerminalMode::UserInfo => "View detailed user information",
            TerminalMode::UserManagement => "Create, delete, or list users",
            TerminalMode::CreateUser => "Create a new user account",
            TerminalMode::DeleteUser => "Remove a user from the system",
            TerminalMode::PermissionTree => "View all permissions, roles, and groups",
            TerminalMode::TerminalManagement => "Manage terminal configurations",
            TerminalMode::CreateTerminal => "Register a new terminal",
            TerminalMode::Configuration => "Configure terminal settings",
        }
    }
    
    pub fn required_permission(&self) -> Option<&'static str> {
        match self {
            TerminalMode::UserManagement | TerminalMode::CreateUser | TerminalMode::DeleteUser => {
                Some("system.manage_users")
            }
            TerminalMode::TerminalManagement | TerminalMode::CreateTerminal => {
                Some("system.manage_terminals")
            }
            TerminalMode::PermissionTree => {
                Some("system.admin")
            }
            _ => None,
        }
    }
}
