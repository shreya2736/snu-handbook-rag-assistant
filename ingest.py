import os, requests
from pypdf import PdfReader
import chromadb
from chromadb.utils import embedding_functions

PDFS = {
    "B.Tech Regulations 2021": "https://www.snuchennai.edu.in/wp-content/uploads/2024/01/Regulations_B.Tech-1.pdf",
}
CHUNK_SIZE, OVERLAP = 800, 150

def download(name, url):
    os.makedirs("data", exist_ok=True)
    path = os.path.join("data", name.replace(" ", "_") + ".pdf")
    if not os.path.exists(path):
        print(f"Downloading {name}...")
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
    return path

def chunk_text(text):
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + CHUNK_SIZE])
        start += CHUNK_SIZE - OVERLAP
    return chunks

def main():
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path="./chroma_db")
    try:
        client.delete_collection("handbook")  # rebuild from scratch each run
    except Exception:
        pass
    col = client.create_collection("handbook", embedding_function=ef,
                                   metadata={"hnsw:space": "cosine"})

    ids, docs, metas = [], [], []
    for name, url in PDFS.items():
        try:
            path = download(name, url)
        except Exception as e:
            print(f"Could not download {name}: {e}")
            continue
        reader = PdfReader(path)
        empty_pages = 0
        for page_no, page in enumerate(reader.pages, start=1):
            text = " ".join((page.extract_text() or "").split())
            if len(text) < 30:
                empty_pages += 1
                continue
            for i, chunk in enumerate(chunk_text(text)):
                ids.append(f"{name}-p{page_no}-c{i}")
                docs.append(chunk)
                metas.append({"source": name, "page": page_no})
        print(f"{name}: {len(reader.pages)} pages, {empty_pages} with no text")
        if empty_pages > len(reader.pages) / 2:
            print(f"  WARNING: '{name}' looks scanned. It needs OCR, so it adds little right now.")

    if not docs:
        print("No text extracted. Nothing to index.")
        return
    for i in range(0, len(docs), 100):  # add in batches
        col.add(ids=ids[i:i+100], documents=docs[i:i+100], metadatas=metas[i:i+100])
    print(f"Indexed {len(docs)} chunks into ./chroma_db")

if __name__ == "__main__":
    main()