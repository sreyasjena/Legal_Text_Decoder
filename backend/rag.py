"""
backend/rag.py
──────────────
RAG (Retrieval Augmented Generation) module for LexAI.
Uses TF-IDF + cosine similarity for legal knowledge retrieval.
Supports both KB retrieval and document-aware Q&A retrieval.
"""

import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ─────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────
KB_FOLDER     = "legal_kb"
CHUNK_SIZE    = 1000
CHUNK_OVERLAP = 200


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    """Split a long text into overlapping chunks for better retrieval."""
    chunks = []
    start  = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return [c for c in chunks if len(c) > 30]


def load_knowledge_base():
    """Load all legal KB txt files and split into chunks."""
    knowledge_chunks = []

    if not os.path.exists(KB_FOLDER):
        return knowledge_chunks

    for file_name in os.listdir(KB_FOLDER):
        if file_name.endswith(".txt"):
            file_path = os.path.join(KB_FOLDER, file_name)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().strip()
                if content:
                    knowledge_chunks.extend(_chunk_text(content))
            except Exception:
                continue

    return knowledge_chunks


def _tfidf_retrieve(query: str, candidates: list, top_k: int, threshold: float = 0.03) -> list:
    """Core TF-IDF retrieval over a list of candidate chunks."""
    if not candidates:
        return []

    documents = candidates + [query]

    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=5000,
            ngram_range=(1, 2),
        )
        vectors      = vectorizer.fit_transform(documents)
        query_vector = vectors[-1]
        cand_vectors = vectors[:-1]

        similarities = cosine_similarity(query_vector, cand_vectors)
        top_indices  = similarities[0].argsort()[-top_k:][::-1]

        return [
            candidates[idx]
            for idx in top_indices
            if similarities[0][idx] > threshold
        ]
    except Exception:
        return []


def retrieve_relevant_knowledge(query: str, top_k: int = 3) -> str:
    """
    Retrieve the most relevant legal KB chunks for the given query.
    Used for initial document analysis.
    """
    knowledge_chunks = load_knowledge_base()

    if not knowledge_chunks:
        return "No legal knowledge base found."

    relevant = _tfidf_retrieve(query, knowledge_chunks, top_k, threshold=0.05)

    if not relevant:
        return "No closely relevant legal context found for this document."

    return "\n\n---\n\n".join(relevant)


def retrieve_from_document(question: str, document_text: str, top_k: int = 4) -> str:
    """
    Retrieve the most relevant chunks from the analyzed document
    that are relevant to the user's question.
    Searches within the document itself for Q&A.
    """
    if not document_text or not document_text.strip():
        return ""

    doc_chunks = _chunk_text(document_text, chunk_size=500, overlap=100)
    relevant   = _tfidf_retrieve(question, doc_chunks, top_k, threshold=0.03)

    return "\n\n".join(relevant) if relevant else ""


def retrieve_for_qa(question: str, document_text: str, top_k_doc: int = 4, top_k_kb: int = 2) -> tuple:
    """
    Combined retrieval for Q&A.
    Searches both the document and KB.
    Returns (doc_context, kb_context) tuple.
    """
    doc_context = retrieve_from_document(question, document_text, top_k=top_k_doc)
    kb_context  = retrieve_relevant_knowledge(question, top_k=top_k_kb)
    return doc_context, kb_context
