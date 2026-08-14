from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Engine


def apply_sql_dir(engine: Engine, sql_dir: Path) -> list[str]:
    applied: list[str] = []
    for sql_file in sorted(sql_dir.glob("*.sql")):
        sql_text = sql_file.read_text()
        with engine.begin() as conn:
            conn.execute(text(sql_text))
        applied.append(sql_file.name)
        print(f"[ok] applied {sql_file.name}")
    return applied
