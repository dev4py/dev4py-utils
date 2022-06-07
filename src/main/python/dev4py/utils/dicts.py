"""
The `dicts` module provides a set of utility functions to simplify dict operations
"""

# Copyright 2022 the original author or authors (i.e.: St4rG00se for Dev4py).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from functools import partial
from typing import Optional, Any

from dev4py.utils.JOptional import JOptional
from dev4py.utils.objects import non_none, require_non_none, to_none
from dev4py.utils.types import K, V, Supplier


def is_dict(value: Any) -> bool:
    """
    If the given value is a dict, returns true, otherwise false

    Returns:
        bool: true if the given value is a dict, otherwise false
    """
    return isinstance(value, dict)


def _get_value(dictionary: dict[K, V], key: K) -> Optional[V]:
    """
    private function to replace get_joptional_value lambda
    Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)
    """
    # lambda d: d.get(key)
    return dictionary.get(key)


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
        .map(partial(_get_value, key=key))


def get_value(
        dictionary: Optional[dict[K, V]], key: K, default_supplier: Supplier[Optional[V]] = to_none
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
        dictionary: Optional[dict[K, Any]], path: list[Any], default_supplier: Supplier[Optional[V]] = to_none
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

    Raises:
        TypeError: if dictionary is not None and not a dict
    """
    if non_none(dictionary) and not is_dict(dictionary):
        raise TypeError("Optional[dict[K, V]] dictionary parameter must be a dict or None value")

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


def put_value(dictionary: dict[K, V], key: K, value: V) -> Optional[V]:
    """
    Associates the specified value with the specified key in the given map. If the map previously contained a mapping
    for the key, the old value is returned and replaced by the specified value

    Args:
        dictionary: The dict
        key: The key with which the specified value is to be associated
        value: The value to be associated with the specified key

    Returns:
        Optional[V]: The previous value associated with key, or None if there was no mapping for key.

    Raises:
        TypeError: if dictionary is not a dict
    """
    if not is_dict(dictionary):
        raise TypeError("dictionary must be a dict value")

    result: Optional[V] = dictionary.get(key)
    dictionary[key] = value
    return result


def empty_dict() -> dict[Any, Any]:
    """
    Returns an empty dict
    Returns:
        dict[Any, Any]: an empty dict
    """
    return {}


def update(dict_1: dict[K, V], dict_2: dict[K, V]) -> dict[K, V]:
    """
    Adds all elements of the second dict to the first one and returns it

    Args:
        dict_1: The dict where add elements
        dict_2: The dict with elements to add

    Returns:
        dict_1 (dict[K, V]): The first dict with added elements from dict_2

    Raises:
        TypeError: if dict_1 or dict_2 is None
    """
    require_non_none(dict_1).update(require_non_none(dict_2))
    return dict_1
