# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->
    
    This system covers GMU off-campus housing experiences, including student reviews of nearby apartments, rental costs, safety perceptions, transportation options, and leasing advice.

This knowledge is valuable because students making housing decisions need real experiences - hidden fees, maintenance problems, landlord behavior, and safety concerns - that official university sources never mention. GMU's official housing pages only provide listings and policies. The actual student-reported experiences are scattered across Reddit threads and informal forums, making them hard to search systematically. This RAG system brings that scattered knowledge into one queryable interface.
---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

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

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->


**Chunk size:** 500 characters

**Overlap:** 100 characters

**Why these choices fit your documents:**

The dataset contains a mix of Reddit discussions and official GMU housing pages. Reddit posts often include apartment names, rent figures, and review opinions within a single paragraph. A 500-character chunk is large enough to keep a full opinion or cost fact together without making embeddings noisy. The 100-character overlap ensures that information spanning a chunk boundary — such as an apartment name at the end of one sentence and its rent in the next — is not lost during retrieval. A minimum length filter of 80 characters removes very short fragments with little semantic meaning.

**Final chunk count:** 67 chunks across 9 documents

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->
**Model used:** sentence-transformers/all-MiniLM-L6-v2

This model was chosen because it is lightweight, runs locally without any API cost, and performs well on semantic similarity tasks for short-to-medium text like Reddit discussions and housing guides. It captures meaning rather than keyword overlap, so queries like "what do students pay for rent" still match chunks that say "most students spend between $750 and $1200."

**Production tradeoff reflection:**

In a production system with no cost constraint, I would evaluate OpenAI's text-embedding-3-large or BGE-large-en. These models have longer context windows and stronger performance on domain-specific and informal text, which matters for Reddit slang and mixed-topic discussions. However, they introduce API latency, cost per embedding, and an external dependency. For GMU's international student population, a multilingual model like paraphrase-multilingual-MiniLM would also be worth testing, since some students may query in their first language.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

The system prompt passed to the Groq LLM is:

```
You are a helpful RAG assistant for GMU off-campus housing.
Rules:
- Use ONLY the provided context to answer.
- Synthesize information across all provided sources.
- If the answer is not in the context, say: 'I don't have enough information in the provided documents.'
- Do NOT use outside knowledge or guess.
- Be thorough but concise.
```

The retrieved chunks are passed as labeled context blocks in the user message, formatted as `[filename]\nchunk text`, so the model can see exactly which document each piece of information came from. Temperature is set to 0.2 to reduce hallucination.

**How source attribution is surfaced in the response:**

Source attribution is handled programmatically, not left to the LLM. After generation, the code extracts the source filename from each retrieved chunk's metadata using `list(set(chunk["source"] for chunk in retrieved_chunks))`. These filenames are displayed in a separate "Retrieved from" textbox in the Gradio UI, guaranteeing attribution regardless of what the model generates.


---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->


| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about Fairfax Square Apartments? | Mixed reviews — good location, but high rent (~$2750/month), mold, hidden fees, thin walls, rent increases | Mentioned $2750/month rent, mold, broken appliances, hidden fees, thin walls, and rent increases. Also noted positive aspects: location, parking, pool | Relevant | Accurate |
| 2 | What is the typical monthly rent for off-campus housing near GMU? | $750–$1200/month when sharing; studios ~$1325, one-bedrooms ~$1675 alone | Reported $750–$1200/month when sharing, studios at $1325, one-bedrooms at $1675, and noted costs have risen in recent years | Relevant | Accurate |
| 3 | What platforms should GMU students use to find off-campus housing? | och.gmu.edu or Apartments.com; avoid Facebook and Craigslist | Recommended och.gmu.edu as the official safe finder, mentioned Apartments.com, and warned against Facebook and Craigslist due to scam risk | Relevant | Accurate |
| 4 | What are common problems students face with off-campus leasing near GMU? | Hidden fees, mold, pest issues, ignored maintenance, rent hikes, thin walls | Covered hidden fees, mold, pest infestations, maintenance being ignored, significant rent increases at renewal, and noise from thin walls | Relevant | Accurate |
| 5 | What should incoming GMU students know before signing a lease? | Start in January, read lease fully, budget for deposit, 4-person limit, use och.gmu.edu | Advised starting search in January/February, reading the lease fully, budgeting for first month + security deposit, Fairfax County 4-person occupancy limit, and using och.gmu.edu | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---
## Retrieval Test results
Q1: s off‑campus housing cheaper than dorms at GMU?

**Top retrieved chunks:**
1. reddit_off_campus_housing_cost.txt — rent ranges $750–$1200, townhouse $550 + utilities

2. gmu_offcampus_housing_guide.txt — cost breakdown for studios ($1325) and one‑bedrooms ($1675)

3. affordable_housing_virginia_square_ballston_gmu.txt — mentions $1400 for half of a two‑bedroom

4. apartments_near_gmu_for_administrator.txt — budget up to $2200 for staff housing

** Why relevant:** All retrieved chunks discuss off‑campus rent prices, but none mention dorm costs — explaining why the model correctly refused to answer.

Q2: What platforms should GMU students use to find off‑campus housing?
**Top retrieved chunks:**
1.tips_for_offcampus_housing.txt — recommends och.gmu.edu and warns against Facebook/Craigslist

2.reddit_offcampus_housing.txt — confirms och.gmu.edu and Apartments.com as safe options

3.reddit_offcampus_housing_lessons.txt — mentions verified housing finder

4.reddit_off_campus_housing_cost.txt — general housing cost context

**Why relevant:  **Chunks directly mention och.gmu.edu and verified housing platforms, aligning perfectly with the expected answer.


Q3: What do students say about Fairfax Square Apartments?
**Top retrieved chunks:**
1. reddit_fairfax_square_apartments.txt — rent ~$2750, mold, hidden fees, thin walls

2. best_apartments_under_2k_near_gmu.txt — mentions Trillium and Fairfax Square comparisons

3. reddit_offcampus_housing_lessons.txt — positive experience when not on ground floor

**Why relevant:  **
All chunks describe Fairfax Square experiences, including rent, amenities, and maintenance issues — producing a complete, accurate summary.
---

## Example Responses

**Example 1 - In-scope Query**
**User:** What do students say about Fairfax Square Apartments?
**Answer:** 
Students report the following about Fairfax Square Apartments: 

1. The rent is approximately $2750 per month before utilities and deposits, which is considered high.
2. Parking is adequate, the pool is nice, and neighbors are generally quiet.
3. Management is not intrusive.
4. The location is convenient and close to daily necessities.
5. Sharing larger apartments or townhouses with multiple roommates can significantly reduce costs compared to Fairfax Square.
6. There are concerns about bathroom mildew due to poor ventilation in some apartments.
7. Living on a ground-floor unit may have a different experience compared to other units. 

Overall, students have a generally positive experience at Fairfax Square Apartments, but with some drawbacks such as high cost and potential issues with ventilation.

**Retrieved From:** 
- reddit_fairfax_square_apartments.txt
- reddit_offcampus_housing_lessons.txt
- best_apartments_under_2k_near_gmu.txt


**Example 2 - In-scope Query**
**User:** What platforms should GMU students use to find off‑campus housing?
**Answer:** GMU students should use the Off‑Campus Housing Finder at och.gmu.edu and Apartments.com. Avoid Facebook and Craigslist due to scam risks.
**Retrieved From:** 
- tips_for_offcampus_housing.txt
- reddit_offcampus_housing.txt
- reddit_offcampus_housing_lessons.txt

**Example 3 - Out-of-scope Query**
**User:** Is off‑campus housing cheaper than dorms at GMU?
**Answer:** I don't have enough information in the provided documents.
**Retrieved From:** 
- reddit_offcampus_housing.txt
- gmu_offcampus_housing_guide.txt
- reddit_off_campus_housing_cost.txt
- affordable_housing_virginia_square_ballston_gmu.txt


---

## Query Interface Description

**Input Fields**
- **Textbox:** User Question
- **Button:** Ask

**Output Fields**
- **Answer Textbox:** Model's grounded response
- **Retrieved From Textbox:** List of source filenames used

**Sample Interaction Transcript**
**User:** What should incoming GMU students know before signing a lease?
**Answer:** Before signing a lease, incoming GMU students should know that leases are legal documents and should not be signed unless they have been fully read and understood. It's essential to carefully review the terms, including items like rent, fees, pet policies, security deposits, and maintenance responsibilities. Students should also be cautious with money, avoiding wire transfers and using traceable forms of payment. Additionally, they should verify the property and landlord before making any payments. It's also recommended to seek advice from an unbiased third party, such as Contemporary Student Services, if something in the lease seems excessive or unclear.
**Retrieved From:**
- tips_for_offcampus_housing.txt
- reddit_offcampus_housing.txt
- reddit_offcampus_housing_lessons.txt


---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

"Is off-campus housing cheaper than dorms at GMU?"

**What the system returned:**

"I don't have enough information in the provided documents."

**Root cause (tied to a specific pipeline stage):**

This failure occurs at the ingestion stage — a document coverage gap. The 9 source documents cover off-campus housing costs in detail but none of them mention GMU on-campus dorm pricing. When the query was run, retrieval correctly returned chunks about off-campus rent figures, but the LLM had no dorm cost data to compare against. Because the grounding instruction correctly prevents the model from using outside knowledge, it refused to answer rather than guessing. The failure is not a retrieval or generation error — it is a missing document problem.

**What you would change to fix it:**

Add a document containing GMU on-campus housing rates, such as the official GMU Housing and Residence Life pricing page (housing.gmu.edu). With dorm costs in the vector store, the retrieval stage would return both on-campus and off-campus cost chunks, giving the LLM enough context to make a direct comparison.

---

## Sample Chunks

**Chunk 1**
- **Source:** `affordable_housing_virginia_square_ballston_gmu.txt`
- **Chunk ID:** affordable_housing_virginia_square_ballston_gmu_0
- **Text:** "An incoming GMU student was looking for affordable housing near Virginia Square or Ballston with Metro access. The student hoped to spend between $1,000 and $1,400 per month and preferred a roommate arrangement where each person had a private bathroom. Commenter 1 noted that Arlington is expensive and suggested Springfield, Falls Church, Annandale, and parts of Alexandria."

---

**Chunk 2**
- **Source:** `reddit_fairfax_square_apartments.txt`
- **Chunk ID:** reddit_fairfax_square_apartments_0
- **Text:** "Student 1 lived in Fairfax Square for one year with two roommates. Rent was approximately $2750 per month before utilities and deposits. Parking was adequate, the pool was nice, neighbors were generally quiet, and management was not intrusive. The location was convenient and close to daily necessities. Main drawback was the high cost."

---

**Chunk 3**
- **Source:** `reddit_off_campus_housing_cost.txt`
- **Chunk ID:** reddit_off_campus_housing_cost_2
- **Text:** "Rooms in the $750-$800 range can still be found, although they often come with restrictions such as shared bathrooms, no guests, or strict house rules. Kings Park West and housing near Roberts Road may cost around $800-$850 per month. Student 4 lives in a townhouse with three roommates at $550/month with utilities of $60-$80 monthly, approximately 10 minutes from campus."

---

**Chunk 4**
- **Source:** `gmu_offcampus_housing_guide.txt`
- **Chunk ID:** gmu_offcampus_housing_guide_0
- **Text:** "Students looking for apartments near George Mason University will have a variety of rental options to choose from. Speed up your off-campus housing search in Fairfax by knowing in advance if you plan on living alone or with roommates, what kind of amenities you want your new place to have, which area of town you want to live in, and your monthly budget for rent."

---

**Chunk 5**
- **Source:** `tips_for_offcampus_housing.txt`
- **Chunk ID:** tips_for_offcampus_housing_2
- **Text:** "Transportation and parking can be a challenge in Northern Virginia. If you do not have a car, look for a place to live close to public transportation. Be sure to look into the local bus, Metro, and Mason Shuttle schedules. Additionally, Fairfax City and Fairfax County legally limit the number of residents to four per residence."

----
## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->
**One way the spec helped you during implementation:**

The Chunking Strategy section in planning.md specified 500-character chunks with 100-character overlap before any code was written. When prompting Claude to implement `chunk_document()`, providing these exact numbers meant the generated function matched the spec on the first attempt without needing to experiment. Having the reasoning written down (preserve apartment name + opinion in the same chunk) also helped evaluate whether sample chunks looked correct during testing.

**One way your implementation diverged from the spec, and why:**

The planning.md AI Tool Plan stated that ChatGPT would be used for all milestones, but Claude was used instead throughout the project. More importantly, the Gradio interface diverged from the initial plan: the original app.py used a manual `gr.Chatbot` with tuple-based history, which broke with the installed Gradio version. The implementation was changed to use separate `gr.Textbox` outputs for Answer and Retrieved From, which is simpler, more reliable across Gradio versions, and better matches the milestone requirement of showing source attribution separately from the answer.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->
**Instance 1**

- *What I gave the AI:* The Chunking Strategy section from planning.md, which specified 500-character chunks with 100-character overlap, and described the document types (Reddit threads and GMU housing pages).
- *What it produced:* A chunk_document() function using a character-based sliding window with the specified chunk size, overlap, and a minimum length filter of 80 characters to remove short fragments.
- *What I changed or overrode:* Added the chunk_id field using a filename-based prefix and counter (e.g., reddit_fairfax_square_apartments_0) so each chunk had a unique ID for ChromaDB storage, which the original generated code did not include.



**Instance 2**

- *What I gave the AI:* The generator.py system prompt and a description of answer quality issues — responses were missing information that existed in the documents, and source citations appeared as "Source 1, Source 2" instead of filenames.
- *What it produced:* An updated system prompt instructing the model to synthesize across all sources, and a revised context block format labeling each chunk with its filename instead of a number.
- *What I changed or overrode:* Moved source attribution out of the LLM response entirely. Instead of asking the model to cite sources, the code now extracts source filenames directly from retrieved chunk metadata and displays them in a separate Gradio textbox, making attribution programmatically guaranteed rather than dependent on the model.

**Instance 3**

- *What I gave the AI:* The broken app.py using manual gr.Chatbot with tuple-based history and the TypeError it was producing on startup.
- *What it produced:* A fixed app.py using gr.ChatInterface(fn=chat, type="messages").
- *What I changed or overrode:* Removed type="messages" because my installed Gradio version did not support it. Then replaced gr.ChatInterface with separate gr.Textbox outputs for answer and sources to match the milestone requirement of displaying source attribution in a dedicated box.

