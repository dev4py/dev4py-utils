"""awaitables module tests"""
import asyncio
from asyncio import Task, Future

import pytest

from dev4py.utils import awaitables


class TestIsAwaitable:
    """is_awaitable function tests"""

    class TestNominalCase:
        def test_none__should__return_false(self) -> None:
            """When value is None should return False"""
            # GIVEN / WHEN
            result: bool = awaitables.is_awaitable(None)

            # THEN
            assert not result

        @pytest.mark.asyncio
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

        @pytest.mark.asyncio
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

        @pytest.mark.asyncio
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
