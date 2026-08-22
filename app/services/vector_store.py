import faiss
import numpy as np
import pickle


def create_vector_store(vectors):
    vector_array = np.array(vectors).astype("float32")

    dimension = vector_array.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(vector_array)

    return index

def search_vector_store(index, query_vector, k=3):
    query_array = np.array(query_vector).astype("float32")

    distances, indices = index.search(query_array, k)

    return distances, indices

def save_vector_store(index, path="faiss_index"):
    faiss.write_index(index, path)


def load_vector_store(path="faiss_index"):
    return faiss.read_index(path)

def save_chunks(chunks, path="chunks.pkl"):
    with open(path, "wb") as file:
        pickle.dump(chunks, file)


def load_chunks(path="chunks.pkl"):
    with open(path, "rb") as file:
        return pickle.load(file)