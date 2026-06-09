from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

_client = Groq(api_key=GROQ_API_KEY)


def generate_response(query, retrieved_chunks):
    if not retrieved_chunks:
        return {
            "answer": "I couldn't find relevant information in the GMU housing documents.",
            "sources": []
        }

    context_blocks = []
    for chunk in retrieved_chunks:
        context_blocks.append(f"[{chunk['source']}]\n{chunk['text']}")
    context = "\n\n".join(context_blocks)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful RAG assistant for GMU off-campus housing.\n"
                "Rules:\n"
                "- Use ONLY the provided context to answer.\n"
                "- Synthesize information across all provided sources.\n"
                "- If the answer is not in the context, say: "
                "'I don't have enough information in the provided documents.'\n"
                "- Do NOT use outside knowledge or guess.\n"
                "- Be thorough but concise."
            )
        },
        {
            "role": "user",
            "content": f"CONTEXT:\n{context}\n\nQUESTION:\n{query}\n\nAnswer:"
        }
    ]

    response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0.2
    )

    sources = list(set(chunk["source"] for chunk in retrieved_chunks))

    return {
        "answer": response.choices[0].message.content,
        "sources": sources
    }