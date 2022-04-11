"""JOptional module tests"""
from typing import Final, Optional, cast
from unittest.mock import patch, MagicMock

from pytest import raises

from dev4py.utils import JOptional
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

            def test_value_exists_and_none_supplier__should__return_value(self) -> None:
                """When value is provided but supplier is none, return the value"""
                # GIVEN
                value: int = 1
                optional: JOptional[int] = JOptional.of_noneable(value)

                # WHEN
                result: int = optional.or_else_get(None)

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

        class TestErrorCase:
            def test_none_value_and_none_supplier__should__raise_type_error(self) -> None:
                """When no value is provided, should raise a TypeError exception"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()

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

            def test_value_exists_and_none_supplier__should__return_value(self) -> None:
                """When value is provided but supplier is none, return the value"""
                # GIVEN
                value: int = 1
                optional: JOptional[int] = JOptional.of_noneable(value)

                # WHEN
                result: int = optional.or_else_raise(None)

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
                assert result.is_empty

            def test_none_value__should__return_empty(self) -> None:
                """When value is not provided, should return an empty JOptional"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()
                mapper: Function[int, str] = lambda i: f"Str value is: '{i}'"

                # WHEN
                result: JOptional[str] = optional.map(mapper)

                # THEN
                assert result.is_empty

            def test_none_value_and_none_mapper__should__return_empty(self) -> None:
                """When value and mapper are not provided, should return an empty JOptional"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()

                # WHEN
                result: JOptional[str] = optional.map(None)

                # THEN
                assert result.is_empty

        class TestErrorCase:
            def test_value_exists_and_none_mapper__should__raise_type_error(self) -> None:
                """When value is provided but mapper is not, should raise a TypeError exception"""
                # GIVEN
                optional: JOptional[int] = JOptional.of(1)

                # WHEN / THEN
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
                assert result.is_empty

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

            @patch('builtins.print')
            def test_none_value_and_none_consumer__should__do_nothing(self, print_mock: MagicMock) -> None:
                """When no value and no consummer are provided, should do nothing"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()

                # WHEN
                optional.if_present(None)

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
            def test_value_exists_and_none_runnable__should__do_nothing(self, print_mock: MagicMock) -> None:
                """When value is provided but runnable is not, should do nothing"""
                # GIVEN
                optional: JOptional[int] = JOptional.of(1)

                # WHEN
                optional.if_empty(cast(Runnable, None))

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
                """When no value and no consummer are provided, should do nothing"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()

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

            @patch('builtins.print')
            def test_value_exists_and_none_runnable__should__call_given_consumer(self,
                                                                                 print_mock: MagicMock) -> None:
                """When value is provided but not the runnable, should call the given consumer"""
                # GIVEN
                value: int = 1
                optional: JOptional[int] = JOptional.of(value)
                consumer: Consumer[[int]] = print

                # WHEN
                optional.if_present_or_else(consumer, cast(Runnable, None))

                # THEN
                print_mock.assert_called_once_with(value)

            @patch('builtins.print')
            def test_none_value_and_none_consumer__should__call_given_runnable(self, print_mock: MagicMock) -> None:
                """When value is not provided and consumer is None, should call the given runnable"""
                # GIVEN
                message: str = "A test message"
                optional: JOptional[int] = JOptional.empty()
                runnable: Runnable = lambda: print("A test message")

                # WHEN
                optional.if_present_or_else(None, runnable)

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

            def test_empty_value_and_none_predicate__should__return_empty(self):
                """When value is empty and predicate is None, should return empty JOptional"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()

                # WHEN
                result: JOptional[int] = optional.filter(None)

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

            @patch('builtins.print')
            def test_none_value_and_none_consumer__should__do_nothing(self, print_mock: MagicMock) -> None:
                """When no value and no consummer are provided, should do nothing"""
                # GIVEN
                optional: JOptional[int] = JOptional.empty()

                # WHEN
                result: JOptional[int] = optional.peek(None)

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
                    optional.if_present(None)
