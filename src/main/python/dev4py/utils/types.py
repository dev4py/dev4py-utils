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
Predicate: TypeAlias = Callable[[T], bool]
Consumer: TypeAlias = Callable[[T], None]
Supplier: TypeAlias = Callable[[], R]
Runnable: TypeAlias = Callable[[], None]
