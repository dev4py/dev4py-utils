"""The `AsyncJOptional` class provides is like the `JOptional` one but simplify the use of Awaitable values"""

from __future__ import annotations

from typing import Generic, Final, Optional, TypeAlias, cast, Any, Awaitable, TypeVar

from dev4py.utils.awaitables import is_awaitable
from dev4py.utils.objects import async_require_non_none, non_none, is_none, require_non_none
from dev4py.utils.types import T, SyncOrAsync, Supplier, Function, R, Consumer, Runnable, Predicate

V = TypeVar('V')
_VType: TypeAlias = SyncOrAsync[Optional[V]]


class AsyncJOptional(Generic[T]):
    __CREATE_KEY: Final[object] = object()
    __NO_VALUE_ERROR_MSG: Final[str] = "No value present"
    __EMPTY: AsyncJOptional[Any]

    @classmethod
    def of(cls, value: _VType[T]) -> AsyncJOptional[T]:
        return AsyncJOptional(async_require_non_none(value, cls.__NO_VALUE_ERROR_MSG), cls.__CREATE_KEY)

    @classmethod
    def of_noneable(cls, value: _VType[T]) -> AsyncJOptional[T]:
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
        if is_awaitable(self._value):
            self._value = await cast(Awaitable[Optional[T]], self._value)
        return cast(Optional[T], self._value)

    async def is_present(self) -> bool:
        return non_none(await self._get_value())

    async def is_empty(self) -> bool:
        return is_none(await self._get_value())

    def get(self) -> Awaitable[T]:
        return self.or_else_raise()

    def or_else(self, other: Optional[T] = None) -> Awaitable[Optional[T]]:
        return self.or_else_get(lambda: other)

    async def or_else_get(self, supplier: Supplier[Optional[T]] = lambda: None) -> Optional[T]:
        return cast(Optional[T], self._value if await self.is_present() else supplier())

    async def or_else_raise(
            self,
            supplier: Supplier[Exception] = lambda: cast(Exception, ValueError(AsyncJOptional.__NO_VALUE_ERROR_MSG))
    ) -> T:
        if await self.is_empty():
            raise supplier()
        return cast(T, self._value)

    def or_get(self, supplier: Supplier[AsyncJOptional[T]]) -> AsyncJOptional[T]:
        require_non_none(supplier)

        async def _async_or_get(current: AsyncJOptional[T], suppl: Supplier[AsyncJOptional[T]]) -> Optional[T]:
            return await current.get() if await current.is_present() else await require_non_none(suppl()).or_else_get()

        return AsyncJOptional.of_noneable(_async_or_get(self, supplier))

    def map(self, mapper: Function[T, _VType[R]]) -> AsyncJOptional[R]:
        require_non_none(mapper)
        return self.flat_map(lambda v: AsyncJOptional.of_noneable(mapper(v)))

    def flat_map(self, mapper: Function[T, AsyncJOptional[R]]) -> AsyncJOptional[R]:
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
        # pylint: disable=W0106
        (await self.is_present()) and consumer(cast(T, self._value))

    async def if_empty(self, empty_action: Runnable) -> None:
        # pylint: disable=W0106
        (await self.is_empty()) and empty_action()

    async def if_present_or_else(self, consumer: Consumer[T], empty_action: Runnable) -> None:
        # pylint: disable=W0106
        consumer(cast(T, self._value)) if await self.is_present() else empty_action()

    def filter(self, predicate: Predicate[T]) -> AsyncJOptional[T]:
        require_non_none(predicate)

        async def _async_filter(current: AsyncJOptional[T]) -> Optional[T]:
            return await current.or_else_get() if await current.is_empty() or predicate(await current.get()) else None

        return AsyncJOptional.of_noneable(_async_filter(self))

    def peek(self, consumer: Consumer[T]) -> AsyncJOptional[T]:
        require_non_none(consumer)

        async def _async_peek(current: AsyncJOptional[T], cons: Consumer[T]) -> Optional[T]:
            await current.if_present(cons)
            return await current.or_else_get()

        return AsyncJOptional.of_noneable(_async_peek(self, consumer))


# INIT STATIC VARIABLES
# noinspection PyProtectedMember
# noinspection PyUnresolvedReferences
# pylint: disable=W0212
AsyncJOptional._AsyncJOptional__EMPTY = AsyncJOptional(None, AsyncJOptional._AsyncJOptional__CREATE_KEY)  # type: ignore
