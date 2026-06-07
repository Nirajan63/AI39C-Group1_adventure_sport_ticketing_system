"""
=============================================================
  OOP Concept: ABSTRACTION & INHERITANCE (Base Model)
=============================================================
  - Abstraction: We define WHAT every model should do
    (find, create, update, delete) without saying HOW.
  - Inheritance: Child classes (like User) will inherit
    these methods and reuse them automatically.
  - Encapsulation: The database connection details are
    hidden inside this class — outside code never sees them.
=============================================================
"""

from abc import ABC, abstractmethod
from .data import Database

# Whitelist of columns that may be interpolated into SQL identifiers.
# This prevents SQL injection via find_by(column, ...) and find_all(order_by=...).
_SAFE_COLUMNS = {
    "id", "name", "email", "role", "status", "created_at",
    "user_id", "activity", "date", "people", "price", "total",
    "payment_status", "payment_method", "txn_code",
    "admin_id", "action", "target_record", "timestamp",
}


def _safe_column(col):
    """Raise ValueError if col is not in the whitelist — stops SQL injection."""
    if col not in _SAFE_COLUMNS:
        raise ValueError(f"Column '{col}' is not in the allowed column whitelist.")
    return col


class BaseModel(ABC):
    """
    Abstract Base Class for all models.

    ABC = Abstract Base Class
    - You CANNOT create an object of BaseModel directly.
    - Child classes MUST define the 'table' property.
    - Child classes INHERIT all the helper methods below.
    """

    # ── Abstract Property (child MUST define this) ──────────
    @property
    @abstractmethod
    def table(self):
        """Each child model must specify its database table name."""
        pass

    # ── Shared Methods (inherited by all child models) ──────

    def find_by_id(self, record_id):
        """Find a single record by its ID."""
        db = Database()
        result = db.fetch_one(
            f"SELECT * FROM {self.table} WHERE id = %s", (record_id,)
        )
        db.close()
        return result

    def find_by(self, column, value):
        """Find a single record by any whitelisted column.
        Example: find_by('email', 'a@b.com')
        """
        _safe_column(column)
        db = Database()
        result = db.fetch_one(
            f"SELECT * FROM {self.table} WHERE {column} = %s", (value,)
        )
        db.close()
        return result

    def find_all(self, order_by="id"):
        """Get all records from the table, ordered by a whitelisted column."""
        _safe_column(order_by)
        db = Database()
        results = db.fetch_all(
            f"SELECT * FROM {self.table} ORDER BY {order_by}"
        )
        db.close()
        return results

    def count_all(self):
        """Count total records in the table."""
        db = Database()
        result = db.fetch_one(f"SELECT COUNT(*) AS total FROM {self.table}")
        db.close()
        return result["total"]

    def delete_by_id(self, record_id):
        """Delete a record by its ID."""
        db = Database()
        db.execute(f"DELETE FROM {self.table} WHERE id = %s", (record_id,))
        db.close()
