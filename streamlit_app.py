import streamlit as st
import requests
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="DocuMind - Self-Correcting RAG",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 DocuMind: Self-Correcting Technical Documentation Assistant")
st.markdown(
    "An intelligent RAG application built with **LangGraph**, **ChromaDB**, **BM25**, and **FastAPI** "
    "that self-corrects retrieval failures, grades document relevance, and validates answer groundedness."
)

tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Ask Question",
    "📚 Document Ingestion & Registry",
    "📊 System Analytics",
    "⚙️ Health & Status"
])

# --- Tab 1: Ask Question ---
with tab1:
    st.header("Ask Technical Documentation Questions")
    question = st.text_area(
        "Enter your question:",
        value="How does dependency injection work in FastAPI?",
        height=100
    )

    if st.button("Submit Query", type="primary"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Executing LangGraph Self-Correcting RAG Workflow..."):
                try:
                    res = requests.post(f"{API_BASE_URL}/query", json={"question": question})
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state["last_query_result"] = data
                    else:
                        st.error(f"API Error ({res.status_code}): {res.text}")
                except Exception as e:
                    st.error(f"Connection failed: {e}")

    if "last_query_result" in st.session_state:
        data = st.session_state["last_query_result"]
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Status", data["status"].upper())
        col2.metric("Confidence Score", f"{data['confidence_score']:.1f}%")
        col3.metric("Query Type", data["query_type"])
        col4.metric("Retries Executed", data["retry_count"])

        st.subheader("Generated Response")
        st.markdown(data["answer"])

        if data.get("citations"):
            st.subheader("Inline Citations")
            for cite in data["citations"]:
                st.info(f"🔖 {cite}")

        st.subheader("LangGraph Workflow Execution Trace")
        trace = data.get("workflow_trace", [])
        st.write(" ➔ ".join([f"`{step}`" for step in trace]))

        st.subheader("Submit Feedback")
        fb_col1, fb_col2 = st.columns([1, 4])
        with fb_col1:
            rating = st.radio("Rating", ["up", "down"], format_func=lambda x: "👍 Good" if x == "up" else "👎 Poor")
        with fb_col2:
            comment = st.text_input("Optional Comment")
            if st.button("Submit Feedback"):
                try:
                    fb_res = requests.post(
                        f"{API_BASE_URL}/feedback",
                        json={
                            "question": question,
                            "answer": data["answer"],
                            "rating": rating,
                            "comment": comment
                        }
                    )
                    if fb_res.status_code == 200:
                        st.success("Thank you for your feedback!")
                except Exception as e:
                    st.error(f"Failed to submit feedback: {e}")

# --- Tab 2: Document Ingestion ---
with tab2:
    st.header("Document Ingestion & Index Registry")
    
    ingest_type = st.radio("Select Ingestion Mode", ["File Upload", "Web URL"], horizontal=True)

    if ingest_type == "File Upload":
        uploaded_file = st.file_uploader("Upload Markdown, TXT, or HTML file", type=["md", "txt", "html"])
        if st.button("Ingest File"):
            if uploaded_file:
                with st.spinner("Processing document..."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    res = requests.post(f"{API_BASE_URL}/ingest", files=files)
                    if res.status_code == 200:
                        st.success(res.json()["message"])
                    else:
                        st.error(f"Error: {res.text}")
    else:
        url = st.text_input("Enter documentation web URL:")
        title_override = st.text_input("Optional Title Override:")
        if st.button("Ingest URL"):
            if url:
                with st.spinner("Fetching and indexing web content..."):
                    res = requests.post(f"{API_BASE_URL}/ingest/url", json={"url": url, "title": title_override})
                    if res.status_code == 200:
                        st.success(res.json()["message"])
                    else:
                        st.error(f"Error: {res.text}")

    st.subheader("Currently Indexed Documents")
    if st.button("Refresh Document List"):
        pass

    try:
        doc_res = requests.get(f"{API_BASE_URL}/documents")
        if doc_res.status_code == 200:
            docs = doc_res.json().get("documents", [])
            if docs:
                st.table(docs)
            else:
                st.info("No documents indexed yet. Run the sample ingestion script or upload files above.")
    except Exception as e:
        st.warning(f"Could not load document registry: {e}")

# --- Tab 3: Analytics ---
with tab3:
    st.header("System Execution Metrics")
    try:
        metrics_res = requests.get(f"{API_BASE_URL}/metrics")
        if metrics_res.status_code == 200:
            m = metrics_res.json()
            mcol1, mcol2, mcol3 = st.columns(3)
            mcol1.metric("Total Queries Processed", m["total_queries"])
            mcol2.metric("Successful Queries", m["successful_queries"])
            mcol3.metric("Insufficient Evidence Queries", m["insufficient_evidence_queries"])

            mcol4, mcol5, mcol6 = st.columns(3)
            mcol4.metric("Average Confidence Score", f"{m['average_confidence']}%")
            mcol5.metric("Average Retries per Query", m["average_retries"])
            mcol6.metric("Feedback Balance", f"👍 {m['positive_feedback']} / 👎 {m['negative_feedback']}")
    except Exception as e:
        st.warning(f"Could not fetch metrics: {e}")

# --- Tab 4: Health ---
with tab4:
    st.header("Application Readiness & Health Check")
    try:
        h_res = requests.get(f"{API_BASE_URL}/health")
        if h_res.status_code == 200:
            st.json(h_res.json())
    except Exception as e:
        st.error(f"Backend API unavailable at {API_BASE_URL}: {e}")
