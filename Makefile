.PHONY: all setup venv db db-stop init run-consumer run-propagator run clean help

VENV_NAME := venv
PYTHON := python3
PIP := $(VENV_NAME)/bin/pip

all: setup run

setup: venv db init

venv:
	@echo "Setting up virtual environment..."
	@if [ ! -d "$(VENV_NAME)" ]; then \
	    $(PYTHON) -m venv $(VENV_NAME); \
	    $(PIP) install --upgrade pip; \
	    $(PIP) install -e .; \
	fi
	@echo "Virtual environment is ready."

db: venv
	@echo "Starting PostgreSQL container..."
	@cd postgres && docker compose up -d
	@echo "Waiting for PostgreSQL to start..."
	@sleep 5

db-stop:
	@echo "Stopping PostgreSQL container..."
	@cd postgres && docker compose down

init: venv
	@echo "Initializing database..."
	@chmod +x db_init_script.sh
	@./db_init_script.sh

run-consumer: venv
	@echo "Starting Event Consumer service..."
	@$(VENV_NAME)/bin/python -m cybercare.consumer --config cybercare/config.yaml

run-propagator: venv
	@echo "Starting Event Propagator service..."
	@$(VENV_NAME)/bin/python -m cybercare.propagator --config cybercare/config.yaml

run: venv
	@echo "Starting all services..."
	@gnome-terminal --tab --title="Consumer" -- bash -c "source $(VENV_NAME)/bin/activate && python -m cybercare.consumer --config cybercare/config.yaml; read"
	@gnome-terminal --tab --title="Propagator" -- bash -c "source $(VENV_NAME)/bin/activate && python -m cybercare.propagator --config cybercare/config.yaml; read"
	@echo "Services started in new terminal tabs"

clean: db-stop
	@echo "Cleaning up..."
	@rm -rf __pycache__ cybercare/__pycache__ tests/__pycache__
	@rm -rf .pytest_cache .mypy_cache

clean-venv: clean
	@echo "Removing virtual environment..."
	@rm -rf $(VENV_NAME)

help:
	@echo "  make help           - Show this help message"
	@echo "  make all            - Setup environment and run all services"
	@echo "  make setup          - Initialize the environment (venv, database and schema)"
	@echo "  make venv           - Create and setup virtual environment"
	@echo "  make db             - Start PostgreSQL container"
	@echo "  make db-stop        - Stop PostgreSQL container"
	@echo "  make init           - Initialize database schema"
	@echo "  make run-consumer   - Run only the event consumer service"
	@echo "  make run-propagator - Run only the event propagator service"
	@echo "  make run            - Run both consumer and propagator services"
	@echo "  make clean          - Stop services and clean up cache files"
	@echo "  make clean-venv     - Clean up and remove virtual environment"

.DEFAULT_GOAL := help
