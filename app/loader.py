import os
from pypdf import PdfReader


def load_txt(path: str):
    with open(path, "r", encoding="utf-8") as file:
        text = file.read()

    return [{
        "source": os.path.basename(path),
        "page": 1,
        "text": text
    }]


def load_pdf(path: str):
    reader = PdfReader(path)
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()

        if text:
            pages.append({
                "source": os.path.basename(path),
                "page": page_number,
                "text": text
            })

    return pages


def load_documents(data_dir: str):
    documents = []

    for filename in os.listdir(data_dir):
        path = os.path.join(data_dir, filename)

        if filename.lower().endswith(".txt"):
            documents.extend(load_txt(path))

        elif filename.lower().endswith(".pdf"):
            documents.extend(load_pdf(path))

    return documents