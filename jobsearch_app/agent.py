from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable
from langgraph.graph import StateGraph, END
from dataclasses import dataclass
import os # Import os to access environment variables

# Langchain Search imports
from langchain_tavily import TavilySearch

# Retrieve the Tavily API key from environment variables
# This needs to be set in the shell before running the application,
# or configured in the deployment environment.
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Check if the API key is not set to provide a warning or error early
if not TAVILY_API_KEY:
    print("WARNING: TAVILY_API_KEY environment variable is not set. TavilySearch will likely fail.")
    # For local testing, you might hardcode it here, but generally avoid this in production:
    # TAVILY_API_KEY = "YOUR_DEV_TAVILY_KEY_HERE"
    

# Langchain SQL imports
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents import AgentExecutor

# Define the Ollama model to use.
# User should ensure this model is downloaded and running via Ollama server.
# For 8GB VRAM (Nvidia 3070ti), consider a smaller model like 'llama3' (requires ~4.7GB) or 'tinyllama'
# You can pull models using `ollama pull llama3` or `ollama pull tinyllama`
# OLLAMA_MODEL can be set via environment variable, defaulting to "gemma3"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3") # Example: "llama3.1", "mistral"

# --- Agent State ---
@dataclass
class AgentState:
    """
    Represents the state of our agent.
    """
    query: str
    response: str
    error: str = None # To handle potential errors
    next_node: str = None # To store the next node determined by the router
    intermediate_steps: list = None # For agents that return intermediate steps

# --- LLM and Prompt ---
# Ensure TAVILY_API_KEY is available when this module is loaded
assert os.getenv("TAVILY_API_KEY") is not None, "TAVILY_API_KEY environment variable must be set."
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

def setup_llm_chain() -> Runnable:
    """
    Sets up the LLM chain with a prompt and Ollama model.
    """
    # Print the model being used for debugging/verification
    print(f"Using Ollama model: {OLLAMA_MODEL} at {OLLAMA_HOST}")
    try:
        # Use ChatOllama for better integration with LangChain
        ollama_llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_HOST)

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
    # Make sure to use the configured OLLAMA_MODEL and OLLAMA_HOST
    llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_HOST)
    sql_agent_executor = setup_sql_agent(llm)
    try:
        response = sql_agent_executor.run(state.query)
        state.response = response
        return state
    except Exception as e:
        state.error = f"Error during SQL agent execution: {e}"
        return state

def call_search_agent(state: AgentState) -> AgentState:
    """
    Calls the Tavily search tool with the user's query and updates the state.
    """
    try:
        # Pass the API key explicitly to ensure it's used
        search_tool = TavilySearch(max_results=2, tavily_api_key=TAVILY_API_KEY) 
        search_results = search_tool.invoke(state.query)
        
        # Process Tavily search results to extract relevant content for a better response
        formatted_results = []
        if search_results and 'results' in search_results:
            for i, result in enumerate(search_results['results']):
                title = result.get('title', 'No Title')
                url = result.get('url', '#')
                content = result.get('content', 'No content available.')
                # Use markdown formatting to ensure newlines are respected in frontend rendering
                # and add extra newlines for better visual separation between results.
                formatted_results.append(
                    f"**Result {i+1}: {title}**\nURL: {url}\n```\n{content}\n```\n\n"
                )
            state.response = "Here are some relevant search results:\n\n" + "".join(formatted_results).strip()
        else:
            state.response = "Could not find relevant search results."

        return state
    except Exception as e:
        state.error = f"Error during search agent execution: {e}"
        return state

# --- Router ---
def route_query(state: AgentState) -> AgentState:
    """
    Decides whether to route the query to different agents and updates state.next_node.
    """
    sql_keywords = ["database", "sql", "query", "table", "schema", "count", "list", "top", "sales", "group by", "join"]
    search_keywords = ["search", "find information", "latest news", "what is", "how to", "current events", "who is", "when did", "forecast", "weather"]
    
    query_lower = state.query.lower()

    # Check for SQL-related keywords
    if any(keyword in query_lower for keyword in sql_keywords):
        print(f"Routing query '{state.query}' to: sql_agent_tool")
        state.next_node = "sql_agent_tool"
    # Check for Search-related keywords
    elif any(keyword in query_lower for keyword in search_keywords):
        print(f"Routing query '{state.query}' to: search_agent_tool")
        state.next_node = "search_agent_tool"
    else:
        print(f"Routing query '{state.query}' to: llm_response")
        state.next_node = "llm_response"
    return state

# --- Graph Definition ---
def create_agent_workflow() -> StateGraph:
    """
    Creates and compiles the LangGraph workflow.
    """
    workflow = StateGraph(AgentState)

    # Define the nodes
    workflow.add_node("llm_response", call_llm)
    workflow.add_node("sql_agent_tool", call_sql_agent)
    workflow.add_node("search_agent_tool", call_search_agent) # Add the new search agent node
    workflow.add_node("router", route_query)

    # Define the entry point
    workflow.set_entry_point("router")

    # Define the conditional edges from the router
    workflow.add_conditional_edges(
        "router",
        lambda state: state.next_node, # This assumes route_query sets a 'next_node' in the state
        {
            "sql_agent_tool": "sql_agent_tool",
            "llm_response": "llm_response",
            "search_agent_tool": "search_agent_tool" # Add conditional edge for search agent
        }
    )
    
    # All agent specific nodes lead to END
    workflow.add_edge("llm_response", END)
    workflow.add_edge("sql_agent_tool", END)
    workflow.add_edge("search_agent_tool", END) # Add edge for search agent

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
