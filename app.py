import gradio as gr
from ingest import load_documents, chunk_document
from retriever import embed_and_store, retrieve, get_collection
from generator import generate_response

def run_ingestion():
    collection = get_collection()
    if collection.count() > 0:
        print(f"DB already has {collection.count()} chunks. Skipping ingestion.")
        return
    print("\nStarting ingestion...\n")
    docs = load_documents()
    all_chunks = []
    for doc in docs:
        chunks = chunk_document(doc["text"], doc["source"])
        all_chunks.extend(chunks)
    embed_and_store(all_chunks)
    print(f"Done. Total chunks: {len(all_chunks)}\n")

def handle_query(question):
    retrieved = retrieve(question)
    result = generate_response(question, retrieved)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources

with gr.Blocks(title="GMU Housing RAG") as demo:
    gr.Markdown("# 🏡 GMU Housing RAG System")
    inp = gr.Textbox(label="Your question")
    btn = gr.Button("Ask")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)
    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

if __name__ == "__main__":
    print("=" * 40)
    print(" GMU Housing RAG Starting ")
    print("=" * 40)
    run_ingestion()
    demo.launch()