import argparse
import sys

import duckdb

from src.config import load_duckdb_path


def break_row_count(con: duckdb.DuckDBPyConnection, n: int) -> int:
    ids = [row[0] for row in con.execute(f"SELECT transaction_id FROM transactions LIMIT {n}").fetchall()]
    if not ids:
        return 0
    placeholders = ", ".join("?" * len(ids))
    con.execute(f"DELETE FROM transactions WHERE transaction_id IN ({placeholders})", ids)
    return len(ids)


def break_referential_integrity(con: duckdb.DuckDBPyConnection, n: int) -> int:
    fake_card_id = con.execute("SELECT COALESCE(MAX(card_id), 0) + 1000000 FROM cards").fetchone()[0]
    ids = [row[0] for row in con.execute(f"SELECT transaction_id FROM transactions LIMIT {n}").fetchall()]
    if not ids:
        return 0
    placeholders = ", ".join("?" * len(ids))
    con.execute(
        f"UPDATE transactions SET card_id = ? WHERE transaction_id IN ({placeholders})",
        [fake_card_id, *ids],
    )
    return len(ids)


def main() -> int:
    parser = argparse.ArgumentParser(description="Intentionally corrupt the DuckDB warehouse for testing reconcile.py.")
    parser.add_argument("--row-count", action="store_true", help="break row-count parity (delete rows from DuckDB only)")
    parser.add_argument("--orphan", action="store_true", help="break referential integrity (point transactions at a nonexistent card)")
    parser.add_argument("-n", type=int, default=5, help="how many rows to affect per corruption (default: 5)")
    args = parser.parse_args()

    run_row_count = args.row_count or not (args.row_count or args.orphan)
    run_orphan = args.orphan or not (args.row_count or args.orphan)

    con = duckdb.connect(load_duckdb_path())
    try:
        if run_row_count:
            deleted = break_row_count(con, args.n)
            print(f"[broken] deleted {deleted} row(s) from transactions (DuckDB only) -- row-count parity should now FAIL")
        if run_orphan:
            orphaned = break_referential_integrity(con, args.n)
            print(f"[broken] pointed {orphaned} transaction(s) at a nonexistent card_id -- referential integrity should now FAIL")
    finally:
        con.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
