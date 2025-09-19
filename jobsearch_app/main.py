from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for
from jobsearch_app.agent import AgentState, create_dataframe_agent
from jobsearch_app.data_processor import load_all_jsonl_data, DATA_DIR
import threading
import time
import ollama
import os

app = Flask(__name__, static_folder='../frontend/dist', template_folder='../frontend/dist')
import os
import pandas as pd # Import pandas because the agent works with DataFrames

# Load and sample data using the custom data_processor
# Use data_processor.DATA_DIR for the path as defined in data_processor.py
df = load_all_jsonl_data(os.path.join(os.path.dirname(__file__), DATA_DIR))

# Sample 10% of the DataFrame for quicker validation, uncomment if needed for performance
# sampled_df = df.sample(frac=0.1, random_state=42)
# print(f"Sampled down to {len(sampled_df)} records (10% of original) for quicker validation.")
# agent_app = create_dataframe_agent(sampled_df)

agent_app = create_dataframe_agent(df)

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
    
    try:
        # The dataframe agent expects 'input' key in the invoke method
        # and returns a dictionary with 'output' key
        response = agent_app.invoke({"input": query})
        output = response.get('output', str(response)) # Ensure we get the 'output' or full response

        print(f"Agent Response: {output}")
        return jsonify({"response": output})
    except Exception as e:
        print(f"Agent Error: {e}")
        return jsonify({"error": str(e)}), 500

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

    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
