import os
import json
import shutil
from typing import List, Dict
from urllib.parse import unquote

from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

from app.retriever import HybridRetriever
from app.generator import generate_answer
from app.indexer import build_index

app = FastAPI(title="Production RAG Application")

retriever = None


class AskRequest(BaseModel):
    question: str
    chat_history: List[Dict[str, str]] = []


@app.on_event("startup")
def startup_event():
    global retriever

    if os.path.exists("indexes/faiss.index"):
        retriever = HybridRetriever()
    else:
        retriever = None


@app.get("/")
def home():
    return {
        "message": "Production RAG Application is running",
        "endpoints": [
            "/upload",
            "/ask",
            "/stats",
            "/files",
            "/delete/{filename}"
        ],
        "features": [
            "PDF Upload",
            "Multiple PDF Support",
            "Show Uploaded Files",
            "Delete Uploaded PDFs",
            "Hybrid Retrieval",
            "BM25",
            "FAISS",
            "CrossEncoder Reranking",
            "Citation Output",
            "Page Metadata",
            "Multi-turn Chat Memory",
            "Backend Stats API"
        ]
    }


@app.get("/stats")
def stats():
    total_pdfs = 0
    total_chunks = 0
    pdf_files = []

    if os.path.exists("data"):
        pdf_files = [
            f for f in os.listdir("data")
            if f.lower().endswith(".pdf")
        ]
        total_pdfs = len(pdf_files)

    if os.path.exists("indexes/chunks.json"):
        try:
            with open("indexes/chunks.json", "r", encoding="utf-8") as f:
                chunks = json.load(f)
                total_chunks = len(chunks)
        except Exception:
            total_chunks = 0

    return {
        "total_pdfs": total_pdfs,
        "total_chunks": total_chunks,
        "pdf_files": pdf_files
    }


@app.get("/files")
def list_files():
    pdf_files = []

    if os.path.exists("data"):
        pdf_files = [
            f for f in os.listdir("data")
            if f.lower().endswith(".pdf")
        ]

    return {
        "files": pdf_files
    }


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global retriever

    os.makedirs("data", exist_ok=True)

    file_path = os.path.join("data", file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    build_index()

    retriever = HybridRetriever()

    return {
        "message": "PDF uploaded and indexed successfully",
        "filename": file.filename
    }


@app.delete("/delete/{filename}")
def delete_pdf(filename: str):
    global retriever

    filename = unquote(filename)
    file_path = os.path.join("data", filename)

    if not os.path.exists(file_path):
        return {
            "error": "File not found",
            "filename": filename
        }

    os.remove(file_path)

    remaining_pdfs = [
        f for f in os.listdir("data")
        if f.lower().endswith(".pdf")
    ]

    if remaining_pdfs:
        build_index()
        retriever = HybridRetriever()
    else:
        if os.path.exists("indexes/faiss.index"):
            os.remove("indexes/faiss.index")
        if os.path.exists("indexes/bm25.pkl"):
            os.remove("indexes/bm25.pkl")
        if os.path.exists("indexes/chunks.json"):
            os.remove("indexes/chunks.json")

        retriever = None

    return {
        "message": "PDF deleted successfully and index updated",
        "filename": filename,
        "remaining_pdfs": remaining_pdfs
    }


@app.post("/ask")
def ask(request: AskRequest):
    if retriever is None:
        return {
            "error": "No index found. Upload a PDF first using /upload."
        }

    full_question = request.question

    if request.chat_history:
        previous_context = ""

        for msg in request.chat_history[-6:]:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            previous_context += f"{role}: {content}\n"

        full_question = f"""
Previous conversation:
{previous_context}

Current question:
{request.question}
"""

    chunks = retriever.retrieve(full_question)
    answer = generate_answer(full_question, chunks)

    citations = []

    for i, chunk in enumerate(chunks, start=1):
        citations.append({
            "citation_id": i,
            "source": chunk["source"],
            "page": chunk.get("page", "N/A"),
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"],
            "rerank_score": chunk["rerank_score"]
        })

    return {
        "question": request.question,
        "used_context": bool(request.chat_history),
        "answer": answer,
        "citations": citations
    }