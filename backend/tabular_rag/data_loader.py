from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import pandas as pd


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@dataclass
class DataContext:
    """
    In-memory representation of all business tables.
    """
    clients: pd.DataFrame
    invoices: pd.DataFrame
    line_items: pd.DataFrame

    def __post_init__(self):
        # Ensure dates are parsed correctly
        if not pd.api.types.is_datetime64_any_dtype(self.invoices["invoice_date"]):
            self.invoices["invoice_date"] = pd.to_datetime(self.invoices["invoice_date"])
        if not pd.api.types.is_datetime64_any_dtype(self.invoices["due_date"]):
            self.invoices["due_date"] = pd.to_datetime(self.invoices["due_date"])


_data_cache: DataContext | None = None


def load_data(refresh: bool = False) -> DataContext:
    """
    Load all Excel tables into memory (with simple caching).

    Parameters
    ----------
    refresh : bool
        If True, forces re-reading from disk.

    Returns
    -------
    DataContext
        Object holding clients, invoices, and line_items DataFrames.
    """
    global _data_cache
    if _data_cache is not None and not refresh:
        return _data_cache

    clients_path = DATA_DIR / "Clients.xlsx"
    invoices_path = DATA_DIR / "Invoices.xlsx"
    line_items_path = DATA_DIR / "InvoiceLineItems.xlsx"

    if not clients_path.exists() or not invoices_path.exists() or not line_items_path.exists():
        raise FileNotFoundError(
            f"Expected Excel files in {DATA_DIR}, but one or more are missing. "
            "Make sure Clients.xlsx, Invoices.xlsx and InvoiceLineItems.xlsx are there."
        )

    clients = pd.read_excel(clients_path)
    invoices = pd.read_excel(invoices_path)
    line_items = pd.read_excel(line_items_path)

    _data_cache = DataContext(
        clients=clients,
        invoices=invoices,
        line_items=line_items,
    )
    return _data_cache
