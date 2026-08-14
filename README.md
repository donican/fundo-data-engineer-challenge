# fundo-data-engineer-challenge

ETL pipeline moving data from an operational database (SQL Server) into an analytical warehouse (DuckDB), with customer/card deduplication and a reconciliation step. Design decisions and trade-offs are in [SOLUTION.md](./SOLUTION.md).

Requires Docker, Docker Compose, and `make`.

## Run

```
make run
```

Builds the images, starts the infra, sets up both databases, loads everything (full-load + incremental/CDC), runs deduplication, and reconciles the warehouse against the source. Safe to re-run any time.

## Test

```
make test
```

## Benchmark (incremental vs. full load)

```
make benchmark
```

Seeds a fresh batch of transaction activity, then times an incremental load against a full reload of the same table.

## Reset

```
make clean && rm -f data/warehouse.duckdb
```

---

Each step above is also available as its own `make` target (`init-db`, `seed-db`, `full-load`, `incremental-load`, `dedup`, `reconcile`, `simulate-activity`, `break-warehouse` to test the reconciliation FAIL path, etc.) — see the `Makefile`.
