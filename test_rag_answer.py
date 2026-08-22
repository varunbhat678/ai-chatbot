from app.services.rag_service import generate_pdf_response


question = "What did I learn during the internship?"

answer = generate_pdf_response(question)

print("\nAI Answer:\n")
print(answer)