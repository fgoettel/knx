# knx
 This consists of 3 parts:

 1. logger
 Log knx messages to a database

 2. projects
 Extract information from knx projects (ETS, GPA)

 3. x1_Nodes
 Custom made nodes for the gira X1

 ## How to start
 ### `logger` and `projects`

 1. Install python3 and poetry
 2. Clone this repository

    ```$ git clone git://github.com/fgoettel/knx/```
 3. Install the virtual environment (individual for each subfolder)
     ```$ poetry install```
 ### `x1_nodes`
 TODO: document setup


## Development

### Python

We're using two tools to administer the python projects:

* [poetry](https://python-poetry.org): All dependency and package management.
* [nox](https://nox.thea.codes/en/stable/index.html): Test automation.

#### Poetry
A few hints to restart. Main point for definitions is `pyproject.toml`.

* Update dependencies: `poetry update`. Do not forget to update the used versions in the github actions.
* Enter poetry shell: `poetry shell`

#### Nox
Run tests with various python versions. As defined in `noxfile.py`.

* Enter nox either inside a poetry shell (`nox`) or via `python -m nox`
* List all sessions: `nox -l`
* Run single session (here: isort): `nox -s isort`
* Reuse existing venv: `nox -r` (Don't do this after a `poetry update`)

 ## TODO
 * reuse code
 * ...
