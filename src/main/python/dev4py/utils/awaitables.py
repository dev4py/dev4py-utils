"""
The `awaitables` module provides a set of utility functions to simplify Awaitable operations
"""
from typing import Awaitable, Any


def is_awaitable(value: Any) -> bool:
    """
    If the given value is an Awaitable (Coroutine, Task or Future), returns true, otherwise false

    Returns:
        bool: true if the given value is an Awaitable, otherwise false
    """
    return isinstance(value, Awaitable)
