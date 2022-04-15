# Dev4py-utils

A set of Python regularly used classes/functions

[![ci](https://github.com/dev4py/dev4py-utils/actions/workflows/ci.yml/badge.svg?event=push&branch=main)](https://github.com/dev4py/dev4py-utils/actions/workflows/ci.yml) <br/>
[![Last release](https://github.com/dev4py/dev4py-utils/actions/workflows/on_release.yml/badge.svg)](https://github.com/dev4py/dev4py-utils/actions/workflows/on_release.yml) <br/>
[![Weekly checks](https://github.com/dev4py/dev4py-utils/actions/workflows/weekly_checks.yml/badge.svg?branch=main)](https://github.com/dev4py/dev4py-utils/actions/workflows/weekly_checks.yml) <br/>
[![Python >= 3.10.1](https://img.shields.io/badge/Python->=3.10.1-informational.svg?style=plastic&logo=python&logoColor=yellow)](https://www.python.org/) <br/>
[![Maintainer](https://img.shields.io/badge/maintainer-St4rG00se-informational?style=plastic&logo=superuser)](https://github.com/St4rG00se) <br/>
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg?style=plastic&logo=github)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity) <br/>
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=plastic&logo=github)](https://opensource.org/licenses/MIT)

## Table of contents

- [Project template](#project-template)
- [Project links](#project-links)
- [Dev4py-utils modules](#dev4py-utils-modules)
    * [dev4py.utils.awaitables](#dev4pyutilsawaitables)
    * [dev4py.utils.JOptional](#dev4pyutilsjoptional)
    * [dev4py.utils.objects](#dev4pyutilsobjects)
    * [dev4py.utils.types](#dev4pyutilstypes)

## Project template

This project is based on [pymsdl_template](https://github.com/dev4py/pymsdl_template)

## Project links

* [Documentation](https://htmlpreview.github.io/?https://github.com/dev4py/dev4py-utils/blob/main/docs/dev4py/utils.html)
* [PyPi project](https://pypi.org/project/dev4py-utils/)

## Dev4py-utils modules

### dev4py.utils.awaitables

[Awaitables documentation](https://htmlpreview.github.io/?https://github.com/dev4py/dev4py-utils/blob/main/docs/dev4py/utils/awaitables.html)

Examples:

```python
import asyncio
from dev4py.utils import awaitables, JOptional

# is_awaitable sample
awaitables.is_awaitable(asyncio.sleep(2))  # True
awaitables.is_awaitable(print("Hello"))  # False


# to_sync_or_async_param_function sample
def mapper(s: str) -> str:
    return s + "_suffix"


async def async_mapper(s: str) -> str:
    await asyncio.sleep(1)
    return s + "_async_suffix"


async def async_test():
    # Note: mapper parameter is str and async_mapper returns an Awaitable[str] so we have to manage it
    result: str = await JOptional.of("A value")\
      .map(async_mapper)\
      .map(awaitables.to_sync_or_async_param_function(mapper))\
      .get()
    print(result)  # A value_async_suffix_suffix

asyncio.run(async_test())
````

### dev4py.utils.JOptional

[JOptional documentation](https://htmlpreview.github.io/?https://github.com/dev4py/dev4py-utils/blob/main/docs/dev4py/utils/JOptional.html)

> ***Note:** [JOptional](src/main/python/dev4py/utils/JOptional.py) class is inspired from
> [java.util.Optional](https://docs.oracle.com/en/java/javase/17/docs/api//java.base/java/util/Optional.html)
> class with some adds (like `peek` method).*

Examples:

```python
from dev4py.utils import JOptional

value = 1
JOptional.of_noneable(value)\
  .map(lambda v: f"The value is {v}")\
  .if_present(print)
```

### dev4py.utils.objects

[Objects documentation](https://htmlpreview.github.io/?https://github.com/dev4py/dev4py-utils/blob/main/docs/dev4py/utils/objects.html)

> ***Note:** The [objects](src/main/python/dev4py/utils/objects.py) module is inspired from
> [java.util.Objects](https://docs.oracle.com/en/java/javase/17/docs/api//java.base/java/util/Objects.html)
> class.*

Examples:

```python
from dev4py.utils import objects

# non_none sample
value = None
objects.non_none(value)

# require_non_none sample
value = "A value"
objects.require_non_none(value)

# to_string sample
value = None
default_value: str = "A default value"
objects.to_string(value, default_value)
```

### dev4py.utils.types

[Types documentation](https://htmlpreview.github.io/?https://github.com/dev4py/dev4py-utils/blob/main/docs/dev4py/utils/types.html)

> ***Note:** The [types](src/main/python/dev4py/utils/types.py) module is inspired from
> [java.util.function](https://docs.oracle.com/en/java/javase/17/docs/api//java.base/java/util/function/package-summary.html)
> package*

Examples:

```python
from dev4py.utils.types import Function, Predicate, Consumer

# Function sample
int_to_str: Function[int, str] = lambda i: str(i)
str_result: str = int_to_str(1)

# Predicate sample
str_predicate: Predicate[str] = lambda s: s == "A value"
pred_result = str_predicate("Value to test")


# Consumer sample
def sample(consumer: Consumer[str], value: str) -> None:
    consumer(value)


def my_consumer(arg: str) -> None:
    print(arg)


sample(my_consumer, "My value")
```
