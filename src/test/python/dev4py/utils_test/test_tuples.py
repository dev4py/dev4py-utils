"""tuples module tests"""

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

from dev4py.utils import tuples


class TestEmptyTuple:
    """empty_tuple function tests"""

    class TestNominalCase:
        def test_should__return_an_empty_tuple(self) -> None:
            """Should return an empty tuple"""
            # GIVEN / WHEN
            result: tuple[int, ...] = tuples.empty_tuple()

            # THEN
            assert result == ()


class TestAppend:
    """append function tests"""

    class TestNominalCase:
        def test_existing_parameters__should__return_the_tuple_with_added_value(self) -> None:
            """When tuple and value are set, should return the tuple with added value"""
            # GIVEN
            tpl: tuple[int, ...] = (1, 2, 3)
            value: int = 4

            # WHEN
            result: tuple[int, ...] = tuples.append(tpl, value)

            # THEN
            assert result == (1, 2, 3, 4)
            assert tpl == (1, 2, 3)

        def test_none_value__should__return_the_tuple_with_added_value(self) -> None:
            """When tuple is set but value is none, should return the tuple with added value"""
            # GIVEN
            tpl: tuple[Optional[int], ...] = (1, 2, 3)
            value: Optional[int] = None

            # WHEN
            result: tuple[Optional[int], ...] = tuples.append(tpl, value)

            # THEN
            assert result == (1, 2, 3, None)
            assert tpl == (1, 2, 3)

    class TestErrorCase:
        def test_none_tuple__should__raise_type_error(self) -> None:
            """When the tuple is None, should raise TypeError exception"""
            # GIVEN
            value: int = 4

            # WHEN / THEN
            with raises(TypeError):
                # noinspection PyTypeChecker
                tuples.append(None, value)


class TestExtend:
    """extend function tests"""

    class TestNominalCase:
        def test_existing_parameters__should__add_elements_to_the_first_tuple_and_return_it(self) -> None:
            """When the tuples are set, should add all value from the second tuple to the first one and return it"""
            # GIVEN
            tpl_1: tuple[int, ...] = (1, 2, 3)
            tpl_2: tuple[int, ...] = (4, 5)

            # WHEN
            result: tuple[int, ...] = tuples.extend(tpl_1, tpl_2)

            # THEN
            assert result == (1, 2, 3, 4, 5)
            assert tpl_1 == (1, 2, 3)
            assert tpl_2 == (4, 5)

    class TestErrorCase:
        def test_none_first_tuple__should__raise_type_error(self) -> None:
            """When the first tuple is None, should raise TypeError exception"""
            # GIVEN
            tpl: tuple[int, ...] = tuples.empty_tuple()

            # WHEN / THEN
            with raises(TypeError):
                # noinspection PyTypeChecker
                tuples.extend(None, tpl)

        def test_none_second_tuple__should__raise_type_error(self) -> None:
            """When the second tuple is None, should raise TypeError exception"""
            # GIVEN
            tpl: tuple[int, ...] = tuples.empty_tuple()

            # WHEN / THEN
            with raises(TypeError):
                # noinspection PyTypeChecker
                tuples.extend(tpl, None)
