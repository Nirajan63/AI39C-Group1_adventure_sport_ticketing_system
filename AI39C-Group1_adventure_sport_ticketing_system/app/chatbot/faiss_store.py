# app/chatbot/faiss_store.py
"""
Builds and caches a FAISS vector index over the FAQ knowledge base so the
chatbot can do semantic search instead of keyword matching.

Embeddings are computed locally with sentence-transformers (all-MiniLM-L6-v2)
-- this is a free, open-weights model that runs on CPU and needs no API key,
so the only paid/external API call in this whole chatbot is the final LLM
call itself.

The index is built once and cached to disk under app/chatbot/.faiss_cache/
so subsequent app restarts don't re-embed everything from scratch.
"""

import os
import threading

from app.chatbot.faq_data import FAQ_ENTRIES

_CACHE_DIR = os.path.join(os.path.dirname(__file__), ".faiss_cache")
_EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_vector_store = None
_lock = threading.Lock()


def _get_embeddings():
    from langchain_huggingface import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(model_name=_EMBEDDING_MODEL_NAME)


def _build_documents():
    from langchain_core.documents import Document
    docs = []
    for entry in FAQ_ENTRIES:
        text = f"Q: {entry['question']}\nA: {entry['answer']}"
        docs.append(Document(page_content=text, metadata={"id": entry["id"], "question": entry["question"]}))
    return docs


def get_vector_store():
    """
    Returns a singleton FAISS vector store, building it on first call and
    loading from disk cache on subsequent app restarts.
    """
    global _vector_store

    if _vector_store is not None:
        return _vector_store

    with _lock:
        if _vector_store is not None:
            return _vector_store

        from langchain_community.vectorstores import FAISS

        embeddings = _get_embeddings()
        index_path = os.path.join(_CACHE_DIR, "index.faiss")

        if os.path.exists(index_path):
            try:
                _vector_store = FAISS.load_local(
                    _CACHE_DIR, embeddings, allow_dangerous_deserialization=True
                )
                return _vector_store
            except Exception as e:
                print(f"[chatbot] Failed to load cached FAISS index, rebuilding: {e}", flush=True)

        docs = _build_documents()
        _vector_store = FAISS.from_documents(docs, embeddings)

        os.makedirs(_CACHE_DIR, exist_ok=True)
        try:
            _vector_store.save_local(_CACHE_DIR)
        except Exception as e:
            print(f"[chatbot] Failed to cache FAISS index to disk (non-fatal): {e}", flush=True)

        return _vector_store


def search_faq(query: str, k: int = 3):
    """Returns up to k (question, answer, score) tuples most relevant to query."""
    store = get_vector_store()
    results = store.similarity_search_with_score(query, k=k)
    out = []
    for doc, score in results:
        out.append({
            "question": doc.metadata.get("question", ""),
            "content": doc.page_content,
            "score": float(score),
        })
    return out
