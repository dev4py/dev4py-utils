"""objects module tests"""
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
