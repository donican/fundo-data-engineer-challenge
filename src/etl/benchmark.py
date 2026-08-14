import sys
import time

import duckdb
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from src.config import load_duckdb_path, load_sqlserver_config
from src.etl.full_loader import full_load_table
from src.etl.incremental_loader import incremental_load_transactions


def _timed(fn, *args) -> tuple[int, float]:
    start = time.perf_counter()
    row_count = fn(*args)
    elapsed = time.perf_counter() - start
    return row_count, elapsed


def main() -> int:
    sqlserver_config = load_sqlserver_config()
    source_engine: Engine = create_engine(sqlserver_config.sqlalchemy_url)
    duckdb_con = duckdb.connect(load_duckdb_path())

    try:
        incremental_rows, incremental_elapsed = _timed(incremental_load_transactions, source_engine, duckdb_con)
        full_rows, full_elapsed = _timed(full_load_table, source_engine, duckdb_con, "Transactions")
    finally:
        duckdb_con.close()

    print("=== Incremental load (delta only) ===")
    print(f"{incremental_rows} row(s) in {incremental_elapsed:.3f}s")
    if incremental_rows == 0:
        print("(no delta since the last run -- try `make simulate-activity` first for a non-trivial comparison)")

    print()
    print("=== Full load (entire table) ===")
    print(f"{full_rows} row(s) in {full_elapsed:.3f}s")

    print()
    print("=== Comparison ===")
    if incremental_elapsed > 0:
        speedup = full_elapsed / incremental_elapsed
        print(f"Incremental was {speedup:.1f}x faster in wall-clock time.")
    else:
        print("Incremental finished too fast to measure a meaningful ratio (essentially instant).")
    if full_rows > 0:
        pct = (incremental_rows / full_rows) * 100
        print(f"Incremental moved {incremental_rows} row(s) -- {pct:.3f}% of the {full_rows} a full reload moves every single time.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
