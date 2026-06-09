import chromadb
from chromadb.utils import embedding_functions
from config import CHROMA_COLLECTION, CHROMA_PATH, EMBEDDING_MODEL, N_RESULTS

_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL
)

_client = chromadb.PersistentClient(path=CHROMA_PATH)

_collection = _client.get_or_create_collection(
    name=CHROMA_COLLECTION,
    embedding_function=_ef,
    metadata={"hnsw:space": "cosine"},
)


def get_collection():
    return _collection


def embed_and_store(chunks):
    _collection.add(
        documents=[c["text"] for c in chunks],
        metadatas=[{"source": c["source"]} for c in chunks],
        ids=[c["chunk_id"] for c in chunks],
    )

    print(f"\nStored {len(chunks)} chunks in vector DB")
    print(f"Total DB size: {_collection.count()}\n")


def retrieve(query, n_results=N_RESULTS):
    if _collection.count() == 0:
        return []

    results = _collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]

    chunks = []

    print("\n=== RETRIEVAL RESULTS ===\n")

    for doc, meta, dist in zip(docs, metas, dists):
        chunk = {
            "text": doc,
            "source": meta["source"],
            "distance": dist
        }
        chunks.append(chunk)

        print(f"[{chunk['source']}] (dist: {dist:.3f})")
        print(doc[:200])
        print("-" * 60)

    return chunks