"""
The `dicts` module provides a set of utility functions to simplify dict operations
"""
from typing import Optional, Any

from dev4py.utils import JOptional
from dev4py.utils.objects import non_none
from dev4py.utils.types import K, V, Supplier


def is_dict(value: Any) -> bool:
    """
    If the given value is a dict, returns true, otherwise false

    Returns:
        bool: true if the given value is a dict, otherwise false
    """
    return isinstance(value, dict)


def get_joptional_value(dictionary: Optional[dict[K, V]], key: K) -> JOptional[V]:
    """
    Tries to get a value from a dict with the given key and returns a JOptional describing the result

    Args:
        dictionary: The dict
        key: The key

    Returns:
        JOptional[V]: An empty JOptional if dictionary is None or the searched key result is None, otherwise a JOptional
        with a present value
    """
    if non_none(dictionary) and not is_dict(dictionary):
        raise TypeError("Optional[dict[K, V]] parameter is required")

    return JOptional \
        .of_noneable(dictionary) \
        .map(lambda d: d.get(key))


def get_value(
        dictionary: Optional[dict[K, V]], key: K, default_supplier: Supplier[Optional[V]] = lambda: None
) -> Optional[V]:
    """
    Returns the value from a dict with the given key if presents, otherwise returns the result produced by the supplying
    function

    Args:
        dictionary: The dict
        key: The searched key
        default_supplier: The supplying function that produces a value to be returned

    Returns:
        Optional[V]: The value, if present, otherwise the result produced by the supplying function (even if dictionary
        is None)

    """
    return get_joptional_value(dictionary, key).or_else_get(default_supplier)


def get_value_from_path(
        dictionary: Optional[dict[K, Any]], path: list[Any], default_supplier: Supplier[Optional[V]] = lambda: None
) -> Optional[V]:
    """
    Returns the value from a deep dict (dict of dicts) with the given key path if present, otherwise returns the result
    produced by the supplying function

    Args:
        dictionary: The dict
        path: The searched key path
        default_supplier: The supplying function that produces a value to be returned

    Returns:
        Optional[V]: The value, if present, otherwise the result produced by the supplying function (even if dictionary
        is None)
    """
    if non_none(dictionary) and not is_dict(dictionary):
        raise TypeError("Optional[dict[K, V]] parameter is required")

    if not path:
        return default_supplier()

    if len(path) == 1:
        return get_value(dictionary, path[0], default_supplier)

    current_path_value: Any = get_value(dictionary, path[0])
    return get_value_from_path(
        current_path_value,
        path[1:],
        default_supplier
    ) if is_dict(current_path_value) else default_supplier()
