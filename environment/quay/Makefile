# Makefile for Quay Registry

.PHONY: help install init-user logs restart uninstall

help:
	@echo "Available commands:"
	@echo "  make install      - Start Quay Registry using Docker Compose"
	@echo "  make logs         - Show live logs from Quay container"
	@echo "  make restart      - Restart Quay container"
	@echo "  make uninstall    - Stop and remove all Quay containers"

install:
	docker compose up -d

logs:
	docker compose logs -f quay-quay-app-1

restart:
	docker restart quay-quay-app-1

uninstall:
	docker compose down -v

status:
	docker compose ps

shell:
	docker exec -it quay-quay-app-1 /bin/bash

db-shell:
	docker exec -it quay-quay-pg-db-1 psql -U quay -d quay

rebuild:
	docker compose down -v
	docker compose build --no-cache
	docker compose up -d

clean-logs:
	docker compose logs --no-color > quay_logs.txt
	@echo "Logs saved to quay_logs.txt"

inspect-config:
	docker exec -it quay-quay-app-1 cat /conf/stack/config.yaml | less