.PHONY: up down build logs ps sh test clean

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

clean:
	docker compose down -v
