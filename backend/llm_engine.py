from litellm import completion

from backend.config import (
    OPENAI_API_KEY,
    DEFAULT_MODEL
)

from backend.rag import retrieve_relevant_knowledge

# ─────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────
# Max characters of document text sent to the LLM.
# ~12,000 chars ≈ 3,000 tokens — safely within most model limits.
# Increase carefully if your model supports a larger context window.
MAX_TEXT_CHARS    = 12000
MAX_CONTEXT_CHARS = 3000   # limit for RAG retrieved context too


def analyze_legal_text(text: str, language: str = "English") -> str:
    """
    Main legal analysis function.
    Retrieves relevant RAG context, builds a structured prompt,
    and calls the LLM via LiteLLM.
    """

    # ── 1. Truncate input text to avoid context window overflow ──
    original_length = len(text)
    if len(text) > MAX_TEXT_CHARS:
        text = (
            text[:MAX_TEXT_CHARS]
            + "\n\n[... Document truncated for analysis. "
            "Showing first section only due to length limits ...]"
        )

    # ── 2. Retrieve relevant legal knowledge (RAG) ────────────────
    try:
        retrieved_context = retrieve_relevant_knowledge(text)
        # Also truncate context if too long
        if len(retrieved_context) > MAX_CONTEXT_CHARS:
            retrieved_context = retrieved_context[:MAX_CONTEXT_CHARS] + "..."
    except Exception:
        retrieved_context = "No additional legal context retrieved."

    # ── 3. Add truncation notice to prompt if needed ──────────────
    truncation_notice = ""
    if original_length > MAX_TEXT_CHARS:
        truncation_notice = (
            f"\n⚠️ NOTE: The original document was {original_length:,} characters long. "
            f"Only the first {MAX_TEXT_CHARS:,} characters were analysed due to model limits.\n"
        )

    # ── 4. Build prompt ───────────────────────────────────────────
    prompt = f"""
You are an expert AI Legal Assistant specialized in legal document analysis, legal reasoning, contract understanding, and risk assessment.

Your task is to carefully analyze the provided legal document or text using the legal knowledge context.
{truncation_notice}
==================================================
LEGAL KNOWLEDGE CONTEXT
==================================================

{retrieved_context}

==================================================
LEGAL DOCUMENT OR TEXT
==================================================

{text}

==================================================
INSTRUCTIONS
==================================================

1. First determine whether the provided text is a legal document or legal-related text.

2. If the text is legal, generate a professional structured analysis.

3. If the text is NOT legal, clearly mention:
   "This is not a legal document or legal-related text."

4. Generate the complete response entirely in {language} language.

5. Use simple and understandable language.

6. Structure the output properly with headings and bullet points.

==================================================
OUTPUT FORMAT
==================================================

1. SUMMARY
- Provide a clear summary of the legal document.
- Explain the purpose of the agreement/document.
- Mention the involved parties and overall objective.

2. IMPORTANT CLAUSES WITH MEANING
- Extract important clauses from the document.
- For each clause:
    • Mention the clause name/title.
    • Explain its meaning in simple language.
    • Explain why the clause is important.

3. RISKS
- Identify possible legal, financial, operational, or compliance risks.
- Explain each risk clearly.
- Mention possible consequences if applicable.

4. ADVICE
- Provide practical legal and precautionary advice.
- Suggest what the user should carefully review.
- Mention any clauses that may require negotiation or legal consultation.
- Give beginner-friendly recommendations.

==================================================
IMPORTANT RULES
==================================================

- Do NOT generate false legal information.
- Keep explanations beginner-friendly.
- Use professional formatting.
- Make the output detailed and well-structured.
- Focus on clarity and usefulness.
"""

    # ── 5. LiteLLM API call with error handling ───────────────────
    try:
        response = completion(
            model=DEFAULT_MODEL,
            api_key=OPENAI_API_KEY,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            max_tokens=2000,   # cap output tokens to avoid runaway costs
        )
        output = response["choices"][0]["message"]["content"]
        return output

    except Exception as e:
        error_msg = str(e)

        # Context window exceeded — retry with smaller text
        if "ContextWindowExceeded" in error_msg or "context_length_exceeded" in error_msg:
            try:
                # Retry with half the text
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
                    f"from the document into the text box directly for analysis.\n\n"
                    f"Error: {retry_error}"
                )

        # Other API errors
        return (
            f"❌ Analysis failed due to an API error.\n\n"
            f"Please try again in a few seconds.\n\n"
            f"Error details: {error_msg}"
        )