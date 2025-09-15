from flask import Flask, request, jsonify
from jobsearch_app.agent import create_agent_workflow, AgentState
import threading
import time
import ollama

app = Flask(__name__)
agent_app = create_agent_workflow()

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    query = data.get("query")

    if not query:
        return jsonify({"error": "No query provided"}), 400

    print(f"Received query: {query}")
    
    initial_state = AgentState(query=query, response="")
    final_state_dict = agent_app.invoke(initial_state)
    final_state = AgentState(**final_state_dict)

    if final_state.error:
        print(f"Agent Error: {final_state.error}")
        return jsonify({"error": final_state.error}), 500
    else:
        print(f"Agent Response: {final_state.response}")
        return jsonify({"response": final_state.response})

# Function to check Ollama server status
def check_ollama_status():
    while True:
        try:
            # A simple way to check if Ollama server is running by trying to connect
            # and list models. This doesn't guarantee the specific model is downloaded,
            # but checks if the server itself is up.
            ollama.Client(host='http://localhost:11434').list()
            print("Ollama server is running.")
            return True
        except Exception:
            print("Ollama server not running. Please start Ollama and pull the model (e.g., 'ollama run llama3'). Retrying in 5 seconds...")
            time.sleep(5)

# Thread to run Ollama status check in background if Flask app is run directly
if __name__ == "__main__":
    print("Initializing Flask app and agent...")
    ollama_thread = threading.Thread(target=check_ollama_status)
    ollama_thread.daemon = True # Allow main program to exit even if thread is still running
    ollama_thread.start()

    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
