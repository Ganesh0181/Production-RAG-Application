import streamlit as st
import requests
import json
import time
from datetime import datetime
from urllib.parse import quote

API_URL = "http://backend:9001"

st.set_page_config(
    page_title="Ask My Docs",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CUSTOM CSS
st.markdown(
    """
<style>
.main .block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020617 0%, #0f172a 100%);
    padding-top: 20px;
}

[data-testid="stSidebar"] * {
    color: #f8fafc !important;
}

[data-testid="stSidebar"] input {
    background: #ffffff !important;
    color: #111827 !important;
    border-radius: 12px !important;
    border: 1px solid #334155 !important;
}

[data-testid="stSidebar"] input::placeholder {
    color: #6b7280 !important;
}

[data-testid="stSidebar"] button {
    border-radius: 12px !important;
    font-weight: 700 !important;
}

/* MAIN PANEL INDUSTRIAL STYLE */
.hero-industrial {
    background: linear-gradient(135deg, #111827 0%, #1e293b 55%, #0f172a 100%);
    border-radius: 12px;
    padding: 36px;
    border-left: 8px solid #2563eb;
    box-shadow: 0 10px 28px rgba(15, 23, 42, 0.18);
    margin-bottom: 22px;
}

.hero-industrial h1 {
    font-size: 42px;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 12px;
}

.hero-industrial p {
    color: #cbd5e1;
    font-size: 17px;
    line-height: 1.6;
}

.app-card {
    background: #f8fafc;
    border-radius: 12px;
    padding: 26px;
    border: 1px solid #cbd5e1;
    border-left: 6px solid #2563eb;
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
    margin-bottom: 20px;
}

.app-card h3 {
    color: #111827;
    font-weight: 800;
    margin-top: 0;
}

.small-text {
    color: #475569;
    font-size: 15px;
    line-height: 1.6;
}

.pipeline-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 22px;
}

.pipeline-item {
    background: #ffffff;
    border: 1px solid #d1d5db;
    border-left: 5px solid #2563eb;
    border-radius: 10px;
    padding: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    font-size: 14px;
    font-weight: 700;
    color: #111827;
}

div[data-testid="stFileUploader"] {
    background: #f1f5f9;
    border: 2px dashed #64748b;
    border-radius: 12px;
    padding: 16px;
}

div[data-testid="stAlert"] {
    border-radius: 12px;
    border-left: 6px solid #16a34a;
}

/* SIDEBAR CARDS */
.file-card {
    background: #1e293b;
    border-radius: 14px;
    padding: 12px;
    color: white;
    margin-top: 10px;
    font-size: 13px;
    word-break: break-word;
    border: 1px solid #334155;
}

.backend-card {
    background: #dbeafe;
    color: #1e40af !important;
    padding: 12px;
    border-radius: 14px;
    margin-bottom: 14px;
    font-size: 14px;
}

.backend-card a {
    color: #1d4ed8 !important;
    font-weight: 800;
    text-decoration: underline;
}

.status-card {
    background: #dcfce7;
    color: #166534 !important;
    padding: 12px;
    border-radius: 14px;
    font-weight: 700;
    margin-bottom: 14px;
}

div[data-testid="stMetric"] {
    background: #1e293b;
    padding: 14px;
    border-radius: 16px;
    border: 1px solid #334155;
}

div[data-testid="stMetric"] label {
    color: #cbd5e1 !important;
}

div[data-testid="stMetric"] div {
    color: #ffffff !important;
}

.stButton > button {
    border-radius: 12px;
    border: none;
    background: #2563eb;
    color: white;
    font-weight: 700;
}

.stButton > button:hover {
    background: #1d4ed8;
    color: white;
}

.stDownloadButton > button {
    width: 100%;
    border-radius: 12px;
    background: #2563eb;
    color: white;
    border: none;
    font-weight: 700;
}
</style>
""",
    unsafe_allow_html=True
)

# SESSION MEMORY
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_retrieved_chunks" not in st.session_state:
    st.session_state.last_retrieved_chunks = 0

if "last_latency" not in st.session_state:
    st.session_state.last_latency = 0

# SIDEBAR
st.sidebar.title("⚙️ Control Panel")

if st.sidebar.button("🧹 Clear Chat", use_container_width=True):
    st.session_state.messages = []
    st.session_state.last_retrieved_chunks = 0
    st.session_state.last_latency = 0
    st.rerun()

# CLICKABLE BACKEND LINK
st.sidebar.markdown(
    """
<div class="backend-card">
<b>FastAPI Backend</b><br>
<a href="http://127.0.0.1:9001/docs" target="_blank">
http://127.0.0.1:9001/docs
</a>
</div>
""",
    unsafe_allow_html=True
)

# API STATUS
try:
    health = requests.get(API_URL, timeout=3)

    if health.status_code == 200:
        st.sidebar.markdown(
            """
<div class="status-card">
✅ Backend Connected
</div>
""",
            unsafe_allow_html=True
        )
    else:
        st.sidebar.error("Backend Not Responding")

except Exception:
    st.sidebar.error("FastAPI server not running")
    st.stop()

# DASHBOARD DATA
total_pdfs = 0
total_chunks = 0
backend_pdf_files = []

try:
    stats_response = requests.get(f"{API_URL}/stats", timeout=5)

    if stats_response.status_code == 200:
        stats_data = stats_response.json()
        total_pdfs = stats_data.get("total_pdfs", 0)
        total_chunks = stats_data.get("total_chunks", 0)
        backend_pdf_files = stats_data.get("pdf_files", [])

except Exception:
    total_pdfs = 0
    total_chunks = 0
    backend_pdf_files = []

# SIDEBAR DASHBOARD
st.sidebar.subheader("📊 RAG Dashboard")

m1, m2 = st.sidebar.columns(2)

with m1:
    st.metric("PDFs", total_pdfs)
    st.metric("Retrieved", st.session_state.last_retrieved_chunks)

with m2:
    st.metric("Chunks", total_chunks)
    st.metric("Latency", f"{st.session_state.last_latency:.2f}s")

# SIDEBAR FILES WITH BETTER DELETE UI
st.sidebar.subheader("📚 Documents")

show_files = st.sidebar.checkbox("Show uploaded files", value=True)

if show_files:
    search_file = st.sidebar.text_input(
        "Search files",
        placeholder="🔍 Search PDFs...",
        key="pdf_search"
    )

    filtered_files = [
        file for file in backend_pdf_files
        if search_file.lower() in file.lower()
    ]

    if filtered_files:
        for file_name in filtered_files:
            st.sidebar.markdown(
                f"""
<div class="file-card">
📄 {file_name}
</div>
""",
                unsafe_allow_html=True
            )

            encoded_name = quote(file_name, safe="")

            if st.sidebar.button(
                "🗑️ Delete this PDF",
                key=f"delete_{file_name}",
                use_container_width=True
            ):
                with st.spinner(f"Deleting {file_name}..."):
                    delete_response = requests.delete(
                        f"{API_URL}/delete/{encoded_name}",
                        timeout=120
                    )

                if delete_response.status_code == 200:
                    delete_data = delete_response.json()

                    if "error" in delete_data:
                        st.error(delete_data["error"])
                    else:
                        st.success(f"{file_name} deleted")
                        st.session_state.last_retrieved_chunks = 0
                        st.session_state.last_latency = 0
                        st.rerun()
                else:
                    st.error("Delete failed")
    else:
        st.sidebar.warning("No matching PDFs found")

# MAIN PANEL INDUSTRIAL LAYOUT
st.markdown(
    """
<div class="hero-industrial">
    <h1>📄 Ask My Docs - Production RAG App</h1>
    <p>
    Industrial-grade document intelligence system using FastAPI, Streamlit,
    FAISS, BM25, Cross-Encoder Reranking, Gemini, Citations, Docker and CI/CD.
    </p>
</div>
""",
    unsafe_allow_html=True
)

st.success(
    f"✅ System Ready | {total_pdfs} PDFs Indexed | {total_chunks} Chunks Available"
)

st.markdown(
    """
<div class="pipeline-grid">
    <div class="pipeline-item">📤 Upload PDF</div>
    <div class="pipeline-item">⚙️ Chunk + Embed</div>
    <div class="pipeline-item">🔎 Hybrid Search</div>
    <div class="pipeline-item">🤖 Answer + Citations</div>
</div>
""",
    unsafe_allow_html=True
)

# UPLOAD SECTION
st.markdown("### 📤 Upload Documents")

st.markdown(
    """
<div class="app-card">
<h3>Document Ingestion Pipeline</h3>
<p class="small-text">
Upload one or more PDF files. The backend stores the files, extracts text,
splits content into chunks, generates embeddings, and rebuilds FAISS + BM25 indexes.
</p>
</div>
""",
    unsafe_allow_html=True
)

uploaded_files = st.file_uploader(
    "Upload PDF files",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        if uploaded_file.name not in backend_pdf_files:
            with st.spinner(f"Uploading and indexing {uploaded_file.name}..."):
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "application/pdf"
                    )
                }

                response = requests.post(
                    f"{API_URL}/upload",
                    files=files,
                    timeout=120
                )

                if response.status_code == 200:
                    st.success(f"{uploaded_file.name} uploaded and indexed")
                    st.rerun()
                else:
                    st.error(response.text)
        else:
            st.info(f"{uploaded_file.name} is already uploaded")

st.markdown(
    f"""
<div class="app-card">
<h3>📌 Current Knowledge Base</h3>
<p><b>{total_pdfs}</b> PDFs indexed</p>
<p><b>{total_chunks}</b> chunks available</p>
<p><b>{st.session_state.last_retrieved_chunks}</b> chunks retrieved in last query</p>
<p><b>{st.session_state.last_latency:.2f}s</b> response latency</p>
</div>
""",
    unsafe_allow_html=True
)

st.divider()

# CHAT SECTION
st.markdown("### 💬 Chat with your documents")

for msg in st.session_state.messages:
    avatar = "🧑" if msg["role"] == "user" else "🤖"

    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

        if msg["role"] == "assistant" and "citations" in msg:
            with st.expander("📌 View Sources / Citations"):
                for citation in msg["citations"]:
                    page_value = citation.get("page", "N/A")
                    st.markdown(
                        f"""
**📄 Source:** {citation["source"]}  
**📍 Page:** {page_value}  
**🔢 Chunk ID:** {citation["chunk_id"]}  
**⭐ Rerank Score:** `{citation["rerank_score"]:.4f}`

**Text Preview:**  
{citation["text"][:700]}

---
"""
                    )

question = st.chat_input(
    "Ask a question from your documents..."
)

if question:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user", avatar="🧑"):
        st.write(question)

    chat_history = []

    for msg in st.session_state.messages[-6:]:
        chat_history.append(
            {
                "role": msg["role"],
                "content": msg["content"]
            }
        )

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Retrieving answer from documents..."):
            try:
                start_time = time.time()

                response = requests.post(
                    f"{API_URL}/ask",
                    json={
                        "question": question,
                        "chat_history": chat_history
                    },
                    timeout=120
                )

                end_time = time.time()
                st.session_state.last_latency = end_time - start_time

                data = response.json()

                if "error" in data:
                    answer = data["error"]
                    citations = []
                else:
                    answer = data.get("answer", "No answer found.")
                    citations = data.get("citations", [])

                st.session_state.last_retrieved_chunks = len(citations)

                st.write(answer)

                if citations:
                    with st.expander("📌 View Sources / Citations"):
                        for citation in citations:
                            page_value = citation.get("page", "N/A")
                            st.markdown(
                                f"""
**📄 Source:** {citation["source"]}  
**📍 Page:** {page_value}  
**🔢 Chunk ID:** {citation["chunk_id"]}  
**⭐ Rerank Score:** `{citation["rerank_score"]:.4f}`

**Text Preview:**  
{citation["text"][:700]}

---
"""
                            )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "citations": citations
                    }
                )

            except Exception as e:
                error_message = f"Error connecting to backend: {str(e)}"
                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                        "citations": []
                    }
                )

# DOWNLOAD CHAT
if st.session_state.messages:
    chat_text = ""

    for msg in st.session_state.messages:
        role = msg["role"].upper()

        chat_text += f"{role}\n"
        chat_text += f"{msg['content']}\n\n"

        if msg["role"] == "assistant" and "citations" in msg:
            chat_text += "SOURCES\n"

            for citation in msg["citations"]:
                page_value = citation.get("page", "N/A")
                chat_text += (
                    f"- {citation['source']} | Page: {page_value} | "
                    f"Chunk: {citation['chunk_id']}\n"
                )

            chat_text += "\n"

        chat_text += "-" * 60 + "\n\n"

    st.sidebar.download_button(
        label="⬇️ Download Chat TXT",
        data=chat_text,
        file_name="rag_chat_history.txt",
        mime="text/plain"
    )

    st.sidebar.download_button(
        label="⬇️ Download Chat JSON",
        data=json.dumps(
            {
                "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "messages": st.session_state.messages
            },
            indent=2
        ),
        file_name="rag_chat_history.json",
        mime="application/json"
    )