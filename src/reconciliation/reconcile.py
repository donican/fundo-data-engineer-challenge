import sys

import duckdb
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.config import load_duckdb_path, load_sqlserver_config

# (source_table, target_table) -- source is dbo.<source_table> in SQL
# Server, target is <target_table> (lowercased, dbo. dropped) in DuckDB.
ROW_COUNT_TABLES = [
    ("Customers", "customers"),
    ("Advances", "advances"),
    ("Cards", "cards"),
    ("Transactions", "transactions"),
]

# (description, query) -- query returns the count of orphaned rows in
# the warehouse; a PASS is exactly 0.
REFERENTIAL_CHECKS = [
    (
        "advances.customer_id -> customers.customer_id",
        """
        SELECT COUNT(*) FROM advances a
        LEFT JOIN customers c ON c.customer_id = a.customer_id
        WHERE c.customer_id IS NULL
        """,
    ),
    (
        "cards.customer_id -> customers.customer_id",
        """
        SELECT COUNT(*) FROM cards ca
        LEFT JOIN customers c ON c.customer_id = ca.customer_id
        WHERE c.customer_id IS NULL
        """,
    ),
    (
        "transactions.customer_id -> customers.customer_id",
        """
        SELECT COUNT(*) FROM transactions t
        LEFT JOIN customers c ON c.customer_id = t.customer_id
        WHERE c.customer_id IS NULL
        """,
    ),
    (
        "transactions.card_id -> cards.card_id",
        """
        SELECT COUNT(*) FROM transactions t
        LEFT JOIN cards ca ON ca.card_id = t.card_id
        WHERE ca.card_id IS NULL
        """,
    ),
]


def check_row_counts(source_engine: Engine, duckdb_con: duckdb.DuckDBPyConnection) -> list[dict]:
    """Returns one result dict per table: {table, source_count,
    target_count, passed}.
    """
    results = []
    with source_engine.connect() as conn:
        for source_table, target_table in ROW_COUNT_TABLES:
            source_count = conn.execute(text(f"SELECT COUNT(*) FROM dbo.{source_table}")).scalar()
            target_count = duckdb_con.execute(f"SELECT COUNT(*) FROM {target_table}").fetchone()[0]
            results.append(
                {
                    "table": target_table,
                    "source_count": source_count,
                    "target_count": target_count,
                    "passed": source_count == target_count,
                }
            )
    return results


def check_referential_integrity(duckdb_con: duckdb.DuckDBPyConnection) -> list[dict]:
    """Returns one result dict per check: {description, orphan_count,
    passed}.
    """
    results = []
    for description, query in REFERENTIAL_CHECKS:
        orphan_count = duckdb_con.execute(query).fetchone()[0]
        results.append(
            {
                "description": description,
                "orphan_count": orphan_count,
                "passed": orphan_count == 0,
            }
        )
    return results


def _print_report(row_count_results: list[dict], referential_results: list[dict]) -> bool:
    """Prints the PASS/FAIL report to stdout. Returns True iff every
    check passed.
    """
    all_passed = True

    print("=== Row count parity (SQL Server vs DuckDB) ===")
    for r in row_count_results:
        all_passed = all_passed and r["passed"]
        status = "PASS" if r["passed"] else "FAIL"
        print(f"[{status}] {r['table']}: source={r['source_count']} target={r['target_count']}")

    print()
    print("=== Referential integrity (warehouse) ===")
    for r in referential_results:
        all_passed = all_passed and r["passed"]
        status = "PASS" if r["passed"] else "FAIL"
        print(f"[{status}] {r['description']}: {r['orphan_count']} orphan row(s)")

    print()
    print(f"=== Overall: {'PASS' if all_passed else 'FAIL'} ===")
    return all_passed


def main() -> int:
    sqlserver_config = load_sqlserver_config()
    source_engine = create_engine(sqlserver_config.sqlalchemy_url)
    duckdb_con = duckdb.connect(load_duckdb_path(), read_only=True)

    try:
        row_count_results = check_row_counts(source_engine, duckdb_con)
        referential_results = check_referential_integrity(duckdb_con)
    finally:
        duckdb_con.close()

    passed = _print_report(row_count_results, referential_results)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
