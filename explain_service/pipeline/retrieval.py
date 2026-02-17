from .vectordb import collection
from .embedder import embed_text


def retrieve(query, top_k=3):

    query_embedding = embed_text([query])[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    context = "\n\n".join(documents)

    sources = list(set([meta["source"] for meta in metadatas]))

    # Convert distance to similarity confidence
    # Lower distance = higher similarity
    avg_distance = sum(distances) / len(distances)

    confidence = round(max(0, 1 - avg_distance) * 100, 2)

    return context, sources, confidence


