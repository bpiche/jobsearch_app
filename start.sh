#!/bin/bash

# Activate the virtual environment
source /home/bpiche/.venv/venv/bin/activate

# Build the React frontend
echo "Building React frontend..."
cd frontend && npm install && npm run build && cd ..

# Check if Ollama server is already running
if ! pgrep -x "ollama" > /dev/null; then
  echo "Starting Ollama server in the background..."
  ollama serve &
else
  echo "Ollama server is already running."
fi

# Wait for Ollama to be available by checking if it can run a minimal model
echo "Waiting for Ollama to initialize and pull llama3..."
until ollama run llama3 "hi" > /dev/null 2>&1; do
  echo "Ollama not ready yet, or llama3 not available. Retrying in 5 seconds..."
  sleep 5
done
echo "Ollama server is ready and llama3 model is available."

# Run the Flask application
echo "Starting Flask application..."
python3 -m jobsearch_app.main
