.PHONY: up down build logs ps sh test init-db seed-db init-warehouse full-load incremental-load dedup simulate-activity reconcile clean

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

clean:
	docker compose down -v
