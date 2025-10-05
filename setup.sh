#!/bin/bash
# Setup script for ShepardOS

set -e

echo "========================================="
echo "ShepardOS Setup"
echo "========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check Rust
if ! command -v cargo &> /dev/null; then
    echo "Error: Rust/Cargo is required but not installed."
    echo "Visit https://rustup.rs to install Rust."
    exit 1
fi

# Setup backend
echo "Setting up backend..."
cd backend
pip install -r requirements.txt
python seed_data.py
cd ..

# Build frontend
echo ""
echo "Building frontend..."
cd frontend
cargo build --release
cd ..

echo ""
echo "========================================="
echo "Setup complete!"
echo "========================================="
echo ""
echo "To start the system:"
echo "  1. Start backend:  cd backend && python main.py"
echo "  2. Start frontend: cd frontend && cargo run --release"
echo ""
echo "Terminal keys for testing:"
echo "  Checkpoint A: checkpoint_a_test_key_12345"
echo "  Store Terminal: store_terminal_test_key_67890"
echo ""
echo "Test user barcodes:"
echo "  Admin: 100000000001"
echo "  Guard: 100000000002"
echo "  Employee: 100000000003"
echo ""
