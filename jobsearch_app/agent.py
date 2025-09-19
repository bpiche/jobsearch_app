from dataclasses import dataclass
import pandas as pd
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_community.chat_models import ChatOllama
from langchain_core.callbacks import StdOutCallbackHandler
import os
from . import data_processor # Keep this for `load_all_jsonl_data`

# --- Agent State ---
@dataclass
class AgentState:
    """
    Represents the state of our agent.
    Since the dataframe agent returns output directly,
    this class might be simplified or adapted based on how errors are propagated.
    Keeping it for now for compatibility and potential future use in complex workflows.
    """
    query: str
    response: str = "" # Default empty string
    error: str = None   # To handle potential errors


def create_dataframe_agent(df: pd.DataFrame):
    # Initialize Ollama LLM as a ChatModel
    # Ensure Ollama server is running and `llama3` model is pulled (e.g., `ollama pull llama3`)
    llm = ChatOllama(model="llama3") 
    agent = create_pandas_dataframe_agent(
        llm, 
        df, 
        verbose=True, 
        agent_type=AgentType.OPENAI_FUNCTIONS, # Specify agent type
        allow_dangerous_code=True,
        handle_parsing_errors=True # Add error handling
    )
    return agent

# Main entry point for the agent if run directly (for testing)
if __name__ == '__main__':
    # Adjust this path if running from a different location for testing
    # Assuming 'data' directory is sibling to 'jobsearch_app' or within it
    # For standalone testing of agent.py, data_processor.py needs to be able to find `data`
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir_path = os.path.join(current_dir, '../data') # Assuming data is in jobsearch_app/data

    if not os.path.exists(data_dir_path):
        # Fallback if data is directly in the project root like jobsearch_app/data
        data_dir_path = os.path.join(current_dir, 'data')

    print(f"Attempting to load data from: {data_dir_path}")
    df = data_processor.load_all_jsonl_data(data_dir_path)
    
    # Always sample for __main__ block testing to prevent excessive memory usage / load times
    sampled_df = df.sample(frac=0.1, random_state=42)
    print(f"Sampled down to {len(sampled_df)} records (10% of original) for quicker validation.")

    print("\nAttempting to create Pandas DataFrame Agent using Ollama and Llama3.")
    print("Please ensure Ollama server is running and 'llama3' model is pulled (e.g., run 'ollama pull llama3' in your terminal).")
    print("If you encounter connection errors, verify your Ollama server is accessible.")

    agent = create_dataframe_agent(sampled_df)

    query = "What inspections required repair in Sacramento, California and what were the pipe materials?"
    print(f"\nQuerying: {query}")
    
    response = agent.invoke({"input": query})
    print("\nResponse:")
    print(response.get('output', str(response)))
