# Automatic tester for assignment 2

This python script runs through the automated test cases also used by PracTool
for you to determine if your program works correctly.

## Requirements
 * Python 2.7 ([download here](https://www.python.org/downloads/release/python-2712/))

## Running

The script has been setup to instantly work when extracted in the root of the
template given to you. If you did not use the standard template, use either
the method described in section Jar or Other.

### Template

First compile your java code by executing `./gradlew build`
You can then run the tests by executing `python test.py` on your terminal.

### Jar

First build an executable jar file in your method of choice. If you do not
know how to do this, either google it or proceed to section Other.
You can then run the tests by executing `python test.py path/to/my.jar`

### Other

The testing script has an extra mode to handle anything.
To use this, you pass the parameter flag '-r' or '--run' (use only one, they
are synonyms) followed by the command you would use to run your source code
in a normal environment.

For an example, if your compiled .class files are in the directory 'out/classes'
and your main class is called Main, you would run the tests by executing
`python test.py -r 'java -cp out/classes Main'`.

## Options

For a complete overview of all options available to you, add the '-h' or the
'--help' flag.

The most useful flags would be:
 * **-e** This will print the error messages being matched, to check if they are
 representative of the errors they should be reporting
 * **-t** To only run a single suite of tests
 * **-v** To increase verbosity of the output. With one `-v` it will show a message
 for each succesful match. With two `-v`'s it will also show what it matches.

## Errors / Help it doesn't work
Create an issue on the github repository of the assignment [here](https://github.com/VU-Programming/AP2-Skeleton/issues)


