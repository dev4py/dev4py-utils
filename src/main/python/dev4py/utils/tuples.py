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

from typing import cast

from dev4py.utils.objects import require_non_none
from dev4py.utils.types import T, Ts, U


def empty_tuple() -> tuple[()]:
    """
    Returns an empty tuple

    Returns:
        tuple[Any, ...]: An empty tuple
    """
    return ()


def append(tpl: tuple[*Ts], value: T) -> tuple[*Ts, T]:
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
    return cast(tuple[*Ts, T], extend(tpl, (value,)))


def extend(tpl_1: tuple[T, ...], tpl_2: tuple[U, ...]) -> tuple[T | U, ...]:
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
