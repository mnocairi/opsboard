.PHONY: run test lint install db-up db-down

run:
	uvicorn app.main:app --reload

test:
	python -m pytest

install:
	pip install -r requirements.txt

db-up:
	docker compose up -d

db-down:
	docker compose down