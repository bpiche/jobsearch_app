# Job Search AI Assistant

This project sets up a LangChain + LangGraph application powered by Ollama to act as an AI assistant for job search related queries. It exposes a Flask endpoint for interaction.

## Setup and Running Instructions

This project can be run either directly on your local machine or containerized using Docker.

### Local Setup and Running (Recommended if you prefer local Ollama setup)

Follow these steps to get the application running directly on your local machine.

#### 1. Python Virtual Environment Setup

It is highly recommended to use a Python virtual environment to manage dependencies.

**From the project's root directory (`/home/bpiche/Projects/jobsearch_app`):**

```bash
python3 -m venv ~/.venv/venv
source ~/.venv/venv/bin/activate
pip install -r requirements.txt
```

This will create and activate a virtual environment, then install all necessary Python packages.

#### 2. Ollama Server and LLM Model Setup (Local)

The application uses Ollama to serve a local Large Language Model (LLM).

**a. Install Ollama:**

If you don't have Ollama installed globally on your system, follow the instructions on their official website:
[https://ollama.com/](https://ollama.com/)

**b. Start Ollama Server and Pull a Model:**

Start the Ollama server. This usually runs in the background. **Open a new terminal for this.**

```bash
ollama serve
```

In the same terminal where `ollama serve` is running (or a third terminal if preferred), pull the desired LLM model.
For systems with 8GB VRAM (like an Nvidia 3070ti), `llama3` is a good choice (requires approximately 4.7GB of VRAM). You can also try `tinyllama` if you encounter memory issues.

```bash
ollama pull llama3
# Or a smaller model, e.g.:
ollama pull tinyllama
```
**Note**: The `jobsearch_app/agent.py` file is configured to use the `llama3` model by default (`OLLAMA_MODEL = "llama3"`). If you pull a different model (e.g., `tinyllama`), you must update this variable in `agent.py` accordingly.

#### 3. Run the Flask Application (Local)

Ensure your virtual environment is activated. Then, from the project's root directory, run the Flask application.

**From the project's root directory (`/home/bpiche/Projects/jobsearch_app`):**

```bash
source ~/.venv/venv/bin/activate
python -m jobsearch_app.main
```
The Flask application will start on `http://0.0.0.0:5000`. It includes a background check for the Ollama server status. Ensure Ollama is running (`ollama serve` in a separate terminal) before interacting with the Flask app.

### Dockerized Setup and Running

Alternatively, you can run the entire application, including Ollama, within a Docker container.

#### 1. Build the Docker Image

From the project's root directory, build the Docker image. This process will install dependencies, Ollama, and pull the `llama3` model (which may take some time).

```bash
docker build -t jobsearch-ai-app .
```

#### 2. Run the Docker Container

Once the image is built, run the container, mapping the necessary ports (Flask app on 5000, Ollama on 11434).

```bash
docker run -p 5000:5000 -p 11434:11434 --name jobsearch-agent-container jobsearch-ai-app
```
**Note**: The `ollama serve` process runs in the background within the container, and `llama3` model is pulled during the build phase to ensure readiness.

### Interacting with the AI Assistant

You can interact with the agent by sending POST requests to the `/predict` endpoint.

**Example using `curl` (from a new terminal, with the virtual environment activated):**

```bash
source ~/.venv/venv/bin/activate
curl -X POST -H "Content-Type: application/json" -d '{"query": "What are the key skills for a Python developer in 2025 and which companies are hiring for them?"}' http://localhost:5000/predict
```

The application will return a JSON response containing the agent's generated answer.
