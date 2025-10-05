use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub enum TerminalMode {
    Menu,
    GatekeepingVerify,
    GatekeepingProcess,
    CurrencyTransfer,
    UserSearch,
    UserInfo,
    Configuration,
}

impl TerminalMode {
    pub fn title(&self) -> &'static str {
        match self {
            TerminalMode::Menu => "ShepardOS Terminal - Main Menu",
            TerminalMode::GatekeepingVerify => "Gatekeeping - Verify Access",
            TerminalMode::GatekeepingProcess => "Gatekeeping - Process Access",
            TerminalMode::CurrencyTransfer => "Currency Transfer",
            TerminalMode::UserSearch => "User Search",
            TerminalMode::UserInfo => "User Information",
            TerminalMode::Configuration => "Terminal Configuration",
        }
    }

    pub fn description(&self) -> &'static str {
        match self {
            TerminalMode::Menu => "Select a mode to continue",
            TerminalMode::GatekeepingVerify => "Scan barcode to verify access permissions (read-only)",
            TerminalMode::GatekeepingProcess => "Scan barcode to process access and deduct currency",
            TerminalMode::CurrencyTransfer => "Transfer currency between accounts",
            TerminalMode::UserSearch => "Search for users by name, barcode, or account number",
            TerminalMode::UserInfo => "View detailed user information",
            TerminalMode::Configuration => "Configure terminal settings",
        }
    }
}
