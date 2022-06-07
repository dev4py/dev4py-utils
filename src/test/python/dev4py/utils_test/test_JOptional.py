"""JOptional module tests"""

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
from typing import Final, Optional, cast, Awaitable
from unittest.mock import patch, MagicMock

from pytest import raises

from dev4py.utils import JOptional, AsyncJOptional
from dev4py.utils.awaitables import to_awaitable
from dev4py.utils.types import Supplier, Function, Consumer, Runnable, Predicate


class TestJOptional:
    """JOptional class tests"""
    NO_VALUE_ERROR_MSG: Final[str] = "No value present"
    CONSTRUCTOR_ERROR_MSG: Final[str] = \
        "JOptional private constructor! Please use JOptional.of or JOptional.of_noneable"

    class TestConstructor:
        """Constructor tests"""

        class TestNominalCase:

            def test_none_create_key__should__raise_assertion_error(self):
                """When create key is none, should raise AssertionError with private constructor message"""
                # GIVEN / WHEN / THEN
                with raises(AssertionError) as error:
                    JOptional("A value", None)

                assert str(error.value) == TestJOptional.CONSTRUCTOR_ERROR_MSG

            def test_invalid_create_key__should__raise_assertion_error(self):
                """When create key is invalid, should raise AssertionError with private constructor message"""
                # GIVEN / WHEN / THEN
                with raises(AssertionError) as error:
                    JOptional("A value", object())

                assert str(error.value) == TestJOptional.CONSTRUCTOR_ERROR_MSG

            def test_valid_create_key__should__create_a_new_joptional(self):
                """When create key is valid, should create a new JOptional"""
                # GIVEN
                value: int = 1

                # WHEN
                # noinspection PyUnresolvedReferences
                optional: JOptional[int] = JOptional(value, JOptional._JOptional__CREATE_KEY)

                # THEN
                assert optional.is_present()
                assert optional._value == value

    class TestOf:
        """of class method tests"""

        class TestNominalCase:
            def test_value_exists__should__return_joptional_with_value(self) -> None:
                """When a value is provided, should return a joptional with value"""
                # GIVEN
                value: int = 1

                # WHEN
                optional: JOptional[int] = JOptional.of(value)

                # THEN
                assert optional._value == value
                assert optional.is_present()

        class TestErrorCase:
            def test_none_value__should__raise_type_error(self) -> None:
                """When no value is provided, should raise a TypeError exception with no value message"""
                # GIVEN / WHEN / THEN
                with raises(TypeError) as error:
                    JOptional.of(None)

                assert str(error.value) == TestJOptional.NO_VALUE_ERROR_MSG

    class TestOfNoneable:
        """of_noneable class method tests"""

        class TestNominalCase:
            def test_value_exists__should__return_joptional_with_value(self) -> None:
                """When a value is provided, should return a joptional with value"""
                # GIVEN
                value: int = 1

                # WHEN
                optional: JOptional[int] = JOptional.of_noneable(value)

                # THEN
                assert optional._value == value
                assert optional.is_present()

            def test_none_value__should__return_empty_joptional(self) -> None:
                """When no value is provided, should return an empty joptional"""
                # GIVEN
                value: Optional[int] = None

                # WHEN
                optional: JOptional[int] = JOptional.of_noneable(value)

                # THEN
                assert optional._value == value
                assert optional.is_empty()

    class TestEmpty:
        """empty class method tests"""

        class TestNominalCase:
            def test_should__return_empty_joptional(self) -> None:
                """Should return a joptional with value"""
                # GIVEN / WHEN
                optional: JOptional[int] = JOptional.empty()

                # THEN
                assert optional._value is None
                assert optional.is_empty()

    class TestIsPresent:
        """is_present method tests"""

        class TestNominalCase:
            def test_value_exists__should__return_true(self) -> None:
                """When a value is provided, should return true"""
                # GIVEN / WHEN
                optional: JOptional[int] = JOptional.of(1)

                # THEN
                assert optional.is_present()

            def test_none_value__should__return_false(self) -> None:
                """When no value is provided, should return false"""
                # GIVEN / WHEN
                optional: JOptional[int] = JOptional.empty()

                # THEN
                assert not optional.is_present()

    class TestIsEmpty:
        """is_empty method tests"""

        class TestNominalCase:
            def test_value_exists__should__return_false(self) -> None:
                """When a value is provided, should return false"""
                # GIVEN / WHEN
                optional: JOptional[int] = JOptional.of(1)

                # THEN
                assert not optional.is_empty()

            def test_none_value__should__return_true(self) -> None:
                """When no value is provided, should return true"""
                # GIVEN / WHEN
                optional: JOptional[int] = JOptional.empty()

                # THEN
                assert optional.is_empty()

    class TestGet:
        """get method tests"""

        class TestNominalCase:
            def test_value_exists__should__return_value(self) -> None:
                """When value is provided, return the value"""
                # GIVEN
                value: int = 1
                optional: JOptional[int] = JOptional.of_noneable(value)

                # WHEN
                result: int = optional.get()

                # THEN
                assert result == value

        class TestErrorCase:
            def test_none_value__should__raise_type_error(self) -> None:
                """When no value is provided, should raise a ValueError exception with no value message"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()

                # WHEN / THEN
                with raises(ValueError) as error:
                    optional.get()

                assert str(error.value) == TestJOptional.NO_VALUE_ERROR_MSG

    class TestOrElse:
        """or_else method tests"""

        class TestNominalCase:
            def test_value_exists__should__return_value(self) -> None:
                """When value is provided, return the value"""
                # GIVEN
                value: int = 1
                default_value: int = 2
                optional: JOptional[int] = JOptional.of_noneable(value)

                # WHEN
                result: int = optional.or_else(default_value)

                # THEN
                assert result == value

            def test_none_value__should__return_default_value(self) -> None:
                """When no value is provided, return the default value"""
                # GIVEN
                default_value: int = 2
                optional: JOptional[int] = JOptional.empty()

                # WHEN
                result: int = optional.or_else(default_value)

                # THEN
                assert result == default_value

            def test_none_value_and_none_default__should__return_none(self) -> None:
                """When no value is provided and default value is None, return the default value"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()

                # WHEN
                result: Optional[int] = optional.or_else(None)

                # THEN
                assert result is None

            def test_none_value_and_no_default__should__return_none(self) -> None:
                """When no value is provided and no default value, return None value"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()

                # WHEN
                result: Optional[int] = optional.or_else()

                # THEN
                assert result is None

    class TestOrElseGet:
        """or_else_get method tests"""

        class TestNominalCase:
            def test_value_exists__should__return_value(self) -> None:
                """When value is provided, return the value"""
                # GIVEN
                value: int = 1
                supplier: Supplier[int] = lambda: 2
                optional: JOptional[int] = JOptional.of_noneable(value)

                # WHEN
                result: int = optional.or_else_get(supplier)

                # THEN
                assert result == value

            def test_none_value__should__return_supplied_value(self) -> None:
                """When no value is provided, return the supplied default value"""
                # GIVEN
                default_value: int = 2
                supplier: Supplier[int] = lambda: default_value
                optional: JOptional[int] = JOptional.empty()

                # WHEN
                result: int = optional.or_else_get(supplier)

                # THEN
                assert result == default_value

            def test_none_value_and_no_supplier__should__return_none_value(self) -> None:
                """When no value is provided, return the supplied default value"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()

                # WHEN
                result: Optional[int] = optional.or_else_get()

                # THEN
                assert result is None

        class TestErrorCase:
            def test_none_value_and_none_supplier__should__raise_type_error(self) -> None:
                """When no value is provided, should raise a TypeError exception"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()

                # WHEN / THEN
                with raises(TypeError):
                    optional.or_else_get(None)

            def test_value_exists_and_none_supplier__should__raise_type_error(self) -> None:
                """When value is provided but supplier is none, should raise a TypeError exception"""
                # GIVEN
                value: int = 1
                optional: JOptional[int] = JOptional.of_noneable(value)

                # WHEN / THEN
                with raises(TypeError):
                    optional.or_else_get(None)

    class TestOrElseRaise:
        """or_else_raise method tests"""

        class TestNominalCase:
            def test_value_exists__should__return_value(self) -> None:
                """When value is provided, return the value"""
                # GIVEN
                value: int = 1
                supplier: Supplier[Exception] = lambda: ValueError("Test error message")
                optional: JOptional[int] = JOptional.of_noneable(value)

                # WHEN
                result: int = optional.or_else_raise(supplier)

                # THEN
                assert result == value

            def test_none_value__should__raise_supplied_exception(self) -> None:
                """When no value is provided, raise the supplied exception"""
                # GIVEN
                given_error: Exception = ValueError("Test error message")
                supplier: Supplier[Exception] = lambda: given_error
                optional: JOptional[int] = JOptional.empty()

                # WHEN / THEN
                with raises(ValueError) as error:
                    optional.or_else_raise(supplier)

                assert str(error.value) == str(given_error)

        class TestErrorCase:
            def test_none_value_and_none_supplier__should__raise_type_error(self) -> None:
                """When no value and no supplier are provided, should raise a TypeError exception"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()

                # WHEN / THEN
                with raises(TypeError):
                    optional.or_else_raise(None)

            def test_value_exists_and_none_supplier__should__raise_type_error(self) -> None:
                """When value is provided but supplier is none, should raise a TypeError exception"""
                # GIVEN
                value: int = 1
                optional: JOptional[int] = JOptional.of_noneable(value)

                # WHEN / THEN
                with raises(TypeError):
                    optional.or_else_raise(None)

    class TestOrGet:
        """or_get method tests"""

        class TestNominalCase:
            def test_value_exists__should__return_self(self) -> None:
                """When value is provided, return the self"""
                # GIVEN
                optional: JOptional[int] = JOptional.of(1)
                supplier: Supplier[JOptional[int]] = lambda: JOptional.of(2)

                # WHEN
                result: JOptional[int] = optional.or_get(supplier)

                # THEN
                assert result == optional

            def test_none_value__should__return_supplied_joptional(self) -> None:
                """When value is not provided, return the supplied default JOptional"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()
                other: JOptional[int] = JOptional.of(2)
                supplier: Supplier[JOptional[int]] = lambda: other

                # WHEN
                result: JOptional[int] = optional.or_get(supplier)

                # THEN
                assert result == other

        class TestErrorCase:
            def test_value_exists_and_none_supplier__should__raise_type_error(self) -> None:
                """When value is provided but supplier is not, should raise a TypeError exception"""
                # GIVEN
                optional: JOptional[int] = JOptional.of(1)

                # WHEN / THEN
                with raises(TypeError):
                    optional.or_get(None)

            def test_none_value_and_none_supplier__should__raise_type_error(self) -> None:
                """When no value and no supplier are provided, should raise a TypeError exception"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()

                # WHEN / THEN
                with raises(TypeError):
                    optional.or_get(None)

    class TestMap:
        """map method tests"""

        class TestNominalCase:
            def test_value_exists__should__joptional_of_mapped_value(self) -> None:
                """When value is provided, should apply the given mapper"""
                # GIVEN
                optional: JOptional[int] = JOptional.of(1)
                mapper: Function[int, str] = lambda i: f"Str value is: '{i}'"

                # WHEN
                result: JOptional[str] = optional.map(mapper)

                # THEN
                assert result.is_present()
                assert result._value == "Str value is: '1'"

            def test_value_exists_and_none_mapper_result__should__empty(self) -> None:
                """When value is provided, should return an empty JOptional"""
                # GIVEN
                optional: JOptional[int] = JOptional.of(1)
                mapper: Function[int, None] = lambda i: None

                # WHEN
                result: JOptional[str] = optional.map(mapper)

                # THEN
                assert result.is_empty()

            def test_none_value__should__return_empty(self) -> None:
                """When value is not provided, should return an empty JOptional"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()
                mapper: Function[int, str] = lambda i: f"Str value is: '{i}'"

                # WHEN
                result: JOptional[str] = optional.map(mapper)

                # THEN
                assert result.is_empty()

        class TestErrorCase:
            def test_value_exists_and_none_mapper__should__raise_type_error(self) -> None:
                """When value is provided but mapper is not, should raise a TypeError exception"""
                # GIVEN
                optional: JOptional[int] = JOptional.of(1)

                # WHEN / THEN
                with raises(TypeError):
                    optional.map(None)

            def test_none_value_and_none_mapper__should__raise_type_error(self) -> None:
                """When value and mapper are not provided, should raise a TypeError exception"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()

                # WHEN
                with raises(TypeError):
                    optional.map(None)

    class TestFlatMap:
        """flat_map method tests"""

        class TestNominalCase:
            def test_value_exists__should__joptional_of_mapped_value(self) -> None:
                """When value is provided, should apply the given mapper"""
                # GIVEN
                optional: JOptional[int] = JOptional.of(1)
                mapper: Function[int, JOptional[str]] = \
                    lambda v: JOptional.of_noneable(v).map(lambda i: f"Str value is: '{i}'")

                # WHEN
                result: JOptional[str] = optional.flat_map(mapper)

                # THEN
                assert result.is_present()
                assert result._value == "Str value is: '1'"

            def test_none_value__should__return_empty(self) -> None:
                """When value is not provided, should return an empty JOptional"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()
                mapper: Function[int, JOptional[str]] = \
                    lambda v: JOptional.of_noneable(v).map(lambda i: f"Str value is: '{i}'")

                # WHEN
                result: JOptional[str] = optional.flat_map(mapper)

                # THEN
                assert result.is_empty()

        class TestErrorCase:
            def test_value_exists_and_none_mapper__should__raise_type_error(self) -> None:
                """When value is provided but mapper is not, should raise a TypeError exception"""
                # GIVEN
                optional: JOptional[int] = JOptional.of(1)

                # WHEN / THEN
                with raises(TypeError):
                    optional.flat_map(None)

            def test_none_value_and_none_mapper__should__raise_type_error(self) -> None:
                """When value and mapper are not provided, should raise a TypeError exception"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()

                # WHEN / THEN
                with raises(TypeError):
                    optional.flat_map(None)

            def test_value_exists_and_none_mapper_result__should__raise_type_error(self) -> None:
                """When value exists and mapper returns None, should raise a TypeError exception"""
                # GIVEN
                optional: JOptional[int] = JOptional.of(1)

                # WHEN / THEN
                with raises(TypeError):
                    optional.flat_map(lambda v: None)

    class TestIfPresent:
        """if_present method tests"""

        class TestNominalCase:

            @patch('builtins.print')
            def test_value_exists__should__call_given_consumer(self, print_mock: MagicMock) -> None:
                """When value is provided, should call the given consumer"""
                # GIVEN
                value: int = 1
                optional: JOptional[int] = JOptional.of(value)
                consumer: Consumer[[int]] = print

                # WHEN
                optional.if_present(consumer)

                # THEN
                print_mock.assert_called_once_with(value)

            @patch('builtins.print')
            def test_none_value__should__do_nothing(self, print_mock: MagicMock) -> None:
                """When no value is provided, should do nothing"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()
                consumer: Consumer[[int]] = print

                # WHEN
                optional.if_present(consumer)

                # THEN
                print_mock.assert_not_called()

        class TestErrorCase:
            def test_value_exists_and_none_consumer__should__raise_type_error(self) -> None:
                """When value is provided but consumer is not, should raise a TypeError exception"""
                # GIVEN
                optional: JOptional[int] = JOptional.of(1)

                # WHEN / THEN
                with raises(TypeError):
                    optional.if_present(None)

            def test_none_value_and_none_consumer__should__raise_type_error(self) -> None:
                """When no value and no consumer are provided, should raise a TypeError exception"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()

                # WHEN / THEN
                with raises(TypeError):
                    optional.if_present(None)

    class TestIfEmpty:
        """if_empty method tests"""

        class TestNominalCase:

            @patch('builtins.print')
            def test_value_exists__should__do_nothing(self, print_mock: MagicMock) -> None:
                """When value is provided, should do nothing"""
                # GIVEN
                optional: JOptional[int] = JOptional.of(1)
                runnable: Runnable = lambda: print("A test message")

                # WHEN
                optional.if_empty(runnable)

                # THEN
                print_mock.assert_not_called()

            @patch('builtins.print')
            def test_none_value__should__call_given_runnable(self, print_mock: MagicMock) -> None:
                """When no value is provided, should call the given runnable"""
                # GIVEN
                message: str = "A test message"
                optional: JOptional[int] = JOptional.empty()
                runnable: Runnable = lambda: print(message)

                # WHEN
                optional.if_empty(runnable)

                # THEN
                print_mock.assert_called_once_with(message)

        class TestErrorCase:
            def test_none_value_and_none_runnable__should__raise_type_error(self) -> None:
                """When no value and no consummer are provided, should raise TypeError exception"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()

                # WHEN / THEN
                with raises(TypeError):
                    optional.if_empty(cast(Runnable, None))

            def test_value_exists_and_none_runnable__should__raise_type_error(self) -> None:
                """When value is provided but runnable is not, should raise TypeError exception"""
                # GIVEN
                optional: JOptional[int] = JOptional.of(1)

                # WHEN / THEN
                with raises(TypeError):
                    optional.if_empty(cast(Runnable, None))

    class TestIfPresentOrElse:
        """if_present_or_else method tests"""

        class TestNominalCase:
            @patch('builtins.print')
            def test_value_exists__should__call_given_consumer(self, print_mock: MagicMock) -> None:
                """When value is provided, should call the given consumer"""
                # GIVEN
                value: int = 1
                optional: JOptional[int] = JOptional.of(value)
                consumer: Consumer[[int]] = print
                runnable: Runnable = lambda: print("A test message")

                # WHEN
                optional.if_present_or_else(consumer, runnable)

                # THEN
                print_mock.assert_called_once_with(value)

            @patch('builtins.print')
            def test_none_value__should__call_given_runnable(self, print_mock: MagicMock) -> None:
                """When value is not provided, should call the given runnable"""
                # GIVEN
                message: str = "A test message"
                optional: JOptional[int] = JOptional.empty()
                consumer: Consumer[[int]] = print
                runnable: Runnable = lambda: print("A test message")

                # WHEN
                optional.if_present_or_else(consumer, runnable)

                # THEN
                print_mock.assert_called_once_with(message)

        class TestErrorCase:
            def test_value_exists_and_none_consumer__should__raise_type_error(self) -> None:
                """When value is provided but consumer is None, should raise a TypeError exception"""
                # GIVEN
                value: int = 1
                optional: JOptional[int] = JOptional.of(value)
                runnable: Runnable = lambda: print("A test message")

                # WHEN / THEN
                with raises(TypeError):
                    optional.if_present_or_else(None, runnable)

            def test_value_exists_and_none_consumer_and_runnable__should__raise_type_error(self) -> None:
                """When value is provided but consumer and runnable are None, should raise a TypeError exception"""
                # GIVEN
                value: int = 1
                optional: JOptional[int] = JOptional.of(value)

                # WHEN / THEN
                with raises(TypeError):
                    optional.if_present_or_else(None, cast(Runnable, None))

            def test_none_value_and_consumer_and_runnable__should__raise_type_error(self) -> None:
                """When value is not provided but consumer and runnable are None, should raise a TypeError exception"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()

                # WHEN / THEN
                with raises(TypeError):
                    optional.if_present_or_else(None, cast(Runnable, None))

            def test_none_value_runnable__should__raise_type_error(self) -> None:
                """When value is not provided and runnable is None, should raise a TypeError exception"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()
                consumer: Consumer[[int]] = print

                # WHEN / THEN
                with raises(TypeError):
                    optional.if_present_or_else(consumer, cast(Runnable, None))

            def test_value_exists_and_none_runnable__should__raise_type_error(self) -> None:
                """When value is provided but not the runnable, should raise a TypeError exception"""
                # GIVEN
                value: int = 1
                optional: JOptional[int] = JOptional.of(value)
                consumer: Consumer[[int]] = print

                # WHEN / THEN
                with raises(TypeError):
                    optional.if_present_or_else(consumer, cast(Runnable, None))

            def test_none_value_and_none_consumer__should__raise_type_error(self) -> None:
                """When value is not provided and consumer is None, should raise a TypeError exception"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()
                runnable: Runnable = lambda: print("A test message")

                # WHEN / THEN
                with raises(TypeError):
                    optional.if_present_or_else(None, runnable)

    class TestFilter:
        """filter method tests"""

        class TestNominalCase:
            def test_value_with_valid_filter__should__return_joptional_with_value(self):
                """When value is present and predicate is valid, should return the JOptional with value"""
                # GIVEN
                value: int = 7
                predicate: Predicate[int] = lambda i: i > 5
                optional: JOptional[int] = JOptional.of(value)

                # WHEN
                result: JOptional[int] = optional.filter(predicate)

                # THEN
                assert result.is_present()
                assert result._value == value

            def test_value_without_valid_filter__should__return_empty(self):
                """When value is present and predicate is not valid, should return empty JOptional"""
                # GIVEN
                value: int = 7
                predicate: Predicate[int] = lambda i: i < 5
                optional: JOptional[int] = JOptional.of(value)

                # WHEN
                result: JOptional[int] = optional.filter(predicate)

                # THEN
                assert result.is_empty()

            def test_empty_value__should__return_empty(self):
                """When value is empty, should return empty JOptional"""
                # GIVEN
                predicate: Predicate[int] = lambda i: i < 5
                optional: JOptional[int] = JOptional.empty()

                # WHEN
                result: JOptional[int] = optional.filter(predicate)

                # THEN
                assert result.is_empty()

        class TestErrorCase:
            def test_value_exists_and_predicate_is_none__should__raise_type_error(self) -> None:
                """When value is provided but predicate is None, should raise a TypeError exception"""
                # GIVEN
                optional: JOptional[int] = JOptional.of(1)

                # WHEN / THEN
                with raises(TypeError):
                    optional.filter(None)

            def test_empty_value_and_none_predicate__should__raise_type_erro(self):
                """When value is empty and predicate is None, should raise a TypeError exception"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()

                # WHEN / THEN
                with raises(TypeError):
                    optional.filter(None)

    class TestPeek:
        """peek method tests"""

        class TestNominalCase:

            @patch('builtins.print')
            def test_value_exists__should__call_given_consumer(self, print_mock: MagicMock) -> None:
                """When value is provided, should call the given consumer"""
                # GIVEN
                value: int = 1
                optional: JOptional[int] = JOptional.of(value)
                consumer: Consumer[[int]] = print

                # WHEN
                result: JOptional[int] = optional.peek(consumer)

                # THEN
                print_mock.assert_called_once_with(value)
                assert result == optional

            @patch('builtins.print')
            def test_none_value__should__do_nothing(self, print_mock: MagicMock) -> None:
                """When no value is provided, should do nothing"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()
                consumer: Consumer[[int]] = print

                # WHEN
                result: JOptional[int] = optional.peek(consumer)

                # THEN
                print_mock.assert_not_called()
                assert result == optional

        class TestErrorCase:
            def test_value_exists_and_none_consumer__should__raise_type_error(self) -> None:
                """When value is provided but consumer is not, should raise a TypeError exception"""
                # GIVEN
                optional: JOptional[int] = JOptional.of(1)

                # WHEN / THEN
                with raises(TypeError):
                    optional.peek(None)

            def test_none_value_and_none_consumer__should__raise_type_error(self) -> None:
                """When no value and no consumer are provided, should raise a TypeError exception"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()

                # WHEN / THEN
                with raises(TypeError):
                    optional.peek(None)

    class TestIsAwaitable:
        """is_awaitable method tests"""

        class TestNominalCase:
            def test_none__should__return_false(self) -> None:
                """When value is None should return False"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()

                # WHEN
                result: bool = optional.is_awaitable()

                # THEN
                assert not result

            async def test_coroutine_value__should__return_true(self) -> None:
                """When value is a Coroutine should return True"""

                # GIVEN
                async def coroutine() -> None: ...

                optional: JOptional[Awaitable[None]] = JOptional.of(coroutine())

                # WHEN
                result: bool = optional.is_awaitable()

                # THEN
                assert result
                await optional.get()  # Remove warning

            async def test_task_value__should__return_true(self) -> None:
                """When value is a Task should return True"""

                # GIVEN
                async def coroutine() -> None: ...

                optional: JOptional[Task] = JOptional.of(asyncio.create_task(coroutine()))

                # WHEN
                result: bool = optional.is_awaitable()

                # THEN
                assert result
                await optional.get()  # Remove warning

            async def test_future_value__should__return_true(self) -> None:
                """When value is a Future should return True"""

                # GIVEN
                async def coroutine() -> None: ...

                optional: JOptional[Future] = JOptional.of(asyncio.ensure_future(coroutine()))

                # WHEN
                result: bool = optional.is_awaitable()

                # THEN
                assert result
                await optional.get()  # Remove warning

            def test_not_awaitable_value__should__return_false(self) -> None:
                """When value is not an awaitable should return False"""
                # GIVEN
                optional: JOptional[str] = JOptional.of("A value")

                # WHEN
                result: bool = optional.is_awaitable()

                # THEN
                assert not result

    class TestToSyncValue:
        """to_sync_value method tests"""

        class TestNominalCase:
            async def test_none_value__should__return_self(self) -> None:
                """When value is None should return self"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()

                # WHEN
                result: JOptional[int] = await optional.to_sync_value()

                # THEN
                assert result == optional

            async def test_not_awaitable_value__should__return_self(self) -> None:
                """When value is not Awaitable should return self"""
                # GIVEN
                optional: JOptional[int] = JOptional.of(1)

                # WHEN
                result: JOptional[int] = await optional.to_sync_value()

                # THEN
                assert result == optional

            async def test_coroutine_value__should__return_joptional_with_synchronized_value(self) -> None:
                """When value is a Coroutine should return a JOptional describing the awaited value"""

                # GIVEN
                value: str = "A string value"

                async def coroutine() -> str: return value

                optional: JOptional[Awaitable[str]] = JOptional.of(coroutine())

                # WHEN
                result: JOptional[str] = await optional.to_sync_value()

                # THEN
                assert result.get() == value

            async def test_task_value__should__return_joptional_with_synchronized_value(self) -> None:
                """When value is a Task should return a JOptional describing the awaited value"""

                # GIVEN
                value: str = "A string value"

                async def coroutine() -> str: return value

                optional: JOptional[Awaitable[str]] = JOptional.of(asyncio.create_task(coroutine()))

                # WHEN
                result: JOptional[str] = await optional.to_sync_value()

                # THEN
                assert result.get() == value

            async def test_future_value__should__return_joptional_with_synchronized_value(self) -> None:
                """When value is a Future should return a JOptional describing the awaited value"""

                # GIVEN
                value: str = "A string value"

                async def coroutine() -> str: return value

                optional: JOptional[Awaitable[str]] = JOptional.of(asyncio.ensure_future(coroutine()))

                # WHEN
                result: JOptional[str] = await optional.to_sync_value()

                # THEN
                assert result.get() == value

    class TestToAsyncJOptional:
        """to_async_joptional method tests"""

        class TestNominalCase:
            async def test_empty__should__return_empty_async_joptional(self) -> None:
                """When value is None should return empty AsyncJOptional"""
                # GIVEN
                optional: JOptional[str] = JOptional.empty()

                # WHEN
                async_optional: AsyncJOptional[str] = optional.to_async_joptional()

                # THEN
                assert await async_optional.is_empty()

            async def test_str_value__should__return_str_async_joptional(self) -> None:
                """When str value should return an AsyncJOptional[str] with value"""
                # GIVEN
                value: str = "A test value"
                optional: JOptional[str] = JOptional.of(value)

                # WHEN
                async_optional: AsyncJOptional[str] = optional.to_async_joptional()

                # THEN
                assert await async_optional.is_present()
                assert await async_optional.get() == value

            async def test_async_str_value__should__return_str_async_joptional(self) -> None:
                """When str value should return an AsyncJOptional[str] with value"""
                # GIVEN
                value: str = "A test value"
                optional: JOptional[Awaitable[str]] = JOptional.of(to_awaitable(value))

                # WHEN
                async_optional: AsyncJOptional[str] = optional.to_async_joptional()

                # THEN
                assert await async_optional.is_present()
                assert await async_optional.get() == value
