"""
Tests for app/models/baseModel.py.

Covers:
  - _safe_column (column whitelist guard)
  - BaseModel.find_by_id
  - BaseModel.find_by
  - BaseModel.find_all
  - BaseModel.count_all
  - BaseModel.delete_by_id
  - BaseModel cannot be instantiated directly (it's an ABC)
"""
import pytest
from unittest.mock import patch, MagicMock

from app.models.baseModel import BaseModel, _safe_column


class _ConcreteModel(BaseModel):
    """Minimal concrete subclass so we can exercise the inherited methods."""
    @property
    def table(self):
        return "users"


# ── _safe_column ─────────────────────────────────────────────────────────
def test_safe_column_allows_whitelisted_column():
    assert _safe_column("email") == "email"


def test_safe_column_rejects_non_whitelisted_column():
    with pytest.raises(ValueError):
        _safe_column("DROP TABLE users; --")


# ── BaseModel is abstract ────────────────────────────────────────────────
def test_basemodel_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        BaseModel()


# ── find_by_id ───────────────────────────────────────────────────────────
@patch("app.models.baseModel.Database")
def test_find_by_id_queries_and_closes(mock_database_cls):
    mock_db = MagicMock()
    mock_database_cls.return_value = mock_db
    mock_db.fetch_one.return_value = {"id": 1, "username": "alice"}

    model = _ConcreteModel()
    result = model.find_by_id(1)

    mock_db.fetch_one.assert_called_once_with("SELECT * FROM users WHERE id = %s", (1,))
    mock_db.close.assert_called_once()
    assert result == {"id": 1, "username": "alice"}


# ── find_by ──────────────────────────────────────────────────────────────
@patch("app.models.baseModel.Database")
def test_find_by_with_whitelisted_column(mock_database_cls):
    mock_db = MagicMock()
    mock_database_cls.return_value = mock_db
    mock_db.fetch_one.return_value = {"id": 2, "email": "bob@example.com"}

    model = _ConcreteModel()
    result = model.find_by("email", "bob@example.com")

    mock_db.fetch_one.assert_called_once_with(
        "SELECT * FROM users WHERE email = %s", ("bob@example.com",)
    )
    assert result == {"id": 2, "email": "bob@example.com"}


def test_find_by_rejects_non_whitelisted_column():
    model = _ConcreteModel()
    with pytest.raises(ValueError):
        model.find_by("password; DROP TABLE users", "x")


# ── find_all ─────────────────────────────────────────────────────────────
@patch("app.models.baseModel.Database")
def test_find_all_default_order(mock_database_cls):
    mock_db = MagicMock()
    mock_database_cls.return_value = mock_db
    mock_db.fetch_all.return_value = [{"id": 1}, {"id": 2}]

    model = _ConcreteModel()
    result = model.find_all()

    mock_db.fetch_all.assert_called_once_with("SELECT * FROM users ORDER BY id")
    assert result == [{"id": 1}, {"id": 2}]


def test_find_all_rejects_non_whitelisted_order_by():
    model = _ConcreteModel()
    with pytest.raises(ValueError):
        model.find_all(order_by="1=1; --")


# ── count_all ────────────────────────────────────────────────────────────
@patch("app.models.baseModel.Database")
def test_count_all_returns_total(mock_database_cls):
    mock_db = MagicMock()
    mock_database_cls.return_value = mock_db
    mock_db.fetch_one.return_value = {"total": 7}

    model = _ConcreteModel()
    result = model.count_all()

    mock_db.fetch_one.assert_called_once_with("SELECT COUNT(*) AS total FROM users")
    assert result == 7


# ── delete_by_id ─────────────────────────────────────────────────────────
@patch("app.models.baseModel.Database")
def test_delete_by_id_executes_delete_and_closes(mock_database_cls):
    mock_db = MagicMock()
    mock_database_cls.return_value = mock_db

    model = _ConcreteModel()
    model.delete_by_id(5)

    mock_db.execute.assert_called_once_with("DELETE FROM users WHERE id = %s", (5,))
    mock_db.close.assert_called_once()
