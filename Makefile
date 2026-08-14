.PHONY: up down build logs ps sh test init-db seed-db init-warehouse full-load dedup clean

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

dedup:
	docker compose exec pipeline python -m src.dedup.detect_duplicates

clean:
	docker compose down -v
