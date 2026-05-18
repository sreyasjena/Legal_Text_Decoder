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
    """
    chat_history = chat_history or []

    doc_context, kb_context = retrieve_for_qa(question, document_text)

    system_prompt = """You are LexAI — an expert AI Legal Assistant answering questions about a specific legal document.

Your job:
1. Answer questions related to the document, its clauses, parties, terms, risks, legal concepts, applicable laws, and related legal topics.
2. Be GENEROUS in what you consider related — questions about government rules, tenant rights, landlord obligations, applicable laws, legal procedures, and general legal concepts ARE all relevant.
3. ONLY redirect if the question is completely unrelated to law or the document — for example: cooking recipes, sports scores, entertainment, casual chat, jokes.
4. When redirecting, respond with EXACTLY: "⚠️ I can only answer questions related to this legal document. Please ask something about the document's clauses, terms, risks, parties, or related legal concepts."
5. Base your answers on the document context and legal knowledge provided. If the exact answer is not in the document, use your legal knowledge to provide a helpful answer while noting it may not be explicitly stated.
6. Keep answers clear, accurate, and beginner-friendly.
7. Never make up legal facts."""

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
- Answer based on the document and legal knowledge context above.
- If unrelated to this document or legal topics, politely redirect.
- Respond in {language} language.
- Be concise but thorough.
- Cite specific clauses or sections where relevant.
"""

    messages = [{"role": "system", "content": system_prompt}]
    for turn in chat_history[-6:]:
        messages.append({"role": "user",      "content": turn["question"]})
        messages.append({"role": "assistant", "content": turn["answer"]})
    messages.append({"role": "user", "content": user_prompt})

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


# ─────────────────────────────────────────────────────────
# DYNAMIC SUGGESTIONS GENERATOR
# ─────────────────────────────────────────────────────────
def generate_qa_suggestions(document_text: str, analysis_result: str) -> list:
    """
    Generate 5 dynamic, document-specific suggested questions
    based on the document content and its analysis result.
    Returns a list of question strings.
    """
    # Use first 3000 chars of document + first 1000 chars of analysis
    doc_preview      = document_text[:3000] if document_text else ""
    analysis_preview = analysis_result[:1000] if analysis_result else ""

    prompt = f"""Based on this legal document and its analysis, generate exactly 5 short, specific questions that a user would naturally want to ask about this document.

DOCUMENT PREVIEW:
{doc_preview}

ANALYSIS PREVIEW:
{analysis_preview}

RULES:
- Questions must be specific to THIS document (mention actual parties, amounts, dates, clauses if present)
- Each question must be under 12 words
- Questions should cover: key terms, risks, obligations, deadlines, penalties
- Return ONLY the 5 questions, one per line, no numbering, no bullets, no extra text
"""

    try:
        response = completion(
            model=DEFAULT_MODEL,
            api_key=OPENAI_API_KEY,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )
        raw = response["choices"][0]["message"]["content"]
        questions = [q.strip() for q in raw.strip().split("\n") if q.strip()]
        # Return max 5 non-empty questions
        return questions[:5] if questions else _default_suggestions()
    except Exception:
        return _default_suggestions()


def _default_suggestions() -> list:
    """Fallback suggestions if generation fails."""
    return [
        "What are the key risks in this document?",
        "Who are the parties involved?",
        "What is the notice period?",
        "What happens if I breach the contract?",
        "What are the payment terms?",
    ]
