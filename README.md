# SNU Chennai Handbook Assistant

A RAG-based Q&A assistant over the Shiv Nadar University Chennai B.Tech Regulations 2021. Students can ask questions in plain English (attendance, grading, arrears, withdrawal, etc.) and get an answer with the source page and the exact passage it came from.

<img width="940" height="525" alt="image" src="https://github.com/user-attachments/assets/37b9908c-dd23-4a54-aa51-1f922bb912e4" />

<img width="940" height="494" alt="image" src="https://github.com/user-attachments/assets/6a60934f-3b90-41f5-9223-df59a451d55d" />

<img width="940" height="366" alt="image" src="https://github.com/user-attachments/assets/291dddd1-52f3-46b4-a79d-027f042d7875" />

## Features
- Semantic search over the regulations PDF, with page-level citations
- Answers generated only from retrieved text, to reduce hallucination
- Refuses to answer when nothing relevant is found ("I couldn't find this in the provided documents")
- Simple chat interface (HTML, CSS, JavaScript) with expandable source passages
- Evaluation script to measure answer accuracy

## Tech Stack
Python, Flask, Sentence Transformers (all-MiniLM-L6-v2), ChromaDB, Groq API (model-openai/gpt-oss-120b), HTML/CSS/JS

## How It Works
1. `ingest.py` downloads the PDF, extracts the text of all pages into one document, and splits it into overlapping chunks (800 characters, 150 overlap). Chunking across page boundaries keeps a clause heading together with its content. Each chunk is embedded and stored in a persistent ChromaDB collection along with the page where it starts.
2. `app.py` embeds the user's question and retrieves the top 6 most similar chunks using cosine distance.
3. Chunks beyond a distance threshold (0.75) are discarded. If none remain, the bot says it couldn't find the answer.
4. The remaining chunks are sent to the LLM with a prompt that restricts it to the provided context (temperature 0).
5. The answer is returned with its source passages and page numbers.

## Project Structure
```
├── app.py              # Flask backend: retrieval + answer generation
├── ingest.py           # Builds the vector index from the PDF
├── eval.py             # Accuracy test on hand-written questions
├── templates/
│   └── index.html      # Chat interface
├── requirements.txt
└── README.md
```

## Setup
```bash
python -m venv venv
venv\Scripts\activate        # Windows (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
```
Create a `.env` file in the project root:
```
GROQ_API_KEY=your_key_here
```
Build the index once, then start the app:
```bash
python ingest.py
python app.py
```
Open http://127.0.0.1:5000

## Evaluation
`python eval.py` runs 19 questions: 17 answerable from the regulations and 2 out-of-scope questions that should be refused. Expected answers were checked by hand against the PDF, and a response counts as correct if it contains the expected key fact.

<img width="940" height="261" alt="image" src="https://github.com/user-attachments/assets/8a39965a-22d7-4179-89b3-7adfb7290bdf" />

<img width="940" height="417" alt="image" src="https://github.com/user-attachments/assets/e36d7abc-bbe1-4c2c-94ed-f8730ce39e75" />

**Result: 18/19 correct.**

Improvements made after the first run, which scored 16/19 on the same questions :
- Switched from page-by-page chunking to chunking across page boundaries, which fixed questions where a clause heading and its value fell on different pages.
- Increased the number of retrieved chunks and tuned the distance threshold.
- Added a prompt instruction not to merge separate categories (e.g. First Class vs First Class with Distinction).

This is a small test set with keyword-based checking, so it is a sanity check rather than a rigorous benchmark.

## Limitations
- Answers can be wrong. Always verify with the official regulations.
- Based on the 2021 regulations, which may not apply to every batch.
- Tables (such as the grade scale) are flattened by text extraction and retrieved less reliably.
- The cited page is the page where a chunk starts, so a passage may continue onto the next page.
- The LLM can occasionally cite a wrong clause number in its answer text. The source passages shown below the answer are the reliable reference.

## Future Improvements
- OCR support for scanned PDFs
- Clause-aware chunking and table-specific parsing
- A larger test set and re-ranking of retrieved chunks
