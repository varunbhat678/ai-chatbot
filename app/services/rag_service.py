from app.services.gemini_service import generate_response
from app.services.embedding_service import create_embeddings
from app.services.vector_store import (
    load_vector_store,
    load_chunks,
    search_vector_store
)


def retrieve_relevant_chunks(
    question: str,
    vector_path: str,
    chunks_path: str,
    k: int = 3
):
    index = load_vector_store(vector_path)
    chunks = load_chunks(chunks_path)

    question_vector = create_embeddings([question])

    distances, indices = search_vector_store(
        index,
        question_vector,
        k=k
    )

    relevant_chunks = []

    for index_number in indices[0]:
        if index_number != -1:
            relevant_chunks.append(chunks[index_number])

    return relevant_chunks


def generate_pdf_response(
    question: str,
    vector_path: str,
    chunks_path: str,
    k: int = 3
):
    relevant_chunks = retrieve_relevant_chunks(
        question,
        vector_path,
        chunks_path,
        k
    )

    context = "\n\n".join(relevant_chunks)

    prompt = f"""
Answer the user's question using only the information provided
in the PDF context below.

If the answer cannot be found in the PDF context, say:
"I couldn't find that information in the uploaded PDF."

PDF Context:
{context}

Question:
{question}
"""

    return generate_response(prompt)