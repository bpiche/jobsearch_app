from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable
from langgraph.graph import StateGraph, END
from dataclasses import dataclass

# Langchain SQL imports
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents import AgentExecutor

# Define the Ollama model to use.
# User should ensure this model is downloaded and running via Ollama server.
# For 8GB VRAM (Nvidia 3070ti), consider a smaller model like 'llama3' (requires ~4.7GB) or 'tinyllama'
# You can pull models using `ollama pull llama3` or `ollama pull tinyllama`
OLLAMA_MODEL = "llama3" # Example: "llama3", "tinyllama"

# --- Agent State ---
@dataclass
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
        # Use ChatOllama for better integration with LangChain
        ollama_llm = ChatOllama(model=OLLAMA_MODEL, base_url='http://localhost:11434')

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful AI assistant specialized in job search related queries."),
                ("user", "{query}")
            ]
        )
        return prompt | ollama_llm | StrOutputParser()
    except Exception as e:
        print(f"Error setting up Ollama LLM: {e}")
        return None

# --- SQL Database Setup ---
def setup_sql_agent(llm) -> AgentExecutor:
    """
    Sets up the Langchain SQL agent.
    """
    # SQLite database file is located in the data/ directory
    db = SQLDatabase.from_uri("sqlite:///./data/ai_jobs.db")
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    sql_agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True
    )
    return sql_agent

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

def call_sql_agent(state: AgentState) -> AgentState:
    """
    Calls the SQL agent with the user's query and updates the state.
    """
    llm = ChatOllama(model=OLLAMA_MODEL, base_url='http://localhost:11434')
    sql_agent_executor = setup_sql_agent(llm)
    try:
        response = sql_agent_executor.run(state.query)
        state.response = response
        return state
    except Exception as e:
        state.error = f"Error during SQL agent execution: {e}"
        return state

# --- Router ---
def route_query(state: AgentState) -> str:
    """
    Decides whether to route the query to the SQL agent or the general LLM.
    """
    sql_keywords = ["database", "sql", "query", "table", "schema", "count", "list", "top", "sales", "group by", "join"]
    
    # Check if the query contains any SQL-related keywords
    if any(keyword in state.query.lower() for keyword in sql_keywords):
        return "sql_agent_tool"
    else:
        return "llm_response"

# --- Graph Definition ---
def create_agent_workflow() -> StateGraph:
    """
    Creates and compiles the LangGraph workflow.
    """
    workflow = StateGraph(AgentState)

    # Define the nodes
    workflow.add_node("llm_response", call_llm)
    workflow.add_node("sql_agent_tool", call_sql_agent)

    # Define the entry point and conditional edge
    workflow.set_entry_point("llm_response") # Start with LLM to decide routing
    workflow.add_conditional_edges(
        "llm_response", # From the LLM response (or initial query processing)
        route_query,
        {
            "sql_agent_tool": "sql_agent_tool",
            "llm_response": "llm_response" # If it's still LLM, it means it was a general query
        }
    )
    
    # SQL agent leads to END or potentially back to LLM for synthesis
    workflow.add_edge("sql_agent_tool", END)

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
