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

def extract_document(path):
    """Join all pages into one text, remembering where each page starts."""
    reader = PdfReader(path)
    full_text, page_starts, empty_pages = "", [], 0
    for page_no, page in enumerate(reader.pages, start=1):
        text = " ".join((page.extract_text() or "").split())
        if len(text) < 30:
            empty_pages += 1
            continue
        page_starts.append((len(full_text), page_no))
        full_text += text + " "
    return full_text, page_starts, len(reader.pages), empty_pages

def page_at(offset, page_starts):
    """Page number on which the character at `offset` appears."""
    page = page_starts[0][1]
    for start_offset, page_no in page_starts:
        if start_offset <= offset:
            page = page_no
        else:
            break
    return page

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

        full_text, page_starts, n_pages, empty_pages = extract_document(path)
        print(f"{name}: {n_pages} pages, {empty_pages} with no text")
        if not page_starts or empty_pages > n_pages / 2:
            print(f"  WARNING: '{name}' looks scanned. It needs OCR, so it is skipped.")
            continue

        start, i = 0, 0
        while start < len(full_text):
            chunk = full_text[start:start + CHUNK_SIZE].strip()
            if chunk:
                ids.append(f"{name}-c{i}")
                docs.append(chunk)
                metas.append({"source": name, "page": page_at(start, page_starts)})
                i += 1
            start += CHUNK_SIZE - OVERLAP

    if not docs:
        print("No text extracted. Nothing to index.")
        return
    for i in range(0, len(docs), 100):  # add in batches
        col.add(ids=ids[i:i+100], documents=docs[i:i+100], metadatas=metas[i:i+100])
    print(f"Indexed {len(docs)} chunks into ./chroma_db")

if __name__ == "__main__":
    main()