from app.retriever import HybridRetriever


def test_retrieval_returns_results():
    retriever = HybridRetriever()
    results = retriever.retrieve("What is hybrid retrieval?")

    assert len(results) > 0


def test_citation_source_exists():
    retriever = HybridRetriever()
    results = retriever.retrieve("What is FAISS?")

    assert "source" in results[0]
    assert "text" in results[0]


def test_retrieval_relevance_gate():
    retriever = HybridRetriever()
    results = retriever.retrieve("What is RAG?")

    combined_text = " ".join([r["text"].lower() for r in results])

    assert "rag" in combined_text or "retrieval" in combined_text