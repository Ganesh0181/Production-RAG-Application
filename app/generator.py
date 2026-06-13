def generate_answer(question: str, chunks):
    if not chunks:
        return "I don't know from the provided documents."

    answer = "Based on the provided documents:\n\n"

    for i, chunk in enumerate(chunks, start=1):
        text = chunk["text"].strip().replace("\n", " ")
        answer += f"{text[:500]} [{i}]\n\n"

    return answer