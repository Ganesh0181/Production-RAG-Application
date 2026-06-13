from app.retriever import HybridRetriever

r = HybridRetriever()

results = r.retrieve("What is hybrid retrieval?")

for i in results:
    print(i["source"])
    print(i["text"][:200])
    print("="*50)