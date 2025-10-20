# Use an official Ubuntu image as a base
FROM ubuntu:latest

# Set environment variables for Python
ENV PYTHONUNBUFFERED 1
ENV VIRTUAL_ENV /opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV TAVILY_API_KEY="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"

# Install system dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv curl wget git && \
    rm -rf /var/lib/apt/lists/*

# Install Ollama directly using their install script
# Note: For production, consider pinning to a specific Ollama version
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt and project code
COPY requirements.txt .
COPY jobsearch_app jobsearch_app/

# Create and activate virtual environment, then install Python dependencies
RUN python3 -m venv "$VIRTUAL_ENV" && \
    pip install --no-cache-dir -r requirements.txt

# Pull the llama3 model during the build process
# This ensures the model is available when the container starts.
# Note: This increases image size. For dynamic model loading, remove this and handle in start.sh
RUN ollama pull llama3

# Copy the startup script
COPY start.sh .
# Make the startup script executable
RUN chmod +x start.sh

# Expose the Flask port (5000) and Ollama port (11434)
EXPOSE 5000
EXPOSE 11434

# Command to run the application using the startup script
CMD ["./start.sh"]
