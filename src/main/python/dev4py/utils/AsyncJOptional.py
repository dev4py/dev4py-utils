"""The `AsyncJOptional` class is like the `JOptional` one but simplify the use of Awaitable values"""

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

from __future__ import annotations

from functools import partial
from typing import Generic, Final, Optional, TypeAlias, cast, Any, Awaitable

from dev4py.utils.JOptional import JOptional
from dev4py.utils.awaitables import is_awaitable
from dev4py.utils.objects import async_require_non_none, non_none, is_none, require_non_none, to_self, to_none
from dev4py.utils.types import T, V, SyncOrAsync, Supplier, Function, R, Consumer, Runnable, Predicate

_VType: TypeAlias = SyncOrAsync[Optional[V]]  # pragma: no mutate


class AsyncJOptional(Generic[T]):
    """A JOptional class for async value mapping"""

    __CREATE_KEY: Final[object] = object()
    __NO_VALUE_ERROR_MSG: Final[str] = "No value present"
    __EMPTY: AsyncJOptional[Any]

    @classmethod
    def of(cls, value: _VType[T]) -> AsyncJOptional[T]:
        """
        Returns a JOptional describing the given non-None value or Awaitable value

        Args:
            value: The value (or Awaitable value) to describe, which must be non-None and not an Awaitable of None

        Returns:
            JOptional[T]: A JOptional of value T or Awaitable[T] type with the value present

        Raises:
            TypeError: Raises a TypeError on terminal operation if value is None or is an Awaitable of None
        """
        return AsyncJOptional(async_require_non_none(value, cls.__NO_VALUE_ERROR_MSG), cls.__CREATE_KEY)

    @classmethod
    def of_noneable(cls, value: _VType[T]) -> AsyncJOptional[T]:
        """
        Returns a JOptional describing the given value or Awaitable value, if non-None, otherwise returns an empty
        AsyncJOptional

        Args:
            value: The possibly-None or Awaitable of None value to describe

        Returns:
            JOptional[T]: A JOptional of value T  or Awaitable[T] type with the value present if the specified value is
            non-None, otherwise an empty AsyncJOptional
        """
        return AsyncJOptional(value, cls.__CREATE_KEY)

    @classmethod
    def empty(cls) -> AsyncJOptional[T]:
        """Return an empty instance of AsyncJOptional"""
        return cls.__EMPTY

    def __init__(self, value: _VType[T], create_key: object):
        """AsyncJOptional private constructor: Constructs an instance with the described value"""
        assert create_key == self.__CREATE_KEY, \
            "AsyncJOptional private constructor! Please use AsyncJOptional.of or AsyncJOptional.of_noneable"
        self._value: _VType[T] = value

    async def _get_value(self) -> Optional[T]:
        """
        Private method in order to manage Sync or Awaitable value

        Returns:
            Optional[T]: the current value
        """
        if is_awaitable(self._value):
            self._value = await cast(Awaitable[Optional[T]], self._value)
        return cast(Optional[T], self._value)

    async def is_present(self) -> bool:
        """
        If a value is present, returns true, otherwise false

        Note: A value is present when not None and not an Awaitable of None

        Returns:
            bool: true if a value is not None and not an Awaitable of None, otherwise false
        """
        return non_none(await self._get_value())

    async def is_empty(self) -> bool:
        """
        If a value is not present, returns true, otherwise false.

        Note: A value is empty when None or an Awaitable of None

        Returns:
            bool: true if a value is None or an Awaitable of None, otherwise false
        """
        return is_none(await self._get_value())

    def get(self) -> Awaitable[T]:
        """
        If a value is present, returns the value, otherwise raises a ValueError

        Returns:
            value: The non-None value described by this AsyncJOptional

        Raises:
            ValueError: Raises a ValueError if the value is empty
        """
        return self.or_else_raise()

    def or_else(self, other: Optional[T] = None) -> Awaitable[Optional[T]]:
        """
        If a value is present, returns the value, otherwise returns other

        Args:
            other: The value to be returned, if no value is present. May be None.

        Returns:
            value: The value, if present, otherwise other
        """
        return self.or_else_get(cast(Supplier[Optional[T]], partial(to_self, obj=other)))

    async def or_else_get(self, supplier: Supplier[Optional[T]] = to_none) -> Optional[T]:
        """
        If a value is present, returns the value, otherwise returns the result produced by the supplying function

        Args:
            supplier: The supplying function that produces a value to be returned

        Returns:
            value: The value, if present, otherwise the result produced by the supplying function

        Raises:
            TypeError: if the supplying function is None
        """
        require_non_none(supplier)
        return cast(Optional[T], self._value if await self.is_present() else supplier())

    @staticmethod  # pragma: no mutate
    def __or_else_raise_supplier_lambda() -> Exception:
        """
        private static method to replace or_else_raise lambda supplier by a function
        Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)
        """
        # lambda: cast(Exception, ValueError(AsyncJOptional.__NO_VALUE_ERROR_MSG))
        return cast(Exception, ValueError(AsyncJOptional.__NO_VALUE_ERROR_MSG))

    async def or_else_raise(
            self,
            supplier: Supplier[Exception] = __or_else_raise_supplier_lambda
    ) -> T:
        """
        If a value is present, returns the value, otherwise raises an exception produced by the exception supplying
        function

        Args:
            supplier: The supplying function that produces an exception to be raised (default: ValueError)

        Returns:
            value: The value, if present

        Raises:
            Exception: If value is empty
            TypeError: if the exception supplying function is None
        """
        require_non_none(supplier)
        if await self.is_empty():
            raise supplier()
        return cast(T, self._value)

    def or_get(self, supplier: Supplier[AsyncJOptional[T]]) -> AsyncJOptional[T]:
        """
        This is the `or` equivalent in java Optional (Reminder: `or` is a python keyword)

        If a value is present, returns an AsyncJOptional describing the value, otherwise returns an AsyncJOptional
        produced by the supplying function

        Args:
            supplier: The supplying function that produces an AsyncJOptional to be returned

        Returns:
            AsyncJOptional[T]: Returns an AsyncJOptional describing the value of this AsyncJOptional, if a value is
            present, otherwise an AsyncJOptional produced by the supplying function

        Raises:
            TypeError: if the supplying function is None
        """
        require_non_none(supplier)

        async def _async_or_get(current: AsyncJOptional[T], suppl: Supplier[AsyncJOptional[T]]) -> Optional[T]:
            return await current.get() if await current.is_present() else await require_non_none(suppl()).or_else_get()

        return AsyncJOptional.of_noneable(_async_or_get(self, supplier))

    @staticmethod  # pragma: no mutate
    def __map_lambda(v: T, mapper: Function[T, _VType[R]]) -> AsyncJOptional[R]:
        """
        private static method to replace inner map lambda supplier by a function
        Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)
        """
        # lambda v: AsyncJOptional.of_noneable(mapper(v))
        return AsyncJOptional.of_noneable(mapper(v))

    def map(self, mapper: Function[T, _VType[R]]) -> AsyncJOptional[R]:
        """
        If a value is present, returns an AsyncJOptional describing (as if by of_noneable) the result of applying the
        given mapping function to the value, otherwise returns an empty AsyncJOptional

        If the mapping function returns a None result then this method returns an empty AsyncJOptional.

        Note: mapping function can be sync or Awaitable (like async coroutine)

        Args:
            mapper: The mapping function to apply to a value, if present

        Returns:
            AsyncJOptional[R]: An AsyncJOptional describing the result of applying a mapping function to the value of
            this AsyncJOptional, if a value is present, otherwise an empty AsyncJOptional

        Raises:
            TypeError: If the mapping function is None
        """
        require_non_none(mapper)
        return self.flat_map(partial(AsyncJOptional.__map_lambda, mapper=mapper))

    def flat_map(self, mapper: Function[T, AsyncJOptional[R]]) -> AsyncJOptional[R]:
        """
        If a value is present, returns the result of applying the given AsyncJOptional-bearing mapping function to the
        value, otherwise returns an empty AsyncJOptional

        This method is similar to map(Function), but the mapping function is one whose result is already an
        AsyncJOptional, and if invoked, flatMap does not wrap it within an additional AsyncJOptional

        Args:
            mapper: The mapping function to apply to a value, if present

        Returns:
            AsyncJOptional[R]: The result of applying a AsyncJOptional-bearing mapping function to the value of this
            AsyncJOptional, if a value is present, otherwise an empty AsyncJOptional

        Raises:
            TypeError: if the mapping function is None
        """
        require_non_none(mapper)

        async def _async_flat_map(
                current: AsyncJOptional[T], flat_mapper: Function[T, AsyncJOptional[R]]
        ) -> Optional[R]:
            if await current.is_present():
                new_async_joptional: AsyncJOptional[R] = require_non_none(flat_mapper(await current.get()))
                return await new_async_joptional.or_else_get()
            return None

        return AsyncJOptional.of_noneable(_async_flat_map(self, mapper))

    async def if_present(self, consumer: Consumer[T]) -> None:
        """
        If a value is present, performs the given consumer with the value, otherwise does nothing

        Args:
            consumer: The consumer to be performed, if a value is present

        Returns:
            Nothing

        Raises:
            TypeError: if the consumer is None
        """
        require_non_none(consumer)
        # pylint: disable=W0106
        (await self.is_present()) and consumer(cast(T, self._value))

    async def if_empty(self, empty_action: Runnable) -> None:
        """
        If a value is not present, performs the given runnable, otherwise does nothing

        Args:
            empty_action: The runnable to be performed, if a value is not present

        Returns:
            Nothing

        Raises:
            TypeError: if the runnable is None
        """
        require_non_none(empty_action)
        # pylint: disable=W0106
        (await self.is_empty()) and empty_action()

    async def if_present_or_else(self, consumer: Consumer[T], empty_action: Runnable) -> None:
        """
        If a value is present, performs the given consumer with the value, otherwise performs the given empty_action

        Args:
            consumer: The consumer to be performed, if a value is present
            empty_action: The runnable to be performed, if a value is not

        Returns:
            Nothing

        Raises:
            TypeError: if the consumer is None or if the runnable is None
        """
        require_non_none(consumer)
        require_non_none(empty_action)
        # pylint: disable=W0106
        consumer(cast(T, self._value)) if await self.is_present() else empty_action()

    def filter(self, predicate: Predicate[T]) -> AsyncJOptional[T]:
        """
        If a value is present, and the value matches the given predicate, returns an AsyncJOptional describing the
        value, otherwise returns an empty AsyncJOptional

        Args:
            predicate: The predicate to apply to a value, if present

        Returns:
            AsyncJOptional[T]: An AsyncJOptional describing the value of this AsyncJOptional, if a value is present and
            the value matches the given predicate, otherwise an empty AsyncJOptional

        Raises:
            TypeError: if the predicate is None
        """
        require_non_none(predicate)

        async def _async_filter(current: AsyncJOptional[T]) -> Optional[T]:
            return await current.or_else_get() if await current.is_empty() or predicate(await current.get()) else None

        return AsyncJOptional.of_noneable(_async_filter(self))

    def peek(self, consumer: Consumer[T]) -> AsyncJOptional[T]:
        """
        If a value is present, performs the given consumer with the value, otherwise does nothing and returns the
        current equivalent of AsyncJOptional

        Args:
            consumer: The consumer to be performed, if a value is present

        Returns:
             AsyncJOptional[T]: The current equivalent of AsyncJOptional

        Raises:
            TypeError: if the consumer is None
        """
        require_non_none(consumer)

        async def _async_peek(current: AsyncJOptional[T], cons: Consumer[T]) -> Optional[T]:
            await current.if_present(cons)
            return await current.or_else_get()

        return AsyncJOptional.of_noneable(_async_peek(self, consumer))

    def to_joptional(self) -> JOptional[Awaitable[Optional[T]]]:
        """
        Convert the current AsyncJOptional to a JOptional

        Note: the returned JOptional will contain an Awaitable[Optional[T]] value

        Returns:
            JOptional[Awaitable[Optional[T]]]: The corresponding JOptional
        """
        return JOptional.of_noneable(cast(Awaitable[Optional[T]], self._get_value()))


# INIT STATIC VARIABLES
# noinspection PyProtectedMember
# noinspection PyUnresolvedReferences
# pylint: disable=W0212
AsyncJOptional._AsyncJOptional__EMPTY = AsyncJOptional(None, AsyncJOptional._AsyncJOptional__CREATE_KEY)  # type: ignore
