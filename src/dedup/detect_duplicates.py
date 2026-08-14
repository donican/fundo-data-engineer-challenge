import sys
from itertools import groupby
from operator import itemgetter

import duckdb

from src.config import load_duckdb_path


def detect_duplicate_groups(con: duckdb.DuckDBPyConnection) -> int:
    rows = con.execute(
        """
        SELECT
            c.government_id,
            c.customer_id,
            c.updated_at,
            c.created_at,
            EXISTS (
                SELECT 1 FROM advances a
                WHERE a.customer_id = c.customer_id
                  AND a.status IN ('funded', 'paid_off')
            ) AS is_protected
        FROM customers c
        WHERE c.government_id IN (
            SELECT government_id FROM customers
            WHERE government_id IS NOT NULL
            GROUP BY government_id
            HAVING COUNT(*) > 1
        )
        ORDER BY c.government_id, c.customer_id
        """
    ).fetchall()

    con.begin()
    try:
        con.execute("TRUNCATE dedup_groups")
        con.execute("TRUNCATE dedup_group_members")

        group_id = 0
        for _government_id, members_iter in groupby(rows, key=itemgetter(0)):
            group_id += 1
            # each member: (government_id, customer_id, updated_at, created_at, is_protected)
            members = list(members_iter)
            protected = [m for m in members if m[4]]
            member_count = len(members)
            protected_member_count = len(protected)

            if protected_member_count == 0:
                survivor_row = max(members, key=lambda m: (m[2], m[3], m[1]))
                survivor_customer_id = survivor_row[1]
                status = "merged"
                reason = "no member has a protected advance; survivor chosen by most recent customer update"
            elif protected_member_count == 1:
                survivor_customer_id = protected[0][1]
                status = "merged"
                reason = "exactly one member has a protected advance (funded/paid_off); it survives automatically"
            else:
                survivor_customer_id = None
                status = "needs_review"
                reason = f"{protected_member_count} members have a protected advance; requires analyst review"

            con.execute(
                """
                INSERT INTO dedup_groups (
                    group_id, evidence_type, status, survivor_customer_id,
                    reason, member_count, protected_member_count, decided_at
                ) VALUES (?, 'government_id', ?, ?, ?, ?, ?, now())
                """,
                [group_id, status, survivor_customer_id, reason, member_count, protected_member_count],
            )

            for _gov_id, customer_id, _updated_at, _created_at, is_protected in members:
                con.execute(
                    """
                    INSERT INTO dedup_group_members (group_id, customer_id, is_protected, is_survivor)
                    VALUES (?, ?, ?, ?)
                    """,
                    [group_id, customer_id, is_protected, customer_id == survivor_customer_id],
                )

        con.commit()
    except Exception:
        con.rollback()
        raise

    return group_id


def main() -> int:
    con = duckdb.connect(load_duckdb_path())
    try:
        group_count = detect_duplicate_groups(con)
    except Exception as exc:
        print(f"[fail] dedup detection failed: {exc}", file=sys.stderr)
        return 1
    finally:
        con.close()

    print(f"[ok] detected {group_count} duplicate group(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
