"""Smoke tests for the full-loader ETL (src/etl/full_loader.py). Confirms
data actually landed in the DuckDB warehouse after a load -- not a
substitute for the reconciliation step described in SOLUTION.md (which
will run after every load in production), just a dev-time check that the
four tables have the right row counts and a couple of consistency
spot-checks survived the trip from SQL Server.

Requires the warehouse file to already exist and be loaded:
make init-warehouse && make full-load
before `make test`. Skips instead of failing if the file isn't reachable.
"""
from __future__ import annotations

import duckdb
import pytest

from src.config import load_duckdb_path


@pytest.fixture(scope="module")
def con() -> duckdb.DuckDBPyConnection:
    path = load_duckdb_path()
    try:
        connection = duckdb.connect(path, read_only=True)
        connection.execute("SELECT 1")
    except Exception as exc:
        pytest.skip(f"DuckDB warehouse not reachable at {path}: {exc}")
    return connection


def _scalar(con: duckdb.DuckDBPyConnection, query: str):
    return con.execute(query).fetchone()[0]


def test_row_counts_match_operational_volumetria(con: duckdb.DuckDBPyConnection) -> None:
    assert _scalar(con, "SELECT COUNT(*) FROM customers") == 5000
    assert _scalar(con, "SELECT COUNT(*) FROM advances") == 2000
    assert _scalar(con, "SELECT COUNT(*) FROM cards") == 6000
    assert _scalar(con, "SELECT COUNT(*) FROM transactions") == 100000


def test_customers_duplicate_documents_survived_the_load(con: duckdb.DuckDBPyConnection) -> None:
    """Same check as tests/test_seed_data.py, but against the warehouse
    copy -- confirms the full loader didn't silently drop or dedupe rows
    in transit (it isn't supposed to; dedup logic doesn't exist yet).
    """
    distinct_docs = _scalar(con, "SELECT COUNT(DISTINCT government_id) FROM customers")
    duplicate_groups = _scalar(
        con,
        """
        SELECT COUNT(*) FROM (
            SELECT government_id FROM customers GROUP BY government_id HAVING COUNT(*) > 1
        ) AS dupes
        """,
    )
    assert distinct_docs == 4900
    assert duplicate_groups == 100


def test_transactions_customer_matches_card_owner(con: duckdb.DuckDBPyConnection) -> None:
    mismatches = _scalar(
        con,
        """
        SELECT COUNT(*)
        FROM transactions t
        JOIN cards c ON c.card_id = t.card_id
        WHERE t.customer_id <> c.customer_id
        """,
    )
    assert mismatches == 0
