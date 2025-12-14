from __future__ import annotations

import sqlite3
from dataclasses import dataclass
import pandas as pd
import threading


from .data_loader import DataContext


@dataclass
class SqlEngine:
    conn: sqlite3.Connection
    
    def __post_init__(self):
        self._lock = threading.Lock()

    @classmethod
    def from_datacontext(cls, ctx: DataContext) -> "SqlEngine":
        """
        Create an in-memory SQLite DB and load the three tables into it.
        """
        conn = sqlite3.connect(":memory:", check_same_thread=False)

        # Write DataFrames into SQLite
        ctx.clients.to_sql("Clients", conn, index=False, if_exists="replace")
        ctx.invoices.to_sql("Invoices", conn, index=False, if_exists="replace")
        ctx.line_items.to_sql("InvoiceLineItems", conn, index=False, if_exists="replace")

        return cls(conn=conn)

    def query(self, sql: str) -> pd.DataFrame:
        sql_stripped = sql.strip().lower()
        if not sql_stripped.startswith("select"):
            raise ValueError("Only SELECT queries are allowed in this engine.")

        with self._lock:
            return pd.read_sql_query(sql, self.conn)
