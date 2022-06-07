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
