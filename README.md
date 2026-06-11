# 🚀 Production RAG Application

> Enterprise-Grade Retrieval Augmented Generation (RAG) System using FastAPI, Streamlit, FAISS, BM25, Cross-Encoder Reranking, and Gemini.

---

## 📌 Overview

Production RAG Application is a document intelligence platform that enables users to upload PDF documents and ask questions using natural language.

The system retrieves relevant information from uploaded documents using Hybrid Retrieval (BM25 + FAISS), reranks results using a Cross-Encoder model, and generates source-grounded answers with citations.

This architecture significantly reduces hallucinations and improves answer accuracy compared to traditional LLM-only approaches.

---

## ✨ Key Features

### 📄 Multi-PDF Upload

* Upload one or multiple PDF documents
* Automatic text extraction
* Dynamic indexing of new documents

### 🔍 Hybrid Retrieval

* FAISS Vector Search
* BM25 Keyword Search
* Improved recall and precision

### 🎯 Cross-Encoder Reranking

* Reorders retrieved chunks based on relevance
* Improves answer quality

### 📚 Citation-Based Answers

* Source document tracking
* Page-level metadata support
* Explainable AI responses

### 💬 Multi-Turn Chat Memory

* Maintains conversational context
* Supports follow-up questions

### 📊 RAG Dashboard

* Total PDFs
* Total Chunks
* Retrieved Chunks
* Query Latency

### 📥 Export Chat

* Download conversation as TXT
* Download conversation as JSON

### ⚡ FastAPI Backend

* REST API architecture
* Scalable and reusable endpoints

---

## 🏗️ System Architecture
<img width="5000" height="2812" alt="image" src="https://github.com/user-attachments/assets/d5ded150-f9e5-4815-b3f5-2082a0f2206f" />

<img width="800" height="533" alt="image" src="https://github.com/user-attachments/assets/166eaa82-4697-42df-b747-f075aa301f29" />

<img width="1412" height="938" alt="image" src="https://github.com/user-attachments/assets/e8ba0daf-e393-47fc-a93c-c25135f91703" />

<img width="1223" height="662" alt="image" src="https://github.com/user-attachments/assets/b2f08aa8-2067-4652-96f9-d77d0bdd4920" />



---

## ⚙️ Tech Stack

### Backend

* Python
* FastAPI

### Frontend

* Streamlit

### Retrieval Layer

* FAISS
* BM25

### Embeddings

* Sentence Transformers
* all-MiniLM-L6-v2

### Reranking

* Cross Encoder
* ms-marco-MiniLM-L-6-v2

### LLM

* Google Gemini

### Testing

* Pytest

### Deployment

* Docker
* GitHub Actions CI/CD

---

## 📂 Project Structure

```text
Production-RAG-Application/
│
├── app/
│   ├── main.py
│   ├── retriever.py
│   ├── generator.py
│   ├── indexer.py
│   ├── loader.py
│   └── config.py
│
├── data/
├── indexes/
├── tests/
│
├── streamlit_app.py
├── requirements.txt
├── Dockerfile
├── README.md
└── .env
```

---

## 🔄 Workflow

1. User uploads PDF documents
2. Backend extracts document text
3. Documents are chunked
4. Embeddings are generated
5. FAISS and BM25 indexes are built
6. User submits a question
7. Hybrid retrieval fetches relevant chunks
8. Cross Encoder reranks results
9. Gemini generates an answer
10. Citations are returned to the user

---

## 🚀 Running the Project

### Start Backend

```bash
uvicorn app.main:app --reload --port 9001
```

Swagger Documentation:

```text
http://127.0.0.1:9001/docs
```

### Start Frontend

```bash
streamlit run streamlit_app.py
```

Application:

```text
http://localhost:8501
```

---

## 🧪 Testing

Run Retriever Test:

```bash
python test_retriever.py
```

Run Unit Tests:

```bash
pytest -v
```

Expected Output:

```text
3 passed
```

---

## 🎯 Future Enhancements

* User Authentication
* PostgreSQL Chat Storage
* OCR Support for Scanned PDFs
* Cloud Deployment (AWS/Azure)
* Real-Time Streaming Responses
* Role-Based Access Control

---

## 👨‍💻 Author

**S.Ganesh chary**
B.Tech – Artificial Intelligence & Machine Learning

Production RAG Application | AI Engineering Project
