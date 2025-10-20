# Job Search AI Assistant (Full-stack)

This project provides a full-stack AI assistant for job search queries, featuring a user-friendly React frontend and a LangChain + LangGraph backend powered by Ollama. The backend exposes a Flask endpoint for AI interaction, while the frontend offers a seamless user experience.

## Setup and Running Instructions

This project can be run either directly on your local machine or containerized using Docker.

### Local Setup and Running (Recommended if you prefer local Ollama setup)

Follow these steps to get the application running directly on your local machine.

#### 1. Python Virtual Environment Setup

It is highly recommended to use a Python virtual environment to manage dependencies.

**From the project's root directory:**

```bash
python3 -m venv ~/.venv/venv
source ~/.venv/venv/bin/activate
pip install -r requirements.txt
```

This will create and activate a virtual environment, then install all necessary Python packages.

#### 2. Frontend Application Setup

The frontend is a React application developed with Vite.

**From the `frontend/` directory:**

```bash
cd frontend
npm install
```

This will install all necessary JavaScript dependencies for the frontend.

#### 3. Ollama Server and LLM Model Setup (Local)

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
For systems with 8GB VRAM (like an Nvidia 3070ti), `llama3.1` is a good choice (requires approximately 4.7GB of VRAM). You can also try `gemma3` if you encounter memory issues.

```bash
ollama pull llama3.1
# Or a smaller model, e.g.:
ollama pull gemma3
```
**Note**: The `jobsearch_app/agent.py` file is configured to use the `gemma3` model by default (`OLLAMA_MODEL = "gemma3"`). If you pull a different model (e.g., `llama3.1`), you must update this variable in `agent.py` accordingly.

#### 4. SQL Database Setup (Local - SQLite in Docker)

A local SQLite database containing AI job dataset is set up using a dedicated Docker container. The database file (`ai_jobs.db`) will be created in the `data/` directory of this project.

**a. Build the SQLite Docker Image:**

From the project's root directory:
```bash
docker build -t sqlite-db -f database_container/Dockerfile .
```

**b. Run the SQLite Docker Container:**

This will start the database container, which now includes the `ai_jobs.db` database automatically populated from `ai_job_dataset.csv` during the build process. It mounts the `data/` directory to persist the database file, and the container will automatically restart if stopped.
```bash
docker run -d --name sqlite-jobsearch -v $(pwd)/data:/app/data --restart unless-stopped sqlite-db
```


#### 5. Run the Flask Application (Local)

Ensure your virtual environment is activated and the SQLite Docker container is running. Then, from the project's root directory, run the Flask application.

**Important Note on `start.sh` and API Keys:**
The `start.sh` script, located in the root directory, is designed to set up the Python virtual environment, export necessary environment variables (like `TAVILY_API_KEY`), and start the Flask backend and React frontend sequentially. It is the recommended way to run the application locally if you intend to use the Search Agent, as it handles the `TAVILY_API_KEY` export automatically. If you run the Flask application manually (as shown below), you must ensure the `TAVILY_API_KEY` is exported in your environment *before* starting the Flask app.

**Option 1: Using `start.sh` (Recommended for full functionality)**

From the project's root directory:
```bash
bash start.sh
```
This script will activate the Python environment, export environment variables, start the Flask backend, and then launch the React frontend.

**Option 2: Manual execution of Flask Application**

From the project's root directory (after manually activating the virtual environment and exporting `TAVILY_API_KEY` if using the Search Agent):

```bash
source ~/.venv/venv/bin/activate
python -m jobsearch_app.main
```
The Flask application will start on `http://0.0.0.0:5000`. It includes a background check for the Ollama server status. Ensure Ollama is running (`ollama serve` in a separate terminal) and the `sqlite-jobsearch` container is active. For the full UI experience, you will also need to run the frontend application.

### Dockerized Setup and Running (Using Docker Compose)

For a more streamlined setup that orchestrates both the database and the main application (backend + frontend + Ollama) in separate but connected containers, use Docker Compose.

**Prerequisites:**
*   Docker and Docker Compose installed on your system.
*   **TAVILY_API_KEY:** Ensure you have your Tavily API key set as an environment variable in your shell (e.g., `export TAVILY_API_KEY="your_api_key_here"`) before running `docker compose up`, as the application container requires it.

**From the project's root directory:**

```bash
docker compose up --build
```

This command will:
1.  Build the `db` service (SQLite database) using `database_container/Dockerfile`, creating and populating `data/ai_jobs.db`.
2.  Build the `app` service using the main `Dockerfile`, which includes installing Python and Node.js dependencies, setting up the virtual environment, pulling the `gemma3` Ollama model, and copying the `start.sh` script.
3.  Start both the `db` and `app` containers. The `app` container's `start.sh` will then launch Ollama, the Flask backend, and the React frontend in the correct order, waiting for dependencies to be ready.
4.  Map the necessary ports: `5000` (Flask backend), `5173` (React frontend), and `11434` (Ollama server) to your host machine.

The application will be accessible via your browser at `http://localhost:5173`.

To stop the containers:
```bash
docker compose down
```

### Interacting with the AI Assistant

**1. Launching the Frontend UI:**

To interact with the full-stack application, navigate to the `frontend/` directory in a new terminal and start the development server:

```bash
cd frontend
npm run dev
```
The application will typically open in your browser at `http://localhost:5173` (or another available port). This UI provides an intuitive way to send queries to the AI assistant.

**2. Direct API Interaction (using `curl`):**

For direct API testing or integration, you can still send POST requests to the `/predict` endpoint. The agent handles both general job search queries and SQL-specific questions to the `ai_job_dataset` table.

**Example using `curl` (from a new terminal, with the Python virtual environment activated):**

```bash
source ~/.venv/venv/bin/activate
curl -X POST -H "Content-Type: application/json" -d '{"query": "What are the key skills for a Python developer in 2025 and which companies are hiring for them?"}' http://localhost:5000/predict'
```

**Example SQL Query via Agent:**

```bash
source ~/.venv/venv/bin/activate
curl -X POST -H "Content-Type: application/json" -d '{"query": "How many rows are in the ai_job_dataset table?"}' http://localhost:5000/predict'
```

The backend will return a JSON response containing the agent's generated answer.

### AI Agent Capabilities

This application features a multi-agent system powered by LangChain and LangGraph, capable of routing user queries to specialized agents based on detected keywords. This allows for more targeted and effective responses to different types of job search inquiries.

#### 1. General LLM Agent

*   **Purpose:** Handles general job search queries, providing comprehensive answers based on its foundational knowledge. This is the default agent when no specific keywords for other agents are detected.
*   **Interaction:** Simply ask your job search-related questions naturally.
*   **Example Query:** "What are the common skills required for a machine learning engineer in 2025 and what are the top companies hiring?"

#### 2. SQL Agent

*   **Purpose:** Interacts with the `ai_job_dataset` SQLite database to answer data-specific questions. This agent is ideal for extracting structured information, performing counts, or listing data entries.
*   **Interaction:** Use keywords like "database", "sql", "query", "table", "count", "list", "top", "group by", or "join" in your questions. You can ask about the database directly.
*   **Example Queries:**
    *   "How many jobs are in the ai_job_dataset table?"
    *   "List the top 5 companies by job count in the database."
    *   "Show me the schema of the ai_job_dataset table."

#### 3. Search Agent

*   **Purpose:** Conducts real-time web searches using the Tavily API to fetch current information, news, or broader context that might not be available in the LLM's training data or the local database.
*   **Interaction:** Trigger this agent by including keywords such as "search", "find information", "latest news", "what is", "how to", "current events", "who is", "when did", "forecast", or "weather" in your query.
*   **Example Queries:**
    *   "Search for the latest trends in remote software development jobs."
    *   "What is the average salary for a data scientist in New York City?"
    *   "Find information about new AI regulations."

---

![Screenshot of the Job Search AI Assistant UI](screenshot.png)
