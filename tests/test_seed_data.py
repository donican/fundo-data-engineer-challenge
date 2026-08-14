import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from src.config import load_sqlserver_config


@pytest.fixture(scope="module")
def engine() -> Engine:
    config = load_sqlserver_config()
    eng = create_engine(config.sqlalchemy_url)
    try:
        with eng.connect():
            pass
    except SQLAlchemyError as exc:
        pytest.skip(f"operational database not reachable: {exc}")
    return eng


def _scalar(engine: Engine, query: str):
    with engine.connect() as conn:
        return conn.execute(text(query)).scalar()


def test_row_counts(engine: Engine) -> None:
    assert _scalar(engine, "SELECT COUNT(*) FROM dbo.Customers") == 5000
    assert _scalar(engine, "SELECT COUNT(*) FROM dbo.Advances") == 2000
    assert _scalar(engine, "SELECT COUNT(*) FROM dbo.Cards") == 6000
    assert _scalar(engine, "SELECT COUNT(*) FROM dbo.Transactions") >= 100000


def test_customers_have_duplicate_documents(engine: Engine) -> None:
    distinct_docs = _scalar(engine, "SELECT COUNT(DISTINCT government_id) FROM dbo.Customers")
    duplicate_groups = _scalar(
        engine,
        """
        SELECT COUNT(*) FROM (
            SELECT government_id
            FROM dbo.Customers
            GROUP BY government_id
            HAVING COUNT(*) > 1
        ) AS dupes
        """,
    )
    assert distinct_docs == 4900
    assert duplicate_groups == 100


def test_customers_with_multiple_cards(engine: Engine) -> None:
    """Customers 1-1000 get a second card (seeds/003_cards.sql)."""
    multi_card_customers = _scalar(
        engine,
        """
        SELECT COUNT(*) FROM (
            SELECT customer_id
            FROM dbo.Cards
            GROUP BY customer_id
            HAVING COUNT(*) > 1
        ) AS multi
        """,
    )
    assert multi_card_customers == 1000


def test_advances_status_distribution(engine: Engine) -> None:
    """funded/paid_off (untouchable) and canceled (touchable) must all be
    present -- see SOLUTION.md -- with funded+paid_off as the majority.
    """
    with engine.connect() as conn:
        counts = dict(
            conn.execute(text("SELECT status, COUNT(*) FROM dbo.Advances GROUP BY status")).all()
        )
    assert counts.get("funded", 0) > 0
    assert counts.get("paid_off", 0) > 0
    assert counts.get("canceled", 0) > 0
    protected = counts.get("funded", 0) + counts.get("paid_off", 0)
    assert protected > counts.get("canceled", 0)


def test_transactions_have_simulated_updates(engine: Engine) -> None:
    updated_after_created = _scalar(
        engine,
        "SELECT COUNT(*) FROM dbo.Transactions WHERE updated_at > created_at",
    )
    assert updated_after_created >= 200


def test_transaction_customer_matches_card_owner(engine: Engine) -> None:
    mismatches = _scalar(
        engine,
        """
        SELECT COUNT(*)
        FROM dbo.Transactions t
        JOIN dbo.Cards c ON c.card_id = t.card_id
        WHERE t.customer_id <> c.customer_id
        """,
    )
    assert mismatches == 0
