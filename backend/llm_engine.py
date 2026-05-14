from litellm import completion

from backend.config import (
    OPENAI_API_KEY,
    DEFAULT_MODEL
)

from backend.rag import retrieve_relevant_knowledge


def analyze_legal_text(text, language="English"):
    """
    Main legal analysis function
    """

    # Retrieve relevant legal knowledge
    retrieved_context = retrieve_relevant_knowledge(text)

    # Prompt Engineering
    prompt = f"""
You are an expert AI Legal Assistant specialized in legal document analysis, legal reasoning, contract understanding, and risk assessment.

Your task is to carefully analyze the provided legal document or text using the legal knowledge context.

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

    # LiteLLM API Call
    response = completion(
        model=DEFAULT_MODEL,
        api_key=OPENAI_API_KEY,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # Extract output
    output = response["choices"][0]["message"]["content"]

    return output