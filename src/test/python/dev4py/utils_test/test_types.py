"""types module tests"""

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

from typing import Callable, Union, Awaitable

from dev4py.utils.types import Function, T, R, Predicate, Consumer, Supplier, Runnable, BiFunction, U, SyncOrAsync, \
    BiConsumer


class TestFunction:
    """Function type tests"""

    class TestNominalCase:

        def test_empty_function__should__be_equivalent_to_callable_t_r(self):
            """Empty Function should be equivalent to Callable[[T], R]"""
            # GIVEN
            current_type = Function

            # WHEN / THEN
            assert current_type == Callable[[T], R]

        def test_int_to_str_function__should__be_equivalent_to_callable_int_str(self):
            """Function[int, str] should be equivalent to Callable[[int], str]"""
            # GIVEN
            current_type = Function[int, str]

            # WHEN / THEN
            assert current_type == Callable[[int], str]

        def test_int_to_str_function__should__not_be_equivalent_to_callable_str_str(self):
            """Function[int, str] should NOT be equivalent to Callable[[str], str]"""
            # GIVEN
            current_type = Function[int, str]

            # WHEN / THEN
            assert current_type != Callable[[str], str]


class TestPredicate:
    """Predicate type tests"""

    class TestNominalCase:
        def test_empty_predicate__should__be_equivalent_to_callable_t_bool(self):
            """Empty Predicate should be equivalent to Callable[[T], bool]"""
            # GIVEN
            current_type = Predicate

            # WHEN / THEN
            assert current_type == Callable[[T], bool]

        def test_int_predicate__should__be_equivalent_to_callable_int_bool(self):
            """Predicate[int] should be equivalent to Callable[[int], bool]"""
            # GIVEN
            current_type = Predicate[int]

            # WHEN / THEN
            assert current_type == Callable[[int], bool]

        def test_int_predicate__should__not_be_equivalent_to_callable_str_bool(self):
            """Predicate[int] should NOT be equivalent to Callable[[str], bool]"""
            # GIVEN
            current_type = Predicate[int]

            # WHEN / THEN
            assert current_type != Callable[[str], bool]


class TestConsumer:
    """Consumer type tests"""

    class TestNominalCase:
        def test_empty_consumer__should__be_equivalent_to_callable_t_none(self):
            """Empty Consumer should be equivalent to Callable[[T], None]"""
            # GIVEN
            current_type = Consumer

            # WHEN / THEN
            assert current_type == Callable[[T], None]

        def test_int_consumer__should__be_equivalent_to_callable_int_none(self):
            """Consumer[int] should be equivalent to Callable[[int], None]"""
            # GIVEN
            current_type = Consumer[int]

            # WHEN / THEN
            assert current_type == Callable[[int], None]

        def test_int_consumer__should__not_be_equivalent_to_callable_str_none(self):
            """Consumer[int] should NOT be equivalent to Callable[[str], None]"""
            # GIVEN
            current_type = Consumer[int]

            # WHEN / THEN
            assert current_type != Callable[[str], None]


class TestSupplier:
    """Supplier type tests"""

    class TestNominalCase:
        def test_empty_supplier__should__be_equivalent_to_callable_empty_r(self):
            """Empty Supplier should be equivalent to Callable[[], R]"""
            # GIVEN
            current_type = Supplier

            # WHEN / THEN
            assert current_type == Callable[[], R]

        def test_int_supplier__should__be_equivalent_to_callable_int_none(self):
            """Supplier[int] should be equivalent to Callable[[], int]"""
            # GIVEN
            current_type = Supplier[int]

            # WHEN / THEN
            assert current_type == Callable[[], int]

        def test_int_supplier__should__not_be_equivalent_to_callable_str_int(self):
            """Supplier[int] should NOT be equivalent to Callable[[str], R]"""
            # GIVEN
            current_type = Supplier[int]

            # WHEN / THEN
            assert current_type != Callable[[str], int]

        def test_int_supplier__should__not_be_str_supplier(self):
            """Supplier[int] should NOT be equivalent to Callable[[], str]"""
            # GIVEN
            current_type = Supplier[int]

            # WHEN / THEN
            assert current_type != Callable[[], str]


class TestRunnable:
    """Runnable type tests"""

    class TestNominalCase:
        def test_runnable__should__be_equivalent_to_callable_empty_none(self):
            """Empty Supplier should be equivalent to Callable[[], None]"""
            # GIVEN
            current_type = Runnable

            # WHEN / THEN
            assert current_type == Callable[[], None]


class TestBiFunction:
    """BiFunction type tests"""

    class TestNominalCase:

        def test_empty_bifunction__should__be_equivalent_to_callable_t_u_r(self):
            """Empty BiFunction should be equivalent to Callable[[T, U], R]"""
            # GIVEN
            current_type = BiFunction

            # WHEN / THEN
            assert current_type == Callable[[T, U], R]

        def test_int_bool_to_str_bifunction__should__be_equivalent_to_callable_int_bool_str(self):
            """BiFunction[int, bool, str] should be equivalent to Callable[[int, bool], str]"""
            # GIVEN
            current_type = BiFunction[int, bool, str]

            # WHEN / THEN
            assert current_type == Callable[[int, bool], str]

        def test_int_bool_to_str_bifunction__should__not_be_equivalent_to_callable_str_bool_str(self):
            """BiFunction[int, str] should NOT be equivalent to Callable[[str, bool], str]"""
            # GIVEN
            current_type = BiFunction[int, bool, str]

            # WHEN / THEN
            assert current_type != Callable[[str, bool], str]

        def test_int_bool_to_str_bifunction__should__not_be_equivalent_to_callable_int_str_str(self):
            """BiFunction[int, str] should NOT be equivalent to Callable[[int, str], str]"""
            # GIVEN
            current_type = BiFunction[int, bool, str]

            # WHEN / THEN
            assert current_type != Callable[[int, str], str]


class TestSyncOrAsync:
    """SyncOrAsync type tests"""

    class TestNominalCase:
        def test_empty_syncorasync__should__be_equivalent_to_union_awaitable_t_t(self):
            """Empty SyncOrAsync should be equivalent to Union[Awaitable[T], T]"""
            # GIVEN
            current_type = SyncOrAsync

            # WHEN / THEN
            assert current_type == Union[Awaitable[T], T]

        def test_int_syncorasync__should__be_equivalent_to_union_awaitable_int_int(self):
            """SyncOrAsync[int] should be equivalent to Union[Awaitable[int], int]"""
            # GIVEN
            current_type = SyncOrAsync[int]

            # WHEN / THEN
            assert current_type == Union[Awaitable[int], int]

        def test_int_syncorasync__should__not_be_equivalent_to_awaitable_str_int(self):
            """SyncOrAsync[int] should NOT be equivalent to Union[Awaitable[str], int]"""
            # GIVEN
            current_type = SyncOrAsync[int]

            # WHEN / THEN
            assert current_type != Union[Awaitable[str], int]

        def test_int_syncorasync__should__not_be_equivalent_to_awaitable_int_str(self):
            """SyncOrAsync[int] should NOT be equivalent to Union[Awaitable[int], str]"""
            # GIVEN
            current_type = SyncOrAsync[int]

            # WHEN / THEN
            assert current_type != Union[Awaitable[int], str]

        def test_int_syncorasync__should__not_be_equivalent_to_awaitable_str_str(self):
            """SyncOrAsync[int] should NOT be equivalent to Union[Awaitable[str], str]"""
            # GIVEN
            current_type = SyncOrAsync[int]

            # WHEN / THEN
            assert current_type != Union[Awaitable[str], str]


class TestBiConsumer:
    """BiConsumer type tests"""

    class TestNominalCase:

        def test_empty_biconsumer__should__be_equivalent_to_callable_t_u_r(self):
            """Empty BiConsumer should be equivalent to Callable[[T, U], None]"""
            # GIVEN
            current_type = BiConsumer

            # WHEN / THEN
            assert current_type == Callable[[T, U], None]

        def test_int_bool_biconsumer__should__be_equivalent_to_callable_int_bool_none(self):
            """BiConsumer[int, bool] should be equivalent to Callable[[int, bool], None]"""
            # GIVEN
            current_type = BiConsumer[int, bool]

            # WHEN / THEN
            assert current_type == Callable[[int, bool], None]

        def test_int_bool_biconsumer__should__not_be_equivalent_to_callable_str_bool_none(self):
            """BiConsumer[int, str] should NOT be equivalent to Callable[[str, bool], none]"""
            # GIVEN
            current_type = BiConsumer[int, bool]

            # WHEN / THEN
            assert current_type != Callable[[str, bool], None]
