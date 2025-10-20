#!/bin/bash

# No need to activate virtual env here; Dockerfile sets up /opt/venv and adds to PATH
# TAVILY_API_KEY will be provided by Docker Compose environment variables, so no .env sourcing needed

# Check if Ollama server is already running
if ! pgrep -x "ollama" > /dev/null; then
  echo "Starting Ollama server in the background..."
  ollama serve &
  OLLAMA_PID=$!
else
  echo "Ollama server is already running."
fi

# Wait for Ollama to be available
echo "Waiting for Ollama to initialize and detect gemma3..."
# Ensure Ollama server is fully up and the gemma3 model is listed
until ollama list | grep -q "gemma3"; do
  echo "Ollama not ready yet, or gemma3 not detected. Retrying in 5 seconds..."
  sleep 5
done
echo "Ollama server is ready and gemma3 model is available."

# Start the Flask application in the background
echo "Starting Flask application..."
python3 -m jobsearch_app.main > /var/log/flask_backend.log 2>&1 &
FLASK_PID=$!

# Navigate to frontend and start the React frontend development server
echo "Starting React frontend development server..."
cd frontend && npm run dev > /var/log/react_frontend.log 2>&1 &
FRONTEND_PID=$!

# Function to clean up background processes
function cleanup {
  echo "Stopping Flask backend (PID: $FLASK_PID)..."
  kill $FLASK_PID
  echo "Stopping React frontend (PID: $FRONTEND_PID)..."
  kill $FRONTEND_PID
  if [ -n "$OLLAMA_PID" ]; then
    echo "Stopping Ollama server (PID: $OLLAMA_PID)..."
    kill $OLLAMA_PID
  else
    echo "Ollama server might have been running externally or was not started by this script. Attempting `pkill ollama`"
    pkill ollama || true
  fi
  exit 0
}

# Trap SIGINT (Ctrl+C) and SIGTERM (docker stop) to run cleanup function
trap cleanup SIGINT SIGTERM

echo "Application is running. Press Ctrl+C to stop."
# Wait for Flask and Frontend processes to keep the script (and container) alive
wait $FLASK_PID &
wait $FRONTEND_PID &
wait -n # Wait for any child process to exit. This helps handle if one crashes.
# If all children still running, wait on main trap signals
wait
