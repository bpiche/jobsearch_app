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
**Note**: The `jobsearch_app/agent.py` file is configured to use the `llama3` model by default (`OLLAMA_MODEL = "llama3"`). If you pull a different model (e.g., `tinyllama`), you must update this variable in `agent.py` accordingly.

#### 4. SQL Database Setup (Local - SQLite in Docker)

A local SQLite database containing AI job dataset is set up using a dedicated Docker container. The database file (`ai_jobs.db`) will be created in the `data/` directory of this project.

**a. Build the SQLite Docker Image:**

From the project's root directory:
```bash
docker build -t sqlite-db database_container
```

**b. Run the SQLite Docker Container:**

This will start the database container and mount the `data/` directory to persist the database file. The container will automatically restart if stopped.
```bash
docker run -d --name sqlite-jobsearch -v $(pwd)/data:/app/data --restart unless-stopped sqlite-db
```

**c. Import Data into SQLite Database:**

Once the container is running, import the `ai_job_dataset.csv` into the `ai_jobs.db` database.
```bash
docker exec -it sqlite-jobsearch bash -c 'csvsql --db sqlite:///ai_jobs.db --insert ai_job_dataset.csv'
```
You can verify the data import and test queries using:
```bash
docker exec -it sqlite-jobsearch sqlite3 ai_jobs.db "SELECT COUNT(*) FROM ai_job_dataset;"
docker exec -it sqlite-jobsearch sqlite3 ai_jobs.db "SELECT * FROM ai_job_dataset LIMIT 3;"
```

#### 5. Run the Flask Application (Local)

Ensure your virtual environment is activated and the SQLite Docker container is running. Then, from the project's root directory, run the Flask application.

**From the project's root directory:**

```bash
source ~/.venv/venv/bin/activate
python -m jobsearch_app.main
```
The Flask application will start on `http://0.0.0.0:5000`. It includes a background check for the Ollama server status. Ensure Ollama is running (`ollama serve` in a separate terminal) and the `sqlite-jobsearch` container is active. For the full UI experience, you will also need to run the frontend application.

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

## UI Screenshot

![Screenshot of the Job Search AI Assistant UI](screenshot.png)
