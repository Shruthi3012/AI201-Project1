import os
from config import DOCS_PATH


def load_documents():
    """Load all .txt documents from the documents folder."""
    documents = []

    for filename in sorted(os.listdir(DOCS_PATH)):
        if filename.endswith(".txt"):
            filepath = os.path.join(DOCS_PATH, filename)

            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()

            documents.append({
                "source": filename,
                "text": text,
            })

    print(f"\nLoaded {len(documents)} documents")
    return documents


def chunk_document(text, source_name):
    """
    Split document into overlapping chunks.
    """
    chunk_size = 500
    overlap = 100
    min_length = 80

    chunks = []
    prefix = source_name.replace(".txt", "").lower().replace(" ", "_")
    counter = 0

    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end].strip()

        if len(chunk_text) >= min_length:
            chunks.append({
                "text": chunk_text,
                "source": source_name,
                "chunk_id": f"{prefix}_{counter}",
            })
            counter += 1

        start += chunk_size - overlap

    return chunks



if __name__ == "__main__":

    print("\n==============================")
    print("  GMU Housing RAG Ingestion  ")
    print("==============================\n")

    docs = load_documents()

    print("\nChunking documents...\n")

    all_chunks = []

    for doc in docs:
        chunks = chunk_document(doc["text"], doc["source"])
        all_chunks.extend(chunks)

        print(f"Processed {doc['source']} → {len(chunks)} chunks")

    print("\n==============================")
    print(f"Total Chunks Created: {len(all_chunks)}")
    print("==============================\n")

    print("\n===== SAMPLE CHUNKS =====\n")

    for c in all_chunks[:5]:
        print("=" * 80)
        print("Source:", c["source"])
        print("Chunk ID:", c["chunk_id"])
        print("\n", c["text"][:300])
        print()