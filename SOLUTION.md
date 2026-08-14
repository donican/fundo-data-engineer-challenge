# Summary for reviewers

Read this before the rest of the doc. Below is the design log this points back to.

## Solved / skipped
- Built: SQL Server schema + seed data, DuckDB warehouse, full-load (Customers/Advances/Cards), incremental/CDC (Transactions), dedup detection, reconciliation.
- Skipped dedup merge execution, only detection/classification. Getting the auto-merge vs. needs-review rule right was the actual hard part; executing the reassignment is mechanical once that decision exists.
- Skipped delete detection on Transactions, assumed create/update only, per the prompt. A timestamp watermark can't see a row that disappeared.
- Skipped a version table, a scratch table, excluding test data from merges, and an automated recovery test. Reasons for each are in the log below.
- Left government_id unconstrained on purpose (see Identity rules).

## Measured vs. estimated
- Measured: 5,000 customers / 2,000 advances / 6,000 cards / 100,000 transactions seeded; 100 duplicate-document groups (4,900 distinct); 1,000 multi-card customers; incremental load moved 1,000 rows in 0.070s vs. a full reload moving 100,500 rows in 1.682s (24.1x faster, 0.995% of the volume); reconcile correctly caught an injected row-count mismatch and 5 orphan rows.
- Estimated: everything about cost, and whether that 24x ratio holds at production scale. No real infrastructure was billed here, this is projection.

## Per-table strategy
- Full-load: Customers, Advances, Cards. They don't grow meaningfully, so a full reload is cheap and always a perfect mirror.
- Incremental/CDC: Transactions. Largest and fastest-growing table, so cost should track activity, not the whole table's history.

## Cost impact (estimated)
- Full-load cost scales with table size; incremental scales with the delta. Transactions is the one table where that gap actually matters, hence the one table with CDC.
- Storage cost doesn't change with load strategy, only with total data volume.
- Reconciliation adds a small, flat cost per run, cheap insurance against a silent bad load.

## Identity rules
- Proves identity: government_id. Only signal used to merge customers.
- Only suggests identity: email/phone, can be shared, so never used to merge, just shown to the analyst on a needs_review case.
- Malformed contacts: not validated or cleaned. Doesn't matter for correctness since they're never used to match.
- Funded customers: 0 protected advances -> auto-merge by recency; 1 protected -> auto-merge, the protected one survives; 2+ protected -> needs_review.
- Cards follow the customer decision, move with the survivor, wait if blocked. Only the decision is implemented, not the reassignment.
- Test data: no is_test flag anywhere. Everything is treated as real.

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
- Both loaders write through an explicit DuckDB transaction (commit/rollback), so a crash mid-write (after the destructive half of the statement because of a TRUNCATE, or the DELETE half of the incremental upsert but before the compensating INSERT) leaves the target table exactly as it was, not half-truncated.
- The incremental loader's watermark is never stored in a separate state table; it's always MAX(updated_at) recomputed live from transactions itself. So if a run dies before committing, the watermark is unchanged, and the very next run (no special repair path, just re-running the same command) picks up the same delta and lands it correctly.
- I prototyped a test for this (monkeypatching the DuckDB connection to raise mid-transaction, then asserting the row count survives and a retry recovers), but the setup needed to fake a mid-transaction crash convincingly added more test complexity than it was worth for this exercise. Leaving it as a documented guarantee rather than an automated one.


## AI usage:
- All decisions in this project, architecture, modeling, scope cuts, the identity rules, were mine.
- I used AI only for manual, reviewed processes: implementing code and SQL from decisions I had already made, drafting and trimming text once I'd decided what it should say, and fixing bugs I pointed it at. Nothing here reflects an AI-made judgment call, and everything it produced was reviewed and tested by me before I accepted it.
