# logger [![logger-codegen-and-lint-and-test](https://github.com/fgoettel/knx/actions/workflows/pytest_logger.yml/badge.svg)](https://github.com/fgoettel/knx/actions/workflows/pytest_logger.yml)

Log knx telegrams to a database.

## How
1. Get a mapping from ga to name & datatypes
    E.g. see `examples/ga_mapping.json`
    If you want to autogenerate these from a .knxproj check `..projects/examples/dump_knxproj_ga_to_json.py`
2. Run the example (e.g. `examples/main.py`)
