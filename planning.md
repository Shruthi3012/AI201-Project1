# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

Domain: GMU Off-Campus Housing Experiences

This system focuses on GMU off-campus housing experiences, including student reviews of nearby apartments, rental costs, safety perceptions, and leasing experiences. This knowledge is difficult to find because official university sources only provide formal housing listings and policies, while real student experiences — such as hidden fees, safety concerns, maintenance issues, and landlord behavior — are shared informally on Reddit and student forums. A RAG system lets students query this scattered knowledge in one place.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | GMU website| | https://och.gmu.edu/listing|
| 2 | GMU website| | https://orientation.gmu.edu/university-life-resources/|
| 3 |GMU website | | https://llc.gmu.edu/housing-applications/returning-students|
| 4 | GMU website| | https://oips.gmu.edu/offcampus/|
| 5 | Reddit| |https://www.reddit.com/r/gmu/comments/1dw28o3/off_campus_housing/ |
| 6 |Reddit | |https://www.reddit.com/r/gmu/comments/h9pv3m/fairfax_circle_apartments/ |
| 7 | Reddit| |https://www.reddit.com/r/gmu/comments/1k3qkiu/off_campus_housing/ |
| 8 | Reddit| | https://www.reddit.com/r/gmu/comments/1jy86w5/off_campus_housing_cost/|
| 9 |Reddit | |https://www.reddit.com/r/gmu/comments/1rabt7m/offcampus_housing_near_gmu_what_caught_you_off/ |
| 10 | Reddit| |https://www.reddit.com/r/nova/comments/1mns7w0/best_apartments_within_25_min_from_gmu_under_2k/ |
| 11 | Reddit| | https://www.reddit.com/r/gmu/comments/1tuyp3b/incoming_gmu_student_looking_for_affordable/|
| 12 | Reddit| | https://www.reddit.com/r/nova/comments/1qmwrhg/apartments_near_george_mason_university_but_for/|
---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->
**Chunk size:** 500 characters

**Overlap:** 100 characters

**Reasoning:**

The dataset contains a mix of Reddit discussions and official GMU housing pages. Reddit posts often contain multiple opinions, apartment names, and cost figures within a single paragraph. A 500-character chunk is large enough to preserve a full opinion or fact (e.g., apartment name + rent + review sentiment) without being so large that embeddings become noisy.

The 100-character overlap ensures that information spanning a chunk boundary — such as an apartment name mentioned at the end of one chunk and its rent in the next — is not lost during retrieval.

Official GMU pages are more structured but contain important details spread across sections such as cost breakdowns and policy rules, which also fit well within 500-character chunks.

A minimum chunk length of 80 characters filters out very short fragments that carry little semantic meaning.
---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** sentence-transformers/all-MiniLM-L6-v2 

**Top-k:** 5


This embedding model is chosen because it is lightweight, runs locally without API cost, and performs well on semantic similarity tasks involving short-to-medium text like Reddit discussions and informational web pages.

The system retrieves the top 5 most similar chunks per query. This provides enough context diversity across multiple documents while avoiding excessive irrelevant information that could confuse the language model.

In a production system, a stronger embedding model such as OpenAI text-embedding-3-large or BGE-large would improve semantic understanding, especially for informal Reddit language, slang, and mixed-topic discussions. However, these models introduce higher cost, latency, and dependency on external APIs. For a multilingual student population, a multilingual model like paraphrase-multilingual-MiniLM would also be worth evaluating.

Semantic search works even when queries do not match exact words in the documents because embeddings capture meaning rather than keyword overlap.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->


| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What do students say about Fairfax Square Apartments? | Mixed reviews — good location and parking, but high rent (~$2750/month), mold, hidden fees, thin walls, and rent increases at renewal |
| 2 | What is the typical monthly rent for off-campus housing near GMU? | $750–$1200/month when sharing. Studios average $1325, one-bedrooms ~$1675 if living alone |
| 3 | What platforms should GMU students use to find off-campus housing? | Use och.gmu.edu (official GMU finder) or Apartments.com. Avoid Facebook and Craigslist due to scam risk |
| 4 | What are common problems students face with off-campus leasing near GMU? | Hidden fees, mold, pest issues, ignored maintenance, rent hikes at renewal, and noise from thin walls |
| 5 | What should incoming GMU students know before signing a lease? | Start searching in January, read the lease fully, budget for security deposit, note Fairfax County's 4-person occupancy limit, and use och.gmu.edu |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Reddit noise and irrelevant content**
Many Reddit threads contain jokes, off-topic comments, or mixed discussions. These can reduce embedding quality and cause retrieval to return chunks that are tangentially related but not directly useful for answering the query.

2. **Chunk boundary splitting**
Important information such as an apartment name, rent price, and review sentiment may be split across chunks. For example, a student might mention the apartment name at the end of one sentence and the rent figure in the next, placing them in separate chunks if the boundary falls between them.

3. **Mixed data structure**
Official GMU pages are structured and factual, while Reddit content is informal and opinion-based. This inconsistency in writing style can affect embedding quality, since the same concept (e.g., "affordable housing") may be expressed very differently across sources.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```
.txt Documents (9 files)
        │
        ▼
[ Ingestion — ingest.py ]
  Load all .txt files from /documents folder
        │
        ▼
[ Chunking — ingest.py ]
  500-char chunks, 100-char overlap, min 80 chars
        │
        ▼
[ Embedding + Vector Store — retriever.py ]
  SentenceTransformer (all-MiniLM-L6-v2)
  Stored in ChromaDB (cosine similarity)
        │
    User Query
        │
        ▼
[ Retrieval — retriever.py ]
  Top-5 similar chunks returned with source metadata
        │
        ▼
[ Generation — generator.py ]
  Context built from retrieved chunks
  Groq LLM (llama-3.3-70b-versatile)
  Grounded system prompt enforces context-only answers
        │
        ▼
[ Gradio UI — app.py ]
  Answer displayed in Answer box
  Source filenames displayed in Retrieved From box
```
---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

## AI Tool Plan

**Milestone 3 — Ingestion and chunking:**
I will use Claude to help implement document loading and chunking functions. I will provide 
the Chunking Strategy section and the list of document types (Reddit threads and GMU housing 
pages). I expect it to generate Python code for loading .txt files and splitting them into 
500-character chunks with 100-character overlap. I will verify by inspecting sample chunks 
to make sure apartment names and opinions are not split awkwardly across boundaries.

**Milestone 4 — Embedding and retrieval:**
I will use Claude to implement embedding generation and ChromaDB storage. I will provide 
the Retrieval Approach section and the chunk format from ingest.py. I expect code that uses 
SentenceTransformer to embed chunks and store them with source metadata. I will verify by 
running a few test queries and checking that the returned chunks are relevant to the question.

**Milestone 5 — Generation and interface:**
I will use Claude to help design the Groq LLM prompt and build a Gradio interface. I will 
provide the architecture diagram and the milestone requirements. I expect a grounded system 
prompt that restricts the model to retrieved context only, and a basic UI where users can 
type questions and see answers. I will test with edge case questions that are not covered 
by my documents to verify the system refuses rather than guesses.
