import uuid
from .validator import validate_text
from .chunker import chunk_text
from .embedder import embed_text
from .file_parser import extract_text_from_file
from .vectordb import collection
from .metadata import generate_metadata
from .versioning import get_next_version


def ingest_file(file_path, filename):

        
    raw_text = extract_text_from_file(file_path)

    validated = validate_text(raw_text)

    chunks = chunk_text(validated)

    embeddings = embed_text(chunks)

    version = get_next_version(filename, collection)

    metadata = generate_metadata(filename, version=version)

    ids = [str(uuid.uuid4()) for _ in chunks]

    collection.add(
        documents = chunks,
        embeddings = embeddings,
        ids=ids,
        metadatas=[metadata for _ in chunks]
    )

    return {
            "chunks_added" : len(chunks),
            "version": version
}