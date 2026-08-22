from app.services.rag_service import retrieve_relevant_chunks


question = "What did I learn during the internship?"

chunks = retrieve_relevant_chunks(question, k=3)

print("\nRelevant PDF chunks:\n")

for i, chunk in enumerate(chunks, start=1):
    print(f"--- Chunk {i} ---")
    print(chunk)
    print()