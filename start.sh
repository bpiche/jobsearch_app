#!/bin/bash
# Start Ollama server in the background
ollama serve &

# Wait for Ollama to be available (optional, but good practice if Flask connects quickly)
# A simple delay is sufficient for this example, or implement a loop to check availability
echo "Waiting for Ollama to initialize..."
sleep 5

# Run the Flask application
echo "Starting Flask application..."
python -m jobsearch_app.main
