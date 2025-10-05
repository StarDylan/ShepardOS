mod api;
mod app;
mod ui;
mod terminal_mode;

use anyhow::Result;
use app::App;
use crossterm::{
    event::{self, DisableMouseCapture, EnableMouseCapture, Event, KeyCode},
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};
use ratatui::{
    backend::CrosstermBackend,
    Terminal,
};
use std::io;

fn main() -> Result<()> {
    // Setup terminal
    enable_raw_mode()?;
    let mut stdout = io::stdout();
    execute!(stdout, EnterAlternateScreen, EnableMouseCapture)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    // Create app
    let mut app = App::new();

    // Run app
    let res = run_app(&mut terminal, &mut app);

    // Restore terminal
    disable_raw_mode()?;
    execute!(
        terminal.backend_mut(),
        LeaveAlternateScreen,
        DisableMouseCapture
    )?;
    terminal.show_cursor()?;

    if let Err(err) = res {
        eprintln!("{:?}", err);
    }

    Ok(())
}

fn run_app<B: ratatui::backend::Backend>(
    terminal: &mut Terminal<B>,
    app: &mut App,
) -> Result<()> {
    use std::time::{Duration, Instant};
    let mut last_key_time = Instant::now();
    let debounce_duration = Duration::from_millis(150); // Prevent double key presses
    
    loop {
        terminal.draw(|f| ui::draw(f, app))?;

        if let Event::Key(key) = event::read()? {
            let now = Instant::now();
            
            // Only process if enough time has passed since last key (except for typing)
            if app.is_input_active() || now.duration_since(last_key_time) >= debounce_duration {
                last_key_time = now;
                
                match key.code {
                    KeyCode::Char('q') if !app.is_input_active() && !app.is_authenticated() => {
                        if app.confirm_quit() {
                            return Ok(());
                        }
                    }
                    _ => {
                        app.handle_key_event(key);
                    }
                }
            }
        }
    }
}
