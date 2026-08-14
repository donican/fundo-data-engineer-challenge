"""Loads synthetic seed data into the source (operational) database.

Dev/test only -- unlike src/db/apply_schema.py, this inserts fake rows and
should never be pointed at a shared/staging/prod database. Scripts are
plain, idempotent .sql files under sql/transaction_schema/seeds/ (sibling
of the schema/ folder -- see src/db/apply_schema.py for that), applied in
filename order. Safe to re-run: every seed script is guarded by
IF NOT EXISTS (SELECT 1 FROM ...), so running this twice is a no-op the
second time.
"""
from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from src.config import load_sqlserver_config
from src.db.sql_runner import apply_sql_dir

SEEDS_DIR = Path(__file__).resolve().parent.parent.parent / "sql" / "transaction_schema" / "seeds"


def main() -> int:
    config = load_sqlserver_config()
    engine = create_engine(config.sqlalchemy_url)
    try:
        applied = apply_sql_dir(engine, SEEDS_DIR)
    except SQLAlchemyError as exc:
        print(f"[fail] seed load failed: {exc}", file=sys.stderr)
        return 1

    if not applied:
        print(f"[fail] no .sql files found under {SEEDS_DIR}", file=sys.stderr)
        return 1

    print(f"[ok] seed data loaded ({len(applied)} script(s) applied)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
