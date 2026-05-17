from litellm import completion

from backend.config import (
    OPENAI_API_KEY,
    DEFAULT_MODEL
)

from backend.rag import retrieve_relevant_knowledge, retrieve_for_qa

# ─────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────
MAX_TEXT_CHARS    = 12000
MAX_CONTEXT_CHARS = 3000


def analyze_legal_text(text: str, language: str = "English") -> str:
    """
    Main legal analysis function.
    Retrieves relevant RAG context, builds a structured prompt,
    and calls the LLM via LiteLLM.
    """

    # ── 1. Truncate input text ────────────────────────────
    original_length = len(text)
    if len(text) > MAX_TEXT_CHARS:
        text = (
            text[:MAX_TEXT_CHARS]
            + "\n\n[... Document truncated for analysis. "
            "Showing first section only due to length limits ...]"
        )

    # ── 2. Retrieve RAG context ───────────────────────────
    try:
        retrieved_context = retrieve_relevant_knowledge(text)
        if len(retrieved_context) > MAX_CONTEXT_CHARS:
            retrieved_context = retrieved_context[:MAX_CONTEXT_CHARS] + "..."
    except Exception:
        retrieved_context = "No additional legal context retrieved."

    # ── 3. Truncation notice ──────────────────────────────
    truncation_notice = ""
    if original_length > MAX_TEXT_CHARS:
        truncation_notice = (
            f"\n⚠️ NOTE: The original document was {original_length:,} characters long. "
            f"Only the first {MAX_TEXT_CHARS:,} characters were analysed.\n"
        )

    # ── 4. Build prompt ───────────────────────────────────
    prompt = f"""
You are an expert AI Legal Assistant specialized in legal document analysis, contract understanding, and risk assessment.

Your task is to analyze the provided text as a legal document or legal-related content.
{truncation_notice}
==================================================
LEGAL KNOWLEDGE CONTEXT (from RAG knowledge base)
==================================================

{retrieved_context}

==================================================
DOCUMENT / TEXT TO ANALYZE
==================================================

{text}

==================================================
INSTRUCTIONS
==================================================

IMPORTANT: Be INCLUSIVE in determining what counts as legal content.
The following ALL count as legal documents or legal-related text:
- Contracts, agreements, NDAs, MOUs
- Terms of service, privacy policies
- Legal clauses, provisions, sections
- Court orders, judgments, case summaries
- Statutes, regulations, bylaws
- Legal notices, demand letters
- Employment agreements, lease agreements
- Any text containing legal terminology or obligations

Only respond with "This is not a legal document or legal-related text."
if the text is clearly something like a recipe, a poem, a news article,
a casual conversation, or obviously non-legal content.

When in doubt — ANALYZE IT as legal content.

Generate your response entirely in {language} language.

==================================================
OUTPUT FORMAT
==================================================

## 📋 1. SUMMARY
- Clear summary of the document
- Purpose of the agreement/document
- Parties involved and overall objective

## ⚖️ 2. KEY CLAUSES & THEIR MEANING
For each important clause:
- **Clause name**: Explanation in simple language
- Why it matters

## ⚠️ 3. RISKS
- Legal, financial, operational, or compliance risks
- Consequences if applicable

## 💡 4. ADVICE
- Practical recommendations
- What to review carefully
- Clauses that may need negotiation or legal consultation

==================================================
RULES
==================================================
- Do NOT generate false legal information
- Keep explanations beginner-friendly
- Be thorough and well-structured
- Focus on clarity and usefulness
- Output must be in {language}
"""

    # ── 5. LLM call ───────────────────────────────────────
    try:
        response = completion(
            model=DEFAULT_MODEL,
            api_key=OPENAI_API_KEY,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional legal analyst. "
                        "Always analyze text as legal content unless it is obviously non-legal "
                        "(e.g. recipes, poems, casual chat). "
                        "When in doubt, treat it as legal and analyze it."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            max_tokens=2000,
        )
        output = response["choices"][0]["message"]["content"]
        return output

    except Exception as e:
        error_msg = str(e)

        if "ContextWindowExceeded" in error_msg or "context_length_exceeded" in error_msg:
            try:
                shorter_text = text[:MAX_TEXT_CHARS // 2] + "\n\n[... Further truncated ...]"
                short_prompt = prompt.replace(text, shorter_text)
                response = completion(
                    model=DEFAULT_MODEL,
                    api_key=OPENAI_API_KEY,
                    messages=[{"role": "user", "content": short_prompt}],
                    max_tokens=2000,
                )
                output = response["choices"][0]["message"]["content"]
                return (
                    "⚠️ Document was very large — analysis based on first portion only.\n\n"
                    + output
                )
            except Exception as retry_error:
                return (
                    f"❌ The document is too large to analyse even after truncation.\n\n"
                    f"**Suggestion:** Please paste a specific section or clause "
                    f"from the document into the text box directly.\n\n"
                    f"Error: {retry_error}"
                )

        return (
            f"❌ Analysis failed due to an API error.\n\n"
            f"Please try again in a few seconds.\n\n"
            f"Error details: {error_msg}"
        )


# ─────────────────────────────────────────────────────────
# DOCUMENT Q&A
# ─────────────────────────────────────────────────────────
def answer_document_question(
    question: str,
    document_text: str,
    language: str = "English",
    chat_history: list = None,
) -> str:
    """
    Answer a user's question about the analyzed document.
    Uses RAG to retrieve relevant chunks from both the document
    and the legal KB for grounded answers.

    Returns a polite redirect if the question is unrelated.
    """
    chat_history = chat_history or []

    # ── Retrieve from document + KB ───────────────────────
    doc_context, kb_context = retrieve_for_qa(question, document_text)

    # ── Build system prompt ───────────────────────────────
    system_prompt = """You are LexAI — an expert AI Legal Assistant answering questions about a specific legal document.

Your job:
1. Answer ONLY questions that are related to the provided legal document or general legal concepts related to it.
2. If the question is clearly unrelated to the document or legal topics (e.g. asking about cooking, sports, weather, movies, general chat), respond with EXACTLY this message:
   "⚠️ I can only answer questions related to this legal document. Please ask something about the document's clauses, terms, risks, parties, or related legal concepts."
3. Base your answers on the document context provided. If the answer is not in the document, say so clearly.
4. Keep answers clear, accurate, and beginner-friendly.
5. Never make up legal facts not supported by the document or knowledge base."""

    # ── Build user prompt ─────────────────────────────────
    doc_section = f"""
==================================================
DOCUMENT CONTENT (relevant sections)
==================================================
{doc_context if doc_context else "No specific section found — answer based on general document knowledge."}
""" if doc_context else ""

    kb_section = f"""
==================================================
LEGAL KNOWLEDGE CONTEXT
==================================================
{kb_context}
""" if kb_context and "No closely" not in kb_context else ""

    user_prompt = f"""
{doc_section}
{kb_section}
==================================================
USER QUESTION
==================================================
{question}

==================================================
INSTRUCTIONS
==================================================
- Answer the question based on the document and legal knowledge context above.
- If the question is not related to this document or legal topics, politely redirect.
- Respond in {language} language.
- Be concise but thorough.
- Cite specific clauses or sections from the document where relevant.
"""

    # ── Build message history ─────────────────────────────
    messages = [{"role": "system", "content": system_prompt}]

    # Add previous chat turns for context (last 6 messages max)
    for turn in chat_history[-6:]:
        messages.append({"role": "user",      "content": turn["question"]})
        messages.append({"role": "assistant", "content": turn["answer"]})

    messages.append({"role": "user", "content": user_prompt})

    # ── LLM call ──────────────────────────────────────────
    try:
        response = completion(
            model=DEFAULT_MODEL,
            api_key=OPENAI_API_KEY,
            messages=messages,
            max_tokens=1000,
        )
        return response["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ Could not get an answer. Please try again.\n\nError: {e}"
