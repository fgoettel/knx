# logger [![logger-codegen-and-lint-and-test](https://github.com/fgoettel/knx/actions/workflows/pytest_logger.yml/badge.svg)](https://github.com/fgoettel/knx/actions/workflows/pytest_logger.yml)

Log knx telegrams to a database.

## How
1. Get a mapping from ga to name & datatypes
    E.g. see `examples/ga_mapping.json`
    If you want to autogenerate these from a .knxproj check `..projects/examples/dump_knxproj_ga_to_json.py`
2. Run the example (e.g. `examples/main.py`)

## Dev

We're using two tools to administer this project:

* [poetry](https://python-poetry.org): All dependency and package management.
* [nox](https://nox.thea.codes/en/stable/index.html): Test automation.

### Poetry
A few hints to restart. Main point for definitions is `pyproject.toml`.

* Update dependencies: `poetry update`. Do not forget to update the used versions in the github actions.
* Enter poetry shell: `poetry shell`

### Nox
Run tests with various python versions. As defined in `noxfile.py`.

* Enter nox either inside a poetry shell (`nox`) or via `python -m nox`
* List all sessions: `nox -l`
* Run single session (here: isort): `nox -s isort`
* Reuse existing venv: `nox -r` (Don't do this after a `poetry update`)