.PHONY: run up down build logs ps sh test init-db seed-db init-warehouse full-load incremental-load dedup simulate-activity reconcile break-warehouse benchmark clean

# One-command entry point: builds, starts the infra, sets up both
# databases, loads everything, and reconciles. Safe to re-run any time
# -- every step it chains is idempotent.
run: build up init-db seed-db init-warehouse full-load incremental-load dedup reconcile

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

ps:
	docker compose ps

sh:
	docker compose exec pipeline bash

test:
	docker compose exec pipeline pytest

init-db:
	docker compose exec pipeline python -m src.db.apply_schema

seed-db:
	docker compose exec pipeline python -m src.db.seed_database

init-warehouse:
	docker compose exec pipeline python -m src.db.apply_warehouse_schema

full-load:
	docker compose exec pipeline python -m src.etl.full_loader

incremental-load:
	docker compose exec pipeline python -m src.etl.incremental_loader

dedup:
	docker compose exec pipeline python -m src.dedup.detect_duplicates

simulate-activity:
	docker compose exec pipeline python -m src.db.simulate_activity

reconcile:
	docker compose exec pipeline python -m src.reconciliation.reconcile

break-warehouse:
	docker compose exec pipeline python -m src.db.break_warehouse

benchmark: simulate-activity
	docker compose exec pipeline python -m src.etl.benchmark

clean:
	docker compose down -v
