use crate::app::{App, AppState};
use crate::terminal_mode::TerminalMode;
use ratatui::{
    backend::Backend,
    layout::{Alignment, Constraint, Direction, Layout, Rect},
    style::{Color, Modifier, Style},
    text::{Line, Span, Text},
    widgets::{Block, Borders, List, ListItem, Paragraph, Wrap},
    Frame,
};

pub fn draw(f: &mut Frame, app: &App) {
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .margin(1)
        .constraints([
            Constraint::Length(3),
            Constraint::Min(10),
            Constraint::Length(3),
        ])
        .split(f.area());

    draw_header(f, chunks[0], app);
    draw_content(f, chunks[1], app);
    draw_footer(f, chunks[2], app);
}

fn draw_header(f: &mut Frame, area: Rect, app: &App) {
    let title = app.mode.title();
    let description = app.mode.description();
    
    let header = Paragraph::new(vec![
        Line::from(Span::styled(title, Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD))),
        Line::from(Span::styled(description, Style::default().fg(Color::Gray))),
    ])
    .block(Block::default().borders(Borders::ALL))
    .alignment(Alignment::Center);
    
    f.render_widget(header, area);
}

fn draw_content(f: &mut Frame, area: Rect, app: &App) {
    match app.state {
        AppState::Input => draw_input(f, area, app),
        AppState::Confirm => draw_confirm(f, area, app),
        AppState::Loading => draw_loading(f, area),
        AppState::DisplayResult => draw_result(f, area, app),
        AppState::Normal => {
            match app.mode {
                TerminalMode::Login => draw_login(f, area, app),
                TerminalMode::Locked => draw_locked(f, area, app),
                TerminalMode::Menu => draw_menu(f, area, app),
                TerminalMode::GatekeepingVerify | TerminalMode::GatekeepingProcess => {
                    draw_gatekeeping(f, area, app)
                }
                TerminalMode::CurrencyTransfer => draw_currency(f, area, app),
                TerminalMode::UserSearch => draw_search(f, area, app),
                TerminalMode::UserInfo => draw_user_info(f, area, app),
                TerminalMode::UserManagement => draw_user_management(f, area, app),
                TerminalMode::PermissionTree => draw_permission_tree(f, area, app),
                TerminalMode::TerminalManagement => draw_terminal_management(f, area, app),
                TerminalMode::Configuration => draw_config(f, area, app),
                _ => draw_placeholder(f, area, app),
            }
        }
    }
}

fn draw_footer(f: &mut Frame, area: Rect, app: &App) {
    let mut footer_text = vec![
        Line::from(vec![
            Span::styled("q: ", Style::default().fg(Color::Yellow)),
            Span::raw("Quit  "),
            Span::styled("ESC: ", Style::default().fg(Color::Yellow)),
            Span::raw("Back to Menu"),
        ]),
    ];

    if let Some(err) = &app.error {
        footer_text.push(Line::from(Span::styled(
            format!("ERROR: {}", err),
            Style::default().fg(Color::Red).add_modifier(Modifier::BOLD),
        )));
    }

    if !app.message.is_empty() {
        footer_text.push(Line::from(Span::styled(
            &app.message,
            Style::default().fg(Color::Green),
        )));
    }

    if !app.confirm_message.is_empty() {
        footer_text.push(Line::from(Span::styled(
            &app.confirm_message,
            Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD),
        )));
    }

    let footer = Paragraph::new(footer_text)
        .block(Block::default().borders(Borders::ALL))
        .alignment(Alignment::Left);
    
    f.render_widget(footer, area);
}

fn draw_menu(f: &mut Frame, area: Rect, app: &App) {
    let available_items = app.get_available_menu_items();
    
    let items: Vec<ListItem> = available_items
        .iter()
        .enumerate()
        .map(|(i, (_, name, _))| {
            let style = if i == app.selected_menu_item {
                Style::default().fg(Color::Black).bg(Color::Cyan).add_modifier(Modifier::BOLD)
            } else {
                Style::default().fg(Color::White)
            };
            ListItem::new(*name).style(style)
        })
        .collect();

    let user_info = if let Some(user) = &app.terminal_user {
        format!(" | Logged in as: {} {}", user.first_name, user.last_name)
    } else {
        String::new()
    };

    let list = List::new(items)
        .block(Block::default().borders(Borders::ALL).title(format!("Select Mode{}", user_info)));

    f.render_widget(list, area);
}

fn draw_gatekeeping(f: &mut Frame, area: Rect, app: &App) {
    let has_key = !app.terminal_key.is_empty();
    
    let mut text = vec![
        Line::from(""),
        Line::from(Span::styled("Terminal Status:", Style::default().add_modifier(Modifier::BOLD))),
        Line::from(if has_key {
            Span::styled("✓ Terminal key configured", Style::default().fg(Color::Green))
        } else {
            Span::styled("✗ Terminal key not configured", Style::default().fg(Color::Red))
        }),
        Line::from(""),
        Line::from(Span::styled("Actions:", Style::default().add_modifier(Modifier::BOLD))),
        Line::from(vec![
            Span::styled("s: ", Style::default().fg(Color::Yellow)),
            Span::raw("Scan barcode"),
        ]),
        Line::from(vec![
            Span::styled("k: ", Style::default().fg(Color::Yellow)),
            Span::raw("Configure terminal key"),
        ]),
    ];

    let mode_specific = match app.mode {
        TerminalMode::GatekeepingVerify => {
            "This mode will verify access without making any changes"
        }
        TerminalMode::GatekeepingProcess => {
            "This mode will verify access AND deduct currency if configured"
        }
        _ => "",
    };

    text.push(Line::from(""));
    text.push(Line::from(Span::styled(mode_specific, Style::default().fg(Color::Cyan))));

    let paragraph = Paragraph::new(text)
        .block(Block::default().borders(Borders::ALL).title("Gatekeeping Terminal"))
        .alignment(Alignment::Left);

    f.render_widget(paragraph, area);
}

fn draw_currency(f: &mut Frame, area: Rect, _app: &App) {
    let text = vec![
        Line::from(""),
        Line::from(Span::styled("Currency Transfer", Style::default().add_modifier(Modifier::BOLD))),
        Line::from(""),
        Line::from(vec![
            Span::styled("t: ", Style::default().fg(Color::Yellow)),
            Span::raw("Start new transfer"),
        ]),
        Line::from(""),
        Line::from(Span::styled("Transfer money between accounts", Style::default().fg(Color::Gray))),
    ];

    let paragraph = Paragraph::new(text)
        .block(Block::default().borders(Borders::ALL).title("Currency Operations"))
        .alignment(Alignment::Left);

    f.render_widget(paragraph, area);
}

fn draw_search(f: &mut Frame, area: Rect, app: &App) {
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([Constraint::Length(5), Constraint::Min(5)])
        .split(area);

    // Search instructions
    let text = vec![
        Line::from(vec![
            Span::styled("s: ", Style::default().fg(Color::Yellow)),
            Span::raw("Start search"),
        ]),
        Line::from(vec![
            Span::styled("↑↓: ", Style::default().fg(Color::Yellow)),
            Span::raw("Navigate results"),
        ]),
        Line::from(vec![
            Span::styled("Enter: ", Style::default().fg(Color::Yellow)),
            Span::raw("View user details"),
        ]),
    ];

    let paragraph = Paragraph::new(text)
        .block(Block::default().borders(Borders::ALL).title("Search"));

    f.render_widget(paragraph, chunks[0]);

    // Search results
    if !app.search_results.is_empty() {
        let items: Vec<ListItem> = app.search_results
            .iter()
            .enumerate()
            .map(|(i, user)| {
                let content = format!(
                    "{} {} | Barcode: {} | Account: {} | Balance: ${:.2}",
                    user.first_name, user.last_name, user.barcode, user.account_number, user.balance
                );
                let style = if i == app.selected_search_result {
                    Style::default().fg(Color::Black).bg(Color::Cyan)
                } else {
                    Style::default()
                };
                ListItem::new(content).style(style)
            })
            .collect();

        let list = List::new(items)
            .block(Block::default().borders(Borders::ALL).title("Results"));

        f.render_widget(list, chunks[1]);
    }
}

fn draw_user_info(f: &mut Frame, area: Rect, app: &App) {
    if let Some(user) = &app.current_user {
        let mut text = vec![
            Line::from(""),
            Line::from(Span::styled("User Information", Style::default().add_modifier(Modifier::BOLD))),
            Line::from(""),
            Line::from(vec![
                Span::styled("Name: ", Style::default().add_modifier(Modifier::BOLD)),
                Span::raw(format!("{} {}", user.first_name, user.last_name)),
            ]),
            Line::from(vec![
                Span::styled("Barcode: ", Style::default().add_modifier(Modifier::BOLD)),
                Span::raw(&user.barcode),
            ]),
            Line::from(vec![
                Span::styled("Account: ", Style::default().add_modifier(Modifier::BOLD)),
                Span::raw(&user.account_number),
            ]),
            Line::from(vec![
                Span::styled("Balance: ", Style::default().add_modifier(Modifier::BOLD)),
                Span::styled(format!("${:.2}", user.balance), Style::default().fg(Color::Green)),
            ]),
        ];

        if let Some(email) = &user.email {
            text.push(Line::from(vec![
                Span::styled("Email: ", Style::default().add_modifier(Modifier::BOLD)),
                Span::raw(email),
            ]));
        }

        if let Some(phone) = &user.phone {
            text.push(Line::from(vec![
                Span::styled("Phone: ", Style::default().add_modifier(Modifier::BOLD)),
                Span::raw(phone),
            ]));
        }

        if let Some(dob) = &user.date_of_birth {
            text.push(Line::from(vec![
                Span::styled("DOB: ", Style::default().add_modifier(Modifier::BOLD)),
                Span::raw(dob),
            ]));
        }

        text.push(Line::from(""));
        text.push(Line::from(Span::styled("Permissions:", Style::default().add_modifier(Modifier::BOLD))));
        
        if user.permissions.is_empty() {
            text.push(Line::from(Span::styled("  None", Style::default().fg(Color::Gray))));
        } else {
            for perm in &user.permissions {
                text.push(Line::from(format!("  • {}", perm)));
            }
        }

        text.push(Line::from(""));
        text.push(Line::from(vec![
            Span::styled("Pass Status: ", Style::default().add_modifier(Modifier::BOLD)),
            if user.pass_revoked {
                Span::styled("REVOKED", Style::default().fg(Color::Red).add_modifier(Modifier::BOLD))
            } else {
                Span::styled("Active", Style::default().fg(Color::Green))
            },
        ]));

        let paragraph = Paragraph::new(text)
            .block(Block::default().borders(Borders::ALL).title("User Details"))
            .wrap(Wrap { trim: true });

        f.render_widget(paragraph, area);
    }
}

fn draw_config(f: &mut Frame, area: Rect, app: &App) {
    let has_key = !app.terminal_key.is_empty();
    
    let text = vec![
        Line::from(""),
        Line::from(Span::styled("Terminal Configuration", Style::default().add_modifier(Modifier::BOLD))),
        Line::from(""),
        Line::from(vec![
            Span::styled("Status: ", Style::default().add_modifier(Modifier::BOLD)),
            if has_key {
                Span::styled("Configured", Style::default().fg(Color::Green))
            } else {
                Span::styled("Not Configured", Style::default().fg(Color::Red))
            },
        ]),
        Line::from(""),
        Line::from(vec![
            Span::styled("k: ", Style::default().fg(Color::Yellow)),
            Span::raw("Set terminal key"),
        ]),
        Line::from(""),
        Line::from(Span::styled(
            "The terminal key is required to authenticate with the server",
            Style::default().fg(Color::Gray)
        )),
    ];

    let paragraph = Paragraph::new(text)
        .block(Block::default().borders(Borders::ALL).title("Configuration"))
        .alignment(Alignment::Left);

    f.render_widget(paragraph, area);
}

fn draw_input(f: &mut Frame, area: Rect, app: &App) {
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([Constraint::Min(5), Constraint::Length(3)])
        .split(area);

    let label = Paragraph::new(vec![
        Line::from(""),
        Line::from(app.input_label.as_str()),
    ])
    .block(Block::default().borders(Borders::ALL).title("Input"));

    f.render_widget(label, chunks[0]);

    let input_widget = Paragraph::new(app.input.value())
        .style(Style::default().fg(Color::Yellow))
        .block(Block::default().borders(Borders::ALL));

    f.render_widget(input_widget, chunks[1]);
}

fn draw_confirm(f: &mut Frame, area: Rect, app: &App) {
    let text = vec![
        Line::from(""),
        Line::from(Span::styled(&app.confirm_message, Style::default().fg(Color::Yellow))),
    ];

    let paragraph = Paragraph::new(text)
        .block(Block::default().borders(Borders::ALL).title("Confirm"))
        .alignment(Alignment::Center)
        .wrap(Wrap { trim: true });

    f.render_widget(paragraph, area);
}

fn draw_loading(f: &mut Frame, area: Rect) {
    let text = vec![
        Line::from(""),
        Line::from(Span::styled("Loading...", Style::default().fg(Color::Cyan).add_modifier(Modifier::BOLD))),
    ];

    let paragraph = Paragraph::new(text)
        .block(Block::default().borders(Borders::ALL))
        .alignment(Alignment::Center);

    f.render_widget(paragraph, area);
}

fn draw_result(f: &mut Frame, area: Rect, app: &App) {
    if let Some(result) = &app.gatekeeping_result {
        let mut text = vec![
            Line::from(""),
            Line::from(Span::styled(
                "Access Verification Result",
                Style::default().add_modifier(Modifier::BOLD)
            )),
            Line::from(""),
        ];

        // Status
        text.push(Line::from(vec![
            Span::styled("Status: ", Style::default().add_modifier(Modifier::BOLD)),
            if result.success {
                Span::styled("✓ ACCESS GRANTED", Style::default().fg(Color::Green).add_modifier(Modifier::BOLD))
            } else {
                Span::styled("✗ ACCESS DENIED", Style::default().fg(Color::Red).add_modifier(Modifier::BOLD))
            },
        ]));

        // Message
        if !result.message.is_empty() {
            text.push(Line::from(""));
            text.push(Line::from(Span::styled(&result.message, Style::default().fg(Color::Yellow))));
        }

        // User info if available
        if let Some(user) = &result.user {
            text.push(Line::from(""));
            text.push(Line::from(Span::styled("User Information:", Style::default().add_modifier(Modifier::BOLD))));
            text.push(Line::from(format!("  Name: {} {}", user.first_name, user.last_name)));
            text.push(Line::from(format!("  Barcode: {}", user.barcode)));
            text.push(Line::from(format!("  Account: {}", user.account_number)));
            text.push(Line::from(format!("  Balance: ${:.2}", result.current_balance)));
        }

        // Permissions
        if !result.required_permissions.is_empty() {
            text.push(Line::from(""));
            text.push(Line::from(Span::styled("Required Permissions:", Style::default().add_modifier(Modifier::BOLD))));
            for perm in &result.required_permissions {
                let has_perm = result.user_permissions.contains(perm);
                text.push(Line::from(vec![
                    if has_perm {
                        Span::styled("  ✓ ", Style::default().fg(Color::Green))
                    } else {
                        Span::styled("  ✗ ", Style::default().fg(Color::Red))
                    },
                    Span::raw(perm),
                ]));
            }
        }

        // Currency info
        if result.currency_required {
            text.push(Line::from(""));
            text.push(Line::from(Span::styled("Currency:", Style::default().add_modifier(Modifier::BOLD))));
            text.push(Line::from(format!("  Required: ${:.2}", result.currency_amount)));
            text.push(Line::from(format!("  Balance: ${:.2}", result.current_balance)));
            
            if result.success && app.mode == TerminalMode::GatekeepingProcess {
                text.push(Line::from(Span::styled(
                    "  Currency has been debited",
                    Style::default().fg(Color::Green)
                )));
            }
        }

        text.push(Line::from(""));
        text.push(Line::from(Span::styled("Press Enter to continue", Style::default().fg(Color::Gray))));

        let paragraph = Paragraph::new(text)
            .block(Block::default().borders(Borders::ALL).title("Verification Result"))
            .wrap(Wrap { trim: true });

        f.render_widget(paragraph, area);
    }
}

fn draw_login(f: &mut Frame, area: Rect, app: &App) {
    let text = vec![
        Line::from(""),
        Line::from(Span::styled("Terminal Authentication Required", Style::default().add_modifier(Modifier::BOLD).fg(Color::Cyan))),
        Line::from(""),
        Line::from("Please scan your barcode or enter your credentials to access this terminal."),
        Line::from(""),
        Line::from(vec![
            Span::styled("l: ", Style::default().fg(Color::Yellow)),
            Span::raw("Login with barcode"),
        ]),
        Line::from(""),
        Line::from(Span::styled("Note: Only authorized personnel may use this terminal", Style::default().fg(Color::Gray))),
    ];

    let paragraph = Paragraph::new(text)
        .block(Block::default().borders(Borders::ALL).title("Login"))
        .alignment(Alignment::Center);

    f.render_widget(paragraph, area);
}

fn draw_locked(f: &mut Frame, area: Rect, app: &App) {
    let user_name = if let Some(user) = &app.terminal_user {
        format!("{} {}", user.first_name, user.last_name)
    } else {
        "Unknown".to_string()
    };

    let text = vec![
        Line::from(""),
        Line::from(Span::styled("🔒 TERMINAL LOCKED", Style::default().add_modifier(Modifier::BOLD).fg(Color::Red))),
        Line::from(""),
        Line::from(format!("Logged in as: {}", user_name)),
        Line::from(""),
        Line::from(vec![
            Span::styled("u: ", Style::default().fg(Color::Yellow)),
            Span::raw("Unlock terminal"),
        ]),
        Line::from(""),
        Line::from(Span::styled("This terminal has been locked for security", Style::default().fg(Color::Gray))),
    ];

    let paragraph = Paragraph::new(text)
        .block(Block::default().borders(Borders::ALL).title("Locked"))
        .alignment(Alignment::Center);

    f.render_widget(paragraph, area);
}

fn draw_user_management(f: &mut Frame, area: Rect, app: &App) {
    let text = vec![
        Line::from(""),
        Line::from(Span::styled("User Management", Style::default().add_modifier(Modifier::BOLD))),
        Line::from(""),
        Line::from(vec![
            Span::styled("c: ", Style::default().fg(Color::Yellow)),
            Span::raw("Create new user"),
        ]),
        Line::from(vec![
            Span::styled("l: ", Style::default().fg(Color::Yellow)),
            Span::raw("List all users"),
        ]),
        Line::from(vec![
            Span::styled("s: ", Style::default().fg(Color::Yellow)),
            Span::raw("Search users"),
        ]),
        Line::from(""),
        Line::from(Span::styled("Manage system users and their access", Style::default().fg(Color::Gray))),
    ];

    let paragraph = Paragraph::new(text)
        .block(Block::default().borders(Borders::ALL).title("User Management"))
        .alignment(Alignment::Left);

    f.render_widget(paragraph, area);
}

fn draw_permission_tree(f: &mut Frame, area: Rect, _app: &App) {
    let text = vec![
        Line::from(""),
        Line::from(Span::styled("Permission Hierarchy", Style::default().add_modifier(Modifier::BOLD))),
        Line::from(""),
        Line::from("System Permissions:"),
        Line::from("  ├─ system.admin - Full system administration"),
        Line::from("  ├─ system.manage_users - Manage users"),
        Line::from("  └─ system.manage_terminals - Manage terminals"),
        Line::from(""),
        Line::from("Custom Permissions:"),
        Line::from("  ├─ checkpoint.a.access - Access Checkpoint A"),
        Line::from("  ├─ checkpoint.b.access - Access Checkpoint B"),
        Line::from("  ├─ store.purchase - Make purchases"),
        Line::from("  └─ facility.entry - Enter facility"),
        Line::from(""),
        Line::from(Span::styled("Press ESC to return to menu", Style::default().fg(Color::Gray))),
    ];

    let paragraph = Paragraph::new(text)
        .block(Block::default().borders(Borders::ALL).title("Permission Tree"))
        .alignment(Alignment::Left);

    f.render_widget(paragraph, area);
}

fn draw_terminal_management(f: &mut Frame, area: Rect, _app: &App) {
    let text = vec![
        Line::from(""),
        Line::from(Span::styled("Terminal Management", Style::default().add_modifier(Modifier::BOLD))),
        Line::from(""),
        Line::from(vec![
            Span::styled("c: ", Style::default().fg(Color::Yellow)),
            Span::raw("Create new terminal"),
        ]),
        Line::from(""),
        Line::from(Span::styled("Configure and manage terminal settings", Style::default().fg(Color::Gray))),
    ];

    let paragraph = Paragraph::new(text)
        .block(Block::default().borders(Borders::ALL).title("Terminal Management"))
        .alignment(Alignment::Left);

    f.render_widget(paragraph, area);
}

fn draw_placeholder(f: &mut Frame, area: Rect, app: &App) {
    let text = vec![
        Line::from(""),
        Line::from(Span::styled("Feature In Development", Style::default().add_modifier(Modifier::BOLD))),
        Line::from(""),
        Line::from(format!("Mode: {:?}", app.mode)),
        Line::from(""),
        Line::from(Span::styled("Press ESC to return to menu", Style::default().fg(Color::Gray))),
    ];

    let paragraph = Paragraph::new(text)
        .block(Block::default().borders(Borders::ALL).title("Coming Soon"))
        .alignment(Alignment::Center);

    f.render_widget(paragraph, area);
}
