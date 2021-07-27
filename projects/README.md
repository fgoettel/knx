# projects
Unzip an exported configuration and extract its devices and communication objects

## Supported Exports
* ETS (.knxproj)
* GPA (.gpa)

## How to use
Explore the examples, e.g.,
    ```$ poetry run projects/examples/example_read_switches.py /Path/To/project.knxproj```

## TODOS
* GPA: Find added but unused variables
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
