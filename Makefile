lint:
	poetry run ruff check . --fix

format:
	poetry run ruff format

mypy:
	mypy .

dev:
	docker compose up web

prod:
	docker compose -f compose.yml -f compose.prod.yml up -d