from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for
from jobsearch_app.agent import create_agent_workflow, AgentState
import threading
import time
import ollama
import os

app = Flask(__name__, static_folder='../frontend/dist', template_folder='../frontend/dist')
agent_app = create_agent_workflow()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return render_template('index.html')

@app.route("/predict", methods=["POST"])
def redirect_predict():
    return redirect(url_for('predict_api'), code=307) # Use 307 for POST requests

@app.route("/api/predict", methods=["POST"])
def predict_api():
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

def check_ollama_status():
    while True:
        try:
            ollama.Client(host='http://localhost:11434').list()
            print("Ollama server is running.")
            return True
        except Exception:
            print("Ollama server not running. Please start Ollama and pull the model (e.g., 'ollama run llama3'). Retrying in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    print("Initializing Flask app and agent...")
    ollama_thread = threading.Thread(target=check_ollama_status)
    ollama_thread.daemon = True
    ollama_thread.start()

    app.run(host="0.0.0.0", port=5001, debug=True, use_reloader=False)
