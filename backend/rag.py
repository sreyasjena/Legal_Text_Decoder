import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Path to knowledge base folder
KB_FOLDER = "legal_kb"

# Chunk size in characters — splits large files into smaller pieces
# so TF-IDF retrieves the specific relevant section, not the whole file
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
    return chunks


def load_knowledge_base():
    """
    Load all legal knowledge base text files and split into chunks.
    Returns a list of small text chunks instead of whole files.
    """
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
                    # Split into chunks instead of using the whole file
                    chunks = _chunk_text(content)
                    knowledge_chunks.extend(chunks)
            except Exception:
                continue

    return knowledge_chunks


def retrieve_relevant_knowledge(query: str, top_k: int = 3) -> str:
    """
    Retrieve the most relevant legal knowledge chunks for the given query.
    Uses TF-IDF + cosine similarity.
    """
    knowledge_chunks = load_knowledge_base()

    if not knowledge_chunks:
        return "No legal knowledge base found."

    # Combine KB chunks with query for vectorization
    documents = knowledge_chunks + [query]

    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",   # remove common words for better signal
            max_features=5000,      # cap vocabulary size for speed
            ngram_range=(1, 2),     # use bigrams too for better legal term matching
        )
        vectors      = vectorizer.fit_transform(documents)
        query_vector = vectors[-1]
        kb_vectors   = vectors[:-1]

        similarities = cosine_similarity(query_vector, kb_vectors)
        top_indices  = similarities[0].argsort()[-top_k:][::-1]

        relevant = []
        for idx in top_indices:
            score = similarities[0][idx]
            if score > 0.05:   # only include chunks with meaningful similarity
                relevant.append(knowledge_chunks[idx])

        if not relevant:
            return "No closely relevant legal context found for this document."

        return "\n\n---\n\n".join(relevant)

    except Exception as e:
        return f"RAG retrieval error: {e}"
