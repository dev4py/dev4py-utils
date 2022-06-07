"""collectors module tests"""

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

from dataclasses import FrozenInstanceError, dataclass
from typing import Final

from pytest import raises

from dev4py.utils import Collector, collectors
from dev4py.utils.objects import non_none, to_self
from dev4py.utils.types import Supplier, BiFunction, BiConsumer, Function


class TestCollector:
    """Collector class tests"""

    class TestConstructor:
        """Constructor tests"""

        class TestNominalCase:

            def test_existing_parameters__should__create_a_new_collector(self) -> None:
                """When all parameters are set, should create a new collector with given parameters"""
                # GIVEN
                supplier: Final[Supplier[int]] = lambda: 0
                accumulator: Final[BiFunction[int, int, int]] = lambda i1, i2: i1 + i2
                combiner: Final[BiFunction[int, int, int]] = lambda i1, i2: i1 + i2

                # WHEN
                collector: Collector = Collector(supplier=supplier, accumulator=accumulator, combiner=combiner)

                # THEN
                assert non_none(collector)
                assert collector.supplier == supplier
                assert collector.accumulator == accumulator
                assert collector.combiner == combiner

        class TestErrorCase:
            def test_none_supplier__should__raise_type_error(self) -> None:
                """When supplier is None should raise a TypeError exception"""
                # GIVEN
                accumulator: Final[BiFunction[int, int, int]] = lambda i1, i2: i1 + i2
                combiner: Final[BiFunction[int, int, int]] = lambda i1, i2: i1 + i2

                # WHEN / THEN
                with raises(TypeError):
                    Collector(supplier=None, accumulator=accumulator, combiner=combiner)

            def test_none_accumulator__should__raise_type_error(self) -> None:
                """When accumulator is None should raise a TypeError exception"""
                # GIVEN
                supplier: Final[Supplier[int]] = lambda: 0
                combiner: Final[BiFunction[int, int, int]] = lambda i1, i2: i1 + i2

                # WHEN / THEN
                with raises(TypeError):
                    Collector(supplier=supplier, accumulator=None, combiner=combiner)

            def test_none_combiner__should__raise_type_error(self) -> None:
                """When combiner is None should raise a TypeError exception"""
                # GIVEN
                supplier: Final[Supplier[int]] = lambda: 0
                accumulator: Final[BiFunction[int, int, int]] = lambda i1, i2: i1 + i2

                # WHEN / THEN
                with raises(TypeError):
                    Collector(supplier=supplier, accumulator=accumulator, combiner=None)

    class TestSetters:
        """Setters tests"""

        class TestErrorCase:
            def test_set_new_supplier__should__raise_frozen_instance_error(self) -> None:
                """When set a new supplier, should raise a FrozenInstanceError exception"""
                # GIVEN
                supplier: Final[Supplier[int]] = lambda: 0
                accumulator: Final[BiFunction[int, int, int]] = lambda i1, i2: i1 + i2
                combiner: Final[BiFunction[int, int, int]] = lambda i1, i2: i1 + i2
                collector: Collector = Collector(supplier=supplier, accumulator=accumulator, combiner=combiner)

                # WHEN / THEN
                new_supplier: Final[Supplier[int]] = lambda: 10
                with raises(FrozenInstanceError):
                    # noinspection PyDataclass
                    collector.supplier = new_supplier

            def test_set_new_accumulator__should__raise_frozen_instance_error(self) -> None:
                """When set a new accumulator, should raise a FrozenInstanceError exception"""
                # GIVEN
                supplier: Final[Supplier[int]] = lambda: 0
                accumulator: Final[BiFunction[int, int, int]] = lambda i1, i2: i1 + i2
                combiner: Final[BiFunction[int, int, int]] = lambda i1, i2: i1 + i2
                collector: Collector = Collector(supplier=supplier, accumulator=accumulator, combiner=combiner)

                # WHEN / THEN
                new_accumulator: Final[BiFunction[int, int, int]] = lambda i1, i2: i1 + i2 + 2
                with raises(FrozenInstanceError):
                    # noinspection PyDataclass
                    collector.accumulator = new_accumulator

            def test_set_new_combiner__should__raise_frozen_instance_error(self) -> None:
                """When set a new combiner, should raise a FrozenInstanceError exception"""
                # GIVEN
                supplier: Final[Supplier[int]] = lambda: 0
                accumulator: Final[BiFunction[int, int, int]] = lambda i1, i2: i1 + i2
                combiner: Final[BiFunction[int, int, int]] = lambda i1, i2: i1 + i2
                collector: Collector = Collector(supplier=supplier, accumulator=accumulator, combiner=combiner)

                # WHEN / THEN
                new_combiner: Final[BiFunction[int, int, int]] = lambda i1, i2: i1 + i2 + 2
                with raises(FrozenInstanceError):
                    # noinspection PyDataclass
                    collector.combiner = new_combiner


class TestOf:
    """of function tests"""

    class TestNominalCase:
        def test_existing_parameters__should__create_a_new_collector(self) -> None:
            """When all parameters are set, should create a new collector with given parameters"""
            # GIVEN
            supplier: Final[Supplier[int]] = lambda: 0
            accumulator: Final[BiFunction[int, int, int]] = lambda i1, i2: i1 + i2
            combiner: Final[BiFunction[int, int, int]] = lambda i1, i2: i1 + i2

            # WHEN
            collector: Collector = collectors.of(supplier=supplier, accumulator=accumulator, combiner=combiner)

            # THEN
            assert non_none(collector)
            assert collector.supplier == supplier
            assert collector.accumulator == accumulator
            assert collector.combiner == combiner

    class TestErrorCase:
        def test_none_supplier__should__raise_type_error(self) -> None:
            """When supplier is None should raise a TypeError exception"""
            # GIVEN
            accumulator: Final[BiFunction[int, int, int]] = lambda i1, i2: i1 + i2
            combiner: Final[BiFunction[int, int, int]] = lambda i1, i2: i1 + i2

            # WHEN / THEN
            with raises(TypeError):
                collectors.of(supplier=None, accumulator=accumulator, combiner=combiner)

        def test_none_accumulator__should__raise_type_error(self) -> None:
            """When accumulator is None should raise a TypeError exception"""
            # GIVEN
            supplier: Final[Supplier[int]] = lambda: 0
            combiner: Final[BiFunction[int, int, int]] = lambda i1, i2: i1 + i2

            # WHEN / THEN
            with raises(TypeError):
                collectors.of(supplier=supplier, accumulator=None, combiner=combiner)

        def test_none_combiner__should__raise_type_error(self) -> None:
            """When combiner is None should raise a TypeError exception"""
            # GIVEN
            supplier: Final[Supplier[int]] = lambda: 0
            accumulator: Final[BiFunction[int, int, int]] = lambda i1, i2: i1 + i2

            # WHEN / THEN
            with raises(TypeError):
                collectors.of(supplier=supplier, accumulator=accumulator, combiner=None)


@dataclass
class IntClass:
    value: int = 0

    def add(self, value: int) -> None:
        self.value += value


class TestOfBiconsumers:
    """of_biconsumers function tests"""

    class TestNominalCase:
        def test_existing_parameters__should__create_a_new_collector(self) -> None:
            """When all parameters are set, should create a new collector with given parameters"""
            # GIVEN
            supplier: Final[Supplier[IntClass]] = lambda: IntClass()
            accumulator: Final[BiConsumer[IntClass, int]] = lambda icls, i: icls.add(i)
            combiner: Final[BiConsumer[IntClass, IntClass]] = lambda icls1, icls2: icls1.add(icls2.value)

            # WHEN
            collector: Collector = collectors \
                .of_biconsumers(supplier=supplier, accumulator=accumulator, combiner=combiner)

            # THEN
            assert non_none(collector)
            collector_supplier: Final[Supplier[IntClass]] = collector.supplier
            assert collector_supplier == supplier
            assert collector_supplier().value == 0
            assert collector.accumulator(IntClass(value=2), 8).value == 10
            assert collector.combiner(IntClass(value=2), IntClass(value=8)).value == 10

    class TestErrorCase:
        def test_none_supplier__should__raise_type_error(self) -> None:
            """When supplier is None should raise a TypeError exception"""
            # GIVEN
            accumulator: Final[BiConsumer[IntClass, int]] = lambda icls, i: icls.add(i)
            combiner: Final[BiConsumer[IntClass, IntClass]] = lambda icls1, icls2: icls1.add(icls2.value)

            # WHEN / THEN
            with raises(TypeError):
                collectors.of_biconsumers(supplier=None, accumulator=accumulator, combiner=combiner)

        def test_none_accumulator__should__raise_type_error(self) -> None:
            """When accumulator is None should raise a TypeError exception"""
            # GIVEN
            supplier: Final[Supplier[IntClass]] = lambda: IntClass()
            combiner: Final[BiConsumer[IntClass, IntClass]] = lambda icls1, icls2: icls1.add(icls2.value)

            # WHEN / THEN
            with raises(TypeError):
                collectors.of_biconsumers(supplier=supplier, accumulator=None, combiner=combiner)

        def test_none_combiner__should__raise_type_error(self) -> None:
            """When combiner is None should raise a TypeError exception"""
            # GIVEN
            supplier: Final[Supplier[IntClass]] = lambda: IntClass()
            accumulator: Final[BiConsumer[IntClass, int]] = lambda icls, i: icls.add(i)

            # WHEN / THEN
            with raises(TypeError):
                collectors.of_biconsumers(supplier=supplier, accumulator=accumulator, combiner=None)


class TestToList:
    """to_list function tests"""

    class TestNominalCase:
        def test_should__return_list_collector(self) -> None:
            """Should return a Collector that accumulates the input elements into a new list"""
            # GIVEN / WHEN
            collector: Collector[int, list[int]] = collectors.to_list()

            # THEN
            assert collector.supplier() == []
            assert collector.accumulator([], 1) == [1]
            assert collector.combiner([1], [2]) == [1, 2]


class TestToDict:
    """to_dict function tests"""

    class TestNominalCase:
        def test_existing_mappers__should__return_dict_collector(self) -> None:
            """When key/value mappers are provided, should return a dict collector"""
            # GIVEN
            key_mapper: Function[int, str] = lambda i: str(i)
            value_mapper: Function[int, int] = to_self

            # WHEN
            collector: Collector[int, dict[str, int]] = collectors.to_dict(key_mapper, value_mapper)

            # THEN
            assert collector.supplier() == {}
            assert collector.accumulator({}, 1) == {'1': 1}
            assert collector.combiner({'1': 1}, {'2': 2}) == {'1': 1, '2': 2}

    class TestErrorCase:
        def test_none_key_mapper__should__raise_type_error(self) -> None:
            """When key mapper is None should raise a TypeError exception"""
            # GIVEN
            value_mapper: Function[int, int] = to_self

            # WHEN / THEN
            with raises(TypeError):
                collectors.to_dict(None, value_mapper)

        def test_none_value_mapper__should__raise_type_error(self) -> None:
            """When value mapper is None should raise a TypeError exception"""
            # GIVEN
            key_mapper: Function[int, str] = lambda i: str(i)

            # WHEN / THEN
            with raises(TypeError):
                collectors.to_dict(key_mapper, None)


class TestToNone:
    """to_none function tests"""

    class TestNominalCase:
        def test_should__return_none_collector(self) -> None:
            """Should return a Collector that always returns None"""
            # GIVEN / WHEN
            collector: Collector[int, None] = collectors.to_none()

            # THEN
            assert collector.supplier() is None
            assert collector.accumulator(None, None) is None
            assert collector.accumulator(None, 1) is None
            assert collector.accumulator([], None) is None
            assert collector.accumulator([], 1) is None
            assert collector.combiner(None, None) is None
            assert collector.combiner([1], None) is None
            assert collector.combiner(None, [2]) is None
            assert collector.combiner([1], [2]) is None


class TestToTuple:
    """to_tuple function tests"""

    class TestNominalCase:
        def test_should__return_tuple_collector(self) -> None:
            """Should return a Collector that accumulates the input elements into a new tuple"""
            # GIVEN / WHEN
            collector: Collector[int, tuple[int, ...]] = collectors.to_tuple()

            # THEN
            assert collector.supplier() == ()
            assert collector.accumulator((), 1) == (1,)
            assert collector.combiner((1,), (2,)) == (1, 2)


class TestToCounter:
    """to_counter function tests"""

    class TestNominalCase:
        def test_should__return_counter_collector(self) -> None:
            """Should return a Collector accepting elements of type T that counts the number of input elements"""
            # GIVEN / WHEN
            collector: Collector[int, int] = collectors.to_counter()

            # THEN
            assert collector.supplier() == 0
            assert collector.accumulator(1, 10) == 2
            assert collector.combiner(3, 7) == 10
