import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from src.config import load_sqlserver_config
from src.db.sql_runner import apply_sql_dir

DEV_DIR = Path(__file__).resolve().parent.parent.parent / "sql" / "transaction_schema" / "dev"


def main() -> int:
    config = load_sqlserver_config()
    engine = create_engine(config.sqlalchemy_url)
    try:
        applied = apply_sql_dir(engine, DEV_DIR)
    except SQLAlchemyError as exc:
        print(f"[fail] activity simulation failed: {exc}", file=sys.stderr)
        return 1

    if not applied:
        print(f"[fail] no .sql files found under {DEV_DIR}", file=sys.stderr)
        return 1

    print(f"[ok] simulated activity ({len(applied)} script(s) applied)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
