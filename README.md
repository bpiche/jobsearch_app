# Job Search AI Assistant

This project sets up a LangChain + LangGraph application powered by Ollama to act as an AI assistant for job search related queries. It exposes a Flask endpoint for interaction.

## Setup and Running Instructions

Follow these steps to get the application running on your local machine.

### 1. Python Virtual Environment Setup

It is highly recommended to use a Python virtual environment to manage dependencies.

**From the project's root directory (`/home/bpiche/Projects/jobsearch_app`):**

```bash
python3 -m venv ~/.venv/venv
source ~/.venv/venv/bin/activate
pip install -r requirements.txt
```

This will create and activate a virtual environment, then install all necessary Python packages.

### 2. Ollama Server and LLM Model Setup

The application uses Ollama to serve a local Large Language Model (LLM).

**a. Install Ollama:**

If you don't have Ollama installed, follow the instructions on their official website:
[https://ollama.com/](https://ollama.com/)

**b. Start Ollama Server and Pull a Model:**

Start the Ollama server. This usually runs in the background.

```bash
ollama serve
```

In a **separate terminal** (or after starting `ollama serve`), pull the desired LLM model.
For systems with 8GB VRAM (like an Nvidia 3070ti), `llama3` is a good choice (requires approximately 4.7GB of VRAM). You can also try `tinyllama` if you encounter memory issues.

```bash
ollama pull llama3
# Or a smaller model, e.g.:
ollama pull tinyllama
```
**Note**: The `jobsearch_app/agent.py` file is configured to use the `llama3` model by default (`OLLAMA_MODEL = "llama3"`). If you pull a different model (e.g., `tinyllama`), you must update this variable in `agent.py` accordingly.

### 3. Run the Flask Application

Navigate to the `jobsearch_app` subdirectory and run the Flask application.

**From the project's root directory (`/home/bpiche/Projects/jobsearch_app`):**

```bash
cd jobsearch_app
python main.py
```
The Flask application will start on `http://0.0.0.0:5000`. It includes an initial check and continuous monitoring (in a background thread) for the Ollama server status. Ensure Ollama is running before (`python main.py`) to avoid errors.

### 4. Interact with the AI Assistant

You can interact with the agent by sending POST requests to the `/predict` endpoint.

**Example using `curl` (from a new terminal, with the virtual environment activated):**

```bash
source ~/.venv/venv/bin/activate
curl -X POST -H "Content-Type: application/json" -d '{"query": "What are the key skills for a Python developer in 2025 and which companies are hiring for them?"}' http://localhost:5000/predict
```

The application will return a JSON response containing the agent's generated answer.
