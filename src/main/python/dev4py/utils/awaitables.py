"""
The `awaitables` module provides a set of utility functions to simplify Awaitable operations
"""
from typing import Awaitable, Any, cast

from dev4py.utils import objects
from dev4py.utils.types import T, R, Function, SyncOrAsync


def is_awaitable(value: Any) -> bool:
    """
    If the given value is an Awaitable (Coroutine, Task or Future), returns true, otherwise false

    Returns:
        bool: true if the given value is an Awaitable, otherwise false
    """
    return isinstance(value, Awaitable)


def to_sync_or_async_param_function(
        function: Function[T, SyncOrAsync[R]]
) -> Function[SyncOrAsync[T], Awaitable[R]]:
    """
    If the given Function uses sync parameter, create a new equivalent async function supporting sync or Awaitable
    parameter

    Returned Function specificities:
        1. Is an async function (it means if the given function result is R the new function result is an Awaitable[R])
        2. If the given function is async (i.e. result is an Awaitable[R]), the new function result stay an Awaitable[R]
        3. !WARNING! If the given function expected parameter is an Awaitable, it will be awaited by the wrapper before
        being passed as given function parameter. So, it will probably raise an error depending on your code

    Note: This function can be useful associated with the map function of a `JOptional` with Awaitable value

    Args:
        function: The function with sync parameter

    Returns:
        sync_or_async_param_function: An async function with awaitable parameter

    Raises:
        TypeError: Raises a TypeError if function is None
        Exception: If the given function expected parameter is an Awaitable, it will be awaited by the wrapper before
        being passed as function parameter, and, it will probably raise an error depending on function your code
    """
    objects.require_non_none(function)

    async def sync_or_async_param_function(param: SyncOrAsync[T]) -> R:
        result: SyncOrAsync[R] = function((await cast(Awaitable[T], param)) if is_awaitable(param) else cast(T, param))
        return (await cast(Awaitable[R], result)) if is_awaitable(result) else cast(R, result)

    return sync_or_async_param_function
