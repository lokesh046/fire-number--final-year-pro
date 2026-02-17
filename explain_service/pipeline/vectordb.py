import chromadb
from chromadb.config import Settings

client = chromadb.Client(
    Settings(
        persist_directory= "./chroma_db",
        is_persistent = True
    )
)

collection = client.get_or_create_collection("financial_knowledge")

def retrieve_context(query, embedder, top_k=3):
    query_embedding = embedder([query])[0]

    result = collectin.query(
        query_embeddings = [query_embedding],
        n_results =top_k
    )

    return "\n".join(result["documents"][o])