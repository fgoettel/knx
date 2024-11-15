.PHONY: install lint test

install:
	poetry lock
	poetry install

lint:  ## Basic quality assurance
	poetry run ruff format .
	poetry run ruff check . --fix
	poetry run mypy .

test: ## Run pytest
	poetry run pytest .
