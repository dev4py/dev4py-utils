"""dicts module tests"""
from typing import Optional, Any

from pytest import raises

from dev4py.utils import dicts, JOptional
from dev4py.utils.types import Supplier


class TestIsDict:
    """is_dict function tests"""

    class TestNominalCase:
        def test_none__should__return_false(self) -> None:
            """When value is None should return False"""
            # GIVEN / WHEN
            result: bool = dicts.is_dict(None)

            # THEN
            assert not result

        def test_not_dict__should__return_false(self) -> None:
            """When value is not a dict should return False"""
            # GIVEN
            value: str = "A test value"

            # WHEN
            result: bool = dicts.is_dict(value)

            # THEN
            assert not result

        def test_dict__should__return_true(self) -> None:
            """When value is a dict should return True"""
            # GIVEN
            value: dict[str, int] = {'a': 1, 'b': 2}

            # WHEN
            result: bool = dicts.is_dict(value)

            # THEN
            assert result


class TestGetJoptionalValue:
    """get_joptional_value function tests"""

    class TestNominalCase:
        def test_none_dict__should__return_empty_joptional(self) -> None:
            """When dict is None should return empty joptional"""
            # GIVEN
            key: str = 'a key'

            # WHEN
            result: JOptional[int] = dicts.get_joptional_value(None, key)

            # THEN
            assert result.is_empty()

        def test_none_value__should__return_empty_joptional(self) -> None:
            """When value is None should return empty joptional"""
            # GIVEN
            key: str = 'c'
            dictionary: dict[str, int] = {'a': 1, 'b': 2}

            # WHEN
            result: JOptional[int] = dicts.get_joptional_value(dictionary, key)

            # THEN
            assert result.is_empty()

        def test_value_exits__should__return_joptional_with_value(self) -> None:
            """When value exists should return a joptional with value"""
            # GIVEN
            key: str = 'b'
            dictionary: dict[str, int] = {'a': 1, 'b': 2}

            # WHEN
            result: JOptional[int] = dicts.get_joptional_value(dictionary, key)

            # THEN
            assert result.is_present()
            assert result.get() == 2

    class TestErrorCase:
        def test_not_dict__should__raise_type_error(self) -> None:
            """When value is None should return False"""
            # GIVEN
            key: str = 'a key'
            dictionary: str = "Not a dict"

            # WHEN / THEN
            with raises(TypeError) as error:
                # noinspection PyTypeChecker
                dicts.get_joptional_value(dictionary, key)

            assert str(error.value) == "Optional[dict[K, V]] parameter is required"


class TestGetValue:
    """get_value function tests"""

    class TestNominalCase:
        def test_none_dict__should__return_none(self) -> None:
            """When dict is None should return None"""
            # GIVEN
            key: str = 'a key'

            # WHEN
            result: Optional[int] = dicts.get_value(None, key)

            # THEN
            assert result is None

        def test_none_dict_with_default_supplier__should__return_supplied_value(self) -> None:
            """When dict is None and default supplier is provided should return the supplied value"""
            # GIVEN
            key: str = 'a key'
            supplier: Supplier[int] = lambda: 2

            # WHEN
            result: Optional[int] = dicts.get_value(None, key, supplier)

            # THEN
            assert result == 2

        def test_none_value__should__return_none(self) -> None:
            """When value is None should return None"""
            # GIVEN
            key: str = 'c'
            dictionary: dict[str, int] = {'a': 1, 'b': 2}

            # WHEN
            result: Optional[int] = dicts.get_value(dictionary, key)

            # THEN
            assert result is None

        def test_none_value_with_default_supplier__should__return_supplied_value(self) -> None:
            """When value is None and default supplier is provided should return the supplied value"""
            # GIVEN
            key: str = 'c'
            dictionary: dict[str, int] = {'a': 1, 'b': 2}
            supplier: Supplier[int] = lambda: 3

            # WHEN
            result: Optional[int] = dicts.get_value(dictionary, key, supplier)

            # THEN
            assert result == 3

        def test_value_exits__should__return_the_value(self) -> None:
            """When value exists should return the value"""
            # GIVEN
            key: str = 'b'
            dictionary: dict[str, int] = {'a': 1, 'b': 2}

            # WHEN
            result: Optional[int] = dicts.get_value(dictionary, key)

            # THEN
            assert result == 2

        def test_value_exits_with_default_supplier__should__return_the_value(self) -> None:
            """When value exists and default supplier is provided should return the value"""
            # GIVEN
            key: str = 'b'
            dictionary: dict[str, int] = {'a': 1, 'b': 2}
            supplier: Supplier[int] = lambda: 3

            # WHEN
            result: Optional[int] = dicts.get_value(dictionary, key, supplier)

            # THEN
            assert result == 2

    class TestErrorCase:
        def test_not_dict__should__raise_type_error(self) -> None:
            """When value is None should return False"""
            # GIVEN
            key: str = 'a key'
            dictionary: str = "Not a dict"

            # WHEN / THEN
            with raises(TypeError) as error:
                # noinspection PyTypeChecker
                dicts.get_value(dictionary, key)

            assert str(error.value) == "Optional[dict[K, V]] parameter is required"


class TestGetValueFromPath:
    """get_value_from_path function tests"""

    class TestNominalCase:
        def test_none_dict__should__return_none(self) -> None:
            """When dict is None should return None"""
            # GIVEN
            path: list[str] = ['key_1', 'key_2']

            # WHEN
            result: Optional[int] = dicts.get_value_from_path(None, path)

            # THEN
            assert result is None

        def test_none_dict_with_default_supplier__should__return_supplied_value(self) -> None:
            """When dict is None and default supplier is provided should return the supplied value"""
            # GIVEN
            path: list[str] = ['key_1', 'key_2']
            supplier: Supplier[int] = lambda: 2

            # WHEN
            result: Optional[int] = dicts.get_value_from_path(None, path, supplier)

            # THEN
            assert result == 2

        def test_none_path__should__return_none(self) -> None:
            """When path is None should return None"""
            # GIVEN
            dictionary: dict[str, int] = {'a': 1, 'b': 2}

            # WHEN
            # noinspection PyTypeChecker
            result: Optional[int] = dicts.get_value_from_path(dictionary, None)

            # THEN
            assert result is None

        def test_none_path_with_default_supplier__should__return_supplied_value(self) -> None:
            """When path is None and default supplier is provided should return the supplied value"""
            # GIVEN
            dictionary: dict[str, int] = {'a': 1, 'b': 2}
            supplier: Supplier[int] = lambda: 2

            # WHEN
            # noinspection PyTypeChecker
            result: Optional[int] = dicts.get_value_from_path(dictionary, None, supplier)

            # THEN
            assert result == 2

        def test_none_value__should__return_none(self) -> None:
            """When value is None should return None"""
            # GIVEN
            path: list[str] = ['key_1', 'key_2']
            dictionary: dict[str, int] = {'a': 1, 'b': 2}

            # WHEN
            result: Optional[int] = dicts.get_value_from_path(dictionary, path)

            # THEN
            assert result is None

        def test_none_value_with_default_supplier__should__return_supplied_value(self) -> None:
            """When value is None and default supplier is provided should return the supplied value"""
            # GIVEN
            path: list[str] = ['key_1', 'key_2']
            dictionary: dict[str, int] = {'a': 1, 'b': 2}
            supplier: Supplier[int] = lambda: 3

            # WHEN
            result: Optional[int] = dicts.get_value_from_path(dictionary, path, supplier)

            # THEN
            assert result == 3

        def test_deep_dict_and_none_value__should__return_none(self) -> None:
            """When value is None in a deep dict should return None"""
            # GIVEN
            path: list[Any] = ['a', 3]
            dictionary: dict[str, dict[int, str]] = {
                'a': {1: 'a1', 2: 'a2'},
                'b': {1: 'b1', 2: 'b2'}
            }

            # WHEN
            result: Optional[str] = dicts.get_value_from_path(dictionary, path)

            # THEN
            assert result is None

        def test_deep_dict_and_none_value_with_default_supplier__should__return_supplied_value(self) -> None:
            """When value is None in a deep dict and default supplier is provided should return the supplied value"""
            # GIVEN
            path: list[Any] = ['a', 3]
            dictionary: dict[str, dict[int, str]] = {
                'a': {1: 'a1', 2: 'a2'},
                'b': {1: 'b1', 2: 'b2'}
            }
            supplier: Supplier[str] = lambda: 'a3'

            # WHEN
            result: Optional[str] = dicts.get_value_from_path(dictionary, path, supplier)

            # THEN
            assert result == 'a3'

        def test_value_exits__should__return_the_value(self) -> None:
            """When value exists should return the value"""
            # GIVEN
            path: list[str] = ['b']
            dictionary: dict[str, int] = {'a': 1, 'b': 2}

            # WHEN
            result: Optional[int] = dicts.get_value_from_path(dictionary, path)

            # THEN
            assert result == 2

        def test_value_exits_with_default_supplier__should__return_the_value(self) -> None:
            """When value exists and default supplier is provided should return the value"""
            # GIVEN
            path: list[str] = ['b']
            dictionary: dict[str, int] = {'a': 1, 'b': 2}
            supplier: Supplier[int] = lambda: 3

            # WHEN
            result: Optional[int] = dicts.get_value_from_path(dictionary, path, supplier)

            # THEN
            assert result == 2

        def test_deep_dict_and_value_exits__should__return_the_value(self) -> None:
            """When value exists in deep dict should return the value"""
            # GIVEN
            path: list[Any] = ['a', 2]
            dictionary: dict[str, dict[int, str]] = {
                'a': {1: 'a1', 2: 'a2'},
                'b': {1: 'b1', 2: 'b2'}
            }
            # WHEN
            result: Optional[str] = dicts.get_value_from_path(dictionary, path)

            # THEN
            assert result == 'a2'

        def test_deep_dict_and_value_exits_with_default_supplier__should__return_the_value(self) -> None:
            """When value exists in a deep dict and default supplier is provided should return the value"""
            # GIVEN
            path: list[Any] = ['a', 2]
            dictionary: dict[str, dict[int, str]] = {
                'a': {1: 'a1', 2: 'a2'},
                'b': {1: 'b1', 2: 'b2'}
            }
            supplier: Supplier[str] = lambda: 'a3'

            # WHEN
            result: Optional[str] = dicts.get_value_from_path(dictionary, path, supplier)

            # THEN
            assert result == 'a2'

    class TestErrorCase:
        def test_not_dict__should__raise_type_error(self) -> None:
            """When value is None should return False"""
            # GIVEN
            key: str = 'a key'
            dictionary: str = "Not a dict"

            # WHEN / THEN
            with raises(TypeError) as error:
                # noinspection PyTypeChecker
                dicts.get_value_from_path(dictionary, key)

            assert str(error.value) == "Optional[dict[K, V]] parameter is required"
