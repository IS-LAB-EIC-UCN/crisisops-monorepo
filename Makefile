.PHONY: install run test lint format compose-up compose-down migration upgrade

install:
	python -m pip install -e ".[dev]"

run:
	uvicorn crisisops.main:app --reload

test:
	pytest --cov=crisisops --cov-report=term-missing

lint:
	ruff check src tests

format:
	ruff format src tests

compose-up:
	docker compose up --build

compose-down:
	docker compose down

migration:
	alembic revision --autogenerate -m "$(m)"

upgrade:
	alembic upgrade head
