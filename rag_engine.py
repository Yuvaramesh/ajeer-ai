"""
rag_engine.py — Future RAG Chatbot Engine
Connects Qdrant VectorDB + Gemini for retrieval-augmented generation.
This module is scaffolded for future development.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import google.generativeai as genai
import hashlib
import os

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "ajeer_knowledge"
EMBED_DIMENSION = 768  # Gemini embedding dimension


class AjeerRAGEngine:
    def __init__(self):
        self.client = QdrantClient(url=QDRANT_URL)
        self.model = genai.GenerativeModel("gemini-2.5-flash-lite")
        self._ensure_collection()

    def _ensure_collection(self):
        """Create Qdrant collection if it doesn't exist."""
        try:
            collections = [c.name for c in self.client.get_collections().collections]
            if COLLECTION_NAME not in collections:
                self.client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=EMBED_DIMENSION, distance=Distance.COSINE
                    ),
                )
                print(f"[RAG] Created Qdrant collection: {COLLECTION_NAME}")
        except Exception as e:
            print(f"[RAG] Qdrant connection error: {e}")

    def _get_embedding(self, text: str) -> list[float]:
        """Get text embedding using Gemini embedding model."""
        result = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document",
        )
        return result["embedding"]

    def index_document(self, doc_id: str, text: str, metadata: dict = None):
        """Add a document to the Qdrant vector store."""
        vector = self._get_embedding(text)
        point_id = int(hashlib.md5(doc_id.encode()).hexdigest()[:8], 16)
        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={"text": text, "doc_id": doc_id, **(metadata or {})},
                )
            ],
        )
        print(f"[RAG] Indexed document: {doc_id}")

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """Retrieve top-k relevant documents for a query."""
        query_vector = self._get_embedding(query)
        results = self.client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=top_k,
        )
        return [
            {
                "text": r.payload.get("text", ""),
                "score": r.score,
                "doc_id": r.payload.get("doc_id"),
            }
            for r in results
        ]

    def rag_answer(self, query: str, context_extra: str = "") -> str:
        """
        Full RAG pipeline:
        1. Retrieve relevant documents from Qdrant
        2. Build augmented prompt with context
        3. Generate answer with Gemini
        """
        # Step 1: Retrieve
        docs = self.retrieve(query, top_k=5)
        context_chunks = "\n\n".join(
            [f"[Doc {i+1}]: {d['text']}" for i, d in enumerate(docs)]
        )

        if not context_chunks.strip():
            context_chunks = "No relevant documents found in knowledge base."

        # Step 2: Build prompt
        prompt = f"""You are Ajeer AI, an intelligent workforce management assistant.
Use the following retrieved context to answer the user's question accurately.

RETRIEVED CONTEXT:
{context_chunks}

ADDITIONAL CONTEXT:
{context_extra}

USER QUESTION: {query}

Provide a helpful, accurate, and concise answer based on the context above.
If the context doesn't contain enough information, say so and provide general guidance."""

        # Step 3: Generate
        response = self.model.generate_content(prompt)
        return response.text

    def seed_sample_data(self):
        """Seed the Qdrant DB with sample Ajeer knowledge base data."""
        sample_docs = [
            {
                "id": "faq-001",
                "text": "Ajeer is a workforce management platform that connects employers with skilled workers across the Middle East, South Asia, and Africa. Workers can register, apply for jobs, and receive payments in their local currencies.",
            },
            {
                "id": "faq-002",
                "text": "To register as a worker on Ajeer, you need a valid national ID, professional certifications, and a bank account for salary disbursement. Registration is free and takes 10-15 minutes.",
            },
            {
                "id": "faq-003",
                "text": "Ajeer supports payments in over 30 currencies including USD, AED, SAR, INR, BDT, PKR, and NGN. Currency conversion is done at live market rates via our integrated payment gateway.",
            },
            {
                "id": "faq-004",
                "text": "Job categories available on Ajeer include construction, healthcare, hospitality, domestic services, technology, transportation, and skilled trades like plumbing and electrical work.",
            },
            {
                "id": "faq-005",
                "text": "Workers on Ajeer are covered under local labor laws. Contracts are digitally signed and stored. Dispute resolution is available through our 24/7 support team.",
            },
        ]

        for doc in sample_docs:
            try:
                self.index_document(doc["id"], doc["text"])
            except Exception as e:
                print(f"[RAG] Error seeding doc {doc['id']}: {e}")

        print(f"[RAG] Seeded {len(sample_docs)} sample documents.")


# Singleton instance (initialized lazily)
_rag_engine = None


def get_rag_engine() -> AjeerRAGEngine:
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = AjeerRAGEngine()
    return _rag_engine
