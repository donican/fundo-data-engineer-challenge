# fundo-data-engineer-challenge

ETL pipeline moving data from an operational database (SQL Server) into an analytical warehouse (DuckDB), with customer/card deduplication and a reconciliation step. Design decisions and trade-offs are in [SOLUTION.md](./SOLUTION.md).

Requires Docker, Docker Compose, and `make`.

## Run

```
cp .env.example .env
make run
```

`.env` holds the SQL Server credentials and paths Docker Compose reads (`SQLSERVER_PASSWORD` has no default, so this step is required, not optional). The example values work out of the box; edit them if you want different ones. `make run` builds the images, starts the infra, sets up both databases, loads everything (full-load + incremental/CDC), runs deduplication, and reconciles the warehouse against the source. Safe to re-run any time.

## Test

```
make test
```

Validates the operational database has the expected shape (row counts, duplicate documents, multi-card customers, advance status mix) and that the warehouse matches it after a load. Skips instead of failing if a database isn't reachable yet.

## Benchmark (incremental vs. full load)

```
make benchmark
```

Seeds a fresh batch of transaction activity, then times an incremental load against a full reload of the same table.

## Prove reconciliation catches real problems

```
make break-warehouse && make reconcile
```

`break-warehouse` intentionally corrupts the DuckDB warehouse (deletes a few transactions, points a few at a nonexistent card) without touching the source, so `reconcile` fails on purpose, both row-count parity and referential integrity reported as FAIL.

`make full-load && make incremental-load` will NOT repair this: full-load skips Transactions by design (see src/etl/full_loader.py), and the incremental loader only pulls rows at or past its watermark, so it can't see rows corrupted below that point. Repair by resetting the warehouse file and forcing a full bootstrap:

```
rm -f data/warehouse.duckdb
make init-warehouse
make full-load
make incremental-load
make reconcile
```

## Reset

```
make clean && rm -f data/warehouse.duckdb
```

---

Each step above is also available as its own `make` target (`init-db`, `seed-db`, `full-load`, `incremental-load`, `dedup`, `reconcile`, `simulate-activity`, etc.), see the `Makefile`.
