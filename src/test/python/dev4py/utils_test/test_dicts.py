"""dicts module tests"""

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

from typing import Optional, Any

from pytest import raises

from dev4py.utils import dicts, JOptional
from dev4py.utils.objects import is_none
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
            """When dictionary is not a dict should raise TypeError exception"""
            # GIVEN
            key: str = 'a key'
            dictionary: str = "Not a dict"

            # WHEN / THEN
            with raises(TypeError) as error:
                # noinspection PyTypeChecker
                dicts.get_value_from_path(dictionary, key)

            assert str(error.value) == "Optional[dict[K, V]] dictionary parameter must be a dict or None value"


class TestPutValue:
    """put_value function tests"""

    class TestNominalCase:
        def test_new_key__should__add_value_and_return_none(self):
            """When key doesn't exist, should add value to the key and return None"""
            # GIVEN
            key: str = 'a key'
            value: int = 1
            dictionary: dict[str, int] = {'key_1': 10}

            # WHEN
            result: Optional[int] = dicts.put_value(dictionary, key, value)

            # THEN
            assert len(dictionary) == 2
            assert dictionary[key] == value
            assert is_none(result)

        def test_key_exists__should__add_value_and_return_old_value(self):
            """When key exists, should add value to the key and return the old value"""
            # GIVEN
            key: str = 'a key'
            value: int = 1
            old_value: int = 666
            dictionary: dict[str, int] = {'key_1': 10, key: old_value}

            # WHEN
            result: Optional[int] = dicts.put_value(dictionary, key, value)

            # THEN
            assert len(dictionary) == 2
            assert dictionary[key] == value
            assert old_value == result

    class TestErrorCase:
        def test_none_dict__should__raise_type_error(self) -> None:
            """When dictionary is none should raise TypeError exception"""
            # GIVEN
            key: str = 'a key'
            value: int = 1
            dictionary: None = None

            # WHEN / THEN
            with raises(TypeError) as error:
                # noinspection PyTypeChecker
                dicts.put_value(dictionary, key, value)

            assert str(error.value) == "dictionary must be a dict value"

        def test_not_dict__should__raise_type_error(self) -> None:
            """When dictionary is not a dict should raise TypeError exception"""
            # GIVEN
            key: str = 'a key'
            value: int = 1
            dictionary: str = "Not a dict"

            # WHEN / THEN
            with raises(TypeError) as error:
                # noinspection PyTypeChecker
                dicts.put_value(dictionary, key, value)

            assert str(error.value) == "dictionary must be a dict value"


class TestEmptyDict:
    """empty_dict function tests"""

    class TestNominalCase:
        def test_should__return_an_empty_dict(self) -> None:
            """Should return an empty dict"""
            # GIVEN / WHEN
            dictionary: dict[str, int] = dicts.empty_dict()

            # THEN
            assert dictionary == {}


class TestUpdate:
    """update function tests"""

    class TestNominalCase:
        def test_existing_parameters__should__return_first_dict_with_added_elements(self) -> None:
            """When all parameters are set, should update and return the first dict with the second one"""
            # GIVEN
            dict_1: dict[str, int] = {'k1_1': 11, 'k1_2': 12}
            dict_2: dict[str, int] = {'k2_1': 21, 'k2_2': 22}

            # WHEN
            result: dict[str, int] = dicts.update(dict_1, dict_2)

            # THEN
            expected_result: dict[str, int] = {'k1_1': 11, 'k1_2': 12, 'k2_1': 21, 'k2_2': 22}
            assert result == expected_result
            assert dict_1 == expected_result
            assert dict_2 == {'k2_1': 21, 'k2_2': 22}

        def test_empty_second_dict__should__return_first_dict_without_update(self) -> None:
            """When the second dict is empty, should return the first dict without update"""
            # GIVEN
            dict_1: dict[str, int] = {'k1_1': 11, 'k1_2': 12}
            dict_2: dict[str, int] = dicts.empty_dict()

            # WHEN
            result: dict[str, int] = dicts.update(dict_1, dict_2)

            # THEN
            expected_result: dict[str, int] = {'k1_1': 11, 'k1_2': 12}
            assert result == expected_result
            assert dict_1 == expected_result
            assert dict_2 == {}

    class TestErrorCase:
        def test_none_first_dict__should__raise_type_error(self) -> None:
            """When the first dict is None should raise TypeError exception"""
            # GIVEN
            dictionary: dict[str, int] = dicts.empty_dict()

            # WHEN / THEN
            with raises(TypeError):
                # noinspection PyTypeChecker
                dicts.update(None, dictionary)

        def test_none_second_dict__should__raise_type_error(self) -> None:
            """When the second dict is None should raise TypeError exception"""
            # GIVEN
            dictionary: dict[str, int] = dicts.empty_dict()

            # WHEN / THEN
            with raises(TypeError):
                # noinspection PyTypeChecker
                dicts.update(dictionary, None)
