"""
backend/rag.py
──────────────
RAG (Retrieval Augmented Generation) module for LexAI.
Uses ChromaDB as vector database and sentence-transformers
for semantic embeddings — pure semantic search, no TF-IDF.
"""

import os
import hashlib

from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# ─────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────
KB_FOLDER       = "legal_kb"
CHROMA_DB_PATH  = ".chromadb"
COLLECTION_NAME = "lexai_legal_kb"
EMBED_MODEL     = "all-MiniLM-L6-v2"
CHUNK_SIZE      = 800
CHUNK_OVERLAP   = 150
TOP_K           = 4
BATCH_SIZE      = 64


# ─────────────────────────────────────────────────────────
# GLOBALS  (loaded once per process)
# ─────────────────────────────────────────────────────────
_embedder          = None
_chroma_collection = None


# ─────────────────────────────────────────────────────────
# TEXT CHUNKING
# ─────────────────────────────────────────────────────────
def _chunk_text(text: str) -> list:
    """Split text into overlapping chunks for fine-grained retrieval."""
    chunks = []
    start  = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end].strip())
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return [c for c in chunks if len(c) > 50]


# ─────────────────────────────────────────────────────────
# EMBEDDER
# ─────────────────────────────────────────────────────────
def _get_embedder() -> SentenceTransformer:
    """Load sentence-transformer model once per process."""
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBED_MODEL)
    return _embedder


# ─────────────────────────────────────────────────────────
# KB HASH  (detects changes in KB files)
# ─────────────────────────────────────────────────────────
def _kb_hash() -> str:
    """MD5 hash of all KB file contents — used to detect changes."""
    if not os.path.exists(KB_FOLDER):
        return ""
    h = hashlib.md5()
    for fname in sorted(os.listdir(KB_FOLDER)):
        if fname.endswith(".txt"):
            fpath = os.path.join(KB_FOLDER, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    h.update(f.read().encode())
            except Exception:
                pass
    return h.hexdigest()


def _get_stored_hash(collection) -> str:
    """Read the stored KB hash from ChromaDB."""
    try:
        result = collection.get(ids=["__kb_hash__"])
        if result and result["documents"]:
            return result["documents"][0]
    except Exception:
        pass
    return ""


# ─────────────────────────────────────────────────────────
# INDEXING
# ─────────────────────────────────────────────────────────
def _index_knowledge_base(collection, current_hash: str):
    """
    Load all KB txt files, chunk them, embed with sentence-transformers,
    and store in ChromaDB. Runs only when KB content changes.
    """
    if not os.path.exists(KB_FOLDER):
        raise FileNotFoundError(f"Knowledge base folder '{KB_FOLDER}' not found.")

    embedder    = _get_embedder()
    all_chunks  = []
    all_ids     = []
    all_metas   = []
    chunk_index = 0

    # ── Clear existing data ───────────────────────────────
    try:
        existing = collection.get()
        if existing["ids"]:
            collection.delete(ids=existing["ids"])
    except Exception:
        pass

    # ── Load and chunk all KB files ───────────────────────
    for fname in sorted(os.listdir(KB_FOLDER)):
        if not fname.endswith(".txt"):
            continue
        fpath = os.path.join(KB_FOLDER, fname)
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().strip()
            if not content:
                continue
            for chunk in _chunk_text(content):
                all_chunks.append(chunk)
                all_ids.append(f"chunk_{chunk_index}")
                all_metas.append({"source": fname})
                chunk_index += 1
        except Exception:
            continue

    if not all_chunks:
        raise ValueError("No content found in knowledge base files.")

    # ── Embed in batches ──────────────────────────────────
    all_embeddings = []
    for i in range(0, len(all_chunks), BATCH_SIZE):
        batch      = all_chunks[i:i + BATCH_SIZE]
        embeddings = embedder.encode(batch, show_progress_bar=False).tolist()
        all_embeddings.extend(embeddings)

    # ── Store in ChromaDB in batches ──────────────────────
    for i in range(0, len(all_chunks), BATCH_SIZE):
        collection.add(
            documents=all_chunks[i:i + BATCH_SIZE],
            embeddings=all_embeddings[i:i + BATCH_SIZE],
            ids=all_ids[i:i + BATCH_SIZE],
            metadatas=all_metas[i:i + BATCH_SIZE],
        )

    # ── Save hash to avoid re-indexing next time ──────────
    collection.add(
        documents=[current_hash],
        ids=["__kb_hash__"],
        metadatas=[{"source": "__meta__"}],
    )


# ─────────────────────────────────────────────────────────
# CHROMADB COLLECTION
# ─────────────────────────────────────────────────────────
def _get_collection():
    """
    Get or create ChromaDB collection.
    Auto re-indexes if KB files have changed since last run.
    """
    global _chroma_collection

    if _chroma_collection is not None:
        return _chroma_collection

    client = chromadb.PersistentClient(
        path=CHROMA_DB_PATH,
        settings=Settings(anonymized_telemetry=False),
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    current_hash = _kb_hash()
    stored_hash  = _get_stored_hash(collection)

    if current_hash != stored_hash:
        _index_knowledge_base(collection, current_hash)

    _chroma_collection = collection
    return collection


# ─────────────────────────────────────────────────────────
# MAIN RETRIEVAL FUNCTION
# ─────────────────────────────────────────────────────────
def retrieve_relevant_knowledge(query: str, top_k: int = TOP_K) -> str:
    """
    Retrieve the most semantically relevant legal knowledge chunks
    using ChromaDB vector search + sentence-transformer embeddings.

    Args:
        query:  The legal document text or search query.
        top_k:  Number of top chunks to retrieve (default 4).

    Returns:
        A string of the most relevant KB chunks joined by separators.
    """
    try:
        collection      = _get_collection()
        embedder        = _get_embedder()
        query_embedding = embedder.encode(
            [query], show_progress_bar=False
        ).tolist()

        results = collection.query(
            query_embeddings=query_embedding,
            n_results=top_k + 1,
            where={"source": {"$ne": "__meta__"}},
        )

        docs      = results.get("documents", [[]])[0]
        distances = results.get("distances",  [[]])[0]

        relevant = []
        for doc, dist in zip(docs, distances):
            # cosine distance: 0 = identical, 2 = opposite
            # dist < 1.5 means cosine similarity > 0.25 — meaningful match
            if dist < 1.5 and doc.strip():
                relevant.append(doc)

        if not relevant:
            return "No closely relevant legal context found for this document."

        return "\n\n---\n\n".join(relevant[:top_k])

    except Exception as e:
        return f"RAG retrieval error: {e}"