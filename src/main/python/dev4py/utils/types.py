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
"""Function[T, R]: A function that accepts one T type argument and produces a R type result"""
Function.__doc__ = \
    "Function[T, R]: A function that accepts one T type argument and produces a R type result"  # pragma: no mutate

Predicate: TypeAlias = Callable[[T], bool]
"""Predicate[T]: A predicate (boolean-valued function) of one T type argument"""
Predicate.__doc__ = "Predicate[T]: A predicate (boolean-valued function) of one T type argument"  # pragma: no mutate

Consumer: TypeAlias = Callable[[T], None]
"""Consumer[T]: An operation that accepts a single T type argument and returns no result"""
Consumer.__doc__ = \
    "Consumer[T]: An operation that accepts a single T type argument and returns no result"  # pragma: no mutate

Supplier: TypeAlias = Callable[[], R]
"""A supplier of results of R type"""
Supplier.__doc__ = "A supplier of results of R type"  # pragma: no mutate

Runnable: TypeAlias = Callable[[], None]
"""A function that accepts no T type argument and returns no result"""
Runnable.__doc__ = "A function that accepts no T type argument and returns no result"  # pragma: no mutate
