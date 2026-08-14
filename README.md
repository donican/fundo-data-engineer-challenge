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

## Prove reconciliation catches real problems

```
make break-warehouse && make reconcile
```

`break-warehouse` intentionally corrupts the DuckDB warehouse (deletes a few transactions, points a few at a nonexistent card) without touching the source, so `reconcile` fails on purpose -- row-count parity and referential integrity, both reported as FAIL. Repair with `make full-load && make incremental-load`.

## Reset

```
make clean && rm -f data/warehouse.duckdb
```

---

Each step above is also available as its own `make` target (`init-db`, `seed-db`, `full-load`, `incremental-load`, `dedup`, `reconcile`, `simulate-activity`, etc.) -- see the `Makefile`.
