from sentence_transformers import SentenceTransformer

model  = SentenceTransformer("BAAI/bge-base-en-v1.5")

def embed_text(text_chunks):
    return model.encode(text_chunks).tolist()

