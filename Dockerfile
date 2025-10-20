# Use an official Ubuntu image as a base
FROM ubuntu:latest

# Set environment variables for Python
ENV PYTHONUNBUFFERED 1
ENV VIRTUAL_ENV /opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ARG TAVILY_API_KEY
ENV TAVILY_API_KEY=$TAVILY_API_KEY

# Install system dependencies (including Node.js and npm for frontend)
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv curl wget git unzip && \
    # Install Node.js and npm for the frontend
    curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install Ollama directly using their install script
# Note: For production, consider pinning to a specific Ollama version
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt and project code
COPY requirements.txt .
COPY jobsearch_app jobsearch_app/
COPY frontend frontend/

# Create and activate virtual environment, then install Python dependencies
RUN python3 -m venv "$VIRTUAL_ENV" && \
    pip install --no-cache-dir -r requirements.txt

# Install frontend dependencies
WORKDIR /app/frontend
RUN npm install
WORKDIR /app

# Pull the gemma3 model during the build process
# This ensures the model is available when the container starts.
# Start Ollama server temporarily in background to pull model during build
RUN (ollama serve &) && \
    /bin/bash -c 'until ollama list | grep -q "gemma3"; do echo "Waiting for Ollama to start..."; sleep 5; done' && \
    ollama pull gemma3 && \
    pkill ollama || true
# Note: This increases image size. For dynamic model loading, consider handling in start.sh only.

# Copy the startup script
COPY start.sh .
# Make the startup script executable
RUN chmod +x start.sh

# Expose the Flask port (5000) and Ollama port (11434)
EXPOSE 5000
EXPOSE 11434

# Command to run the application using the startup script
CMD ["./start.sh"]
