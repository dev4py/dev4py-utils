"""The `retry` module provides tools to create retryable callable using exponential backoff"""

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
from asyncio import sleep as async_sleep
from dataclasses import dataclass
from functools import partial, wraps
from time import sleep
from typing import Callable, Awaitable, Union, Optional, cast

from dev4py.utils.objects import require_non_none, is_none
from dev4py.utils.types import T, P, Function


##############################
#     PUBLIC MODULE CLASS    #
##############################
@dataclass(frozen=True)
class RetryConfiguration:
    """
    RetryConfiguration class that represents a retry configuration

    A retry configuration describes:
        * The maximum number of tries (first try included. I.e.: 1 means no retry on failure)
        * The exponential backoff elements (exponent & delay)
            Note: exponential backoff (/ waiting_interval) = delay * (exponent^retry_number)

    Args:
        exponent (int): the exponential backoff exponent / an arbitrary multiplier to determine delay between each try
            (default = 2)
        delay (float): the exponential backoff delay in second / the initial wait for the first retry (default = 0.1)
        max_tries (int): max try number (first try included) (default = 3, i.e.: first try and 2 retry)

    Raises:
        TypeError: if exponent or delay or max_tries is None
        ValueError: if exponent or delay is less than 0 or max_tries is less than 1
    """
    exponent: int = 2
    delay: float = 0.1  # seconds
    max_tries: int = 3

    def get_waiting_interval(self, retry_number: int) -> float:
        """
        Returns the waiting interval in second in case of a retry occurs
        Args:
            retry_number: the current retry number

        Returns:
            float: the waiting interval in second for the given `retry_numbers`

        Raises:
            TypeError: if retry_number is None
            ValueError: if retry_number is lesser than or equals to 0 or retry_number greater than max_tries
        """
        if require_non_none(retry_number) <= 0:
            raise ValueError('retry_number must be greater than 0')

        if retry_number > self.max_tries:
            raise ValueError('retry_number greater than configured max_tries')

        return self.delay * (self.exponent ** retry_number)

    def __post_init__(self):
        if require_non_none(self.exponent, "exponent must be non None") < 0:
            raise ValueError("exponent must be greater than or equals to 0")
        if require_non_none(self.delay, "delay must be non None") < 0:
            raise ValueError("delay must be greater than or equals to 0")
        if require_non_none(self.max_tries, "max_tries must be non None") < 1:
            raise ValueError("max_tries must be greater than or equals to 1")


##############################
#  PRIVATE MODULE FUNCTIONS  #
##############################
def _default_retry_on_failure(exception: BaseException) -> T:
    """
    Default value for on_failure parameter
    Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)

    Args:
        exception: The on failure exception

    Raises:
        Exception: the given exception
    """
    raise exception


def _with_retry(
        sync_callable: Callable[P, T],
        retry_config: RetryConfiguration,
        on_failure: Function[BaseException, T],
        retry_number: int,
        *args: P.args,
        **kwargs: P.kwargs
) -> T:
    """
    Used to define a retryable function from `sync_callable` parameter by using the RetryConfig, on_failure and
    retry_number parameters

    Note: inner functions are not used in order to be compatible with multiprocessing
    """
    if retry_number > 0:
        sleep(retry_config.get_waiting_interval(retry_number))

    try:
        return sync_callable(*args, **kwargs)
    except BaseException as e:  # pylint: disable=W0703
        retry_number += 1  # pragma: no mutate

        if retry_number >= retry_config.max_tries:
            return on_failure(e)

        return _with_retry(sync_callable, retry_config, on_failure, retry_number, *args, **kwargs)


async def _with_async_retry(
        async_callable: Callable[P, Awaitable[T]],
        retry_config: RetryConfiguration,
        on_failure: Function[BaseException, T],
        retry_number: int,
        *args: P.args,
        **kwargs: P.kwargs
) -> T:
    """
    Used to define a retryable function from `async_callable` parameter by using the RetryConfig, on_failure and
    retry_number parameters

    Note: inner functions are not used in order to be compatible with multiprocessing
    """
    if retry_number > 0:
        await async_sleep(retry_config.get_waiting_interval(retry_number))

    try:
        return await async_callable(*args, **kwargs)
    except BaseException as e:  # pylint: disable=W0703
        retry_number += 1  # pragma: no mutate

        if retry_number >= retry_config.max_tries:
            return on_failure(e)

        return await _with_async_retry(async_callable, retry_config, on_failure, retry_number, *args, **kwargs)


##############################
#      PUBLIC FUNCTIONS      #
##############################

def retryable(
        sync_callable: Optional[Callable[P, T]] = None,
        retry_config: RetryConfiguration = RetryConfiguration(),
        on_failure: Function[BaseException, T] = _default_retry_on_failure
) -> Union[Callable[P, T], Function[Callable[P, T], Callable[P, T]]]:
    """
    SINCE: 3.5.0: a `to_retryable` equivalent that can also be used as decorator

    Transforms a callable to a retryable one by using the given RetryConfiguration

    If an error occurs when executing the returned callable the call is retried by using the given RetryConfiguration.
    An exponential backoff is used in order to determinate the waiting time between each call. If max_tries is reached
    then the on_failure function is called in order to return a default value or raise an exception. By default, it
    raises the last raised exception

    Args:
        sync_callable: The callable to transform
        retry_config: The given RetryConfiguration
        on_failure: The action to perform if max_tries is reached (Note: can return a default value)

    Returns:
        Function[Callable[P, T], Callable[P, T]]: Corresponding to a partial `to_retryable` function filled with
            `retry_config` and `on_failure` parameters if sync_callable is None

        Callable[P, Awaitable[T]]: The retryable callable (is equivalent to `to_retryable` call) if sync_callable is not
            None

    Raises:
        TypeError: if retry_config or on_failure is None
    """
    require_non_none(retry_config)
    require_non_none(on_failure)

    def _retryable_decorator(func: Callable[P, T]) -> Callable[P, T]:
        require_non_none(func)

        @wraps(func)
        def _retryable_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            return _with_retry(func, retry_config, on_failure, 0, *args, **kwargs)

        return _retryable_wrapper

    return _retryable_decorator if is_none(sync_callable) else _retryable_decorator(cast(Callable[P, T], sync_callable))


def to_retryable(
        sync_callable: Callable[P, T] = None,
        *,
        retry_config: RetryConfiguration = RetryConfiguration(),
        on_failure: Function[BaseException, T] = _default_retry_on_failure
) -> Callable[P, T]:
    """
    Transforms a callable to a retryable one by using the given RetryConfiguration

    If an error occurs when executing the returned callable the call is retried by using the given RetryConfiguration.
    An exponential backoff is used in order to determinate the waiting time between each call. If max_tries is reached
    then the on_failure function is called in order to return a default value or raise an exception. By default, it
    raises the last raised exception

    Args:
        sync_callable: The callable to transform
        retry_config: The given RetryConfiguration
        on_failure: The action to perform if max_tries is reached (Note: can return a default value)

    Returns:
        Callable[P, T]: The retryable callable

    Raises:
        TypeError: if sync_callable or retry_config or on_failure is None
    """
    require_non_none(sync_callable)
    require_non_none(retry_config)
    require_non_none(on_failure)
    return partial(_with_retry, *[sync_callable, retry_config, on_failure, 0])


def async_retryable(
        async_callable: Optional[Callable[P, Awaitable[T]]] = None,
        *,
        retry_config: RetryConfiguration = RetryConfiguration(),
        on_failure: Function[BaseException, T] = _default_retry_on_failure
) -> Union[Function[Callable[P, Awaitable[T]], Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """
    SINCE: 3.5.0: a `to_async_retryable` equivalent that can also be used as decorator

    Transforms an async callable to an async retryable one by using the given RetryConfiguration

    If an error occurs when executing the returned callable the call is retried by using the given RetryConfiguration.
    An exponential backoff is used in order to determinate the waiting time between each call. If max_tries is reached
    then the on_failure function is called in order to return a default value or raise an exception. By default, it
    raises the last raised exception

    Args:
        async_callable: The async callable to transform
        retry_config: The given RetryConfiguration
        on_failure: The action to perform if max_tries is reached (Note: can return a default value)

    Returns:
        Function[Callable[P, Awaitable[T]], Callable[P, Awaitable[T]]]: Corresponding to a partial `to_async_retryable`
            function filled with `retry_config` and `on_failure` parameters if async_callable is None

        Callable[P, Awaitable[T]]: The async retryable callable (is equivalent to `to_async_retryable` call) if
            async_callable is not None

    Raises:
        TypeError: if retry_config or on_failure is None
    """
    require_non_none(retry_config)
    require_non_none(on_failure)

    def _async_retryable_decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        require_non_none(func)

        @wraps(func)
        def _async_retryable_wrapper(*args: P.args, **kwargs: P.kwargs) -> Awaitable[T]:
            return _with_async_retry(func, retry_config, on_failure, 0, *args, **kwargs)

        return _async_retryable_wrapper

    return _async_retryable_decorator if is_none(async_callable) else \
        _async_retryable_decorator(cast(Callable[P, Awaitable[T]], async_callable))


def to_async_retryable(
        async_callable: Callable[P, Awaitable[T]],
        retry_config: RetryConfiguration = RetryConfiguration(),
        on_failure: Function[BaseException, T] = _default_retry_on_failure
) -> Callable[P, Awaitable[T]]:
    """
    Transforms an async callable to an async retryable one by using the given RetryConfiguration

    If an error occurs when executing the returned callable the call is retried by using the given RetryConfiguration.
    An exponential backoff is used in order to determinate the waiting time between each call. If max_tries is reached
    then the on_failure function is called in order to return a default value or raise an exception. By default, it
    raises the last raised exception

    Args:
        async_callable: The async callable to transform
        retry_config: The given RetryConfiguration
        on_failure: The action to perform if max_tries is reached (Note: can return a default value)

    Returns:
        Callable[P, Awaitable[T]]: The async retryable callable

    Raises:
        TypeError: if async_callable or retry_config or on_failure is None
    """
    require_non_none(async_callable)
    require_non_none(retry_config)
    require_non_none(on_failure)
    return partial(_with_async_retry, *[async_callable, retry_config, on_failure, 0])
