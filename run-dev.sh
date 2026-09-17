#!/usr/bin/env bash

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

sudo -v || exit 1

cleanup() {
    echo -e "\nCleaning up tmux sessions..."
    tmux kill-session -t fastapi 2>/dev/null
    tmux kill-session -t vue 2>/dev/null
    tmux kill-session -t minio 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

clear

echo "Starting minio server..."
tmux new-session -d -s minio -c "$PROJECT_ROOT/minio_data" "bash -c 'sudo ./run_minio.sh; exec bash'"

sleep 5  # Wait for minio to start

echo "Starting fastapi server..."
tmux new-session -d -s fastapi -c "$PROJECT_ROOT" "bash -c 'sudo $PROJECT_ROOT/venv/bin/fastapi dev backend/main.py; exec bash'"


echo "Starting vue frontend server..."
tmux new-session -d -s vue -c "$PROJECT_ROOT/frontend" "npm run dev"

echo "All servers started. Press Ctrl+C to stop."

while true; do
    sleep 1
done