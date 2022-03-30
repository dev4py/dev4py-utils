"""
The `types` module provides a set commonly used types useful for static type checking
"""

from typing import TypeVar, TypeAlias, Callable

T = TypeVar('T')  # pragma: no mutate
R = TypeVar('R')  # pragma: no mutate

# See: https://peps.python.org/pep-0484/#type-aliases
#   Examples:
#     -> Function[int, bool] is equivalent to Callable[[int], bool]
#     -> Predicate[str] is equivalent to Callable[[str], bool]
#     -> Supplier[str] is equivalent to Callable[[], str]
# Note (on march 2022): Use mypy for typing validation (By default pycharm is not compliant)

Function: TypeAlias = Callable[[T], R]
Function.__doc__ = \
    """Function[T, R]: Represents a function that accepts one argument of T type and produces a result of R type"""

Predicate: TypeAlias = Callable[[T], bool]
Predicate.__doc__ = """Predicate[T]: Represents a predicate (boolean-valued function) of one argument of T type"""

Consumer: TypeAlias = Callable[[T], None]
Consumer.__doc__ = \
    """Consumer[T]: Represents an operation that accepts a single input argument of T type and returns no result"""

Supplier: TypeAlias = Callable[[], R]
Supplier.__doc__ = "Represents a supplier of results of R type"

Runnable: TypeAlias = Callable[[], None]
Runnable.__doc__ = """Represents a function that accepts no argument of T type and returns no result"""
