import os
from dotenv import load_dotenv

# Force .env values to override old Windows environment variables
load_dotenv(override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2"
)

RERANKER_MODEL = os.getenv(
    "RERANKER_MODEL",
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

DATA_DIR = "data"
INDEX_DIR = "indexes"

CHUNK_SIZE = 700
CHUNK_OVERLAP = 120

TOP_K_VECTOR = 8
TOP_K_BM25 = 8
TOP_K_FINAL = 4