from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
import operator
import json
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from google.generativeai import GenerativeModel
import os


class AgentState(TypedDict):
    """State for the agent graph"""

    user_query: str
    faq_results: List[dict]
    agent_decision: str
    final_response: str
    conversation_history: List[dict]
    user_id: str


class VectorDBManager:
    """Manager for Qdrant vector database operations"""

    def __init__(self, qdrant_url, api_key=None):
        self.client = QdrantClient(url=qdrant_url, api_key=api_key)
        self.collection_name = "faqs_collection"

    def init_collection(self):
        """Initialize Qdrant collection for FAQ embeddings"""
        try:
            # Check if collection exists
            try:
                self.client.get_collection(self.collection_name)
            except:
                # Create collection with embedding vector size
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
                )
                print(f"[v0] Created Qdrant collection: {self.collection_name}")
        except Exception as e:
            print(f"[v0] Error initializing Qdrant collection: {e}")

    def add_faq(self, faq_id, question, answer, embedding):
        """Add FAQ to vector database"""
        try:
            point = PointStruct(
                id=int(faq_id) if isinstance(faq_id, str) else faq_id,
                vector=embedding,
                payload={"question": question, "answer": answer, "type": "faq"},
            )
            self.client.upsert(collection_name=self.collection_name, points=[point])
            print(f"[v0] Added FAQ to Qdrant: {faq_id}")
        except Exception as e:
            print(f"[v0] Error adding FAQ to Qdrant: {e}")

    def search_similar_faqs(self, query_embedding, top_k=3, similarity_threshold=0.7):
        """Search for similar FAQs using vector similarity"""
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
            )

            # Filter by similarity threshold
            faqs = []
            for result in results:
                if result.score >= similarity_threshold:
                    faqs.append(
                        {
                            "id": result.id,
                            "score": result.score,
                            "question": result.payload.get("question", ""),
                            "answer": result.payload.get("answer", ""),
                        }
                    )

            return faqs
        except Exception as e:
            print(f"[v0] Error searching Qdrant: {e}")
            return []


class RAGAgentSystem:
    """Multi-agent RAG system using LangGraph"""

    def __init__(self, qdrant_url, api_key=None, google_api_key=None):
        self.vector_db = VectorDBManager(qdrant_url, api_key)
        self.vector_db.init_collection()

        # Initialize Gemini models
        os.environ["GOOGLE_API_KEY"] = google_api_key or os.getenv("GOOGLE_API_KEY")
        self.embedding_model = GenerativeModel("gemini-1.5-flash")
        self.llm_model = GenerativeModel("gemini-2.5-flash-lite")

        # Create the agent graph
        self.graph = self._create_graph()

    def _create_graph(self):
        """Create the LangGraph workflow"""
        graph = StateGraph(AgentState)

        # Add nodes
        graph.add_node("router", self._router_node)
        graph.add_node("faq_agent", self._faq_agent_node)
        graph.add_node("general_agent", self._general_agent_node)
        graph.add_node("response_formatter", self._response_formatter_node)

        # Add edges
        graph.add_edge("router", "faq_agent")
        graph.add_conditional_edges(
            "faq_agent",
            self._should_use_general_agent,
            {"general_agent": "general_agent", "response": "response_formatter"},
        )
        graph.add_edge("general_agent", "response_formatter")
        graph.add_edge("response_formatter", END)

        # Set entry point
        graph.set_entry_point("router")

        return graph.compile()

    def _router_node(self, state: AgentState) -> AgentState:
        """Route the query to appropriate agent"""
        state["agent_decision"] = "routing"
        return state

    def _faq_agent_node(self, state: AgentState) -> AgentState:
        """FAQ Agent: Search knowledge base"""
        try:
            # Generate embedding for user query using Gemini
            embedding_response = self.embedding_model.embed_content(
                content=state["user_query"], task_type="RETRIEVAL_QUERY"
            )
            query_embedding = embedding_response["embedding"]

            # Search similar FAQs
            faq_results = self.vector_db.search_similar_faqs(
                query_embedding, top_k=3, similarity_threshold=0.7
            )

            state["faq_results"] = faq_results
            state["agent_decision"] = "faq_search"

            print(f"[v0] FAQ Agent found {len(faq_results)} similar FAQs")
        except Exception as e:
            print(f"[v0] FAQ Agent error: {e}")
            state["faq_results"] = []

        return state

    def _should_use_general_agent(self, state: AgentState):
        """Decide if we should use general agent"""
        if not state["faq_results"]:
            return "general_agent"
        return "response"

    def _general_agent_node(self, state: AgentState) -> AgentState:
        """General Agent: Use LLM for unknown questions"""
        try:
            # Prepare context from conversation history
            context = "\n".join(
                [
                    (
                        f"User: {msg['content']}"
                        if msg["role"] == "user"
                        else f"Assistant: {msg['content']}"
                    )
                    for msg in state["conversation_history"][-5:]
                ]
            )

            prompt = f"""You are a helpful assistant for the Ajeer Dashboard.
            
Conversation History:
{context}

Current Question: {state['user_query']}

Please provide a helpful and concise response. If you don't have information about Ajeer specifically, provide general guidance."""

            response = self.llm_model.generate_content(
                prompt, generation_config={"temperature": 0.7, "max_output_tokens": 500}
            )

            state["final_response"] = response.text
            state["agent_decision"] = "general_response"

            print(f"[v0] General Agent generated response")
        except Exception as e:
            print(f"[v0] General Agent error: {e}")
            state["final_response"] = (
                "I apologize, but I encountered an error processing your request. Please try again."
            )

        return state

    def _response_formatter_node(self, state: AgentState) -> AgentState:
        """Format the final response"""
        if state["agent_decision"] == "faq_search" and state["faq_results"]:
            # Use FAQ answer
            best_match = state["faq_results"][0]
            state["final_response"] = (
                f"{best_match['answer']}\n\n(Confidence: {best_match['score']:.1%})"
            )

        return state

    def process_query(self, user_query, user_id, conversation_history=None):
        """Process user query through the agent system"""
        if conversation_history is None:
            conversation_history = []

        # Prepare state
        state = {
            "user_query": user_query,
            "faq_results": [],
            "agent_decision": "",
            "final_response": "",
            "conversation_history": conversation_history,
            "user_id": user_id,
        }

        # Run graph
        result = self.graph.invoke(state)

        return {
            "response": result["final_response"],
            "agent_type": result["agent_decision"],
            "faq_used": len(result["faq_results"]) > 0,
        }

    def add_faq_to_kb(self, faq_id, question, answer, embedding=None):
        """Add FAQ to knowledge base"""
        if embedding is None:
            # Generate embedding using Gemini
            try:
                embedding_response = self.embedding_model.embed_content(
                    content=question, task_type="RETRIEVAL_DOCUMENT"
                )
                embedding = embedding_response["embedding"]
            except Exception as e:
                print(f"[v0] Error generating embedding: {e}")
                return False

        self.vector_db.add_faq(faq_id, question, answer, embedding)
        return True
