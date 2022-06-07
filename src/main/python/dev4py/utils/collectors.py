"""The `collectors` module provides a set of collectors inspired by java (java.util.stream.Collectors)"""

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

from dataclasses import dataclass
from functools import partial
from typing import Generic, Any

from dev4py.utils import lists, dicts, objects, tuples
from dev4py.utils.objects import require_non_none
from dev4py.utils.types import BiConsumer, BiFunction, Supplier, T, R, Function, K, V


##############################
#  MODULE CLASSES/FUNCTIONS  #
##############################
@dataclass(frozen=True)
class Collector(Generic[T, R]):
    """
    Collector class: A generic dataclass to describe a collector[T,R]

    Args:
        supplier (Supplier[R]): A function that creates and returns a new result container
        accumulator (BiFunction[R, T, R]): A function that folds a value into a result container
        combiner (BiFunction[R, R, R]): A function that accepts two partial results and merges them
    """
    supplier: Supplier[R]
    accumulator: BiFunction[R, T, R]
    combiner: BiFunction[R, R, R]

    def __post_init__(self):
        """
        Post init values checker
        Raises:
            TypeError: Raises a TypeError at least one parameter is None
        """
        require_non_none(self.supplier)
        require_non_none(self.accumulator)
        require_non_none(self.combiner)


def of(supplier: Supplier[R], accumulator: BiFunction[R, T, R], combiner: BiFunction[R, R, R]) -> Collector[T, R]:
    """
    Returns a Collector by using the given parameters

    Args:
        supplier (Supplier[R]): A function that creates and returns a new result container
        accumulator (BiFunction[R, T, R]): A function that folds a value into a result container
        combiner (BiFunction[R, R, R]): A function that accepts two partial results and merges them

    Returns:
        collector: a collector[T,R] built with given parameters

    Raises:
        TypeError: Raises a TypeError at least one parameter is None
    """
    return Collector(
        supplier=require_non_none(supplier),
        accumulator=require_non_none(accumulator),
        combiner=require_non_none(combiner)
    )


def of_biconsumers(supplier: Supplier[R], accumulator: BiConsumer[R, T], combiner: BiConsumer[R, R]) -> Collector[T, R]:
    """
    Returns a Collector by using the given parameters (biconsumer instead of bifunction)

    Args:
        supplier (Supplier[R]): A function that creates and returns a new result container
        accumulator (BiConsumer[R, T]): A function that folds a value into a result container
        combiner (BiConsumer[R, R]): A function that accepts two partial results and merges them

    Returns:
        collector: a collector[T,R] built with given parameters

    Raises:
        TypeError: Raises a TypeError at least one parameter is None
    """
    return of(
        supplier=require_non_none(supplier),
        accumulator=_to_bifunction(accumulator),
        combiner=_to_bifunction(combiner)
    )


def to_list() -> Collector[T, list[T]]:
    """
    Returns a Collector that accumulates the input elements into a new list

    Returns:
        Collector[T, list[T]]: a Collector that accumulates the input elements into a new list
    """
    return of(
        supplier=lists.empty_list,
        accumulator=lists.append,
        combiner=lists.extend
    )


def to_dict(key_mapper: Function[T, K], value_mapper: Function[T, V]) -> Collector[T, dict[K, V]]:
    """
    Returns a Collector that accumulates elements into a dict whose keys and values are the result of applying the
    provided mapping functions to the input elements

    Args:
        key_mapper: a mapping function to produce keys
        value_mapper: a mapping function to produce values

    Returns:
         Collector[T, dict[K, V]]: a Collector which collects elements into a dict whose keys and values are the result
            of applying mapping functions to the input elements
    """
    require_non_none(key_mapper)
    require_non_none(value_mapper)
    return of_biconsumers(
        supplier=dicts.empty_dict,
        accumulator=partial(_to_dict_accumulator, key_mapper=key_mapper, value_mapper=value_mapper),
        combiner=_to_dict_combiner
    )


def to_none() -> Collector[T, None]:
    """
    Returns a Collector that always returns None

    Returns:
        Collector[T, None]: A collector that always returns None
    """
    return of(
        supplier=objects.to_none,
        accumulator=objects.to_none,
        combiner=objects.to_none
    )


def to_tuple() -> Collector[T, tuple[T, ...]]:
    """
    Returns a Collector that accumulates the input elements into a new tuple

    Returns:
        Collector[T, tuple[T, ...]]: a Collector that accumulates the input elements into a new tuple
    """
    return of(
        supplier=tuples.empty_tuple,
        accumulator=tuples.append,
        combiner=tuples.extend
    )


def to_counter() -> Collector[T, int]:
    """
    Returns a Collector accepting elements of type T that counts the number of input elements

    Returns:
        Collector[T, int]: a Collector accepting elements of type T that counts the number of input elements
    """
    return of(
        supplier=_to_counter_supplier,
        accumulator=_to_counter_accumulator,
        combiner=_to_counter_combiner
    )


##############################
#  PRIVATE MODULE FUNCTIONS  #
##############################
def _bifunction_from_biconsumer(t: T, r: R, biconsumer: BiConsumer[T, R]) -> T:
    """
    private function to create a BiFunction from a BiConsumer by using `partial` function
    Note: lambda or inner function are not used in order to be compatible with multiprocessing (lambda are not
    serializable)
    """
    require_non_none(biconsumer)(t, r)
    return t


def _to_bifunction(biconsumer: BiConsumer[T, R]) -> BiFunction[T, R, T]:
    """
    private function to create a BiFunction from a BiConsumer
    Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)
    """
    return partial(_bifunction_from_biconsumer, biconsumer=require_non_none(biconsumer))


def _to_dict_accumulator(d: dict[K, V], value: T, key_mapper: Function[T, K], value_mapper: Function[T, V]) -> None:
    """
    private function to represent a dict accumulator
    Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)
    """
    dicts.put_value(d, key_mapper(value), value_mapper(value))


def _to_dict_combiner(d1: dict[K, V], d2: dict[K, V]) -> None:
    """
    private function to represent a dict combiner
    Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)
    """
    dicts.update(d1, d2)


def _to_counter_supplier() -> int:
    """
    private function to represent a counter supplier
    Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)
    """
    return 0


def _to_counter_accumulator(i: int, value: Any) -> int:  # pylint: disable=W0613
    """
    private function to represent a counter accumulator
    Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)
    """
    return i + 1


def _to_counter_combiner(i1: int, i2: int) -> int:
    """
    private function to represent a counter combiner
    Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)
    """
    return i1 + i2
