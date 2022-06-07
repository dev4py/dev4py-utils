"""
The `objects` module provides a set of utility functions to simplify objects/variables operations or checks
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

from typing import Any, Optional, cast, Awaitable

from dev4py.utils.awaitables import is_awaitable
from dev4py.utils.types import Supplier, T, SyncOrAsync


def is_none(obj: Any) -> bool:
    """
    Checks if the given object is None

    Args:
        obj: The object to check

    Returns:
        object: True if obj is None, False otherwise
    """
    return obj is None


def non_none(obj: Any) -> bool:
    """
    Checks if the given object is not None

    Args:
        obj: The object to check

    Returns:
        object: True if obj is NOT None, False otherwise
    """
    return obj is not None


def require_non_none(obj: Optional[T], message: str = "None object error") -> T:
    """
    Checks if the given object is not None or raises an error

    Args:
        obj: The object to check
        message: The error message is case of obj is None

    Returns:
        object: obj if obj is not None

    Raises:
        TypeError: Raises a TypeError if obj is None
    """
    if is_none(obj):
        raise TypeError(message)
    return cast(T, obj)


def require_non_none_else(obj: Optional[T], default: T) -> T:
    """
    Checks if the given object is not None and returns it or returns the default one

    Args:
        obj: The object to check and return
        default: The default object to return if obj is None

    Returns:
        object: obj if not None, default_obj otherwise

    Raises:
        TypeError: Raises a TypeError if obj and default_obj are None
    """
    return cast(T, obj) if non_none(obj) else require_non_none(default)


def require_non_none_else_get(obj: Optional[T], supplier: Supplier[T]) -> T:
    """
    Checks if the given object is not None and returns it or returns the object from the given supplier

    Args:
        obj: The object to check and return
        supplier: The supplier to call if obj is None

    Returns:
        object: obj if not None, the supplier call result otherwise

    Raises:
        TypeError: Raises a TypeError if obj and supplier or supplied object are None
    """
    return cast(T, obj) if non_none(obj) else require_non_none(require_non_none(supplier, "Supplier cannot be None")())


def to_string(obj: Any, default_str: Optional[str] = None) -> str:
    """
    Returns the result of calling str function for the given object if not null or default_str otherwise

    Args:
        obj: The object to stringify
        default_str: The str value to return if obj is None

    Returns:
        str: A str representing obj, default_str otherwise
    """
    return str(obj if non_none(obj) else default_str)


async def async_require_non_none(obj: SyncOrAsync[T], message: str = "None async object error") -> T:
    """
    Checks if the given object or awaitable object result is not None or raises an error

    Args:
        obj: The object or awaitable object to check
        message: The error message is case of obj or awaitable obj is None

    Returns:
        object: obj if obj is not None and not an Awaitable or Awaitable result if obj is an awaitable and the result is
        not None

    Raises:
        TypeError: Raises a TypeError if obj is None or if obj is an awaitable with None result
    """
    return require_non_none(await cast(Awaitable[T], obj) if is_awaitable(obj) else cast(T, obj), message)


async def async_require_non_none_else(obj: SyncOrAsync[Optional[T]], default: T) -> T:
    """
    Checks if the given object or awaitable object result is not None and returns it or returns the default one

    Args:
        obj: The object or awaitable object to check
        default: The default object to return if obj is None

    Returns:
        object:obj if obj is not None and not an Awaitable or Awaitable result if obj is an awaitable and the result is
        not None, default_obj otherwise

    Raises:
        TypeError: Raises a TypeError if obj (or await obj) and default_obj are None
    """
    return require_non_none_else(
        await cast(Awaitable[Optional[T]], obj) if is_awaitable(obj) else cast(Optional[T], obj),
        default
    )


async def async_require_non_none_else_get(obj: SyncOrAsync[Optional[T]], supplier: Supplier[T]) -> T:
    """
    Checks if the given object or awaitable object result is not None and returns it or returns the object from the
    given supplier

    Args:
        obj: The object or awaitable object to check
        supplier: The supplier to call if obj or awaitable obj result is None

    Returns:
        object: obj if not None and not an Awaitable or Awaitable result if obj is an awaitable and the result is
        not None, the supplier call result otherwise

    Raises:
        TypeError: Raises a TypeError if obj (or await obj)  and supplier or supplied object are None
    """
    return require_non_none_else_get(
        await cast(Awaitable[Optional[T]], obj) if is_awaitable(obj) else cast(Optional[T], obj),
        supplier
    )


def to_none(*args: Any, **kwargs: Any) -> None:  # pylint: disable=W0613
    """
    Returns None whatever the parameters

    Args:
        *args: positional parameters
        **kwargs: named parameters

    Returns:
        None: None whatever the parameters
    """
    return None


def to_self(obj: T) -> T:
    """
    Returns the given parameter
    Note: can be useful with multiprocessing where lambda cannot be used (lambda are not serializable)

    Args:
        obj: The object to return

    Returns:
        obj (T): The given parameter
    """
    return obj
