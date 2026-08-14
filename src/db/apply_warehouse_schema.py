import sys
from pathlib import Path

import duckdb

from src.config import load_duckdb_path

SCHEMA_DIR = Path(__file__).resolve().parent.parent.parent / "sql" / "warehouse_schema"


def apply_warehouse_schema(con: duckdb.DuckDBPyConnection, schema_dir: Path = SCHEMA_DIR) -> list[str]:
    """Execute every .sql file in schema_dir, in filename order."""
    applied: list[str] = []
    for sql_file in sorted(schema_dir.glob("*.sql")):
        con.execute(sql_file.read_text())
        applied.append(sql_file.name)
        print(f"[ok] applied {sql_file.name}")
    return applied


def main() -> int:
    con = duckdb.connect(load_duckdb_path())
    try:
        applied = apply_warehouse_schema(con)
    except Exception as exc:
        print(f"[fail] warehouse schema apply failed: {exc}", file=sys.stderr)
        return 1
    finally:
        con.close()

    if not applied:
        print(f"[fail] no .sql files found under {SCHEMA_DIR}", file=sys.stderr)
        return 1

    print(f"[ok] warehouse schema initialized ({len(applied)} script(s) applied)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
