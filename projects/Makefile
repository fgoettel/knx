.PHONY: clean help lint test coverage
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r"^([a-zA-Z_-]+):.*?## (.*)$$", line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python3 -c "$$BROWSER_PYSCRIPT"

help:
	@python3 -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: ## remove all build, test, coverage and python artifacts
	find . -name ".coverage" -exec rm -f {} +
	find . -name "*.pyc" -exec rm -f {} +
	find . -name "*.pyo" -exec rm -f {} +
	find . -name "*~" -exec rm -f {} +
	find . -name "__pycache__" -exec rm -fr {} +
	find . -name "htmlcov" -exec rm -rf {} +
	find . -name ".mypy_cache" -exec rm -rf {} +
	find . -name ".pytest_cache" -exec rm -rf {} +

lint: ## check style with flake8
	poetry run isort .
	poetry run black .
	poetry run pydocstyle .
	poetry run pylint test projects
	poetry run pylint examples --disable=duplicate-code
	poetry run mypy .

test: ## run tests quickly with the poetry python
	poetry run pytest

coverage: ## check code coverage quickly with the default Python
	poetry run pytest --cov=. --cov-report=html test
	$(BROWSER) htmlcov/index.html

doc: ## Collection of interesting data
    # TODO: Add coverage
	poetry run pyreverse -o png -p project ./projects
