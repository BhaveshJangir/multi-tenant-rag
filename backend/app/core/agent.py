import json
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END, START
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from app.db.vector_store import qdrant_client, COLLECTION_NAME
from sentence_transformers import SentenceTransformer

# A state for the graph
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "add_messages"]
    tenant_id: str
    next_node: str
from app.core.config import settings

embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)

from app.core.config import settings

# We configure ChatOpenAI. By changing base_url it can point to Ollama, vLLM, etc.
# The API key is securely loaded from the .env file via Pydantic settings.
llm = ChatOpenAI(temperature=0, model="gpt-4o-mini", api_key=settings.OPENAI_API_KEY)

from qdrant_client.http import models

def retrieve_documents(query: str, tenant_id: str) -> str:
    """Retrieve relevant documents from Qdrant for the given tenant."""
    query_vector = embedding_model.encode(query).tolist()
    search_result = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=3,
        query_filter=models.Filter(
            must=[models.FieldCondition(key="tenant_id", match=models.MatchValue(value=tenant_id))]
        )
    ).points
    
    contexts = []
    for hit in search_result:
        contexts.append(hit.payload.get("text", ""))
        
    return "\n\n---\n\n".join(contexts)

def guardrail_check(state: AgentState):
    """Check for prompt injections or data exfiltration attempts."""
    last_message = state["messages"][-1].content.lower()
    malicious_phrases = ["ignore previous instructions", "reveal system prompt", "drop table"]
    for phrase in malicious_phrases:
        if phrase in last_message:
            return {"messages": [AIMessage(content="I cannot fulfill this request due to security guardrails.")], "next_node": END}
    return {"next_node": "supervisor"}

def supervisor(state: AgentState):
    """Routes the query to the correct agent."""
    # Simplified routing: always go to retrieval for now
    return {"next_node": "retrieval"}

def retrieval_agent(state: AgentState):
    """Fetches documents."""
    last_message = state["messages"][-1].content
    tenant_id = state["tenant_id"]
    
    context = retrieve_documents(last_message, tenant_id)
    # Append the context to a system message for the response agent
    context_msg = SystemMessage(content=f"Retrieved Context:\n{context}")
    return {"messages": [context_msg], "next_node": "response"}

from langfuse.langchain import CallbackHandler

langfuse_handler = CallbackHandler()

def response_agent(state: AgentState):
    """Synthesizes the final answer."""
    # Run the LLM over the messages
    response = llm.invoke(state["messages"], config={"callbacks": [langfuse_handler]})
    return {"messages": [response], "next_node": END}

# Build the Graph
workflow = StateGraph(AgentState)

workflow.add_node("guardrails", guardrail_check)
workflow.add_node("supervisor", supervisor)
workflow.add_node("retrieval", retrieval_agent)
workflow.add_node("response", response_agent)

workflow.add_edge(START, "guardrails")

# Conditional routing from guardrails
def route_from_guardrails(state: AgentState):
    return state.get("next_node", "supervisor")

workflow.add_conditional_edges("guardrails", route_from_guardrails, {"supervisor": "supervisor", END: END})

workflow.add_edge("supervisor", "retrieval")
workflow.add_edge("retrieval", "response")
workflow.add_edge("response", END)

app_graph = workflow.compile()
