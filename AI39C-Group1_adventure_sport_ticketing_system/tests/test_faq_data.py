"""
Tests for app/chatbot/faq_data.py.

This module exposes only static data (no functions), so the tests
verify the data's structural integrity, which other code (faiss_store.py,
tools.py) implicitly depends on.
"""
from app.chatbot.faq_data import FAQ_ENTRIES


def test_faq_entries_is_non_empty_list():
    assert isinstance(FAQ_ENTRIES, list)
    assert len(FAQ_ENTRIES) > 0


def test_every_entry_has_required_keys():
    for entry in FAQ_ENTRIES:
        assert "id" in entry
        assert "question" in entry
        assert "answer" in entry


def test_every_entry_field_is_non_empty_string():
    for entry in FAQ_ENTRIES:
        assert isinstance(entry["id"], str) and entry["id"]
        assert isinstance(entry["question"], str) and entry["question"]
        assert isinstance(entry["answer"], str) and entry["answer"]


def test_entry_ids_are_unique():
    ids = [entry["id"] for entry in FAQ_ENTRIES]
    assert len(ids) == len(set(ids))


def test_contains_expected_known_entry():
    ids = {entry["id"] for entry in FAQ_ENTRIES}
    assert "booking-cancel" in ids
    assert "payment-refund" in ids
