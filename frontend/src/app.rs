use crate::api::{ApiClient, GatekeepingCheck, GatekeepingResponse, User, TransactionCreate, SearchResult};
use crate::terminal_mode::TerminalMode;
use crossterm::event::{KeyCode, KeyEvent};
use tui_input::backend::crossterm::EventHandler;
use tui_input::Input;

#[derive(Debug, Clone)]
pub enum AppState {
    Normal,
    Input,
    Confirm,
    Loading,
    DisplayResult,
}

pub struct App {
    pub mode: TerminalMode,
    pub state: AppState,
    pub input: Input,
    pub message: String,
    pub error: Option<String>,
    pub api_client: ApiClient,
    pub terminal_key: String,
    pub current_user: Option<User>,
    pub gatekeeping_result: Option<GatekeepingResponse>,
    pub search_results: Vec<User>,
    pub selected_menu_item: usize,
    pub selected_search_result: usize,
    pub input_label: String,
    pub input_mode: InputMode,
    pub from_account: String,
    pub to_account: String,
    pub amount: String,
    pub description: String,
    pub confirm_message: String,
    pub should_quit: bool,
}

#[derive(Debug, Clone, PartialEq)]
pub enum InputMode {
    None,
    Barcode,
    Search,
    TerminalKey,
    FromAccount,
    ToAccount,
    Amount,
    Description,
}

impl App {
    pub fn new() -> Self {
        Self {
            mode: TerminalMode::Menu,
            state: AppState::Normal,
            input: Input::default(),
            message: String::new(),
            error: None,
            api_client: ApiClient::default(),
            terminal_key: String::new(),
            current_user: None,
            gatekeeping_result: None,
            search_results: Vec::new(),
            selected_menu_item: 0,
            selected_search_result: 0,
            input_label: String::new(),
            input_mode: InputMode::None,
            from_account: String::new(),
            to_account: String::new(),
            amount: String::new(),
            description: String::new(),
            confirm_message: String::new(),
            should_quit: false,
        }
    }

    pub fn is_input_active(&self) -> bool {
        matches!(self.state, AppState::Input | AppState::Confirm)
    }

    pub fn confirm_quit(&mut self) -> bool {
        if self.should_quit {
            return true;
        }
        self.should_quit = true;
        self.confirm_message = "Press 'q' again to quit, or any other key to cancel".to_string();
        false
    }

    pub fn handle_key_event(&mut self, key: KeyEvent) {
        // Reset quit confirmation on any key press
        if self.should_quit && key.code != KeyCode::Char('q') {
            self.should_quit = false;
            self.confirm_message.clear();
        }

        match self.state {
            AppState::Normal => self.handle_normal_keys(key),
            AppState::Input => self.handle_input_keys(key),
            AppState::Confirm => self.handle_confirm_keys(key),
            AppState::DisplayResult => self.handle_result_keys(key),
            AppState::Loading => {} // Ignore keys while loading
        }
    }

    fn handle_normal_keys(&mut self, key: KeyEvent) {
        match self.mode {
            TerminalMode::Menu => self.handle_menu_keys(key),
            TerminalMode::GatekeepingVerify | TerminalMode::GatekeepingProcess => {
                self.handle_gatekeeping_keys(key)
            }
            TerminalMode::CurrencyTransfer => self.handle_currency_keys(key),
            TerminalMode::UserSearch => self.handle_search_keys(key),
            TerminalMode::UserInfo => self.handle_user_info_keys(key),
            TerminalMode::Configuration => self.handle_config_keys(key),
        }
    }

    fn handle_menu_keys(&mut self, key: KeyEvent) {
        match key.code {
            KeyCode::Up => {
                if self.selected_menu_item > 0 {
                    self.selected_menu_item -= 1;
                }
            }
            KeyCode::Down => {
                if self.selected_menu_item < 5 {
                    self.selected_menu_item += 1;
                }
            }
            KeyCode::Enter => {
                self.mode = match self.selected_menu_item {
                    0 => TerminalMode::GatekeepingVerify,
                    1 => TerminalMode::GatekeepingProcess,
                    2 => TerminalMode::CurrencyTransfer,
                    3 => TerminalMode::UserSearch,
                    4 => TerminalMode::UserInfo,
                    5 => TerminalMode::Configuration,
                    _ => TerminalMode::Menu,
                };
                self.reset_state();
            }
            KeyCode::Esc => {
                self.mode = TerminalMode::Menu;
                self.reset_state();
            }
            _ => {}
        }
    }

    fn handle_gatekeeping_keys(&mut self, key: KeyEvent) {
        match key.code {
            KeyCode::Char('s') => {
                self.start_barcode_scan();
            }
            KeyCode::Char('k') => {
                self.start_terminal_key_input();
            }
            KeyCode::Esc => {
                self.mode = TerminalMode::Menu;
                self.reset_state();
            }
            _ => {}
        }
    }

    fn handle_currency_keys(&mut self, key: KeyEvent) {
        match key.code {
            KeyCode::Char('t') => {
                self.start_transfer_input();
            }
            KeyCode::Esc => {
                self.mode = TerminalMode::Menu;
                self.reset_state();
            }
            _ => {}
        }
    }

    fn handle_search_keys(&mut self, key: KeyEvent) {
        match key.code {
            KeyCode::Char('s') => {
                self.start_search_input();
            }
            KeyCode::Up => {
                if self.selected_search_result > 0 {
                    self.selected_search_result -= 1;
                }
            }
            KeyCode::Down => {
                if self.selected_search_result < self.search_results.len().saturating_sub(1) {
                    self.selected_search_result += 1;
                }
            }
            KeyCode::Enter => {
                if !self.search_results.is_empty() {
                    self.current_user = Some(self.search_results[self.selected_search_result].clone());
                    self.mode = TerminalMode::UserInfo;
                }
            }
            KeyCode::Esc => {
                self.mode = TerminalMode::Menu;
                self.reset_state();
            }
            _ => {}
        }
    }

    fn handle_user_info_keys(&mut self, key: KeyEvent) {
        match key.code {
            KeyCode::Esc | KeyCode::Char('b') => {
                self.mode = TerminalMode::UserSearch;
                self.current_user = None;
            }
            _ => {}
        }
    }

    fn handle_config_keys(&mut self, key: KeyEvent) {
        match key.code {
            KeyCode::Char('k') => {
                self.start_terminal_key_input();
            }
            KeyCode::Esc => {
                self.mode = TerminalMode::Menu;
                self.reset_state();
            }
            _ => {}
        }
    }

    fn handle_input_keys(&mut self, key: KeyEvent) {
        match key.code {
            KeyCode::Enter => {
                self.submit_input();
            }
            KeyCode::Esc => {
                self.cancel_input();
            }
            _ => {
                self.input.handle_event(&crossterm::event::Event::Key(key));
            }
        }
    }

    fn handle_confirm_keys(&mut self, key: KeyEvent) {
        match key.code {
            KeyCode::Char('y') | KeyCode::Char('Y') => {
                self.confirm_action();
            }
            KeyCode::Char('n') | KeyCode::Char('N') | KeyCode::Esc => {
                self.cancel_action();
            }
            _ => {}
        }
    }

    fn handle_result_keys(&mut self, key: KeyEvent) {
        match key.code {
            KeyCode::Enter | KeyCode::Esc => {
                self.state = AppState::Normal;
                self.gatekeeping_result = None;
            }
            _ => {}
        }
    }

    fn start_barcode_scan(&mut self) {
        self.state = AppState::Input;
        self.input_mode = InputMode::Barcode;
        self.input_label = "Scan or enter barcode:".to_string();
        self.input = Input::default();
        self.error = None;
    }

    fn start_terminal_key_input(&mut self) {
        self.state = AppState::Input;
        self.input_mode = InputMode::TerminalKey;
        self.input_label = "Enter terminal key:".to_string();
        self.input = Input::default();
        self.error = None;
    }

    fn start_search_input(&mut self) {
        self.state = AppState::Input;
        self.input_mode = InputMode::Search;
        self.input_label = "Search users (name, barcode, account):".to_string();
        self.input = Input::default();
        self.error = None;
    }

    fn start_transfer_input(&mut self) {
        self.state = AppState::Input;
        self.input_mode = InputMode::FromAccount;
        self.input_label = "From account number:".to_string();
        self.input = Input::default();
        self.error = None;
    }

    fn submit_input(&mut self) {
        let value = self.input.value().to_string();
        
        match self.input_mode {
            InputMode::Barcode => {
                self.process_barcode(value);
            }
            InputMode::TerminalKey => {
                self.terminal_key = value;
                self.message = "Terminal key configured".to_string();
                self.state = AppState::Normal;
            }
            InputMode::Search => {
                self.perform_search(value);
            }
            InputMode::FromAccount => {
                self.from_account = value;
                self.input_mode = InputMode::ToAccount;
                self.input_label = "To account number:".to_string();
                self.input = Input::default();
            }
            InputMode::ToAccount => {
                self.to_account = value;
                self.input_mode = InputMode::Amount;
                self.input_label = "Amount:".to_string();
                self.input = Input::default();
            }
            InputMode::Amount => {
                self.amount = value;
                self.input_mode = InputMode::Description;
                self.input_label = "Description (optional):".to_string();
                self.input = Input::default();
            }
            InputMode::Description => {
                self.description = value;
                self.confirm_transfer();
            }
            InputMode::None => {}
        }
    }

    fn cancel_input(&mut self) {
        self.state = AppState::Normal;
        self.input_mode = InputMode::None;
        self.input = Input::default();
        self.from_account.clear();
        self.to_account.clear();
        self.amount.clear();
        self.description.clear();
    }

    fn process_barcode(&mut self, barcode: String) {
        if self.terminal_key.is_empty() {
            self.error = Some("Please configure terminal key first (press 'k')".to_string());
            self.state = AppState::Normal;
            return;
        }

        self.state = AppState::Loading;
        
        let check = GatekeepingCheck {
            barcode,
            terminal_key: self.terminal_key.clone(),
        };

        let result = match self.mode {
            TerminalMode::GatekeepingVerify => self.api_client.verify_access(&check),
            TerminalMode::GatekeepingProcess => self.api_client.process_access(&check),
            _ => {
                self.state = AppState::Normal;
                return;
            }
        };

        match result {
            Ok(response) => {
                self.gatekeeping_result = Some(response);
                self.state = AppState::DisplayResult;
                self.error = None;
            }
            Err(e) => {
                self.error = Some(format!("Error: {}", e));
                self.state = AppState::Normal;
            }
        }
    }

    fn perform_search(&mut self, query: String) {
        self.state = AppState::Loading;
        
        match self.api_client.search_users(&query) {
            Ok(result) => {
                self.search_results = result.users;
                self.selected_search_result = 0;
                self.message = format!("Found {} users", result.total);
                self.state = AppState::Normal;
                self.error = None;
            }
            Err(e) => {
                self.error = Some(format!("Search error: {}", e));
                self.state = AppState::Normal;
            }
        }
    }

    fn confirm_transfer(&mut self) {
        self.state = AppState::Confirm;
        self.confirm_message = format!(
            "Transfer {} from {} to {}?\nPress 'y' to confirm, 'n' to cancel",
            self.amount, self.from_account, self.to_account
        );
    }

    fn confirm_action(&mut self) {
        self.state = AppState::Loading;
        
        if let Ok(amount) = self.amount.parse::<f64>() {
            let transfer = TransactionCreate {
                from_account_number: self.from_account.clone(),
                to_account_number: self.to_account.clone(),
                amount,
                description: if self.description.is_empty() {
                    None
                } else {
                    Some(self.description.clone())
                },
                terminal_key: Some(self.terminal_key.clone()),
            };

            match self.api_client.transfer_money(&transfer) {
                Ok(_) => {
                    self.message = format!("Transfer of {} completed successfully", amount);
                    self.state = AppState::Normal;
                    self.error = None;
                    self.from_account.clear();
                    self.to_account.clear();
                    self.amount.clear();
                    self.description.clear();
                }
                Err(e) => {
                    self.error = Some(format!("Transfer error: {}", e));
                    self.state = AppState::Normal;
                }
            }
        } else {
            self.error = Some("Invalid amount".to_string());
            self.state = AppState::Normal;
        }
    }

    fn cancel_action(&mut self) {
        self.state = AppState::Normal;
        self.from_account.clear();
        self.to_account.clear();
        self.amount.clear();
        self.description.clear();
    }

    fn reset_state(&mut self) {
        self.state = AppState::Normal;
        self.input = Input::default();
        self.message.clear();
        self.error = None;
        self.gatekeeping_result = None;
        self.search_results.clear();
        self.selected_search_result = 0;
        self.from_account.clear();
        self.to_account.clear();
        self.amount.clear();
        self.description.clear();
        self.input_mode = InputMode::None;
    }
}
