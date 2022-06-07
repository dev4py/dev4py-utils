"""lists module tests"""

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

from typing import Optional

from pytest import raises

from dev4py.utils import lists


class TestEmptyList:
    """empty_list function tests"""

    class TestNominalCase:
        def test_should__return_an_empty_list(self) -> None:
            """Should return an empty list"""
            # GIVEN / WHEN
            result: list[int] = lists.empty_list()

            # THEN
            assert result == []


class TestAppend:
    """append function tests"""

    class TestNominalCase:
        def test_existing_parameters__should__return_the_list_with_added_value(self) -> None:
            """When list and value are set, should return the list with added value"""
            # GIVEN
            lst: list[int] = [1, 2, 3]
            value: int = 4

            # WHEN
            result: list[int] = lists.append(lst, value)

            # THEN
            expected_result: list[int] = [1, 2, 3, 4]
            assert result == expected_result
            assert lst == expected_result

        def test_none_value__should__return_the_list_with_added_value(self) -> None:
            """When list is set but value is none, should return the list with added value"""
            # GIVEN
            lst: list[Optional[int]] = [1, 2, 3]
            value: Optional[int] = None

            # WHEN
            result: list[Optional[int]] = lists.append(lst, value)

            # THEN
            expected_result: list[Optional[int]] = [1, 2, 3, None]
            assert result == expected_result
            assert lst == expected_result

    class TestErrorCase:
        def test_none_list__should__raise_type_error(self) -> None:
            """When the list is None, should raise TypeError exception"""
            # GIVEN
            value: int = 4

            # WHEN / THEN
            with raises(TypeError):
                # noinspection PyTypeChecker
                lists.append(None, value)


class TestExtend:
    """extend function tests"""

    class TestNominalCase:
        def test_existing_parameters__should__add_elements_to_the_first_list_and_return_it(self) -> None:
            """When the lists are set, should add all value from the second list to the first one and return it"""
            # GIVEN
            lst_1: list[int] = [1, 2, 3]
            lst_2: list[int] = [4, 5]

            # WHEN
            result: list[int] = lists.extend(lst_1, lst_2)

            # THEN
            expected_result: list[int] = [1, 2, 3, 4, 5]
            assert result == expected_result
            assert lst_1 == expected_result
            assert lst_2 == [4, 5]

    class TestErrorCase:
        def test_none_first_list__should__raise_type_error(self) -> None:
            """When the first list is None, should raise TypeError exception"""
            # GIVEN
            lst: list[int] = lists.empty_list()

            # WHEN / THEN
            with raises(TypeError):
                # noinspection PyTypeChecker
                lists.extend(None, lst)

        def test_none_second_list__should__raise_type_error(self) -> None:
            """When the second list is None, should raise TypeError exception"""
            # GIVEN
            lst: list[int] = lists.empty_list()

            # WHEN / THEN
            with raises(TypeError):
                # noinspection PyTypeChecker
                lists.extend(lst, None)
