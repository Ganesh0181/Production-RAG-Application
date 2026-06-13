from langchain_text_splitters import RecursiveCharacterTextSplitter

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

            chunks.append({
                "source": doc["source"],
                "chunk_id": idx,
                "text": chunk
            })

    return chunks