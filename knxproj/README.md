# knxproj
Unzip an exported configuration and ...

## Features

### ETS
Read a .knxproj and ...

### GPA
Read a GPA export and ...

## Intro in a nutshell

0. Install python3 and poetry
1. Clone this repository

   ```$ git clone git://github.com/fgoettel/knx/knxproj```

2. Install the virtual environment

    ```$ poetry install```

3. Explore the examples, e.g.,

    ```$ poetry run knxproj/examples/example_read_switches.py /Path/To/project.knxproj```

## TODOS

* Check exports from ETS != 5.7
* Check on Windows
* MDT GT
    * Nice documentation
    * Nice examples
    * Evaluate kurz/lang and print both
    * Layout other than 2*6
    * Notify LED / Message usage
    * Good tests
    * Good test coverage
