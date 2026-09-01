
from app.services.gemini_service import generate_response

from app.services.embedding_service import create_embeddings

from app.services.vector_store import (
    load_vector_store,
    load_chunks,
    search_vector_store
)


# ==========================================
# RETRIEVE RELEVANT PDF CHUNKS
# ==========================================

def retrieve_relevant_chunks(
    question: str,
    vector_path: str,
    chunks_path: str,
    k: int = 3
):

    index = load_vector_store(
        vector_path
    )

    chunks = load_chunks(
        chunks_path
    )

    # Create embedding for the user's question
    question_vector = create_embeddings(
        [question]
    )

    # Search FAISS
    distances, indices = search_vector_store(
        index,
        question_vector,
        k=k
    )

    relevant_chunks = []

    for index_number in indices[0]:

        if index_number != -1:

            relevant_chunks.append(
                chunks[index_number]
            )

    return relevant_chunks


# ==========================================
# GENERATE PDF RESPONSE
# ==========================================

def generate_pdf_response(
    question: str,
    vector_path: str,
    chunks_path: str,
    conversation_history: str = "",
    k: int = 3
):

    # ------------------------------------------
    # Retrieve relevant PDF information
    # ------------------------------------------

    relevant_chunks = retrieve_relevant_chunks(
        question,
        vector_path,
        chunks_path,
        k
    )

    context = "\n\n".join(
        relevant_chunks
    )


    # ------------------------------------------
    # Build conversation-aware prompt
    # ------------------------------------------

    prompt = f"""
You are an AI assistant helping the user understand
an uploaded PDF.

Answer the user's question using the PDF context
provided below.

You may also use the previous conversation to
understand references and follow-up questions.

IMPORTANT RULES:

1. Use the PDF context as the primary source.
2. Do not invent information that is not present
   in the PDF.
3. If the requested information cannot be found
   in the PDF, say:
   "I couldn't find that information in the uploaded PDF."
4. Use previous conversation only to understand
   what the user is referring to.
5. Answer naturally and clearly.
6. If the user asks a follow-up question, connect it
   with the previous conversation when appropriate.

Previous conversation:
{conversation_history}

PDF Context:
{context}

Current Question:
{question}

Answer:
"""

    return generate_response(
        prompt
    )

