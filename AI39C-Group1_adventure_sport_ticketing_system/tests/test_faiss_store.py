"""
Tests for app/chatbot/faiss_store.py.

Covers:
  - _get_embeddings
  - _build_documents
  - get_vector_store (cache hit, cache miss/build, load failure -> rebuild)
  - search_faq
"""
import pytest
from unittest.mock import patch, MagicMock

import app.chatbot.faiss_store as faiss_store


@pytest.fixture(autouse=True)
def reset_singleton():
    """The module keeps a process-global `_vector_store` singleton; reset
    it before/after each test so tests don't leak state into each other."""
    faiss_store._vector_store = None
    yield
    faiss_store._vector_store = None


# ── _get_embeddings ──────────────────────────────────────────────────────
@patch("langchain_huggingface.HuggingFaceEmbeddings")
def test_get_embeddings_creates_huggingface_embeddings(mock_embeddings_cls):
    result = faiss_store._get_embeddings()

    mock_embeddings_cls.assert_called_once_with(model_name=faiss_store._EMBEDDING_MODEL_NAME)
    assert result is mock_embeddings_cls.return_value


# ── _build_documents ─────────────────────────────────────────────────────
def test_build_documents_builds_one_document_per_faq_entry():
    docs = faiss_store._build_documents()

    assert len(docs) == len(faiss_store.FAQ_ENTRIES)
    first_entry = faiss_store.FAQ_ENTRIES[0]
    assert first_entry["question"] in docs[0].page_content
    assert first_entry["answer"] in docs[0].page_content
    assert docs[0].metadata["id"] == first_entry["id"]
    assert docs[0].metadata["question"] == first_entry["question"]


# ── get_vector_store ─────────────────────────────────────────────────────
@patch("langchain_community.vectorstores.FAISS")
@patch("app.chatbot.faiss_store._build_documents")
@patch("app.chatbot.faiss_store._get_embeddings")
@patch("os.path.exists", return_value=False)
@patch("os.makedirs")
def test_get_vector_store_builds_fresh_when_no_cache(
    mock_makedirs, mock_exists, mock_get_embeddings, mock_build_documents, mock_faiss_cls
):
    mock_get_embeddings.return_value = "EMBEDDINGS"
    mock_build_documents.return_value = ["DOC1", "DOC2"]
    fake_store = MagicMock()
    mock_faiss_cls.from_documents.return_value = fake_store

    result = faiss_store.get_vector_store()

    mock_faiss_cls.from_documents.assert_called_once_with(["DOC1", "DOC2"], "EMBEDDINGS")
    fake_store.save_local.assert_called_once()
    assert result is fake_store
    # Calling again should hit the in-memory singleton, not rebuild.
    second_call = faiss_store.get_vector_store()
    assert second_call is fake_store
    assert mock_build_documents.call_count == 1


@patch("langchain_community.vectorstores.FAISS")
@patch("app.chatbot.faiss_store._build_documents")
@patch("app.chatbot.faiss_store._get_embeddings")
@patch("os.path.exists", return_value=True)
def test_get_vector_store_loads_from_disk_cache_when_present(
    mock_exists, mock_get_embeddings, mock_build_documents, mock_faiss_cls
):
    mock_get_embeddings.return_value = "EMBEDDINGS"
    fake_store = MagicMock()
    mock_faiss_cls.load_local.return_value = fake_store

    result = faiss_store.get_vector_store()

    mock_faiss_cls.load_local.assert_called_once()
    mock_build_documents.assert_not_called()
    assert result is fake_store


@patch("langchain_community.vectorstores.FAISS")
@patch("app.chatbot.faiss_store._build_documents")
@patch("app.chatbot.faiss_store._get_embeddings")
@patch("os.path.exists", return_value=True)
@patch("os.makedirs")
def test_get_vector_store_rebuilds_when_cache_load_fails(
    mock_makedirs, mock_exists, mock_get_embeddings, mock_build_documents, mock_faiss_cls
):
    mock_get_embeddings.return_value = "EMBEDDINGS"
    mock_build_documents.return_value = ["DOC1"]
    mock_faiss_cls.load_local.side_effect = Exception("corrupt cache")
    fake_store = MagicMock()
    mock_faiss_cls.from_documents.return_value = fake_store

    result = faiss_store.get_vector_store()

    mock_faiss_cls.from_documents.assert_called_once()
    assert result is fake_store


# ── search_faq ───────────────────────────────────────────────────────────
@patch("app.chatbot.faiss_store.get_vector_store")
def test_search_faq_returns_question_content_score(mock_get_vector_store):
    mock_store = MagicMock()
    fake_doc = MagicMock()
    fake_doc.metadata = {"question": "How do I cancel?"}
    fake_doc.page_content = "Q: How do I cancel?\nA: Go to your dashboard."
    mock_store.similarity_search_with_score.return_value = [(fake_doc, 0.42)]
    mock_get_vector_store.return_value = mock_store

    result = faiss_store.search_faq("cancel booking", k=3)

    mock_store.similarity_search_with_score.assert_called_once_with("cancel booking", k=3)
    assert result == [{
        "question": "How do I cancel?",
        "content": "Q: How do I cancel?\nA: Go to your dashboard.",
        "score": 0.42,
    }]


@patch("app.chatbot.faiss_store.get_vector_store")
def test_search_faq_default_k_is_three(mock_get_vector_store):
    mock_store = MagicMock()
    mock_store.similarity_search_with_score.return_value = []
    mock_get_vector_store.return_value = mock_store

    faiss_store.search_faq("anything")

    mock_store.similarity_search_with_score.assert_called_once_with("anything", k=3)
