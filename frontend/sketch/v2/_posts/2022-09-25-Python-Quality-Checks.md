## Introduction

I use python 3.9 poetry as dependency management. So probably it works from Python 3.8 and up. I always have to remind myself to write clean code. I hate to remember all those standards and coding guidelines, but in a team you have to follow them. SO I use tooling to format my code. These tooling here are all used to write nice clean formatted code and to remind me I need to write documentation. I don't get into details of the tools themselves, but I will when discussing each tool individually.

You'll see at the end how to create documentation from your Python source code with **Sphinx**, bat this is in a later blog-post. It does seem to be the standard when extracting docstrings from your Python code.

What would I like to write in later blogs:

- Using **Sphinx** to build documentation.
- Settings in **Interrogate** to ignore documentation reminders in python code. This is quite important, because you don't wan't to write documentation everywhere. Small private utility functions do explain themselves and are most of the time not a part of your API. APIs on the contrary should be well documented.
- Settings to ignore quality checks in the code.
- CI/CD integration using **Buildbot**. It's written in python.
- HTML publishing of Quality Check results

We build a small project to calculate fibonacci numbers using python with command line. The main goal is to check the code quality, testing and coverage. As I did in the past with Java projects.

Github project: [pyton-qa-project](https://github.com/cryptable/python-qa-project)

### Tools used:

- Pycharm IDE
- Poetry dependency manager and packaging
- Linting using PyLama
- Code converters Black and docformatter
- My old buildbot CI/CD
- gitignore (gi)
- documentation generator Sphinx

### Business requirements

Fibonacci tool runs as follows:

```
> test1 fibonacci --level 5
> test1 fibonacci --max-value 125 -j
> test1 fibonacci --max-value 125 -x
> test1 fibonacci --max-value 125 --verbose --xml

```

- Return parameters: -json and -xml are used as return value
- Output parameters: -verbose which gives extensive information on each level
- Input parameters: -level \<number\>, where 'number' specifies teh number steps taken to calculate fibonnaci number. -max-value \<number\> will run fibonacci loop as long as the result is smaller then the 'number'.

'test1' is the application, which executes the function 'fibonacci' with its parameters.

## Development

### Create a project:

```
> poetry new test1
> cd test1
```

### Create your tests:

test_test1.py:

```python
from test1 import __version__
from test1.main import get_argument_parser
import xml.etree.ElementTree as ET
import json

def test_version():
    assert __version__ == '0.1.0'

def test_fibonacci_level():
    parser = get_argument_parser()
    arguments = parser.parse_args("fibo --level 5".split(" "))
    root = ET.fromstring(arguments.func(arguments))
    assert int(root.findtext('result')) == 13

def test_fibonacci_max_value_xml():
    parser = get_argument_parser()
    arguments = parser.parse_args("fibo --max-value 125".split(" "))
    root = ET.fromstring(arguments.func(arguments))
    assert int(root.findtext('result')) == 89

def test_fibonacci_max_value_json():
    parser = get_argument_parser()
    arguments = parser.parse_args("fibo --max-value 125 -j".split(" "))
    root = json.loads(arguments.func(arguments))
    assert int(root['result']) == 89

```

As example, I use bad formatting.

### Create the code

main.py:

```python
import argparse
from .fibonacci import Fibonacci

parser = argparse.ArgumentParser()
parent_subparser = parser.add_subparsers()
fibo = Fibonacci(parent_subparser)

def get_argument_parser():
    return parser

def main():
    parser = get_argument_parser()
    args = parser.parse_args()
    if hasattr(args,'func'):
        exit(args.func(args))
    else:
        parser.print_help()
        exit(-1)

if __name__ == '__main__':
    main()
```


The 'get_argument_parser()' function will allow to make the code testable. The 'main()' will not be tested, so keep it as simple as possible. For a CLI it only contains the code to parse the arguments and call the corresponding function.
The 'get_argument_parser()' just creates the base parent argument parse for 'test1' application. It creates a subparsers which will be populated by the underlying classes in their constructors. The Classes know which arguments they'll need.

fibonacci.py:

```python
class Fibonacci:

    def _fibo(self, level, max, verbose=False):
        result1 = 1;
        result2 = 1;
        while True:
            if level != -1 and level == 0:
                return result2
            if max != -1 and result2 > max:
                return result1
            result2 = result1 + result2
            result1 = result2 - result1
            level -= 1

    def _output_error_xml(self, value, error_msg):
        return '<fibonacci><result>{}</result><error-msg>{}</error-msg></fibonacci>'.format(value, error_msg)

    def _output_error_json(self, value, error_msg):
        return '{{ "{{" }}"result":{},"error-msg>":"{}"}}'.format(value, error_msg)

    def _output_value_xml(self, value):
        return '<fibonacci><result>{}</result></fibonacci>'.format(value)

    def _output_value_json(self, value):
        return '{{ "{{" }}"result":{}}}'.format(value)

    def _output(self, json_format, value, error_msg=None):
        if error_msg:
            return  self._output_error_json(value, error_msg) if json_format else self._output_error_xml(value, error_msg)
        return self._output_value_json(value) if json_format else self._output_value_xml(value)

    def process(self, args):
        if args.level == -1 and args.max_value == -1:
            return self._output(args.json, -1, error_msg="Missing arguments, 'level' or 'max-value' is obligatory")
        result = self._fibo(args.level, args.max_value, args.verbose)
        return self._output(args.json, result)

    def __init__(self, parent_parser):
        subparser = parent_parser.add_parser("fibo")
        subparser.add_argument(
            "-l", "--level", type=int, default=-1, help="Number steps for Fibonacci to take"
        )
        subparser.add_argument(
            "-m", "--max-value", type=int, default=-1, help="Run steps for Fibonacci as long as its less then 'max-value'"
        )
        subparser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Verbose output, prints each step of Fibonacci series!",
        )
        subparser.add_argument(
            "-j",
            "--json",
            action="store_true",
            help="Return json result",
        )
        subparser.add_argument(
            "-x",
            "--xml",
            action="store_true",
            help="Return xml result",
        )
        subparser.set_defaults(func=self.process)

```

Still no documentation and bad formatting in the code on purpose to check the linters.

### Create the .gitignore

Developers are lazy, so use [gitignore](https://gitignore.io). Just install and use *gi*, look at it and understand what it did. In the root of your project run:

```shell
> gi pycharm,python > .gitignore
```

It is fun to work on the shoulders of all great developers.

### Add *test1* CLI support in pyproject.toml

When installing the project using *poetry*, you can create the shell command *test1* by adding folling to the *pyproject.toml* file.

```toml
[tool.poetry.scripts]
test1 = "test1.main:main"
```

### Build the project using poetry

When you want to test not using the IDE testing facilities, you need to build the project

```shell
> poetry build
```

### Run tests

Run the tests in your IDE or use *pytest* in *poetry*, which run all tests in the virtual environment setup by *poetry*.

```shell
> poetry run pytest
```

### Run *test1* CLI command

This runs the *test1* CLI application in the virtual environment setup by *poetry*.

```shell
> poetry run test1 fibo --level 5 -j
{"result":13}
```

### Directory tree of poetry

Final tree view on Linux without the hidden files.

```shell
.
├── dist
│   ├── test1-0.1.0-py3-none-any.whl
│   └── test1-0.1.0.tar.gz
├── poetry.lock
├── pyproject.toml
├── README.rst
├── test1
│   ├── fibonacci.py
│   ├── __init__.py
│   ├── main.py
│   └── __pycache__
│       ├── fibonacci.cpython-38.pyc
│       ├── __init__.cpython-38.pyc
│       └── main.cpython-38.pyc
└── tests
    ├── __init__.py
    ├── __pycache__
    │   ├── __init__.cpython-38.pyc
    │   └── test_test1.cpython-38-pytest-5.4.3.pyc
    └── test_test1.py
```

## Quality checks

In your IDE you should install Flake8, Black, docformatter support, but you should also need results when checking code in. With test driven development, you need also to verify the coverage of test in the python code. And what about documentation? ...

### Code conventions and quality

We will use PyLama, which include *flake8*.

Add a development depedency in poetry *pyproject.toml* file.

```toml
[tool.poetry.dev-dependencies]
pytest = "^7.1.3"
pylama = "^8.4.1"
```

Update your project and run:

```shell
> poetry update
```

Run pylama to check quality of your code

```shell
> poetry run pylama
test1/main.py:8:1 E302 expected 2 blank lines, found 1 [pycodestyle]
test1/main.py:11:1 E302 expected 2 blank lines, found 1 [pycodestyle]
test1/main.py:14:20 E231 missing whitespace after ',' [pycodestyle]
test1/main.py:20:1 E305 expected 2 blank lines after class or function definition, found 1 [pycodestyle]
test1/main.py:21:11 W292 no newline at end of file [pycodestyle]
test1/fibonacci.py:5:20 E703 statement ends with a semicolon [pycodestyle]
test1/fibonacci.py:6:20 E703 statement ends with a semicolon [pycodestyle]
test1/fibonacci.py:17:101 E501 line too long (109 > 100 characters) [pycodestyle]
test1/fibonacci.py:30:101 E501 line too long (122 > 100 characters) [pycodestyle]
test1/fibonacci.py:30:19 E271 multiple spaces after keyword [pycodestyle]
test1/fibonacci.py:35:101 E501 line too long (115 > 100 characters) [pycodestyle]
test1/fibonacci.py:45:101 E501 line too long (122 > 100 characters) [pycodestyle]
tests/test_test1.py:6:1 E302 expected 2 blank lines, found 1 [pycodestyle]
tests/test_test1.py:9:1 E302 expected 2 blank lines, found 1 [pycodestyle]
tests/test_test1.py:15:1 E302 expected 2 blank lines, found 1 [pycodestyle]
tests/test_test1.py:21:1 E302 expected 2 blank lines, found 1 [pycodestyle]
```

You can also run pylama as part of your testing using *pytest*

```shell
> poetry  run pytest --pylama
======================================= test session starts =======================================
platform linux -- Python 3.8.10, pytest-7.1.3, pluggy-1.0.0
rootdir: /home/david/workspacehd/workspace/python-fun/test/test1
plugins: pylama-8.4.1
collected 9 items                                                                                                                                                                                                                                        

test1/__init__.py s                                                                                                                                                                                                                                [ 11%]
test1/fibonacci.py F                                                                                                                                                                                                                               [ 22%]
test1/main.py F                                                                                                                                                                                                                                    [ 33%]
tests/__init__.py s                                                                                                                                                                                                                                [ 44%]
tests/test_test1.py F....                                                                                                                                                                                                                          [100%]

============================================ FAILURES =============================================
____________________________________ test session _________________________________________________
test1/fibonacci.py:5:20 [E] E703 statement ends with a semicolon [pycodestyle]
test1/fibonacci.py:6:20 [E] E703 statement ends with a semicolon [pycodestyle]
test1/fibonacci.py:17:101 [E] E501 line too long (109 > 100 characters) [pycodestyle]
test1/fibonacci.py:30:101 [E] E501 line too long (122 > 100 characters) [pycodestyle]
test1/fibonacci.py:30:19 [E] E271 multiple spaces after keyword [pycodestyle]
test1/fibonacci.py:35:101 [E] E501 line too long (115 > 100 characters) [pycodestyle]
test1/fibonacci.py:45:101 [E] E501 line too long (122 > 100 characters) [pycodestyle]
____________________________________ test session _________________________________________________
test1/main.py:8:1 [E] E302 expected 2 blank lines, found 1 [pycodestyle]
test1/main.py:11:1 [E] E302 expected 2 blank lines, found 1 [pycodestyle]
test1/main.py:14:20 [E] E231 missing whitespace after ',' [pycodestyle]
test1/main.py:20:1 [E] E305 expected 2 blank lines after class or function definition, found 1 [pycodestyle]
test1/main.py:21:11 [W] W292 no newline at end of file [pycodestyle]
____________________________________ test session _________________________________________________
tests/test_test1.py:6:1 [E] E302 expected 2 blank lines, found 1 [pycodestyle]
tests/test_test1.py:9:1 [E] E302 expected 2 blank lines, found 1 [pycodestyle]
tests/test_test1.py:15:1 [E] E302 expected 2 blank lines, found 1 [pycodestyle]
tests/test_test1.py:21:1 [E] E302 expected 2 blank lines, found 1 [pycodestyle]
=================================== short test summary info =======================================
FAILED test1/fibonacci.py::pylama
FAILED test1/main.py::pylama
FAILED tests/test_test1.py::pylama
============================ 3 failed, 4 passed, 2 skipped in 0.03s ===============================
```

The pytest show failures now, because the quality of the code is not sufficient. You can fine-tune the tests, but herefor you need to read the documentation.

#### References

- https://klen.github.io/pylama/

### Enforcing Coding conventions: Black

**Black** is one of the best code convention enforcer to transform your python code to PEP8 standard. You can integrate always integrate it in your favorite IDE, but you'll need to check the internet for the explanation. This will even auto-format your code when saving the file.
Install it in your poetry configuration file *pyproject.toml* as a development depedency.

```toml
[tool.poetry.dev-dependencies]
pytest = "^7.1.3"
pylama = "^8.4.1"
black = "^22.8.0"
```

Update your project by running:

```shell
> poetry  update
```

Run *black* to autoformat your python-files:

```shell
> poetry  run black .
```

Run the autoformatter for your code and tests!

We check if the code quality has increased using *pylama*.

```shell
> poetry  run pylama
```

No more coding quality problem.

#### References

- https://black.readthedocs.io/en/latest/the_black_code_style/index.html

### Enforcing Coding conventions: docformatter

**Black** is one of the best code convention enforcer to transform your python code to PEP8 standard, but has some problems with docstrings and their maximum line length. **docformatter** can handle them perfectly. So you can run *docformatter* if *pylama* is still complaining of line lengths in 'docstrings'. *docformatter* handle multi-line strings differently as *black*. So it is up to your opinion to run *black* after or before *docformatter*.

```toml
[tool.poetry.dev-dependencies]
pytest = "^7.1.3"
pylama = "^8.4.1"
black = "^22.8.0"
docformatter="^1.5.0"
```

Update your project by running:

```shell
> poetry  update
```

We'll add to our *pyproject.toml* the following configuration:

```
[tool.docformatter]
recursive = true
blank = true
```

Run *docformatter* to autoformat your python-files:

```shell
> poetry  run docformatter --config pyproject.toml --in-place test1
```

Run the autoformatter for your code and tests!

We check if the code quality has increased using *pylama*.

```shell
> poetry  run pylama
```

No more coding quality problem.

#### References

- https://github.com/PyCQA/docformatter
- https://docformatter.readthedocs.io/en/latest/

### Code coverage when testing your code

With TDD this should normally be 100%, but who does really 100% TDD. So it makes sense to regularly check you code coverage of your code. First to see if tests are missing, but also check if you don't have to much code, which will be a maintenance cost.

Install pytest-cov in your poetry configuration file *pyproject.toml* as a development depedency.

```toml
[tool.poetry.dev-dependencies]
pytest = "^7.1.3"
pylama = "^8.4.1"
black = "^22.8.0"
docformatter="^1.5.0"
pytest-cov = "^3.0.0"
```

Update your project by running:

```shell
> poetry  update
```

To run your code-coverage

```shell
>oetry run pytest --cov=test1
============================================== test session starts ===============================================
platform linux -- Python 3.8.10, pytest-7.1.3, pluggy-1.0.0
rootdir: /home/david/workspacehd/workspace/python-fun/test/test1
plugins: cov-3.0.0, pylama-8.4.1
collected 4 items                                                                                                

tests/test_test1.py ....                                                                                   [100%]

---------- coverage: platform linux, python 3.8.10-final-0 -----------
Name                 Stmts   Miss  Cover
----------------------------------------
test1/__init__.py        1      0   100%
test1/fibonacci.py      36      4    89%
test1/main.py           16      7    56%
----------------------------------------
TOTAL                   53     11    79%


=============================================== 4 passed in 0.02s ================================================
```

To let pytest fail under a certain code-coverage percentage, you run:

```shell
> poetry  run pytest --cov=test1 tests/ --cov-fail-under=80
============================================== test session starts ===============================================
platform linux -- Python 3.8.10, pytest-7.1.3, pluggy-1.0.0
rootdir: /home/david/workspacehd/workspace/python-fun/test/test1
plugins: cov-3.0.0, pylama-8.4.1
collected 4 items                                                                                                

tests/test_test1.py ....                                                                                   [100%]

---------- coverage: platform linux, python 3.8.10-final-0 -----------
Name                 Stmts   Miss  Cover
----------------------------------------
test1/__init__.py        1      0   100%
test1/fibonacci.py      36      4    89%
test1/main.py           16      7    56%
----------------------------------------
TOTAL                   53     11    79%

FAIL Required test coverage of 80% not reached. Total coverage: 79.25%

=============================================== 4 passed in 0.02s ================================================
```

This will return that the tests failed. So for now, we run tests together with codecoverage on the CI/CD pipelines with a minimal coverage setting of 80%.

### Code coverage for documentation

Nobody likes to write documentation in code, but it must be done. Certainly for API specifications and main important code parts of your python code.
We will use *interrogate* for this part to create a report of the coverage of documentation of the python files and classes.

```toml
[tool.poetry.dev-dependencies]
pytest = "^7.1.3"
pylama = "^8.4.1"
black = "^22.8.0"
docformatter="^1.5.0"
pytest-cov = "^3.0.0"
interrogate="^1.5.0"
```

Update your project by running:

```shell
> poetry  update
```

We'll add to our *pyproject.toml* the following configuration:

```
[tool.interrogate]
ignore-init-method = false
ignore-init-module = true
ignore-magic = false
ignore-semiprivate = false
ignore-private = false
ignore-property-decorators = false
ignore-module = false
ignore-nested-functions = false
ignore-nested-classes = true
ignore-setters = false
fail-under = 95
exclude = ["setup.py", "docs", "build"]
ignore-regex = ["^get$", "^mock_.*", ".*BaseClass.*"]
# possible values: 0 (minimal output), 1 (-v), 2 (-vv)
verbose = 0
quiet = false
whitelist-regex = []
color = true
omit-covered-files = false
# generate-badge = "."
# badge-format = "svg"
```

Ignore the __init__ module, because it most of the time it is empty, but when you do put code in the __init__.py file, don't forget to enable it.
Let's add some comments to our code:

main.py:

```python
"""Main code for test1 CLI

This module is the basis of the CLI. It only parser arguments and execute the connected function to the parser. The 
parameters and function connection is done in the submodules. 

"""
import argparse
from .fibonacci import Fibonacci

parser = argparse.ArgumentParser()
parent_subparser = parser.add_subparsers()
fibo = Fibonacci(parent_subparser)


def get_argument_parser():
    """get parser for the arguments

    Mainly used for testing purposes (see tests)

    :return: The argument parser
    """
    return parser


def main():
    """main function to execute

    Run the app, all logic and business functions are located in submodules.

    :return: depends on the submodules.
    """
    args = parser.parse_args()
    if hasattr(args, "func"):
        exit(args.func(args))
    else:
        parser.print_help()
        exit(-1)


if __name__ == "__main__":
    main()
```

The IDE was complaining about static function in the Fibonacci class. So we refactored it outside the class.

fibonaccy.py

```python
"""fibonacci module

This module contains the implementation of the Fibonacci class

"""


def _fibo(level, max, verbose=False):
    """the fibonacci calculation function

    Calculates the fibonacci series according to its input parameters

    :param level: How many steps does fibo function needs to take.
    :param max: Maximum value to reach
    :param verbose: Verbose output
    :return: the fibonacci number
    """
    result1 = 1
    result2 = 1
    while True:
        if level != -1 and level == 0:
            return result2
        if max != -1 and result2 > max:
            return result1
        result2 = result1 + result2
        result1 = result2 - result1
        level -= 1


def _output_error_xml(value, error_msg):
    """show error message in xml

    :param value: Error code
    :param error_msg: descriptive error message
    :return:
    """
    return "<fibonacci><result>{}</result><error-msg>{}</error-msg></fibonacci>".format(
        value, error_msg
    )


def _output_error_json(value, error_msg):
    """show error message in json

    :param value: Error code
    :param error_msg: descriptive error message
    :return:
    """
    return '{{ "{{" }}"result":{},"error-msg>":"{}"}}'.format(value, error_msg)


def _output_value_xml(value):
    """show result in xml

    :param value: Fibonacci result
    :return:
    """
    return "<fibonacci><result>{}</result></fibonacci>".format(value)


def _output_value_json(value):
    """show result in json

    :param value: Fibonacci result
    :return:
    """
    return '{{ "{{" }}"result":{}}}'.format(value)


def _output(json_format, value, error_msg=None):
    """output result

    According to the parameters the output will be an XML or JSON result.

    :param json_format: True/False to show JSON otherwise it is XML.
    :param value: value of Fibonacci or error code when error_msg is present
    :param error_msg: a descriptive error message
    :return: string with XML or JSON
    """
    if error_msg:
        return (
            _output_error_json(value, error_msg)
            if json_format
            else _output_error_xml(value, error_msg)
        )
    return _output_value_json(value) if json_format else _output_value_xml(value)


class Fibonacci:
    """Fibonacci class

    Fibonacci class contains the business logic for the fibonacci commandline tool

    """

    def _process(self, args):
        """calculate the Fibonacci number

        This process will validate the arguments, calulate Fibonacci number and return the result in the requested
        format.

        :param args:
        :return:
        """
        if args.level == -1 and args.max_value == -1:
            return _output(
                args.json,
                -1,
                error_msg="Missing arguments, 'level' or 'max-value' is obligatory",
            )
        result = _fibo(args.level, args.max_value, args.verbose)
        return _output(args.json, result)

    def __init__(self, parent_parser):
        """constructor

        Initializes the Fibonacci class where we add the necessary arguments to parse by the argument parser

        :param parent_parser:
        """
        subparser = parent_parser.add_parser("fibo")
        subparser.add_argument(
            "-l",
            "--level",
            type=int,
            default=-1,
            help="Number steps for Fibonacci to take",
        )
        subparser.add_argument(
            "-m",
            "--max-value",
            type=int,
            default=-1,
            help="Run steps for Fibonacci as long as its less then 'max-value'",
        )
        subparser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Verbose output, prints each step of Fibonacci series!",
        )
        subparser.add_argument(
            "-j",
            "--json",
            action="store_true",
            help="Return json result",
        )
        subparser.add_argument(
            "-x",
            "--xml",
            action="store_true",
            help="Return xml result",
        )
        subparser.set_defaults(func=self._process)

```

When you rerun the *iterrogate* command it shows it is 100%.

```shell
> poetry  run interrogate test1
RESULT: PASSED (minimum: 95.0%, actual: 100.0%)
```

So for now, we run documentation coverage on the CI/CD pipelines with a minimal coverage setting of 80%. Also check run your *docformatter* to cleanup your 'docstrings'.

#### References

- https://github.com/econchick/interrogate
- https://interrogate.readthedocs.io/en/latest/

### Testing the example code in your documentation

Writing examples in your documentation is very valuable to explain what the function does. This example code should be kept up to date, so this code in the documentation can also be tested using *doctest*. Which is a standard tool in python. This can ofcourse be integrated in your IDE. Here is an explanation to integrate this in a CI/CD pipeline.

First change the 'docstring' of the *\_fibo()* function to:
```
    """the fibonacci calculation function.

    Calculates the fibonacci series according to its input parameters

    Example:
        >>> _fibo(5, -1)
        15

    :param level: How many steps does fibo function needs to take.
    :param max: Maximum value to reach
    :param verbose: Verbose output
    :return: the fibonacci number

    """
```

The example is wrong and the result should be 13. So to test a source-file with examples in the comments:

```shell
> poetry run python -m doctest test1/fibonacci.py
**********************************************************************
File "/home/david/workspacehd/workspace/python-fun/test/test1/test1/fibonacci.py", line 14, in fibonacci._fibo
Failed example:
    _fibo(5, -1)
Expected:
    15
Got:
    13
**********************************************************************
1 items had failures:
   1 of   1 in fibonacci._fibo
***Test Failed*** 1 failures.
```

It shows that the comment is wrong. We can also run this as part of *pytest*:

```shell
> poetry  run pytest --doctest-modules
============================================== test session starts ===============================================
platform linux -- Python 3.8.10, pytest-7.1.3, pluggy-1.0.0
rootdir: /home/david/workspacehd/workspace/python-fun/test/test1
plugins: cov-3.0.0, pylama-8.4.1
collected 5 items                                                                                                

test1/fibonacci.py F                                                                                       [ 20%]
tests/test_test1.py ....                                                                                   [100%]

==================================================== FAILURES ====================================================
________________________________________ [doctest] test1.fibonacci._fibo _________________________________________
009 the fibonacci calculation function.
010 
011     Calculates the fibonacci series according to its input parameters
012 
013     Example:
014         >>> _fibo(5, -1)
Expected:
    15
Got:
    13

/home/david/workspacehd/workspace/python-fun/test/test1/test1/fibonacci.py:14: DocTestFailure
============================================ short test summary info =============================================
FAILED test1/fibonacci.py::test1.fibonacci._fibo
========================================== 1 failed, 4 passed in 0.01s ===========================================
```

Change the value 15 to 13 in the comment and check it again:

```shell
> poetry  run pytest --doctest-modules
============================================== test session starts ===============================================
platform linux -- Python 3.8.10, pytest-7.1.3, pluggy-1.0.0
rootdir: /home/david/workspacehd/workspace/python-fun/test/test1
plugins: cov-3.0.0, pylama-8.4.1
collected 5 items                                                                                                

test1/fibonacci.py .                                                                                       [ 20%]
tests/test_test1.py ....                                                                                   [100%]

=============================================== 5 passed in 0.01s ================================================
```

#### References

- https://docs.python.org/3/library/doctest.html

### Conclusion

You can combine the different pytest checks or run them seperately. This will be a strategy for the reporting and quality of the python code. Your CI/CD is now setup to verify and correct the code such that your team creates 'quality' code with the necessary documentation in the code. Now let's generate the documentation now with *sphinx*.

## Documentation generation

The main tool to generate documentation is *sphinx*, which is not as straight forward as the tools above.
To install sphinx, add it to your *pyproject.toml*.

```toml
[tool.poetry.dev-dependencies]
pytest = "^7.1.3"
pylama = "^8.4.1"
black = "^22.8.0"
docformatter="^1.5.0"
pytest-cov = "^3.0.0"
interrogate="^1.5.0"
sphinx="^5.1.1"
```

Update your project by running:

```shell
> poetry  update
```
This way to complex to explain. So another blog will come about 'documentation' generation using *sphinx*

### References

- https://www.sphinx-doc.org/en/master/index.html

## Conclusion

These tools won't fix any bugs in the code or just bad code, but it helps at least that the code has 'some' quality and follow python standards. In a team everybody should now be more conftable to read the code if everybody stick to these standards.
Pull request needs still to be reviewed if the code is nicely written and the necessary tests are available. Also verify if the documentation is still up to date.
When writing open-source, the users of your project will have more confidence in the quality of your code when you have everywhere high stats of the checks. It is still no guarantee the code is functioning as requested. The tools are here just to help you remind to write beautiful code.
