"""types module tests"""

from typing import Callable

from dev4py.utils.types import Function, T, R, Predicate, Consumer, Supplier, Runnable


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
