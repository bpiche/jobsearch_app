import ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable
from langgraph.graph import StateGraph, END

# Define the Ollama model to use.
# User should ensure this model is downloaded and running via Ollama server.
# For 8GB VRAM (Nvidia 3070ti), consider a smaller model like 'llama3' (requires ~4.7GB) or 'tinyllama'
# You can pull models using `ollama pull llama3` or `ollama pull tinyllama`
OLLAMA_MODEL = "llama3" # Example: "llama3", "tinyllama"

# --- Agent State ---
class AgentState:
    """
    Represents the state of our agent.
    """
    query: str
    response: str
    error: str = None # To handle potential errors

# --- LLM and Prompt ---
def setup_llm_chain() -> Runnable:
    """
    Sets up the LLM chain with a prompt and Ollama model.
    """
    try:
        ollama_llm = ollama.Client(host='http://localhost:11434')
        # Check if model is available (rudimentary check, actual inference will confirm)
        # Note: A more robust check might involve listing models or a test inference
        models = ollama_llm.list()['models']
        if not any(model['name'].startswith(OLLAMA_MODEL) for model in models):
            print(f"Warning: Ollama model '{OLLAMA_MODEL}' not found. Please pull it using `ollama pull {OLLAMA_MODEL}`.")

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful AI assistant specialized in job search related queries."),
                ("user", "{query}")
            ]
        )
        return prompt | ollama_llm.chat | StrOutputParser()
    except Exception as e:
        print(f"Error setting up Ollama LLM: {e}")
        return None

# --- Nodes ---
def call_llm(state: AgentState) -> AgentState:
    """
    Calls the LLM with the user's query and updates the state.
    """
    llm_chain = setup_llm_chain()
    if llm_chain is None:
        state.error = "LLM setup failed. Is Ollama running and the model available?"
        return state
    
    try:
        response = llm_chain.invoke({"query": state.query})
        state.response = response
        return state
    except Exception as e:
        state.error = f"Error during LLM inference: {e}"
        return state

# --- Graph Definition ---
def create_agent_workflow() -> StateGraph:
    """
    Creates and compiles the LangGraph workflow.
    """
    workflow = StateGraph(AgentState)

    # Define the nodes
    workflow.add_node("llm_response", call_llm)

    # Define the entry point
    workflow.set_entry_point("llm_response")

    # Define the end point
    workflow.set_finish_point("llm_response")

    app = workflow.compile()
    return app

# Main entry point for the agent if run directly (for testing)
if __name__ == "__main__":
    agent_app = create_agent_workflow()

    print("Agent initialized. Type 'exit' to quit.")
    while True:
        user_query = input("You: ")
        if user_query.lower() == 'exit':
            break
        
        # Initial state
        initial_state = AgentState(query=user_query, response="")
        
        # Run the agent
        final_state = agent_app.invoke(initial_state)
        
        if final_state.error:
            print(f"Agent Error: {final_state.error}")
        else:
            print(f"Agent: {final_state.response}")
