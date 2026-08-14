"""Full-loader ETL: copies whole tables from the operational SQL Server
database into the DuckDB warehouse, replacing all rows in each target
table on every run.

Per SOLUTION.md, full-load is the pattern for Customers, Advances, and
Cards -- tables that don't grow enough to justify anything more complex.

Transactions is NOT in this list. It used to be, as a way to bootstrap
the warehouse before the incremental/CDC loader existed -- now that
src/etl/incremental_loader.py exists, Transactions goes through that
instead, watermarked on updated_at, so it doesn't get fully reloaded
(and doesn't need to be) on every run.

Requires the warehouse schema to already exist -- run
src/db/apply_warehouse_schema.py (make init-warehouse) first. Loading
into a pre-existing, explicitly-typed table (sql/warehouse_schema/) means
every load is cast into those declared types, rather than each run
silently redefining the schema from whatever pandas happens to infer.

Table names are lowercased and the `dbo.` prefix is dropped going into
DuckDB (Customers -> customers, etc.) to match the target warehouse's
BigQuery-style naming.

Each table's load is timed (read from SQL Server + truncate + insert into
DuckDB) and printed alongside the row count, plus a total across all
tables.
"""
from __future__ import annotations

import sys
import time

import duckdb
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from src.config import load_duckdb_path, load_sqlserver_config

TABLES = ["Customers", "Advances", "Cards"]


def full_load_table(source_engine: Engine, duckdb_con: duckdb.DuckDBPyConnection, table: str) -> int:
    df = pd.read_sql(f"SELECT * FROM dbo.{table}", source_engine)
    target = table.lower()

    duckdb_con.begin()
    try:
        duckdb_con.execute(f"TRUNCATE {target}")
        # DuckDB's Python API scans the local `df` variable directly
        # (zero-copy, via its replacement-scan mechanism); INSERT INTO
        # casts each column into the target's declared types.
        duckdb_con.execute(f"INSERT INTO {target} SELECT * FROM df")
        duckdb_con.commit()
    except Exception:
        duckdb_con.rollback()
        raise

    return len(df)


def main() -> int:
    sqlserver_config = load_sqlserver_config()
    source_engine = create_engine(sqlserver_config.sqlalchemy_url)
    duckdb_con = duckdb.connect(load_duckdb_path())

    total_start = time.perf_counter()
    try:
        for table in TABLES:
            table_start = time.perf_counter()
            try:
                row_count = full_load_table(source_engine, duckdb_con, table)
            except Exception as exc:
                print(f"[fail] full load of {table} failed: {exc}", file=sys.stderr)
                return 1
            elapsed = time.perf_counter() - table_start
            print(f"[ok] loaded {row_count} row(s) into {table.lower()} ({elapsed:.2f}s)")
    finally:
        duckdb_con.close()

    total_elapsed = time.perf_counter() - total_start
    print(f"[ok] full load complete ({len(TABLES)} table(s), {total_elapsed:.2f}s total)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
