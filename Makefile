.PHONY: help build run stop clean test lint format install-dev

help:
	@echo "Available commands:"
	@echo "  build      - Build Docker image"
	@echo "  run        - Run honeypot with Docker Compose"
	@echo "  stop       - Stop honeypot"
	@echo "  clean      - Clean up containers and volumes"
	@echo "  test       - Run tests"
	@echo "  lint       - Run linting"
	@echo "  format     - Format code"
	@echo "  install-dev - Install development dependencies"

build:
	docker-compose build

run:
	docker-compose up -d

stop:
	docker-compose down

clean:
	docker-compose down -v
	docker system prune -f

test:
	python -m pytest tests/ -v

lint:
	flake8 src/
	mypy src/

format:
	black src/ tests/
	isort src/ tests/

install-dev:
	pip install -r requirements-dev.txt

logs:
	docker-compose logs -f rassh-honeypot

shell:
	docker-compose exec rassh-honeypot /bin/bash