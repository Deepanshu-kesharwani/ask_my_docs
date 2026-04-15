# import streamlit as st
# import httpx
#
# # API_URL = st.sidebar.text_input("API URL", "http://backend:8000")
# API_URL = st.sidebar.text_input("API URL", "http://127.0.0.1:8000")
# model = st.sidebar.text_input("Model", "anthropic/claude-3.5-sonnet")
# files = st.sidebar.file_uploader("Upload documents", accept_multiple_files=True, type=["pdf", "docx", "txt", "html", "htm"])
#
# st.title("Ask My Docs")
#
# if st.sidebar.button("Ingest") and files:
#     payload = []
#     for f in files:
#         payload.append(("files", (f.name, f.getvalue(), f.type)))
#     with httpx.Client(timeout=120) as client:
#         r = client.post(f"{API_URL}/ingest", files=payload)
#     st.success(r.json())
#
# query = st.text_input("Ask a question")
# if st.button("Search"):
#     with httpx.Client(timeout=120) as client:
#         r = client.post(f"{API_URL}/query", json={"query": query, "model": model, "top_k": 5})
#     data = r.json()
#     st.subheader("Answer")
#     if r.status_code != 200:
#         st.error(r.text)
#     else:
#         data = r.json()
#         st.write(data.get("answer", "No answer"))
#     # st.write(data["answer"])
#
#     st.subheader("Citations")
#     for c in data["citations"]:
#         st.markdown(f"- **{c['source']}** page `{c['page']}` chunk `{c['chunk_id']}`")
#         st.caption(c["excerpt"])
#
#     with st.expander("Retrieved chunks"):
#         for ch in data["retrieved_chunks"]:
#             st.markdown(f"**{ch['source']}** | page {ch['page']} | `{ch['chunk_id']}`")
#             st.write(ch["text"])







import streamlit as st
import httpx
import os

# =========================
# ⚙️ CONFIG
# =========================
API_URL = st.sidebar.text_input(
    "API URL",
    os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
)

model = st.sidebar.text_input(
    "Model",
    "anthropic/claude-3.5-sonnet"
)

# =========================
# 📂 FILE UPLOAD
# =========================
files = st.sidebar.file_uploader(
    "Upload documents",
    accept_multiple_files=True,
    type=["pdf", "docx", "txt", "html", "htm"]
)

st.title("🧠 Ask My Docs")

# =========================
# 📥 INGEST
# =========================
if st.sidebar.button("Ingest"):
    if not files:
        st.warning("Please upload at least one file.")
    else:
        with st.spinner("Ingesting documents..."):
            try:
                payload = []
                for f in files:
                    payload.append(("files", (f.name, f.getvalue(), f.type)))

                with httpx.Client(timeout=120) as client:
                    r = client.post(f"{API_URL}/ingest", files=payload)

                if r.status_code != 200:
                    st.error(f"Ingest failed: {r.text}")
                else:
                    data = r.json()
                    st.success(f"Ingested {data.get('documents')} documents, {data.get('chunks')} chunks")

            except Exception as e:
                st.error(f"Ingest Error: {str(e)}")

# =========================
# 🔍 QUERY
# =========================
query = st.text_input("Ask a question")

if st.button("Search"):
    if not query.strip():
        st.warning("Please enter a query.")
    else:
        with st.spinner("Searching..."):
            try:
                with httpx.Client(timeout=120) as client:
                    r = client.post(
                        f"{API_URL}/query",
                        json={"query": query, "model": model, "top_k": 5}
                    )

                # =========================
                # ❌ ERROR HANDLING
                # =========================
                try:
                    data = r.json()
                except Exception:
                    st.error("Invalid response from backend")
                    st.text(r.text)
                    st.stop()

                if r.status_code != 200:
                    st.error(f"Backend Error: {data.get('detail', r.text)}")
                    st.stop()

                # =========================
                # ✅ ANSWER
                # =========================
                st.subheader("Answer")
                st.write(data.get("answer", "No answer returned"))

                # =========================
                # 📚 CITATIONS
                # =========================
                st.subheader("Citations")

                citations = data.get("citations", [])
                if not citations:
                    st.info("No citations returned.")
                else:
                    for c in citations:
                        st.markdown(
                            f"- **{c.get('source')}** | page `{c.get('page')}` | chunk `{c.get('chunk_id')}`"
                        )
                        st.caption(c.get("excerpt"))

                # =========================
                # 🔎 DEBUG VIEW (optional)
                # =========================
                with st.expander("🔍 Retrieved Chunks (Debug)"):
                    for ch in data.get("retrieved_chunks", []):
                        st.markdown(
                            f"**{ch.get('source')}** | page {ch.get('page')} | `{ch.get('chunk_id')}`"
                        )
                        st.write(ch.get("text"))

            except Exception as e:
                st.error(f"Query Error: {str(e)}")