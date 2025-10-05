#!/bin/bash
# Run script for ShepardOS

echo "========================================="
echo "Starting ShepardOS"
echo "========================================="
echo ""

# Start backend in background
echo "Starting backend server..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting frontend TUI..."
cd frontend
cargo run --release

# Cleanup on exit
kill $BACKEND_PID 2>/dev/null
