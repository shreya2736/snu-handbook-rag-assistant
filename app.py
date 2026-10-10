import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from groq import Groq
import chromadb
from chromadb.utils import embedding_functions

load_dotenv()
app = Flask(__name__)

TOP_K = 4
MAX_DISTANCE = 0.65   # cosine distance; higher = less similar. Tune using eval.py
MODEL = "openai/gpt-oss-120b"

ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("handbook", embedding_function=ef)
llm = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = (
    "You are an assistant that answers student questions about Shiv Nadar University Chennai "
    "using ONLY the provided context. If the context does not contain the answer, reply exactly: "
    "\"I couldn't find this in the provided documents.\" Do not use outside knowledge. "
    "Be concise and mention clause numbers when they appear in the context."
)

def answer_question(question):
    res = collection.query(query_texts=[question], n_results=TOP_K)
    docs, metas, dists = res["documents"][0], res["metadatas"][0], res["distances"][0]

    # Keep only chunks that are close enough to the question
    hits = [(d, m, s) for d, m, s in zip(docs, metas, dists) if s <= MAX_DISTANCE]
    if not hits:
        return "I couldn't find this in the provided documents.", []

    context = "\n\n".join(
        f"[{m['source']}, page {m['page']}]\n{d}" for d, m, _ in hits
    )
    completion = llm.chat.completions.create(
        model=MODEL,
        temperature=0,
        reasoning_effort="low",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
    )
    sources = [{"source": m["source"], "page": m["page"], "text": d,
                "score": round(1 - s, 2)} for d, m, s in hits]
    return completion.choices[0].message.content, sources

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    question = (request.json or {}).get("question", "").strip()
    if not question:
        return jsonify({"error": "Please enter a question."}), 400
    try:
        answer, sources = answer_question(question)
        return jsonify({"answer": answer, "sources": sources})
    except Exception as e:
        return jsonify({"error": f"Something went wrong: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)