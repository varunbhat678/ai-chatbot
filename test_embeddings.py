from app.services.embedding_service import create_embeddings
from app.services.vector_store import (
    create_vector_store,
    search_vector_store,
    save_vector_store,
    load_vector_store,
    save_chunks,
    load_chunks
)


chunks = [
    "Robots learn tasks from expert demonstrations using AI.",
    "Behavior cloning allows robots to learn from demonstrations.",
    "The internship lasted for eight weeks."
]

# 1. Create embeddings
vectors = create_embeddings(chunks)

# 2. Create FAISS index
index = create_vector_store(vectors)

# 3. Save both
save_vector_store(index)
save_chunks(chunks)

print("Vector store and chunks saved.")


# 4. Load them again
loaded_index = load_vector_store()
loaded_chunks = load_chunks()

print("Vector store loaded.")
print("Number of vectors:", loaded_index.ntotal)
print("Number of chunks:", len(loaded_chunks))


# 5. Test search after loading
question = "How do robots learn tasks?"

question_vector = create_embeddings([question])

distances, indices = search_vector_store(
    loaded_index,
    question_vector,
    k=2
)

print("\nSearch results:")

for i in indices[0]:
    print("-", loaded_chunks[i])