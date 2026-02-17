def get_next_version(filename, collection):

    results = collection.get(where={"source": filename})

    if not results["metadatas"]:
        return 1

    versions = [m["version"] for m in results["metadatas"]]
    return max(versions) + 1
