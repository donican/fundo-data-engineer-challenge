"""Applies SQL schema (DDL) scripts to the source (operational) database.

Not a migration framework by design -- just enough to keep local/dev setup
reproducible. Scripts are plain, idempotent .sql files under
sql/transaction_schema/schema/ (not its sibling seeds/ folder -- see
src/db/seed_database.py for that), applied in filename order. Safe to
re-run: every CREATE TABLE is guarded by IF OBJECT_ID(...) IS NULL, so
running this twice is a no-op the second time. Contains no data, so this is
also the entrypoint you'd point at a shared/staging/prod database to
bootstrap the schema there.
"""
from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from src.config import load_sqlserver_config
from src.db.sql_runner import apply_sql_dir

SCHEMA_DIR = Path(__file__).resolve().parent.parent.parent / "sql" / "transaction_schema" / "schema"


def main() -> int:
    config = load_sqlserver_config()
    engine = create_engine(config.sqlalchemy_url)
    try:
        applied = apply_sql_dir(engine, SCHEMA_DIR)
    except SQLAlchemyError as exc:
        print(f"[fail] schema apply failed: {exc}", file=sys.stderr)
        return 1

    if not applied:
        print(f"[fail] no .sql files found under {SCHEMA_DIR}", file=sys.stderr)
        return 1

    print(f"[ok] schema initialized ({len(applied)} script(s) applied)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
