# Architecture decision:

- I will use SQL Server as the operational database, since it better represents the proposed scenario and offers more compatibility for a possible migration to production.
- As the Data Warehouse, I will use DuckDB, since it's a columnar database with good similarity to Google BigQuery, the managed production service.

# Modeling decisions:


## Customers:
- Duplicate people: I will consider that what defines a person is their identity document, not email or phone number, which can be shared.
- I will treat the document as government_id, already normalized.
- Malformed emails and phones: I will deliberately disregard these cases to simplify the problem and address the project's main pain points. Emails and phones will still be available to help the decision-maker resolve duplicate cases that involve advances with an untouchable status.
- Columns: customer_id, first_name, last_name, email, phone, government_id, date_of_birth, address, created_at, updated_at.

## Advances:
- The funded and paid_off statuses are untouchable (they will not be merged before an analyst's review). I will consider one additional status, "canceled", touchable and included for completeness.
- Columns: id, customer_id, amount, status, created_at, updated_at.

## Cards:
- Cards duplicated due to duplicate people: if it involves protected advances, it must wait for analyst review. Otherwise, the merge will proceed automatically, based on recency.
- Columns: id, customer_id, card_number, status, created_at, updated_at.

## Transactions
- The largest table in the project. I will apply a simplified change-data-capture pattern (based on a timestamp column, not server-side metadata) only to this table, to keep the project simple. Every other table will be processed with the full-loader pattern. Depending on volume, this could reasonably be carried into production, since the number of customers, cards, and advances doesn't grow meaningfully over time. The only case that, in my view, needs immediate attention is the transactions table, which is already enough to satisfy the goal of the exercise and the problem statement.
- The prompt states that a transaction is rarely changed. I will treat a transaction as something that can only be created or updated, never deleted, and I'm designing for idempotency on that assumption. Given that, I will use the following columns: id, customer_id, card_id, item, value, occurred_at, created_at, updated_at.

## Version Table:
- I considered building an append-only version table for Advances, loaded with the incremental pattern based on created_at, so an internal audit process could easily check when something changed. For simplicity, and to prioritize getting the deduplication piece right first, I'm leaving this for a future iteration of the project.

## Scratch table: 
- I will deliberately skip this part of the problem, since it doesn't add business value.

## One bad schema choice: 
- government_id in customers should be unique (or at least carry some uniqueness guarantee), but I forced it to be a varchar with no uniqueness constraint, which allows duplicate cases to exist in the first place.

## Test data is excluded, not merged: 
- I will disregard this part of the project, since it's straightforward to add later. Right now I'm focused on what brings real value.

## Prove the data is correct:
- I will validate the warehouse with a reconciliation step that runs after every load and reports a clear PASS/FAIL, rather than relying on manual spot checks. Of everything that could be tested, I consider two checks essential:
- Row count parity between source and warehouse, table by table (SQL Server vs. DuckDB). This is the cheapest, most direct signal that a load actually completed: any full load or incremental run that silently dropped rows, timed out mid-batch, or missed a watermark window shows up immediately as a count mismatch.
Referential integrity inside the warehouse (orphan foreign keys). Since DuckDB is used here as a constraint-free analytical database, it enforces no real FKs. Nothing else verifies that every advances.customer_id, cards.customer_id, and transactions.customer_id/card_id actually points to an existing row. This matters even more given that cards and advances get reassigned between customers during merges: a mistake there is exactly the kind of issue that would otherwise stay invisible until a downstream query breaks.

## Recovering from a failure mid-run:
- Both loaders write through an explicit DuckDB transaction (commit/rollback), so a crash mid-write (after the destructive half of the statement -- TRUNCATE, or the DELETE half of the incremental upsert -- but before the compensating INSERT) leaves the target table exactly as it was, not half-truncated.
- The incremental loader's watermark is never stored in a separate state table; it's always MAX(updated_at) recomputed live from transactions itself. So if a run dies before committing, the watermark is unchanged, and the very next run -- no special repair path, just re-running the same command -- picks up the same delta and lands it correctly.
- I prototyped a test for this (monkeypatching the DuckDB connection to raise mid-transaction, then asserting the row count survives and a retry recovers), but the setup needed to fake a mid-transaction crash convincingly added more test complexity than it was worth for this exercise. Leaving it as a documented guarantee rather than an automated one.