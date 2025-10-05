use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct User {
    pub id: i32,
    pub barcode: String,
    pub account_number: String,
    pub first_name: String,
    pub last_name: String,
    pub email: Option<String>,
    pub phone: Option<String>,
    pub date_of_birth: Option<String>,
    pub photo_url: Option<String>,
    pub pass_revoked: bool,
    pub can_go_negative: bool,
    pub permissions: Vec<String>,
    pub balance: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GatekeepingCheck {
    pub barcode: String,
    pub terminal_key: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GatekeepingResponse {
    pub success: bool,
    pub user: Option<User>,
    pub message: String,
    pub required_permissions: Vec<String>,
    pub user_permissions: Vec<String>,
    pub missing_permissions: Vec<String>,
    pub currency_required: bool,
    pub currency_amount: f64,
    pub current_balance: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TransactionCreate {
    pub from_account_number: String,
    pub to_account_number: String,
    pub amount: f64,
    pub description: Option<String>,
    pub terminal_key: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Transaction {
    pub id: i32,
    pub from_account_id: i32,
    pub to_account_id: i32,
    pub amount: f64,
    pub description: Option<String>,
    pub terminal_id: Option<i32>,
    pub created_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchResult {
    pub users: Vec<User>,
    pub total: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Balance {
    pub account_number: String,
    pub balance: f64,
    pub transaction_count: i32,
}

pub struct ApiClient {
    base_url: String,
    client: reqwest::blocking::Client,
}

impl ApiClient {
    pub fn new(base_url: String) -> Self {
        Self {
            base_url,
            client: reqwest::blocking::Client::new(),
        }
    }

    pub fn verify_access(&self, check: &GatekeepingCheck) -> Result<GatekeepingResponse> {
        let url = format!("{}/api/gatekeeping/verify", self.base_url);
        let response = self.client.post(&url).json(check).send()?;
        let result: GatekeepingResponse = response.json()?;
        Ok(result)
    }

    pub fn process_access(&self, check: &GatekeepingCheck) -> Result<GatekeepingResponse> {
        let url = format!("{}/api/gatekeeping/process", self.base_url);
        let response = self.client.post(&url).json(check).send()?;
        let result: GatekeepingResponse = response.json()?;
        Ok(result)
    }

    pub fn search_users(&self, query: &str) -> Result<SearchResult> {
        let url = format!("{}/api/users/search?query={}&limit=20", self.base_url, query);
        let response = self.client.get(&url).send()?;
        let result: SearchResult = response.json()?;
        Ok(result)
    }

    pub fn get_user_by_barcode(&self, barcode: &str) -> Result<User> {
        let url = format!("{}/api/users/barcode/{}", self.base_url, barcode);
        let response = self.client.get(&url).send()?;
        let result: User = response.json()?;
        Ok(result)
    }

    pub fn get_user_by_account(&self, account_number: &str) -> Result<User> {
        let url = format!("{}/api/users/account/{}", self.base_url, account_number);
        let response = self.client.get(&url).send()?;
        let result: User = response.json()?;
        Ok(result)
    }

    pub fn get_balance(&self, account_number: &str) -> Result<Balance> {
        let url = format!("{}/api/currency/balance/{}", self.base_url, account_number);
        let response = self.client.get(&url).send()?;
        let result: Balance = response.json()?;
        Ok(result)
    }

    pub fn transfer_money(&self, transfer: &TransactionCreate) -> Result<Transaction> {
        let url = format!("{}/api/currency/transfer", self.base_url);
        let response = self.client.post(&url).json(transfer).send()?;
        let result: Transaction = response.json()?;
        Ok(result)
    }
    
    pub fn authenticate(&self, barcode: &str, password: &str) -> Result<User> {
        let url = format!("{}/api/users/authenticate?barcode={}&password={}", self.base_url, barcode, password);
        let response = self.client.post(&url).send()?;
        let result: User = response.json()?;
        Ok(result)
    }
}

impl Default for ApiClient {
    fn default() -> Self {
        Self::new("http://localhost:8000".to_string())
    }
}
