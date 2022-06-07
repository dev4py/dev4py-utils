"""objects module tests"""

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

from typing import Optional, Final

from pytest import raises

from dev4py.utils import objects
from dev4py.utils.types import Supplier


class TestIsNone:
    """is_none function tests"""

    class TestNominalCase:

        def test_none_value__should__return_true(self) -> None:
            """On None value should return True"""
            # GIVEN / WHEN
            result: bool = objects.is_none(None)

            # THEN
            assert result

        def test_non_none_value__should__return_false(self) -> None:
            """On non None value should return False"""
            # GIVEN / WHEN
            result: bool = objects.is_none("A non None value")

            # THEN
            assert not result

        def test_empty_value__should__return_false(self) -> None:
            """On empty value should return False"""
            # GIVEN / WHEN
            result: bool = objects.is_none({})

            # THEN
            assert not result

        def test_false_bool_value__should__return_false(self) -> None:
            """On false boolean value should return False"""
            # GIVEN / WHEN
            result: bool = objects.is_none(False)

            # THEN
            assert not result


class TestNonNone:
    """non_none function tests"""

    class TestNominalCase:

        def test_none_value__should__return_false(self) -> None:
            """On None value should return False"""
            # GIVEN / WHEN
            result: bool = objects.non_none(None)

            # THEN
            assert not result

        def test_non_none_value__should__return_true(self) -> None:
            """On non None value should return True"""
            # GIVEN / WHEN
            result: bool = objects.non_none("A non None value")

            # THEN
            assert result

        def test_empty_value__should__return_true(self) -> None:
            """On empty value should return True"""
            # GIVEN / WHEN
            result: bool = objects.non_none({})

            # THEN
            assert result

        def test_false_bool_value__should__return_true(self) -> None:
            """On false boolean value should return True"""
            # GIVEN / WHEN
            result: bool = objects.non_none(False)

            # THEN
            assert result


class TestRequireNonNone:
    """require_non_none function tests"""
    DEFAULT_ERROR_MESSAGE: Final[str] = "None object error"

    class TestNominalCase:

        def test_non_none_value__should__return_value(self) -> None:
            """When the value is not None, should return it"""
            # GIVEN
            value: str = "A value"

            # WHEN
            result: str = objects.require_non_none(value)

            # THEN
            assert result == value

        def test_none_value__should__raise_type_error(self) -> None:
            """When the value is None, should raise TypeError with default message"""
            # GIVEN / WHEN / THEN
            with raises(TypeError) as error:
                objects.require_non_none(None)

            assert str(error.value) == TestRequireNonNone.DEFAULT_ERROR_MESSAGE

        def test_none_value_with_message__should__raise_type_error_with_given_message(self) -> None:
            """When the value is None and a message is specified, should raise TypeError with given message"""
            # GIVEN
            message: str = "An error message"

            # WHEN / THEN
            with raises(TypeError) as error:
                objects.require_non_none(None, message=message)

            assert str(error.value) == message


class TestRequireNonNoneElse:
    """require_non_none_else function tests"""

    class TestNominalCase:
        def test_non_none_value__should__return_value(self) -> None:
            """When the value is not None, should return it"""
            # GIVEN
            value: str = "A value"
            default_value: str = "A default value"

            # WHEN
            result: str = objects.require_non_none_else(value, default=default_value)

            # THEN
            assert result == value

        def test_non_none_value_with_none_default__should__return_value(self) -> None:
            """When the value is not None and default value is None, should return the value"""
            # GIVEN
            value: str = "A value"
            # noinspection PyTypeChecker
            default_value: str = None

            # WHEN
            result: str = objects.require_non_none_else(value, default=default_value)

            # THEN
            assert result == value

        def test_none_value__should__return_the_default_value(self) -> None:
            """When the value is None, should return the default value"""
            # GIVEN
            value: Optional[str] = None
            default_value: str = "A default value"

            # WHEN
            result: str = objects.require_non_none_else(value, default=default_value)

            # THEN
            assert result == default_value

    class TestErrorCase:

        def test_none_value_with_none_default__should__raise_type_error(self) -> None:
            """When the value and default are None, should raise TypeError"""
            # GIVEN / WHEN / THEN
            with raises(TypeError) as error:
                objects.require_non_none_else(None, default=None)

            assert str(error.value) == TestRequireNonNone.DEFAULT_ERROR_MESSAGE


class TestRequireNonNoneElseGet:
    """require_non_none_else_get function tests"""

    class TestNominalCase:
        def test_non_none_value__should__return_value(self) -> None:
            """When the value is not None, should return it"""
            # GIVEN
            value: str = "A value"
            default_supplier: Supplier[str] = lambda: "A default value"

            # WHEN
            result: str = objects.require_non_none_else_get(value, supplier=default_supplier)

            # THEN
            assert result == value

        def test_non_none_value_with_none_default__should__return_value(self) -> None:
            """When the value is not None and default supplier value is None, should return the value"""
            # GIVEN
            value: str = "A value"
            # noinspection PyTypeChecker
            default_supplier: Supplier[str] = lambda: None

            # WHEN
            result: str = objects.require_non_none_else_get(value, supplier=default_supplier)

            # THEN
            assert result == value

        def test_non_none_value_with_none_supplier__should__return_value(self) -> None:
            """When the value is not None and default supplier is None, should return the value"""
            # GIVEN
            value: str = "A value"
            # noinspection PyTypeChecker
            default_supplier: Supplier[str] = None

            # WHEN
            result: str = objects.require_non_none_else_get(value, supplier=default_supplier)

            # THEN
            assert result == value

        def test_none_value__should__return_the_default_value(self) -> None:
            """When the value is None, should return the default value"""
            # GIVEN
            value: Optional[str] = None
            default_value: str = "A default value"
            default_supplier: Supplier[str] = lambda: default_value

            # WHEN
            result: str = objects.require_non_none_else_get(value, supplier=default_supplier)

            # THEN
            assert result == default_value

    class TestErrorCase:

        def test_none_value_with_none_default__should__raise_type_error(self) -> None:
            """When the value and default are None, should raise TypeError"""
            # GIVEN / WHEN / THEN
            with raises(TypeError) as error:
                objects.require_non_none_else_get(None, supplier=lambda: None)

            assert str(error.value) == TestRequireNonNone.DEFAULT_ERROR_MESSAGE

        def test_none_value_with_none_supplier__should__raise_type_error(self) -> None:
            """When the value and supplier are None, should raise TypeError"""
            # GIVEN / WHEN / THEN
            with raises(TypeError) as error:
                objects.require_non_none_else_get(None, None)

            assert str(error.value) == "Supplier cannot be None"


class TestToString:
    """to_string function tests"""

    class TestNominalCase:
        def test_non_none_value__should__return_value_as_str(self) -> None:
            """When the value is not None, should return it as str format"""
            # GIVEN
            value: int = 77

            # WHEN
            result: str = objects.to_string(value)

            # THEN
            assert result == "77"

        def test_non_none_value_with_non_none_default__should__return_value_as_str(self) -> None:
            """When the value and default value are not None, should return it as str format"""
            # GIVEN
            value: int = 77
            default_value: str = "A default value"

            # WHEN
            result: str = objects.to_string(value, default_value)

            # THEN
            assert result == "77"

        def test_none_value_with_non_none_default__should__return_default_value(self) -> None:
            """When the value is None and default value is not none, should return the default value"""
            # GIVEN
            default_value: str = "A default value"

            # WHEN
            result: str = objects.to_string(None, default_value)

            # THEN
            assert result == default_value

        def test_none_value_with_none_default__should__return_none_as_str(self) -> None:
            """When the value and default value are None, should return 'None' str"""
            # GIVEN / WHEN
            result: str = objects.to_string(None, None)

            # THEN
            assert result == str(None)


class TestAsyncRequireNonNone:
    """async_require_non_none function tests"""
    DEFAULT_ERROR_MESSAGE: Final[str] = "None async object error"

    class TestNominalCase:

        async def test_non_none_value__should__return_value(self) -> None:
            """When the value is not None, should return it"""
            # GIVEN
            value: str = "A value"

            # WHEN
            result: str = await objects.async_require_non_none(value)

            # THEN
            assert result == value

        async def test_non_none_async_value__should__return_value(self) -> None:
            """When the value an awaitable with non None result, should return it"""
            # GIVEN
            value: str = "A value"

            async def coroutine() -> str:
                return value

            # WHEN
            result: str = await objects.async_require_non_none(coroutine())

            # THEN
            assert result == value

        async def test_none_value__should__raise_type_error(self) -> None:
            """When the value is None, should raise TypeError with default message"""
            # GIVEN / WHEN / THEN
            with raises(TypeError) as error:
                await objects.async_require_non_none(None)

            assert str(error.value) == TestAsyncRequireNonNone.DEFAULT_ERROR_MESSAGE

        async def test_none_async_value__should__raise_type_error(self) -> None:
            """When the value is an awaitable with None result, should raise TypeError with default message"""

            # GIVEN
            async def coroutine() -> None:
                return None

            # WHEN / THEN
            with raises(TypeError) as error:
                await objects.async_require_non_none(coroutine())

            assert str(error.value) == TestAsyncRequireNonNone.DEFAULT_ERROR_MESSAGE

        async def test_none_value_with_message__should__raise_type_error_with_given_message(self) -> None:
            """When the value is None and a message is specified, should raise TypeError with given message"""
            # GIVEN
            message: str = "An error message"

            # WHEN / THEN
            with raises(TypeError) as error:
                await objects.async_require_non_none(None, message=message)

            assert str(error.value) == message


class TestAsyncRequireNonNoneElse:
    """async_require_non_none_else function tests"""

    class TestNominalCase:
        async def test_non_none_value__should__return_value(self) -> None:
            """When the value is not None, should return it"""
            # GIVEN
            value: str = "A value"
            default_value: str = "A default value"

            # WHEN
            result: str = await objects.async_require_non_none_else(value, default=default_value)

            # THEN
            assert result == value

        async def test_non_none_async_value__should__return_value(self) -> None:
            """When the value is a non None async value, should return it"""
            # GIVEN
            value: str = "A value"

            async def coroutine() -> str: return value

            default_value: str = "A default value"

            # WHEN
            result: str = await objects.async_require_non_none_else(coroutine(), default=default_value)

            # THEN
            assert result == value

        async def test_non_none_value_with_none_default__should__return_value(self) -> None:
            """When the value is not None and default value is None, should return the value"""
            # GIVEN
            value: str = "A value"
            # noinspection PyTypeChecker
            default_value: str = None

            # WHEN
            result: str = await objects.async_require_non_none_else(value, default=default_value)

            # THEN
            assert result == value

        async def test_non_none_async_value_with_none_default__should__return_value(self) -> None:
            """When the value is non None async value and default value is None, should return the value"""
            # GIVEN
            value: str = "A value"

            async def coroutine() -> str: return value

            # noinspection PyTypeChecker
            default_value: str = None

            # WHEN
            result: str = await objects.async_require_non_none_else(coroutine(), default=default_value)

            # THEN
            assert result == value

        async def test_none_value__should__return_the_default_value(self) -> None:
            """When the value is None, should return the default value"""
            # GIVEN
            value: Optional[str] = None
            default_value: str = "A default value"

            # WHEN
            result: str = await objects.async_require_non_none_else(value, default=default_value)

            # THEN
            assert result == default_value

        async def test_none_async_value__should__return_the_default_value(self) -> None:
            """When the value is None async value, should return the default value"""

            # GIVEN
            async def coroutine() -> Optional[str]: return None

            default_value: str = "A default value"

            # WHEN
            result: str = await objects.async_require_non_none_else(coroutine(), default=default_value)

            # THEN
            assert result == default_value

    class TestErrorCase:

        async def test_none_value_with_none_default__should__raise_type_error(self) -> None:
            """When the value and default are None, should raise TypeError"""
            # GIVEN / WHEN / THEN
            with raises(TypeError) as error:
                await objects.async_require_non_none_else(None, default=None)

            assert str(error.value) == TestRequireNonNone.DEFAULT_ERROR_MESSAGE

        async def test_none_async_value_with_none_default__should__raise_type_error(self) -> None:
            """When the async value and default are None, should raise TypeError"""

            # GIVEN
            async def coroutine() -> Optional[str]: return None

            # WHEN / THEN
            with raises(TypeError) as error:
                await objects.async_require_non_none_else(coroutine(), default=None)

            assert str(error.value) == TestRequireNonNone.DEFAULT_ERROR_MESSAGE


class TestAsyncRequireNonNoneElseGet:
    """async_require_non_none_else_get function tests"""

    class TestNominalCase:
        async def test_non_none_value__should__return_value(self) -> None:
            """When the value is not None, should return it"""
            # GIVEN
            value: str = "A value"
            default_supplier: Supplier[str] = lambda: "A default value"

            # WHEN
            result: str = await objects.async_require_non_none_else_get(value, supplier=default_supplier)

            # THEN
            assert result == value

        async def test_non_none_async_value__should__return_value(self) -> None:
            """When the value is non None async, should return it"""
            # GIVEN
            value: str = "A value"
            default_supplier: Supplier[str] = lambda: "A default value"

            async def coroutine() -> str: return value

            # WHEN
            result: str = await objects.async_require_non_none_else_get(coroutine(), supplier=default_supplier)

            # THEN
            assert result == value

        async def test_non_none_value_with_none_default__should__return_value(self) -> None:
            """When the value is not None and default supplier value is None, should return the value"""
            # GIVEN
            value: str = "A value"
            # noinspection PyTypeChecker
            default_supplier: Supplier[str] = lambda: None

            # WHEN
            result: str = await objects.async_require_non_none_else_get(value, supplier=default_supplier)

            # THEN
            assert result == value

        async def test_non_none_async_value_with_none_default__should__return_value(self) -> None:
            """When the value is non None async and default supplier value is None, should return the value"""
            # GIVEN
            value: str = "A value"
            # noinspection PyTypeChecker
            default_supplier: Supplier[str] = lambda: None

            async def coroutine() -> str: return value

            # WHEN
            result: str = await objects.async_require_non_none_else_get(coroutine(), supplier=default_supplier)

            # THEN
            assert result == value

        async def test_non_none_value_with_none_supplier__should__return_value(self) -> None:
            """When the value is not None and default supplier is None, should return the value"""
            # GIVEN
            value: str = "A value"
            # noinspection PyTypeChecker
            default_supplier: Supplier[str] = None

            # WHEN
            result: str = await objects.async_require_non_none_else_get(value, supplier=default_supplier)

            # THEN
            assert result == value

        async def test_non_none_async_value_with_none_supplier__should__return_value(self) -> None:
            """When the value is non None async and default supplier is None, should return the value"""
            # GIVEN
            value: str = "A value"
            # noinspection PyTypeChecker
            default_supplier: Supplier[str] = None

            async def coroutine() -> str: return value

            # WHEN
            result: str = await objects.async_require_non_none_else_get(coroutine(), supplier=default_supplier)

            # THEN
            assert result == value

        async def test_none_value__should__return_the_default_value(self) -> None:
            """When the value is None, should return the default value"""
            # GIVEN
            value: Optional[str] = None
            default_value: str = "A default value"
            default_supplier: Supplier[str] = lambda: default_value

            # WHEN
            result: str = await objects.async_require_non_none_else_get(value, supplier=default_supplier)

            # THEN
            assert result == default_value

        async def test_none_async_value__should__return_the_default_value(self) -> None:
            """When the value is async None, should return the default value"""
            # GIVEN
            default_value: str = "A default value"
            default_supplier: Supplier[str] = lambda: default_value

            async def coroutine() -> Optional[str]: return None

            # WHEN
            result: str = await objects.async_require_non_none_else_get(coroutine(), supplier=default_supplier)

            # THEN
            assert result == default_value

    class TestErrorCase:

        async def test_none_value_with_none_default__should__raise_type_error(self) -> None:
            """When the value and default are None, should raise TypeError"""
            # GIVEN / WHEN / THEN
            with raises(TypeError) as error:
                await objects.async_require_non_none_else_get(None, supplier=lambda: None)

            assert str(error.value) == TestRequireNonNone.DEFAULT_ERROR_MESSAGE

        async def test_none_async_value_with_none_default__should__raise_type_error(self) -> None:
            """When the value is async None and default are None, should raise TypeError"""

            # GIVEN
            async def coroutine() -> Optional[str]: return None

            # WHEN / THEN
            with raises(TypeError) as error:
                await objects.async_require_non_none_else_get(coroutine(), supplier=lambda: None)

            assert str(error.value) == TestRequireNonNone.DEFAULT_ERROR_MESSAGE

        async def test_none_value_with_none_supplier__should__raise_type_error(self) -> None:
            """When the value and supplier are None, should raise TypeError"""
            # GIVEN / WHEN / THEN
            with raises(TypeError) as error:
                await objects.async_require_non_none_else_get(None, None)

            assert str(error.value) == "Supplier cannot be None"

        async def test_none_async_value_with_none_supplier__should__raise_type_error(self) -> None:
            """When the value is None async and supplier are None, should raise TypeError"""

            # GIVEN
            async def coroutine() -> Optional[str]: return None

            # WHEN / THEN
            with raises(TypeError) as error:
                await objects.async_require_non_none_else_get(coroutine(), None)

            assert str(error.value) == "Supplier cannot be None"


class TestToNone:
    """to_none function tests"""

    class TestNominalCase:

        def test__should__return_none(self) -> None:
            """Should return None whatever the parameters"""
            # GIVEN / WHEN / THEN
            assert objects.to_none(1, 'a', named_param=True) is None


class TestToSelf:
    """to_self function tests"""

    class TestNominalCase:

        def test_existing_parameter__should__return_given_parameter(self) -> None:
            """Should return the given parameter"""
            # GIVEN
            obj: str = "A test str"

            # WHEN
            result: str = objects.to_self(obj)

            # THEN
            assert result == obj

        def test_none_parameter__should__return_none(self) -> None:
            """Should return the given parameter"""
            # GIVEN / WHEN
            result: None = objects.to_self(None)

            # THEN
            assert result is None
