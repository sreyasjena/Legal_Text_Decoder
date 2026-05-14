import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Path to knowledge base folder
KB_FOLDER = "legal_kb"


def load_knowledge_base():
    """
    Load all legal knowledge base text files
    """

    knowledge_chunks = []

    # Read all txt files
    for file_name in os.listdir(KB_FOLDER):

        if file_name.endswith(".txt"):

            file_path = os.path.join(KB_FOLDER, file_name)

            with open(file_path, "r", encoding="utf-8") as file:

                content = file.read()

                knowledge_chunks.append(content)

    return knowledge_chunks


def retrieve_relevant_knowledge(query, top_k=3):
    """
    Retrieve most relevant legal knowledge
    """

    # Load KB
    knowledge_chunks = load_knowledge_base()

    # Add query
    documents = knowledge_chunks + [query]

    # TF-IDF vectorization
    vectorizer = TfidfVectorizer()

    vectors = vectorizer.fit_transform(documents)

    # Query vector
    query_vector = vectors[-1]

    # KB vectors
    kb_vectors = vectors[:-1]

    # Similarity calculation
    similarities = cosine_similarity(query_vector, kb_vectors)

    # Top matches
    top_indices = similarities[0].argsort()[-top_k:][::-1]

    relevant_knowledge = []

    for idx in top_indices:
        relevant_knowledge.append(knowledge_chunks[idx])

    return "\n\n".join(relevant_knowledge)