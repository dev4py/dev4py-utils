"""awaitables module tests"""

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


import asyncio
from asyncio import Task, Future
from typing import Awaitable

from pytest import raises

from dev4py.utils import awaitables
from dev4py.utils.types import Function, SyncOrAsync


class TestIsAwaitable:
    """is_awaitable function tests"""

    class TestNominalCase:
        def test_none__should__return_false(self) -> None:
            """When value is None should return False"""
            # GIVEN / WHEN
            result: bool = awaitables.is_awaitable(None)

            # THEN
            assert not result

        async def test_coroutine_value__should__return_true(self) -> None:
            """When value is a Coroutine should return True"""

            # GIVEN
            async def coroutine() -> None: ...

            value = coroutine()

            # WHEN
            result: bool = awaitables.is_awaitable(value)

            # THEN
            assert result
            await value  # Remove warning

        async def test_task_value__should__return_true(self) -> None:
            """When value is a Task should return True"""

            # GIVEN
            async def coroutine() -> None: ...

            value: Task = asyncio.create_task(coroutine())

            # WHEN
            result: bool = awaitables.is_awaitable(value)

            # THEN
            assert result
            await value  # Remove warning

        async def test_future_value__should__return_true(self) -> None:
            """When value is a Future should return True"""

            # GIVEN
            async def coroutine() -> None: ...

            value: Future = asyncio.ensure_future(coroutine())

            # WHEN
            result: bool = awaitables.is_awaitable(value)

            # THEN
            assert result
            await value  # Remove warning

        def test_not_awaitable_value__should__return_false(self) -> None:
            """When value is not an awaitable should return False"""
            # GIVEN / WHEN
            result: bool = awaitables.is_awaitable("A string")

            # THEN
            assert not result


class TestToSyncOrAsyncParamFunction:
    """to_sync_or_async_param_function function tests"""

    class TestNominalCase:

        async def test_sync_param_function__should__return_sync_or_async_param_async_function(self) -> None:
            """When given Function uses sync parameter, should return an async function with SyncOrAsync parameter"""
            # GIVEN
            param_value: str = "A string"
            sync_param_function: Function[str, str] = lambda s: s + '_suffix'

            # WHEN
            result_function: Function[SyncOrAsync[str], Awaitable[str]] = \
                awaitables.to_sync_or_async_param_function(sync_param_function)

            # THEN
            # -> Sync parameter call should work
            assert await result_function(param_value) == sync_param_function(param_value)

            # -> Async parameter call should work
            async def async_param_supplier() -> str: return param_value

            assert await result_function(async_param_supplier()) == sync_param_function(param_value)

        async def test_sync_param_async_function__should__return_sync_or_async_param_async_function(self) -> None:
            """When the given Function uses sync parameter and is async (i.e. returns an Awaitable[R]), should return an
            async function with SyncOrAsync parameter with Awaitable[R] result (not an Awaitable[Awaitable[R]])"""
            # GIVEN
            param_value: str = "A string"

            async def async_param_async_function(s: str) -> str: return s + '_suffix'

            # WHEN
            result_function: Function[SyncOrAsync[str], Awaitable[str]] = \
                awaitables.to_sync_or_async_param_function(async_param_async_function)

            # THEN
            # -> Sync parameter call should work
            assert await result_function(param_value) == await async_param_async_function(param_value)

            # -> Async parameter call should work
            async def async_param_supplier() -> str: return param_value

            assert await result_function(async_param_supplier()) == await async_param_async_function(param_value)

    class TestErrorCase:

        def test_none_function__should__raise_type_error(self) -> None:
            """When the function is None, should raise TypeError"""

            # GIVEN / WHEN / THEN
            with raises(TypeError):
                awaitables.to_sync_or_async_param_function(None)

        async def test_async_param_function__should__probably_raise_an_error(self) -> None:
            """When the given Function uses async parameter (i.e. Awaitable[T]), should probably raise an error because
            the wrapper will await the parameter before calling the given function"""

            # GIVEN
            async def async_param_supplier() -> str: return "A string"

            def async_param_function(awaitable: Awaitable[str]) -> str:
                # Do something...
                if not awaitables.is_awaitable(awaitable):
                    raise TypeError()
                return "A result string"

            # WHEN
            result_function: Function[SyncOrAsync[str], Awaitable[str]] = \
                awaitables.to_sync_or_async_param_function(async_param_function)

            # THEN
            async_value: Awaitable[str] = async_param_supplier()
            assert async_param_function(async_value) == "A result string"
            with raises(TypeError):
                await result_function(async_param_supplier())

            await async_value  # Remove warning

        async def test_async_param_async_function__should__probably_raise_an_error(self) -> None:
            """When the given Function uses async parameter (i.e. Awaitable[T]) and is async, should probably raise an
            error because the wrapper will await the parameter before calling the given function"""

            # GIVEN
            async def async_param_supplier() -> str: return "A string"

            async def async_param_async_function(awaitable: Awaitable[str]) -> str:
                return await awaitable

            # WHEN
            result_function: Function[SyncOrAsync[str], Awaitable[str]] = \
                awaitables.to_sync_or_async_param_function(async_param_async_function)

            # THEN
            assert await async_param_async_function(async_param_supplier()) == await async_param_supplier()
            with raises(TypeError):
                await result_function(async_param_supplier())


class TestToAwaitable:
    """to_awaitable function tests"""

    class TestNominalCase:
        async def test_none__should__return_awaitable_of_none(self) -> None:
            """When value is None should return Awaitable[None]"""
            # GIVEN / WHEN
            result: Awaitable[None] = awaitables.to_awaitable(None)

            # THEN
            assert await result is None

        async def test_t_coroutine_value__should__return_t_awaitable(self) -> None:
            """When value is a Coroutine of T should return Awaitable[T]"""

            # GIVEN
            expected_result: int = 1

            async def coroutine() -> int:
                return expected_result

            value = coroutine()

            # WHEN
            result: Awaitable[int] = awaitables.to_awaitable(value)

            # THEN
            assert await result == expected_result

        async def test_t_task_value__should__return_t_awaitable(self) -> None:
            """When value is a Task of T should return Awaitable[T]"""

            # GIVEN
            expected_result: int = 1

            async def coroutine() -> int:
                return expected_result

            value: Task = asyncio.create_task(coroutine())

            # WHEN
            result: Awaitable[int] = awaitables.to_awaitable(value)

            # THEN
            assert await result == expected_result

        async def test_t_future_value__should__return_t_awaitable(self) -> None:
            """When value is a Future of T should return Awaitable[T]"""

            # GIVEN
            expected_result: int = 1

            async def coroutine() -> int:
                return expected_result

            value: Future = asyncio.ensure_future(coroutine())

            # WHEN
            result: Awaitable[int] = awaitables.to_awaitable(value)

            # THEN
            assert await result == expected_result

        async def test_not_awaitable_t_value__should__return_t_awaitable(self) -> None:
            """When value of T is not an awaitable should return Awaitable[T]"""
            # GIVEN
            value: int = 1

            # WHEN
            result: Awaitable[int] = awaitables.to_awaitable(value)

            # THEN
            assert await result == value


class TestAsyncNone:
    """async_none function tests"""

    class TestNominalCase:
        async def test_should__return_awaitable_of_none(self) -> None:
            """Should return Awaitable[None]"""
            # GIVEN / WHEN
            result: Awaitable[None] = awaitables.async_none()

            # THEN
            assert await result is None
