import os
import json
import pickle
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import DATA_DIR, INDEX_DIR, EMBEDDING_MODEL


def load_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def load_pdf(path: str) -> str:
    from pypdf import PdfReader

    reader = PdfReader(path)
    pages = []

    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)

    return "\n".join(pages)


def load_documents(data_dir: str):
    documents = []

    for filename in os.listdir(data_dir):
        path = os.path.join(data_dir, filename)

        if filename.lower().endswith(".txt"):
            text = load_txt(path)
        elif filename.lower().endswith(".pdf"):
            text = load_pdf(path)
        else:
            continue

        documents.append(
            {
                "source": filename,
                "text": text
            }
        )

    return documents


def tokenize(text: str):
    return text.lower().split()


def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=120,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    chunks = []

    for doc in documents:
        text_chunks = splitter.split_text(doc["text"]) 
        for idx, chunk in enumerate(text_chunks):
             chunks.append(
                {
                    "source": doc["source"],
                    "chunk_id": idx,
                    "text": chunk
                }
    )
    return chunks


def build_index():
    os.makedirs(INDEX_DIR, exist_ok=True)

    print("Loading documents...")
    docs = load_documents(DATA_DIR)

    print("Chunking documents with RecursiveCharacterTextSplitter...")
    all_chunks = chunk_documents(docs)

    if not all_chunks:
        raise ValueError("No documents found in data folder.")

    print(f"Total chunks: {len(all_chunks)}")

    print("Loading embedding model...")
    embedder = SentenceTransformer(EMBEDDING_MODEL)

    texts = [chunk["text"] for chunk in all_chunks]

    print("Creating embeddings...")
    embeddings = embedder.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    embeddings = embeddings.astype("float32")
    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    print("Saving FAISS index...")
    faiss.write_index(index, os.path.join(INDEX_DIR, "faiss.index"))

    print("Saving chunks...")
    with open(os.path.join(INDEX_DIR, "chunks.json"), "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print("Building BM25 index...")
    tokenized_corpus = [tokenize(text) for text in texts]
    bm25 = BM25Okapi(tokenized_corpus)

    with open(os.path.join(INDEX_DIR, "bm25.pkl"), "wb") as f:
        pickle.dump(bm25, f)

    print("Indexing completed successfully.")


if __name__ == "__main__":
    build_index()