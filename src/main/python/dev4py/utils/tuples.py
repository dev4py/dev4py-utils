from typing import Any

from dev4py.utils.objects import require_non_none
from dev4py.utils.types import T


def empty_tuple() -> tuple[Any, ...]:
    """
    Returns an empty tuple

    Returns:
        tuple[Any, ...]: An empty tuple
    """
    return tuple()


def append(tpl: tuple[T, ...], value: T) -> tuple[T, ...]:
    """
    Adds the given value to the given tuple and returns the new tuple with added value

    Args:
        tpl: the tuple
        value: the value to add

    Returns:
        tuple[T, ...]: A new tuple with all elements from tpl and the added value

    Raises:
        TypeError: if the tuple is None
    """
    return extend(tpl, (value,))


def extend(tpl_1: tuple[T, ...], tpl_2: tuple[T, ...]) -> tuple[T, ...]:
    """
    Adds all values from the second tuple to the first one and returns the new created tuple

    Args:
        tpl_1: The tuple where to add elements
        tpl_2: The tuple with the elements to add

    Returns:
        tuple[T, ...]: A new tuple with all elements from tpl_1 and tpl_2

    Raises:
        TypeError: if tpl_1 or tpl_2 is None
    """
    return require_non_none(tpl_1) + require_non_none(tpl_2)
