[![hypothesis-auto - Fully Automatic Tests for Type Annotated Functions Using Hypothesis.](https://raw.github.com/timothycrosley/hypothesis-auto/master/art/logo_large.png)](https://timothycrosley.github.io/hypothesis-auto/)
_________________

[![PyPI version](https://badge.fury.io/py/hypothesis-auto.svg)](http://badge.fury.io/py/hypothesis-auto)
[![Build Status](https://travis-ci.org/timothycrosley/hypothesis-auto.svg?branch=master)](https://travis-ci.org/timothycrosley/hypothesis-auto)
[![codecov](https://codecov.io/gh/timothycrosley/hypothesis-auto/branch/master/graph/badge.svg)](https://codecov.io/gh/timothycrosley/hypothesis-auto)
[![Join the chat at https://gitter.im/timothycrosley/hypothesis-auto](https://badges.gitter.im/timothycrosley/hypothesis-auto.svg)](https://gitter.im/timothycrosley/hypothesis-auto?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://pypi.python.org/pypi/hypothesis-auto/)
[![Downloads](https://pepy.tech/badge/hypothesis-auto)](https://pepy.tech/project/hypothesis-auto)
_________________

[Read Latest Documentation](https://timothycrosley.github.io/hypothesis-auto/) - [Browse GitHub Code Repository](https://github.com/timothycrosley/hypothesis-auto/)
_________________

**hypothesis-auto** is an extension for the [Hypothesis](https://hypothesis.readthedocs.io/en/latest/) project that enables fully automatic tests for type annotated functions.

[![Hypothesis Pytest Auto Example](https://raw.github.com/timothycrosley/hypothesis-auto/master/art/demo.gif)](https://github.com/timothycrosley/hypothesis-auto/blob/master/art/demo.gif)

Key Features:

* **Type Annotation Powered**: Utilize your function's existing type annotations to build dozens of test cases automatically.
* **Low Barrier**: Start utilizing property-based testing in the lowest barrier way possible. Just run `auto_test(FUNCTION)` to run dozens of test.
* **py.test Compatible**: Built-in compatibility with the popular [py.test](https://docs.pytest.org/en/latest/) testing framework. This means that you can turn your automatically generated tests into individual py.test test cases with one line.
* **Scales Up**: As you find your self needing to customize your auto_test cases, you can easily utilize all the features of [Hypothesis](https://hypothesis.readthedocs.io/en/latest/), including custom strategies per a parameter.

## Installation:

To get started - install `hypothesis-auto` into your projects virtual environment:

`pip3 install hypothesis-auto`

OR

`poetry add hypothesis-auto`

OR

`pipenv install hypothesis-auto`

## Usage Examples:

### Framework independent usage

Basic `auto_test` usage:

```python31
from hypothesis_auto import auto_test


def add(number_1: int, number_2: int = 1) -> int:
    return number_1 + number_2


auto_test(add)  # 50 property based scenerios are generated and ran against add
auto_test(add, _auto_runs=1_000)  # Let's make that 1,000
```

Adding an allowed exception:

```python3
from hypothesis_auto import auto_test


def divide(number_1: int, number_2: int) -> int:
    return number_1 / number_2

auto_test(divide)

-> 1012                     raise the_error_hypothesis_found
   1013
   1014         for attrib in dir(test):

<ipython-input-2-65a3aa66e9f9> in divide(number_1, number_2)
      1 def divide(number_1: int, number_2: int) -> int:
----> 2     return number_1 / number_2
      3

0/0

ZeroDivisionError: division by zero


auto_test(divide, _auto_allow_exceptions=(ZeroDivisionError, ))
```

For the full set of parameters, you can pass into auto_test see its [API reference documentation](https://timothycrosley.github.io/hypothesis-auto/reference/hypothesis_auto/tester/).

### py.test usage

Using `auto_pytest_magic` to auto-generate dozens of py.test test cases:

```python3
from hypothesis_auto import auto_pytest_magic


def add(number_1: int, number_2: int = 1) -> int:
    return number_1 + number_2


auto_pytest_magic(add)
```

Using `auto_pytest` to run dozens of test case within a temporary directory:

```
from hypothesis_auto import auto_pytest


def add(number_1: int, number_2: int = 1) -> int:
    return number_1 + number_2


@auto_pytest()
def test_add(test_case, tmpdir):
    tmpdir.mkdir().chdir()
    test_case()
```

For the full reference of the py.test integration API see the [API reference documentation](https://timothycrosley.github.io/hyp othesis-auto/reference/hypothesis_auto/pytest/).

## Why Create hypothesis-auto?

I wanted a no/low resistance way to start incorporating property-based tests across my projects. Such a solution that also encouraged the use of type hints was a win/win for me.

I hope you too find `hypothesis-auto` useful!

~Timothy Crosley
