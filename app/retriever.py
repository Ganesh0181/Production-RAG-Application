import os
import json
import pickle
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer, CrossEncoder

from app.config import (
    INDEX_DIR,
    EMBEDDING_MODEL,
    RERANKER_MODEL,
    TOP_K_VECTOR,
    TOP_K_BM25,
    TOP_K_FINAL
)


def tokenize(text: str):
    return text.lower().split()


class HybridRetriever:
    def __init__(self):
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        self.reranker = CrossEncoder(RERANKER_MODEL)

        self.faiss_index = faiss.read_index(
            os.path.join(INDEX_DIR, "faiss.index")
        )

        with open(os.path.join(INDEX_DIR, "chunks.json"), "r", encoding="utf-8") as f:
            self.chunks = json.load(f)

        with open(os.path.join(INDEX_DIR, "bm25.pkl"), "rb") as f:
            self.bm25 = pickle.load(f)

    def make_item_id(self, item):
        return item.get(
            "id",
            f"{item.get('source', 'unknown')}-page-{item.get('page', 1)}-chunk-{item.get('chunk_id', 0)}"
        )

    def vector_search(self, query: str):
        query_embedding = self.embedder.encode(
            [query],
            convert_to_numpy=True
        )

        query_embedding = query_embedding.astype("float32")
        faiss.normalize_L2(query_embedding)

        scores, indices = self.faiss_index.search(
            query_embedding,
            TOP_K_VECTOR
        )

        results = []

        for score, idx in zip(scores[0], indices[0]):
            if idx != -1:
                item = self.chunks[idx].copy()
                item["vector_score"] = float(score)

                if "id" not in item:
                    item["id"] = self.make_item_id(item)

                results.append(item)

        return results

    def bm25_search(self, query: str):
        query_tokens = tokenize(query)
        scores = self.bm25.get_scores(query_tokens)

        top_indices = np.argsort(scores)[::-1][:TOP_K_BM25]

        results = []

        for idx in top_indices:
            item = self.chunks[idx].copy()
            item["bm25_score"] = float(scores[idx])

            if "id" not in item:
                item["id"] = self.make_item_id(item)

            results.append(item)

        return results

    def retrieve(self, query: str):
        vector_results = self.vector_search(query)
        bm25_results = self.bm25_search(query)

        combined = {}

        for item in vector_results + bm25_results:
            item_id = self.make_item_id(item)
            combined[item_id] = item

        candidates = list(combined.values())

        if not candidates:
            return []

        pairs = [(query, item["text"]) for item in candidates]
        rerank_scores = self.reranker.predict(pairs)

        for item, score in zip(candidates, rerank_scores):
            item["rerank_score"] = float(score)

        candidates.sort(
            key=lambda x: x["rerank_score"],
            reverse=True
        )

        return candidates[:TOP_K_FINAL]