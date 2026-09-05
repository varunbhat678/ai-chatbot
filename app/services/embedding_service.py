from langchain_huggingface import HuggingFaceEmbeddings


embeddings = None


def get_embeddings():
    global embeddings

    if embeddings is None:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

    return embeddings


def create_embeddings(chunks):

    return get_embeddings().embed_documents(chunks)