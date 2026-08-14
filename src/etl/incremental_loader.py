import sys
import time

import duckdb
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.config import load_duckdb_path, load_sqlserver_config


def incremental_load_transactions(source_engine: Engine, duckdb_con: duckdb.DuckDBPyConnection) -> int:
    watermark = duckdb_con.execute("SELECT MAX(updated_at) FROM transactions").fetchone()[0]

    if watermark is None:
        df = pd.read_sql("SELECT * FROM dbo.Transactions", source_engine)
    else:
        df = pd.read_sql(
            text("SELECT * FROM dbo.Transactions WHERE updated_at >= :watermark"),
            source_engine,
            params={"watermark": watermark},
        )

    if df.empty:
        return 0

    duckdb_con.begin()
    try:
        duckdb_con.execute("DELETE FROM transactions WHERE transaction_id IN (SELECT transaction_id FROM df)")
        duckdb_con.execute("INSERT INTO transactions SELECT * FROM df")
        duckdb_con.commit()
    except Exception:
        duckdb_con.rollback()
        raise

    return len(df)


def main() -> int:
    sqlserver_config = load_sqlserver_config()
    source_engine = create_engine(sqlserver_config.sqlalchemy_url)
    duckdb_con = duckdb.connect(load_duckdb_path())

    start = time.perf_counter()
    try:
        row_count = incremental_load_transactions(source_engine, duckdb_con)
    except Exception as exc:
        print(f"[fail] incremental load of transactions failed: {exc}", file=sys.stderr)
        return 1
    finally:
        duckdb_con.close()

    elapsed = time.perf_counter() - start
    print(f"[ok] upserted {row_count} row(s) into transactions ({elapsed:.2f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
