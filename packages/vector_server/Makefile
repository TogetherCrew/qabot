# Makefile for running Docker Compose commands with conditional -f option

# Default Docker Compose file
COMPOSE_FILE = docker-compose.dev.yml

# Check if the 'prod' option is set
ifdef prod
    COMPOSE_FILE = docker-compose.yml
endif

# Default service name
SERVICE = vector_api_dev

# Check if the 'service' option is set
ifdef service
    SERVICE = $(service)
endif

# Default target (when you run just "make" without specifying a target)
default: up

# Target to start the specified service using Docker Compose
up:
	docker compose -f $(COMPOSE_FILE) up -d $(SERVICE)

# Target to view the logs of the specified service using Docker Compose
logs-full:
	docker compose -f $(COMPOSE_FILE) logs $(SERVICE) -f

logs:
	docker compose -f $(COMPOSE_FILE) logs $(SERVICE) -f -n 50 -t

# Target to stop and remove the specified service using Docker Compose
down:
	docker compose -f $(COMPOSE_FILE) down $(SERVICE)

# Target to stop the specified service using Docker Compose (without removing it)
stop:
	docker compose -f $(COMPOSE_FILE) stop $(SERVICE)

# Target to restart the specified service using Docker Compose
restart:
	docker compose -f $(COMPOSE_FILE) restart $(SERVICE)

# Target to rebuild the specified service using Docker Compose
build:
	docker compose -f $(COMPOSE_FILE) up -d --build $(SERVICE)

# Target to show help message (list available targets)
help:
	@echo "Available targets:"
	@echo "  up       - Start the specified service using Docker Compose"
	@echo "  logs     - View the logs of the specified service using Docker Compose"
	@echo "  down     - Stop and remove the specified service using Docker Compose"
	@echo "  stop     - Stop the specified service using Docker Compose (without removing it)"
	@echo "  restart  - Restart the specified service using Docker Compose"
	@echo "  build    - Rebuild the specified service using Docker Compose"
	@echo "  help     - Show this help message"

.PHONY: up logs down stop restart build help
