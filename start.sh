#!/bin/bash

# Activate the virtual environment
source /home/bpiche/.venv/venv/bin/activate

# Load environment variables from .env
set -a
source .env
set +a

# Check if Ollama server is already running
if ! pgrep -x "ollama" > /dev/null; then
  echo "Starting Ollama server in the background..."
  ollama serve &
else
  echo "Ollama server is already running."
fi

# Wait for Ollama to be available by checking if it can run a minimal model
echo "Waiting for Ollama to initialize and pull gemma3..."
until ollama run gemma3 "hi" > /dev/null 2>&1; do
  echo "Ollama not ready yet, or gemma3 not available. Retrying in 5 seconds..."
  sleep 5
done
echo "Ollama server is ready and gemma3 model is available."

# Start the Flask application in the background
echo "Starting Flask application..."
python3 -m jobsearch_app.main &

# Start the React frontend development server in the background
echo "Starting React frontend development server..."
cd frontend && npm install && npm run dev
