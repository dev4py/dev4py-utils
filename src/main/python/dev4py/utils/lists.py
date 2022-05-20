from typing import Any

from dev4py.utils.objects import require_non_none
from dev4py.utils.types import T


def empty_list() -> list[Any]:
    """
    Returns an empty list

    Returns:
        list[Any]: An empty list
    """
    return []


def append(lst: list[T], value: T) -> list[T]:
    """
    Adds the given value to the given list and returns the list

    Args:
        lst: the list
        value: the value to add

    Returns:
        list[T]: The list with the added value

    Raises:
        TypeError: if the list is None
    """
    require_non_none(lst).append(value)
    return lst


def extend(lst_1: list[T], lst_2: list[T]) -> list[T]:
    """
    Adds all values from the second list to the first one and returns it

    Args:
        lst_1: The list where to add elements
        lst_2: The list with the elements to add

    Returns:
        lst_1 (list[T]): The first list with added elements

    Raises:
        TypeError: if lst_1 or lst_2 is None
    """
    require_non_none(lst_1).extend(require_non_none(lst_2))
    return lst_1
