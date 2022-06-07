"""AsyncJOptional module tests"""

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

from typing import Final, Optional, cast, Awaitable
from unittest.mock import patch, MagicMock

from pytest import raises

from dev4py.utils import AsyncJOptional, JOptional
from dev4py.utils.awaitables import to_awaitable, async_none
from dev4py.utils.types import Supplier, Function, Consumer, Runnable, Predicate


class TestAsyncJOptional:
    """AsyncJOptional class tests"""
    NO_VALUE_ERROR_MSG: Final[str] = "No value present"
    CONSTRUCTOR_ERROR_MSG: Final[str] = \
        "AsyncJOptional private constructor! Please use AsyncJOptional.of or AsyncJOptional.of_noneable"

    class TestConstructor:
        """Constructor tests"""

        class TestNominalCase:

            def test_none_create_key__should__raise_assertion_error(self):
                """When create key is none, should raise AssertionError with private constructor message"""
                # GIVEN / WHEN / THEN
                with raises(AssertionError) as error:
                    AsyncJOptional("A value", None)

                assert str(error.value) == TestAsyncJOptional.CONSTRUCTOR_ERROR_MSG

            def test_invalid_create_key__should__raise_assertion_error(self):
                """When create key is invalid, should raise AssertionError with private constructor message"""
                # GIVEN / WHEN / THEN
                with raises(AssertionError) as error:
                    AsyncJOptional("A value", object())

                assert str(error.value) == TestAsyncJOptional.CONSTRUCTOR_ERROR_MSG

            async def test_valid_create_key__should__create_a_new_async_joptional(self):
                """When create key is valid, should create a new AsyncJOptional"""
                # GIVEN
                value: int = 1

                # WHEN
                # noinspection PyUnresolvedReferences
                optional: AsyncJOptional[int] = AsyncJOptional(value, AsyncJOptional._AsyncJOptional__CREATE_KEY)

                # THEN
                assert await optional.is_present()
                assert await optional.get() == value

    class TestOf:
        """of class method tests"""

        class TestNominalCase:
            async def test_value_exists__should__return_async_joptional_with_value(self) -> None:
                """When a value is provided, should return an async joptional with value"""
                # GIVEN
                value: int = 1

                # WHEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(value)

                # THEN
                assert await optional.is_present()
                assert await optional.get() == value

            async def test_async_value_exists__should__return_async_joptional_with_value(self) -> None:
                """When an async value is provided, should return an async joptional with value"""
                # GIVEN
                value: int = 1

                # WHEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(to_awaitable(value))

                # THEN
                assert await optional.is_present()
                assert await optional.get() == value

        class TestErrorCase:
            async def test_none_value__should__raise_type_error_on_terminal_operation(self) -> None:
                """When no value is provided, should raise a TypeError exception on terminal operation"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(None)

                # WHEN / THEN
                with raises(TypeError) as error:
                    await optional.get()

                assert str(error.value) == TestAsyncJOptional.NO_VALUE_ERROR_MSG

            async def test_async_none_value__should__raise_type_error_on_terminal_operation(self) -> None:
                """When async none value is provided, should raise a TypeError exception on terminal operation"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(async_none())

                # WHEN / THEN
                with raises(TypeError) as error:
                    await optional.get()

                assert str(error.value) == TestAsyncJOptional.NO_VALUE_ERROR_MSG

    class TestOfNoneable:
        """of_noneable class method tests"""

        class TestNominalCase:
            async def test_value_exists__should__return_async_joptional_with_value(self) -> None:
                """When a value is provided, should return an async joptional with value"""
                # GIVEN
                value: int = 1

                # WHEN
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(value)

                # THEN
                assert await optional.is_present()
                assert await optional.get() == value

            async def test_async_value_exists__should__return_async_joptional_with_value(self) -> None:
                """When an async value is provided, should return an async joptional with value"""
                # GIVEN
                value: int = 1

                # WHEN
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(to_awaitable(value))

                # THEN
                assert await optional.is_present()
                assert await optional.get() == value

            async def test_none_value__should__return_empty_async_joptional(self) -> None:
                """When no value is provided, should return an empty async joptional"""
                # GIVEN
                value: Optional[int] = None

                # WHEN
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(value)

                # THEN
                assert optional._value == value
                assert await optional.is_empty()

            async def test_async_none_value__should__return_empty_async_joptional(self) -> None:
                """When async None value is provided, should return an empty async joptional"""
                # GIVEN / WHEN
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_none())

                # THEN
                assert await optional.is_empty()
                assert await optional.or_else_get() is None

    class TestEmpty:
        """empty class method tests"""

        class TestNominalCase:
            async def test_should__return_empty_async_joptional(self) -> None:
                """Should return an async joptional with value"""
                # GIVEN / WHEN
                optional: AsyncJOptional[int] = AsyncJOptional.empty()

                # THEN
                assert optional._value is None
                assert await optional.is_empty()

    class TestIsPresent:
        """is_present method tests"""

        class TestNominalCase:
            async def test_value_exists__should__return_true(self) -> None:
                """When a value is provided, should return true"""
                # GIVEN / WHEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(1)

                # THEN
                assert await optional.is_present()

            async def test_async_value_exists__should__return_true(self) -> None:
                """When an async value is provided, should return true"""
                # GIVEN / WHEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(to_awaitable(1))

                # THEN
                assert await optional.is_present()

            async def test_none_value__should__return_false(self) -> None:
                """When no value is provided, should return false"""
                # GIVEN / WHEN
                optional: AsyncJOptional[int] = AsyncJOptional.empty()

                # THEN
                assert not await optional.is_present()

            async def test_async_none_value__should__return_false(self) -> None:
                """When async None value is provided, should return false"""
                # GIVEN / WHEN
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_none())

                # THEN
                assert not await optional.is_present()

    class TestIsEmpty:
        """is_empty method tests"""

        class TestNominalCase:
            async def test_value_exists__should__return_false(self) -> None:
                """When a value is provided, should return false"""
                # GIVEN / WHEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(1)

                # THEN
                assert not await optional.is_empty()

            async def test_async_value_exists__should__return_false(self) -> None:
                """When an async value is provided, should return false"""
                # GIVEN / WHEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(to_awaitable(1))

                # THEN
                assert not await optional.is_empty()

            async def test_none_value__should__return_true(self) -> None:
                """When no value is provided, should return true"""
                # GIVEN / WHEN
                optional: AsyncJOptional[int] = AsyncJOptional.empty()

                # THEN
                assert await optional.is_empty()

            async def test_async_none_value__should__return_true(self) -> None:
                """When async None value is provided, should return true"""
                # GIVEN / WHEN
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_none())

                # THEN
                assert await optional.is_empty()

    class TestGet:
        """get method tests"""

        class TestNominalCase:
            async def test_value_exists__should__return_value(self) -> None:
                """When value is provided, return the value"""
                # GIVEN
                value: int = 1
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(value)

                # WHEN
                result: int = await optional.get()

                # THEN
                assert result == value

            async def test_async_value_exists__should__return_value(self) -> None:
                """When async value is provided, return the value"""
                # GIVEN
                value: int = 1
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(to_awaitable(value))

                # WHEN
                result: int = await optional.get()

                # THEN
                assert result == value

        class TestErrorCase:
            async def test_none_value__should__raise_type_error(self) -> None:
                """When no value is provided, should raise a ValueError exception with no value message"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.empty()

                # WHEN / THEN
                with raises(ValueError) as error:
                    await optional.get()

                assert str(error.value) == TestAsyncJOptional.NO_VALUE_ERROR_MSG

            async def test_async_none_value__should__raise_type_error(self) -> None:
                """When async None value is provided, should raise a ValueError exception with no value message"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_none())

                # WHEN / THEN
                with raises(ValueError) as error:
                    await optional.get()

                assert str(error.value) == TestAsyncJOptional.NO_VALUE_ERROR_MSG

    class TestOrElse:
        """or_else method tests"""

        class TestNominalCase:
            async def test_value_exists__should__return_value(self) -> None:
                """When value is provided, return the value"""
                # GIVEN
                value: int = 1
                default_value: int = 2
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(value)

                # WHEN
                result: int = await optional.or_else(default_value)

                # THEN
                assert result == value

            async def test_async_value_exists__should__return_value(self) -> None:
                """When async value is provided, return the value"""
                # GIVEN
                value: int = 1
                default_value: int = 2
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(to_awaitable(value))

                # WHEN
                result: int = await optional.or_else(default_value)

                # THEN
                assert result == value

            async def test_none_value__should__return_default_value(self) -> None:
                """When no value is provided, return the default value"""
                # GIVEN
                default_value: int = 2
                optional: AsyncJOptional[int] = AsyncJOptional.empty()

                # WHEN
                result: int = await optional.or_else(default_value)

                # THEN
                assert result == default_value

            async def test_async_none_value__should__return_default_value(self) -> None:
                """When async None value is provided, return the default value"""
                # GIVEN
                default_value: int = 2
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_none())

                # WHEN
                result: int = await optional.or_else(default_value)

                # THEN
                assert result == default_value

            async def test_none_value_and_none_default__should__return_none(self) -> None:
                """When no value is provided and default value is None, return the default value"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.empty()

                # WHEN
                result: Optional[int] = await optional.or_else(None)

                # THEN
                assert result is None

            async def test_async_none_value_and_none_default__should__return_none(self) -> None:
                """When async None value is provided and default value is None, return the default value"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_none())

                # WHEN
                result: Optional[int] = await optional.or_else(None)

                # THEN
                assert result is None

            async def test_none_value_and_no_default__should__return_none(self) -> None:
                """When no value is provided and no default value, return None value"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.empty()

                # WHEN
                result: Optional[int] = await optional.or_else()

                # THEN
                assert result is None

            async def test_async_none_value_and_no_default__should__return_none(self) -> None:
                """When async None value is provided and no default value, return None value"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_none())

                # WHEN
                result: Optional[int] = await optional.or_else()

                # THEN
                assert result is None

    class TestOrElseGet:
        """or_else_get method tests"""

        class TestNominalCase:
            async def test_value_exists__should__return_value(self) -> None:
                """When value is provided, return the value"""
                # GIVEN
                value: int = 1
                supplier: Supplier[int] = lambda: 2
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(value)

                # WHEN
                result: int = await optional.or_else_get(supplier)

                # THEN
                assert result == value

            async def test_async_value_exists__should__return_value(self) -> None:
                """When async value is provided, return the value"""
                # GIVEN
                value: int = 1
                supplier: Supplier[int] = lambda: 2
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(to_awaitable(value))

                # WHEN
                result: int = await optional.or_else_get(supplier)

                # THEN
                assert result == value

            async def test_none_value__should__return_supplied_value(self) -> None:
                """When no value is provided, return the supplied default value"""
                # GIVEN
                default_value: int = 2
                supplier: Supplier[int] = lambda: default_value
                optional: AsyncJOptional[int] = AsyncJOptional.empty()

                # WHEN
                result: int = await optional.or_else_get(supplier)

                # THEN
                assert result == default_value

            async def test_async_none_value__should__return_supplied_value(self) -> None:
                """When async None value is provided, return the supplied default value"""
                # GIVEN
                default_value: int = 2
                supplier: Supplier[int] = lambda: default_value
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_none())

                # WHEN
                result: int = await optional.or_else_get(supplier)

                # THEN
                assert result == default_value

            async def test_none_value_and_no_supplier__should__return_none_value(self) -> None:
                """When no value is provided, return the supplied default value"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.empty()

                # WHEN
                result: Optional[int] = await optional.or_else_get()

                # THEN
                assert result is None

            async def test_async_none_value_and_no_supplier__should__return_none_value(self) -> None:
                """When async None value is provided, return the supplied default value"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_none())

                # WHEN
                result: Optional[int] = await optional.or_else_get()

                # THEN
                assert result is None

        class TestErrorCase:
            async def test_none_value_and_none_supplier__should__raise_type_error(self) -> None:
                """When no value is provided, should raise a TypeError exception"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.empty()

                # WHEN / THEN
                with raises(TypeError):
                    await optional.or_else_get(None)

            async def test_async_none_value_and_none_supplier__should__raise_type_error(self) -> None:
                """When async None value is provided, should raise a TypeError exception"""
                # GIVEN
                async_value: Awaitable[None] = async_none()
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_value)

                # WHEN / THEN
                with raises(TypeError):
                    await optional.or_else_get(None)

                await optional.or_else_get()  # Remove warning

            async def test_value_exists_and_none_supplier__should__raise_type_error(self) -> None:
                """When value is provided but supplier is none, should raise a TypeError exception"""
                # GIVEN
                value: int = 1
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(value)

                # WHEN / THEN
                with raises(TypeError):
                    await optional.or_else_get(None)

                await optional.or_else_get()  # Remove warning

            async def test_async_value_exists_and_none_supplier__should__raise_type_error(self) -> None:
                """When async value is provided but supplier is none, should raise a TypeError exception"""
                # GIVEN
                value: Awaitable[int] = to_awaitable(1)
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(value)

                # WHEN / THEN
                with raises(TypeError):
                    await optional.or_else_get(None)

                await value  # Remove warning

    class TestOrElseRaise:
        """or_else_raise method tests"""

        class TestNominalCase:
            async def test_value_exists__should__return_value(self) -> None:
                """When value is provided, return the value"""
                # GIVEN
                value: int = 1
                supplier: Supplier[Exception] = lambda: ValueError("Test error message")
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(value)

                # WHEN
                result: int = await optional.or_else_raise(supplier)

                # THEN
                assert result == value

            async def test_async_value_exists__should__return_value(self) -> None:
                """When async value is provided, return the value"""
                # GIVEN
                value: int = 1
                supplier: Supplier[Exception] = lambda: ValueError("Test error message")
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(to_awaitable(value))

                # WHEN
                result: int = await optional.or_else_raise(supplier)

                # THEN
                assert result == value

            async def test_none_value__should__raise_supplied_exception(self) -> None:
                """When no value is provided, raise the supplied exception"""
                # GIVEN
                given_error: Exception = ValueError("Test error message")
                supplier: Supplier[Exception] = lambda: given_error
                optional: AsyncJOptional[int] = AsyncJOptional.empty()

                # WHEN / THEN
                with raises(ValueError) as error:
                    await optional.or_else_raise(supplier)

                assert str(error.value) == str(given_error)

            async def test_async_none_value__should__raise_supplied_exception(self) -> None:
                """When async None value is provided, raise the supplied exception"""
                # GIVEN
                given_error: Exception = ValueError("Test error message")
                supplier: Supplier[Exception] = lambda: given_error
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_none())

                # WHEN / THEN
                with raises(ValueError) as error:
                    await optional.or_else_raise(supplier)

                assert str(error.value) == str(given_error)

        class TestErrorCase:
            async def test_none_value_and_none_supplier__should__raise_type_error(self) -> None:
                """When no value and no supplier are provided, should raise a TypeError exception"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.empty()

                # WHEN / THEN
                with raises(TypeError):
                    await optional.or_else_raise(None)

            async def test_async_none_value_and_none_supplier__should__raise_type_error(self) -> None:
                """When async None value and no supplier are provided, should raise a TypeError exception"""
                # GIVEN
                async_value: Awaitable[None] = async_none()
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_value)

                # WHEN / THEN
                with raises(TypeError):
                    await optional.or_else_raise(None)

                await optional.or_else_get()  # Remove warning

            async def test_value_exists_and_none_supplier__should__raise_type_error(self) -> None:
                """When value is provided but supplier is none, should raise a TypeError exception"""
                # GIVEN
                value: int = 1
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(value)

                # WHEN / THEN
                with raises(TypeError):
                    await optional.or_else_raise(None)

                await optional.or_else_get()  # Remove warning

            async def test_async_value_exists_and_none_supplier__should__raise_type_error(self) -> None:
                """When async value is provided but supplier is none, should raise a TypeError exception"""
                # GIVEN
                value: Awaitable[int] = to_awaitable(1)
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(value)

                # WHEN / THEN
                with raises(TypeError):
                    await optional.or_else_raise(None)

                await value  # Remove warning

    class TestOrGet:
        """or_get method tests"""

        class TestNominalCase:
            async def test_value_exists__should__return_self_value_async_joptional(self) -> None:
                """When value is provided, return the self value AsyncJOptional"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(1)
                supplier: Supplier[AsyncJOptional[int]] = lambda: AsyncJOptional.of(2)

                # WHEN
                result: AsyncJOptional[int] = optional.or_get(supplier)

                # THEN
                assert await result.get() == 1

            async def test_async_value_exists__should__return_self_value_async_joptional(self) -> None:
                """When async value is provided, return the self value AsyncJOptional"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(to_awaitable(1))
                supplier: Supplier[AsyncJOptional[int]] = lambda: AsyncJOptional.of(2)

                # WHEN
                result: AsyncJOptional[int] = optional.or_get(supplier)

                # THEN
                assert await result.get() == 1

            async def test_none_value__should__return_supplied_async_joptional(self) -> None:
                """When value is not provided, return the supplied default AsyncJOptional"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.empty()
                other: AsyncJOptional[int] = AsyncJOptional.of(2)
                supplier: Supplier[AsyncJOptional[int]] = lambda: other

                # WHEN
                result: AsyncJOptional[int] = optional.or_get(supplier)

                # THEN
                assert await result.get() == 2

            async def test_async_none_value__should__return_supplied_async_joptional(self) -> None:
                """When provided value is async None, return the supplied default AsyncJOptional"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_none())
                other: AsyncJOptional[int] = AsyncJOptional.of(2)
                supplier: Supplier[AsyncJOptional[int]] = lambda: other

                # WHEN
                result: AsyncJOptional[int] = optional.or_get(supplier)

                # THEN
                assert await result.get() == 2

        class TestErrorCase:
            async def test_value_exists_and_none_supplier__should__raise_type_error(self) -> None:
                """When value is provided but supplier is not, should raise a TypeError exception"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(1)

                # WHEN / THEN
                with raises(TypeError):
                    optional.or_get(None)

                await optional.or_else_get()  # Remove warning

            async def test_async_value_exists_and_none_supplier__should__raise_type_error(self) -> None:
                """When async value is provided but supplier is not, should raise a TypeError exception"""
                # GIVEN
                async_value: Awaitable[int] = to_awaitable(1)
                optional: AsyncJOptional[int] = AsyncJOptional.of(async_value)

                # WHEN / THEN
                with raises(TypeError):
                    optional.or_get(None)

                await optional.or_else_get()  # Remove warning

            def test_none_value_and_none_supplier__should__raise_type_error(self) -> None:
                """When no value and no supplier are provided, should raise a TypeError exception"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.empty()

                # WHEN / THEN
                with raises(TypeError):
                    optional.or_get(None)

            async def test_async_none_value_and_none_supplier__should__raise_type_error(self) -> None:
                """When async None value and no supplier are provided, should raise a TypeError exception"""
                # GIVEN
                async_value: Awaitable[None] = to_awaitable(1)
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_value)

                # WHEN / THEN
                with raises(TypeError):
                    optional.or_get(None)

                await optional.or_else_get()  # Remove warning

    class TestMap:
        """map method tests"""

        class TestNominalCase:
            async def test_value_exists__should__async_joptional_of_mapped_value(self) -> None:
                """When value is provided, should apply the given mapper"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(1)
                mapper: Function[int, str] = lambda i: f"Str value is: '{i}'"

                # WHEN
                result: AsyncJOptional[str] = optional.map(mapper)

                # THEN
                assert await result.is_present()
                assert await result.get() == "Str value is: '1'"

            async def test_async_value_exists__should__async_joptional_of_mapped_value(self) -> None:
                """When async value is provided, should apply the given mapper"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(to_awaitable(1))
                mapper: Function[int, str] = lambda i: f"Str value is: '{i}'"

                # WHEN
                result: AsyncJOptional[str] = optional.map(mapper)

                # THEN
                assert await result.is_present()
                assert await result.get() == "Str value is: '1'"

            async def test_value_exists_with_async_mapper__should__async_joptional_of_mapped_value(self) -> None:
                """When value is provided with async mapper, should apply the given mapper"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(1)

                async def async_mapper(i: int) -> str:
                    return f"Str value is: '{i}'"

                # WHEN
                result: AsyncJOptional[str] = optional.map(async_mapper)

                # THEN
                assert await result.is_present()
                assert await result.get() == "Str value is: '1'"

            async def test_async_value_exists_with_async_mapper__should__async_joptional_of_mapped_value(self) -> None:
                """When async value is provided with async mapper, should apply the given mapper"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(to_awaitable(1))

                async def async_mapper(i: int) -> str:
                    return f"Str value is: '{i}'"

                # WHEN
                result: AsyncJOptional[str] = optional.map(async_mapper)

                # THEN
                assert await result.is_present()
                assert await result.get() == "Str value is: '1'"

            async def test_value_exists_and_none_mapper_result__should__empty(self) -> None:
                """When value is provided but None mapper result, should return an empty AsyncJOptional"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(1)
                mapper: Function[int, None] = lambda i: None

                # WHEN
                result: AsyncJOptional[str] = optional.map(mapper)

                # THEN
                assert await result.is_empty()

            async def test_async_value_exists_and_none_mapper_result__should__empty(self) -> None:
                """When async value is provided but None mapper result, should return an empty AsyncJOptional"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(to_awaitable(1))
                mapper: Function[int, None] = lambda i: None

                # WHEN
                result: AsyncJOptional[str] = optional.map(mapper)

                # THEN
                assert await result.is_empty()

            async def test_value_exists_and_async_none_mapper_result__should__empty(self) -> None:
                """When value is provided but async None mapper result, should return an empty AsyncJOptional"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(1)
                mapper: Function[int, Awaitable[None]] = lambda i: async_none()

                # WHEN
                result: AsyncJOptional[str] = optional.map(mapper)

                # THEN
                assert await result.is_empty()

            async def test_async_value_exists_and_async_none_mapper_result__should__empty(self) -> None:
                """When async value is provided but async None mapper result, should return an empty AsyncJOptional"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(to_awaitable(1))
                mapper: Function[int, Awaitable[None]] = lambda i: async_none()

                # WHEN
                result: AsyncJOptional[str] = optional.map(mapper)

                # THEN
                assert await result.is_empty()

            async def test_none_value__should__return_empty(self) -> None:
                """When value is not provided, should return an empty AsyncJOptional"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.empty()
                mapper: Function[int, str] = lambda i: f"Str value is: '{i}'"

                # WHEN
                result: AsyncJOptional[str] = optional.map(mapper)

                # THEN
                assert await result.is_empty()

            async def test_async_none_value__should__return_empty(self) -> None:
                """When async None value is provided, should return an empty AsyncJOptional"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_none())
                mapper: Function[int, str] = lambda i: f"Str value is: '{i}'"

                # WHEN
                result: AsyncJOptional[str] = optional.map(mapper)

                # THEN
                assert await result.is_empty()

        class TestErrorCase:
            async def test_value_exists_and_none_mapper__should__raise_type_error(self) -> None:
                """When value is provided but mapper is not, should raise a TypeError exception"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(1)

                # WHEN / THEN
                with raises(TypeError):
                    optional.map(None)

                await optional.or_else_get()  # Remove warning

            async def test_async_value_exists_and_none_mapper__should__raise_type_error(self) -> None:
                """When async value is provided but mapper is not, should raise a TypeError exception"""
                # GIVEN
                async_value: Awaitable[int] = to_awaitable(1)
                optional: AsyncJOptional[int] = AsyncJOptional.of(async_value)

                # WHEN / THEN
                with raises(TypeError):
                    optional.map(None)

                await optional.or_else_get()  # Remove warning

            async def test_none_value_and_none_mapper__should__raise_type_error(self) -> None:
                """When value and mapper are not provided, should raise a TypeError exception"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.empty()

                # WHEN / THEN
                with raises(TypeError):
                    optional.map(None)

            async def test_async_none_value_and_none_mapper__should__raise_type_error(self) -> None:
                """When async none value is provided and mapper is None, should raise a TypeError exception"""
                # GIVEN
                async_value: Awaitable[int] = async_none()
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_value)

                # WHEN / THEN
                with raises(TypeError):
                    optional.map(None)

                await optional.or_else_get()  # Remove warning

    class TestFlatMap:
        """flat_map method tests"""

        class TestNominalCase:
            async def test_value_exists__should__async_joptional_of_mapped_value(self) -> None:
                """When value is provided, should apply the given mapper"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(1)
                mapper: Function[int, AsyncJOptional[str]] = \
                    lambda v: AsyncJOptional.of_noneable(v).map(lambda i: f"Str value is: '{i}'")

                # WHEN
                result: AsyncJOptional[str] = optional.flat_map(mapper)

                # THEN
                assert await result.is_present()
                assert await result.get() == "Str value is: '1'"

            async def test_async_value_exists__should__async_joptional_of_mapped_value(self) -> None:
                """When async value is provided, should apply the given mapper"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(to_awaitable(1))
                mapper: Function[int, AsyncJOptional[str]] = \
                    lambda v: AsyncJOptional.of_noneable(v).map(lambda i: f"Str value is: '{i}'")

                # WHEN
                result: AsyncJOptional[str] = optional.flat_map(mapper)

                # THEN
                assert await result.is_present()
                assert await result.get() == "Str value is: '1'"

            async def test_none_value__should__return_empty(self) -> None:
                """When value is not provided, should return an empty AsyncJOptional"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.empty()
                mapper: Function[int, AsyncJOptional[str]] = \
                    lambda v: AsyncJOptional.of_noneable(v).map(lambda i: f"Str value is: '{i}'")

                # WHEN
                result: AsyncJOptional[str] = optional.flat_map(mapper)

                # THEN
                assert await result.is_empty()

            async def test_async_none_value__should__return_empty(self) -> None:
                """When async None value is provided, should return an empty AsyncJOptional"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_none())
                mapper: Function[int, AsyncJOptional[str]] = \
                    lambda v: AsyncJOptional.of_noneable(v).map(lambda i: f"Str value is: '{i}'")

                # WHEN
                result: AsyncJOptional[str] = optional.flat_map(mapper)

                # THEN
                assert await result.is_empty()

        class TestErrorCase:
            async def test_value_exists_and_none_mapper__should__raise_type_error(self) -> None:
                """When value is provided but mapper is not, should raise a TypeError exception"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(1)

                # WHEN / THEN
                with raises(TypeError):
                    optional.flat_map(None)

                await optional.or_else_get()  # Remove warning

            async def test_async_value_exists_and_none_mapper__should__raise_type_error(self) -> None:
                """When async value is provided but mapper is not, should raise a TypeError exception"""
                # GIVEN
                async_value: Awaitable[int] = to_awaitable(1)
                optional: AsyncJOptional[int] = AsyncJOptional.of(async_value)

                # WHEN / THEN
                with raises(TypeError):
                    optional.flat_map(None)

                await optional.or_else_get()  # Remove warning

            async def test_none_value_and_none_mapper__should__raise_type_error(self) -> None:
                """When value and mapper are not provided, should raise a TypeError exception"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.empty()

                # WHEN / THEN
                with raises(TypeError):
                    optional.flat_map(None)

            async def test_async_none_value_and_none_mapper__should__raise_type_error(self) -> None:
                """When async None value is provided and mapper is None, should raise a TypeError exception"""
                # GIVEN
                async_value: Awaitable[None] = async_none()
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_value)

                # WHEN / THEN
                with raises(TypeError):
                    optional.flat_map(None)

                await optional.or_else_get()  # Remove warning

            async def test_value_exists_and_none_mapper_result__should__raise_type_error_on_terminal_operation(
                    self
            ) -> None:
                """
                When value exists and mapper returns None, should raise a TypeError exception on terminal operation
                """
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(1)

                # WHEN / THEN
                with raises(TypeError):
                    await optional.flat_map(lambda v: None).or_else_get()

            async def test_async_value_exists_and_none_mapper_result__should__raise_type_error_on_terminal_operation(
                    self
            ) -> None:
                """
                When async value exists and mapper returns None, should raise a TypeError exception on terminal
                operation
                """
                # GIVEN
                async_value: Awaitable[int] = to_awaitable(1)
                optional: AsyncJOptional[int] = AsyncJOptional.of(async_value)

                # WHEN / THEN
                with raises(TypeError):
                    await optional.flat_map(lambda v: None).or_else_get()

    class TestIfPresent:
        """if_present method tests"""

        class TestNominalCase:

            @patch('builtins.print')
            async def test_value_exists__should__call_given_consumer(self, print_mock: MagicMock) -> None:
                """When value is provided, should call the given consumer"""
                # GIVEN
                value: int = 1
                optional: AsyncJOptional[int] = AsyncJOptional.of(value)
                consumer: Consumer[[int]] = print

                # WHEN
                await optional.if_present(consumer)

                # THEN
                print_mock.assert_called_once_with(value)

            @patch('builtins.print')
            async def test_async_value_exists__should__call_given_consumer(self, print_mock: MagicMock) -> None:
                """When async value is provided, should call the given consumer"""
                # GIVEN
                value: int = 1
                optional: AsyncJOptional[int] = AsyncJOptional.of(to_awaitable(value))
                consumer: Consumer[[int]] = print

                # WHEN
                await optional.if_present(consumer)

                # THEN
                print_mock.assert_called_once_with(value)

            @patch('builtins.print')
            async def test_none_value__should__do_nothing(self, print_mock: MagicMock) -> None:
                """When no value is provided, should do nothing"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.empty()
                consumer: Consumer[[int]] = print

                # WHEN
                await optional.if_present(consumer)

                # THEN
                print_mock.assert_not_called()

            @patch('builtins.print')
            async def test_async_none_value__should__do_nothing(self, print_mock: MagicMock) -> None:
                """When async None value is provided, should do nothing"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_none())
                consumer: Consumer[[int]] = print

                # WHEN
                await optional.if_present(consumer)

                # THEN
                print_mock.assert_not_called()

        class TestErrorCase:
            async def test_value_exists_and_none_consumer__should__raise_type_error(self) -> None:
                """When value is provided but consumer is not, should raise a TypeError exception"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(1)

                # WHEN / THEN
                with raises(TypeError):
                    await optional.if_present(None)

                await optional.or_else_get()  # Remove warning

            async def test_async_value_exists_and_none_consumer__should__raise_type_error(self) -> None:
                """When async value is provided but consumer is not, should raise a TypeError exception"""
                # GIVEN
                async_value: Awaitable[int] = to_awaitable(1)
                optional: AsyncJOptional[int] = AsyncJOptional.of(async_value)

                # WHEN / THEN
                with raises(TypeError):
                    await optional.if_present(None)

                await optional.or_else_get()  # Remove warning

            async def test_none_value_and_none_consumer__should__raise_type_error(self) -> None:
                """When no value and no consumer are provided, should raise a TypeError exception"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.empty()

                # WHEN / THEN
                with raises(TypeError):
                    await optional.if_present(None)

            async def test_async_none_value_and_none_consumer__should__raise_type_error(self) -> None:
                """When async None value and no consumer are provided, should raise a TypeError exception"""
                # GIVEN
                async_value: Awaitable[None] = async_none()
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_value)

                # WHEN / THEN
                with raises(TypeError):
                    await optional.if_present(None)

                await optional.or_else_get()  # Remove warning

    class TestIfEmpty:
        """if_empty method tests"""

        class TestNominalCase:

            @patch('builtins.print')
            async def test_value_exists__should__do_nothing(self, print_mock: MagicMock) -> None:
                """When value is provided, should do nothing"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(1)
                runnable: Runnable = lambda: print("A test message")

                # WHEN
                await optional.if_empty(runnable)

                # THEN
                print_mock.assert_not_called()

            @patch('builtins.print')
            async def test_async_value_exists__should__do_nothing(self, print_mock: MagicMock) -> None:
                """When async value is provided, should do nothing"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(to_awaitable(1))
                runnable: Runnable = lambda: print("A test message")

                # WHEN
                await optional.if_empty(runnable)

                # THEN
                print_mock.assert_not_called()

            @patch('builtins.print')
            async def test_none_value__should__call_given_runnable(self, print_mock: MagicMock) -> None:
                """When no value is provided, should call the given runnable"""
                # GIVEN
                message: str = "A test message"
                optional: AsyncJOptional[int] = AsyncJOptional.empty()
                runnable: Runnable = lambda: print(message)

                # WHEN
                await optional.if_empty(runnable)

                # THEN
                print_mock.assert_called_once_with(message)

            @patch('builtins.print')
            async def test_async_none_value__should__call_given_runnable(self, print_mock: MagicMock) -> None:
                """When async None value is provided, should call the given runnable"""
                # GIVEN
                message: str = "A test message"
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_none())
                runnable: Runnable = lambda: print(message)

                # WHEN
                await optional.if_empty(runnable)

                # THEN
                print_mock.assert_called_once_with(message)

        class TestErrorCase:
            async def test_none_value_and_none_runnable__should__raise_type_error(self) -> None:
                """When no value and no runnable are provided, should raise TypeError exception"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.empty()

                # WHEN / THEN
                with raises(TypeError):
                    await optional.if_empty(cast(Runnable, None))

            async def test_async_none_value_and_none_runnable__should__raise_type_error(self) -> None:
                """When async None value and no runnable are provided, should raise TypeError exception"""
                # GIVEN
                async_value: Awaitable[None] = async_none()
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_value)

                # WHEN / THEN
                with raises(TypeError):
                    await optional.if_empty(cast(Runnable, None))

                await optional.or_else_get()  # Remove warning

            async def test_value_exists_and_none_runnable__should__raise_type_error(self) -> None:
                """When value is provided but runnable is not, should raise TypeError exception"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(1)

                # WHEN / THEN
                with raises(TypeError):
                    await optional.if_empty(cast(Runnable, None))

                await optional.or_else_get()  # Remove warning

            async def test_async_value_exists_and_none_runnable__should__raise_type_error(self) -> None:
                """When async value is provided but runnable is not, should do nothing"""
                # GIVEN
                async_value: Awaitable[int] = to_awaitable(1)
                optional: AsyncJOptional[int] = AsyncJOptional.of(async_value)

                # WHEN / THEN
                with raises(TypeError):
                    await optional.if_empty(cast(Runnable, None))

                await optional.or_else_get()  # Remove warning

    class TestIfPresentOrElse:
        """if_present_or_else method tests"""

        class TestNominalCase:
            @patch('builtins.print')
            async def test_value_exists__should__call_given_consumer(self, print_mock: MagicMock) -> None:
                """When value is provided, should call the given consumer"""
                # GIVEN
                value: int = 1
                optional: AsyncJOptional[int] = AsyncJOptional.of(value)
                consumer: Consumer[[int]] = print
                runnable: Runnable = lambda: print("A test message")

                # WHEN
                await optional.if_present_or_else(consumer, runnable)

                # THEN
                print_mock.assert_called_once_with(value)

            @patch('builtins.print')
            async def test_async_value_exists__should__call_given_consumer(self, print_mock: MagicMock) -> None:
                """When async value is provided, should call the given consumer"""
                # GIVEN
                value: int = 1
                optional: AsyncJOptional[int] = AsyncJOptional.of(to_awaitable(value))
                consumer: Consumer[[int]] = print
                runnable: Runnable = lambda: print("A test message")

                # WHEN
                await optional.if_present_or_else(consumer, runnable)

                # THEN
                print_mock.assert_called_once_with(value)

            @patch('builtins.print')
            async def test_none_value__should__call_given_runnable(self, print_mock: MagicMock) -> None:
                """When value is not provided, should call the given runnable"""
                # GIVEN
                message: str = "A test message"
                optional: AsyncJOptional[int] = AsyncJOptional.empty()
                consumer: Consumer[[int]] = print
                runnable: Runnable = lambda: print("A test message")

                # WHEN
                await optional.if_present_or_else(consumer, runnable)

                # THEN
                print_mock.assert_called_once_with(message)

            @patch('builtins.print')
            async def test_async_none_value__should__call_given_runnable(self, print_mock: MagicMock) -> None:
                """When async None value provided, should call the given runnable"""
                # GIVEN
                message: str = "A test message"
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_none())
                consumer: Consumer[[int]] = print
                runnable: Runnable = lambda: print("A test message")

                # WHEN
                await optional.if_present_or_else(consumer, runnable)

                # THEN
                print_mock.assert_called_once_with(message)

        class TestErrorCase:
            async def test_value_exists_and_none_consumer__should__raise_type_error(self) -> None:
                """When value is provided but consumer is None, should raise a TypeError exception"""
                # GIVEN
                value: int = 1
                optional: AsyncJOptional[int] = AsyncJOptional.of(value)
                runnable: Runnable = lambda: print("A test message")

                # WHEN / THEN
                with raises(TypeError):
                    await optional.if_present_or_else(None, runnable)

                await optional.or_else_get()  # Remove warning

            async def test_async_value_exists_and_none_consumer__should__raise_type_error(self) -> None:
                """When async value is provided but consumer is None, should raise a TypeError exception"""
                # GIVEN
                async_value: Awaitable[int] = to_awaitable(1)
                optional: AsyncJOptional[int] = AsyncJOptional.of(async_value)
                runnable: Runnable = lambda: print("A test message")

                # WHEN / THEN
                with raises(TypeError):
                    await optional.if_present_or_else(None, runnable)

                await optional.or_else_get()  # Remove warning

            async def test_value_exists_and_none_consumer_and_runnable__should__raise_type_error(self) -> None:
                """When value is provided but consumer and runnable are None, should raise a TypeError exception"""
                # GIVEN
                value: int = 1
                optional: AsyncJOptional[int] = AsyncJOptional.of(value)

                # WHEN / THEN
                with raises(TypeError):
                    await optional.if_present_or_else(None, cast(Runnable, None))

                await optional.or_else_get()  # Remove warning

            async def test_async_value_exists_and_none_consumer_and_runnable__should__raise_type_error(self) -> None:
                """
                When async value is provided but consumer and runnable are None, should raise a TypeError exception
                """
                # GIVEN
                async_value: Awaitable[int] = to_awaitable(1)
                optional: AsyncJOptional[int] = AsyncJOptional.of(to_awaitable(async_value))

                # WHEN / THEN
                with raises(TypeError):
                    await optional.if_present_or_else(None, cast(Runnable, None))

                await optional.or_else_get()  # Remove warning

            async def test_none_value_and_consumer_and_runnable__should__raise_type_error(self) -> None:
                """When value is not provided but consumer and runnable are None, should raise a TypeError exception"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.empty()

                # WHEN / THEN
                with raises(TypeError):
                    await optional.if_present_or_else(None, cast(Runnable, None))

            async def test_async_none_value_and_consumer_and_runnable__should__raise_type_error(self) -> None:
                """
                When async None value is provided but consumer and runnable are None, should raise a TypeError exception
                """
                # GIVEN
                async_value: Awaitable[None] = async_none()
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_value)

                # WHEN / THEN
                with raises(TypeError):
                    await optional.if_present_or_else(None, cast(Runnable, None))

                await optional.or_else_get()  # Remove warning

            async def test_none_value_runnable__should__raise_type_error(self) -> None:
                """When value is not provided and runnable is None, should raise a TypeError exception"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.empty()
                consumer: Consumer[[int]] = print

                # WHEN / THEN
                with raises(TypeError):
                    await optional.if_present_or_else(consumer, cast(Runnable, None))

            async def test_async_none_value_runnable__should__raise_type_error(self) -> None:
                """When async value is not provided and runnable is None, should raise a TypeError exception"""
                # GIVEN
                async_value: Awaitable[None] = async_none()
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_value)
                consumer: Consumer[[int]] = print

                # WHEN / THEN
                with raises(TypeError):
                    await optional.if_present_or_else(consumer, cast(Runnable, None))

                await optional.or_else_get()  # Remove warning

            async def test_value_exists_and_none_runnable__should__raise_type_error(self) -> None:
                """When value is provided but not the runnable, should raise a TypeError exception"""
                # GIVEN
                value: int = 1
                optional: AsyncJOptional[int] = AsyncJOptional.of(value)
                consumer: Consumer[[int]] = print

                # WHEN / THEN
                with raises(TypeError):
                    await optional.if_present_or_else(consumer, cast(Runnable, None))

                await optional.or_else_get()  # Remove warning

            async def test_async_value_exists_and_none_runnable__should__raise_type_error(self) -> None:
                """When async value is provided but not the runnable, should raise a TypeError exception"""
                # GIVEN
                async_value: Awaitable[int] = to_awaitable(1)
                optional: AsyncJOptional[int] = AsyncJOptional.of(to_awaitable(async_value))
                consumer: Consumer[[int]] = print

                # WHEN / THEN
                with raises(TypeError):
                    await optional.if_present_or_else(consumer, cast(Runnable, None))

                await optional.or_else_get()  # Remove warning

            async def test_none_value_and_none_consumer__should__raise_type_error(self) -> None:
                """When value is not provided and consumer is None, should raise a TypeError exception"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.empty()
                runnable: Runnable = lambda: print("A test message")

                # WHEN / THEN
                with raises(TypeError):
                    await optional.if_present_or_else(None, runnable)

            async def test_async_none_value_and_none_consumer__should__raise_type_error(self) -> None:
                """When async None value is provided and consumer is None, should raise a TypeError exception"""
                # GIVEN
                async_value: Awaitable[None] = async_none()
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_value)
                runnable: Runnable = lambda: print("A test message")

                # WHEN / THEN
                with raises(TypeError):
                    await optional.if_present_or_else(None, runnable)

                await optional.or_else_get()  # Remove warning

    class TestFilter:
        """filter method tests"""

        class TestNominalCase:
            async def test_value_with_valid_filter__should__return_async_joptional_with_value(self):
                """When value is present and predicate is valid, should return the AsyncJOptional with value"""
                # GIVEN
                value: int = 7
                predicate: Predicate[int] = lambda i: i > 5
                optional: AsyncJOptional[int] = AsyncJOptional.of(value)

                # WHEN
                result: AsyncJOptional[int] = optional.filter(predicate)

                # THEN
                assert await result.is_present()
                assert await result.get() == value

            async def test_async_value_with_valid_filter__should__return_async_joptional_with_value(self):
                """When async value is present and predicate is valid, should return the AsyncJOptional with value"""
                # GIVEN
                value: int = 7
                predicate: Predicate[int] = lambda i: i > 5
                optional: AsyncJOptional[int] = AsyncJOptional.of(to_awaitable(value))

                # WHEN
                result: AsyncJOptional[int] = optional.filter(predicate)

                # THEN
                assert await result.is_present()
                assert await result.get() == value

            async def test_value_without_valid_filter__should__return_empty(self):
                """When value is present and predicate is not valid, should return empty AsyncJOptional"""
                # GIVEN
                value: int = 7
                predicate: Predicate[int] = lambda i: i < 5
                optional: AsyncJOptional[int] = AsyncJOptional.of(value)

                # WHEN
                result: AsyncJOptional[int] = optional.filter(predicate)

                # THEN
                assert await result.is_empty()

            async def test_async_value_without_valid_filter__should__return_empty(self):
                """When async value is present and predicate is not valid, should return empty AsyncJOptional"""
                # GIVEN
                value: int = 7
                predicate: Predicate[int] = lambda i: i < 5
                optional: AsyncJOptional[int] = AsyncJOptional.of(to_awaitable(value))

                # WHEN
                result: AsyncJOptional[int] = optional.filter(predicate)

                # THEN
                assert await result.is_empty()

            async def test_empty_value__should__return_empty(self):
                """When value is empty, should return empty AsyncJOptional"""
                # GIVEN
                predicate: Predicate[int] = lambda i: i < 5
                optional: AsyncJOptional[int] = AsyncJOptional.empty()

                # WHEN
                result: AsyncJOptional[int] = optional.filter(predicate)

                # THEN
                assert await result.is_empty()

            async def test_async_none_value__should__return_empty(self):
                """When value is async None, should return empty AsyncJOptional"""
                # GIVEN
                predicate: Predicate[int] = lambda i: i < 5
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_none())

                # WHEN
                result: AsyncJOptional[int] = optional.filter(predicate)

                # THEN
                assert await result.is_empty()

        class TestErrorCase:
            async def test_value_exists_and_predicate_is_none__should__raise_type_error(self) -> None:
                """When value is provided but predicate is None, should raise a TypeError exception"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(1)

                # WHEN / THEN
                with raises(TypeError):
                    optional.filter(None)

                await optional.or_else_get()  # Remove warning

            async def test_async_value_exists_and_predicate_is_none__should__raise_type_error(self) -> None:
                """When async value is provided but predicate is None, should raise a TypeError exception"""
                # GIVEN
                async_value: Awaitable[int] = to_awaitable(1)
                optional: AsyncJOptional[int] = AsyncJOptional.of(async_value)

                # WHEN / THEN
                with raises(TypeError):
                    optional.filter(None)

                await optional.or_else_get()  # Remove warning

            async def test_empty_value_and_none_predicate__should__raise_type_error(self):
                """When value is empty and predicate is None, should raise a TypeError exception"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.empty()

                # WHEN / THEN
                with raises(TypeError):
                    optional.filter(None)

            async def test_async_none_value_and_none_predicate__should__raise_type_error(self):
                """When value is async None and predicate is None, should raise a TypeError exception"""
                # GIVEN
                async_value: Awaitable[int] = async_none()
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_value)

                # WHEN / THEN
                with raises(TypeError):
                    optional.filter(None)

                await optional.or_else_get()  # Remove warning

    class TestPeek:
        """peek method tests"""

        class TestNominalCase:

            @patch('builtins.print')
            async def test_value_exists__should__call_given_consumer_on_terminal_operation(
                    self, print_mock: MagicMock
            ) -> None:
                """When value is provided, should call the given consumer on terminal operation"""
                # GIVEN
                value: int = 1
                optional: AsyncJOptional[int] = AsyncJOptional.of(value)
                consumer: Consumer[[int]] = print

                # WHEN
                result: AsyncJOptional[int] = optional.peek(consumer)

                # THEN
                assert await result.get() == await optional.get()
                print_mock.assert_called_once_with(value)

            @patch('builtins.print')
            async def test_async_value_exists__should__call_given_consumer_on_terminal_operation(
                    self, print_mock: MagicMock
            ) -> None:
                """When async value is provided, should call the given consumer on terminal operation"""
                # GIVEN
                value: int = 1
                optional: AsyncJOptional[int] = AsyncJOptional.of(to_awaitable(value))
                consumer: Consumer[[int]] = print

                # WHEN
                result: AsyncJOptional[int] = optional.peek(consumer)

                # THEN
                assert await result.get() == await optional.get()
                print_mock.assert_called_once_with(value)

            @patch('builtins.print')
            async def test_none_value__should__do_nothing_on_terminal_operation(self, print_mock: MagicMock) -> None:
                """When no value is provided, should do nothing on terminal operation"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.empty()
                consumer: Consumer[[int]] = print

                # WHEN
                result: AsyncJOptional[int] = optional.peek(consumer)

                # THEN
                assert await result.or_else_get() == await optional.or_else_get()
                print_mock.assert_not_called()

            @patch('builtins.print')
            async def test_async_none_value__should__do_nothing_on_terminal_operation(
                    self, print_mock: MagicMock
            ) -> None:
                """When async None value is provided, should do nothing on terminal operation"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_none())
                consumer: Consumer[[int]] = print

                # WHEN
                result: AsyncJOptional[int] = optional.peek(consumer)

                # THEN
                assert await result.or_else_get() == await optional.or_else_get()
                print_mock.assert_not_called()

        class TestErrorCase:
            async def test_value_exists_and_none_consumer__should__raise_type_error(self) -> None:
                """When value is provided but consumer is not, should raise a TypeError exception"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.of(1)

                # WHEN / THEN
                with raises(TypeError):
                    optional.peek(None)

                await optional.or_else_get()  # Remove warning

            async def test_async_value_exists_and_none_consumer__should__raise_type_error(self) -> None:
                """When async value is provided but consumer is not, should raise a TypeError exception"""
                # GIVEN
                async_value: Awaitable[int] = to_awaitable(1)
                optional: AsyncJOptional[int] = AsyncJOptional.of(async_value)

                # WHEN / THEN
                with raises(TypeError):
                    optional.peek(None)

                await optional.or_else_get()  # Remove warning

            def test_none_value_and_none_consumer__should__raise_type_error(self) -> None:
                """When no value and no consumer are provided, should raise a TypeError exception"""
                # GIVEN
                optional: AsyncJOptional[int] = AsyncJOptional.empty()

                # WHEN / THEN
                with raises(TypeError):
                    optional.peek(None)

            async def test_async_none_value_and_none_consumer__should__raise_type_error(self) -> None:
                """When async None value and no consumer are provided, should raise a TypeError exception"""
                # GIVEN
                async_value: Awaitable[None] = async_none()
                optional: AsyncJOptional[int] = AsyncJOptional.of_noneable(async_value)

                # WHEN / THEN
                with raises(TypeError):
                    optional.peek(None)

                await optional.or_else_get()  # Remove warning

    class TestToJOptional:
        """to_joptional method tests"""

        class TestNominalCase:
            async def test_empty__should__return_awaitable_none_joptional(self) -> None:
                """When empty AsyncJOptional should return empty JOptional[Awaitable[None]]"""
                # GIVEN
                async_optional: AsyncJOptional[str] = AsyncJOptional.empty()

                # WHEN
                optional: JOptional[Awaitable[str]] = async_optional.to_joptional()

                # THEN
                assert optional.is_awaitable()
                assert await optional.get() is None

            async def test_async_none_value__should__return_awaitable_none_joptional(self) -> None:
                """When async None value should return empty JOptional[Awaitable[None]]"""
                # GIVEN
                async_optional: AsyncJOptional[str] = AsyncJOptional.of_noneable(async_none())

                # WHEN
                optional: JOptional[Awaitable[str]] = async_optional.to_joptional()

                # THEN
                assert optional.is_awaitable()
                assert await optional.get() is None

            async def test_str_value__should__return_awaitable_str_joptional(self) -> None:
                """When str value should return an JOptional[Awaitable[str]] with value"""
                # GIVEN
                value: str = "A test value"
                async_optional: AsyncJOptional[str] = AsyncJOptional.of(value)

                # WHEN
                optional: JOptional[Awaitable[str]] = async_optional.to_joptional()

                # THEN
                assert optional.is_awaitable()
                assert await optional.get() == value

            async def test_async_str_value__should__return_awaitable_str_joptional(self) -> None:
                """When async str value should return an JOptional[Awaitable[str]] with value"""
                # GIVEN
                value: str = "A test value"
                async_optional: AsyncJOptional[str] = AsyncJOptional.of(to_awaitable(value))

                # WHEN
                optional: JOptional[Awaitable[str]] = async_optional.to_joptional()

                # THEN
                assert optional.is_awaitable()
                assert await optional.get() == value
