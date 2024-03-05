COMPOSE_DEV := docker compose -f docker-compose.yml

start:
	python src/tgbot/main.py

up:
	$(COMPOSE_DEV) up -d --build
stop:
	$(COMPOSE_DEV) stop
down:
	$(COMPOSE_DEV) down -v
restart:
	$(COMPOSE_DEV) up -d --build bot
