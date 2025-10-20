#!/bin/bash

# Activate the virtual environment
source /Users/bpiche/.venv/venv/bin/activate

# Load environment variables from .env
set -a
source .env
set +a

# Export OLLAMA_HOST, which will always be local
export OLLAMA_HOST=$OLLAMA_HOST_LOCAL

# Determine if --cloud flag is used
USE_CLOUD_MODEL="false"
for arg in "$@"; do
  if [ "$arg" == "--cloud" ]; then
    USE_CLOUD_MODEL="true"
    break
  fi
done

# Set OLLAMA_MODEL based on the flag
if [ "$USE_CLOUD_MODEL" == "true" ]; then
  export OLLAMA_MODEL=$OLLAMA_CLOUD_MODEL
  ollama run "$OLLAMA_MODEL" "hi" > /dev/null 2>&1
  echo "Using cloud Ollama model: $OLLAMA_MODEL from $OLLAMA_HOST"
else
  export OLLAMA_MODEL=$OLLAMA_LOCAL_MODEL
  echo "Using local Ollama model: $OLLAMA_MODEL from $OLLAMA_HOST"

  # Check if Ollama server is already running for local model
  if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama server in the background..."
    ollama serve &
  else
    echo "Ollama server is already running."
  fi

  # Wait for Ollama to be available by checking if it can run the local model
  echo "Waiting for Ollama to initialize and pull $OLLAMA_MODEL..."
  until ollama run "$OLLAMA_MODEL" "hi" > /dev/null 2>&1; do
    echo "Ollama not ready yet, or $OLLAMA_MODEL not available. Retrying in 5 seconds..."
    sleep 5
  done
  echo "Ollama server is ready and $OLLAMA_MODEL model is available."
fi

# Start the Flask application in the background
echo "Starting Flask application..."
python3 -m jobsearch_app.main &

# Start the React frontend development server in the background
echo "Starting React frontend development server..."
cd frontend && npm install && npm run dev
