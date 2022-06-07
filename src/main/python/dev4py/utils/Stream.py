"""Stream module inspired by `java.util.stream`"""  # pylint: disable=C0302

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

from __future__ import annotations

from concurrent.futures import Executor, wait, FIRST_COMPLETED, Future, as_completed
from dataclasses import dataclass
from functools import partial, cmp_to_key
from typing import Generic, Final, Optional, cast, Any, Collection, Iterable, Iterator

from dev4py.utils import collectors
from dev4py.utils.JOptional import JOptional
from dev4py.utils.collectors import Collector
from dev4py.utils.iterables import get_chunks
from dev4py.utils.objects import require_non_none, require_non_none_else_get, to_self
from dev4py.utils.pipeline import StepPipeline, StepResult
from dev4py.utils.types import T, Function, R, V, Predicate, Supplier, BiConsumer, K, Consumer, BiFunction


##############################
#  PRIVATE MODULE FUNCTIONS  #
##############################
def _default_handler(v: V) -> StepResult[R]:
    """
    private function to describe default pipeline handler
    Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)
    """
    # lambda v: StepResult(cast(R, v))
    return StepResult(cast(R, v))


def _root_pipeline() -> StepPipeline[V, R]:
    """
    private function to describe default pipeline
    Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)
    """
    return StepPipeline.of(_default_handler)


def _none_collector() -> Collector[T, R]:
    """
    private function to cast none_collector
    Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)
    """
    return cast(Collector[T, R], collectors.to_none())


def _map_lambda(v: T, mapper: Function[T, R]) -> StepResult[R]:
    """
    private function to describe map method handler
    Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)
    """
    # lambda v: StepResult(value=mapper(v))
    return StepResult(value=mapper(v))


def _filter_lambda(v: T, predicate: Predicate[T]) -> StepResult[T]:
    """
    private function to describe filter method handler
    Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)
    """
    # lambda v: StepResult(value=v, go_next=predicate(v))
    return StepResult(value=v, go_next=predicate(v))


def _and_lambda(b1: bool, b2: bool) -> bool:
    """
    private function to describe a AND BiFunction
    Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)
    """
    # lambda b1, b2: b1 and b2
    return b1 and b2


def _stream_to_list_lambda(stream: Stream[T]) -> list[T]:
    """
    private function to describe a stream to list Function
    Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)
    Note: use lists because generators cannot be used in parallel context (generators are not serializable)
    """
    # lambda stream: stream.to_list()
    return stream.to_list()


def _peek_mapper(value: T, consumer: Consumer[T]) -> T:
    """
    private function to describe peek method mapper
    Note: inner function are not used in order to be compatible with multiprocessing (inner function are not
    serializable)
    """
    consumer(value)
    return value


def _natural_comparator(o1: Any, o2: Any) -> int:
    """
    private function to describe a natural order comparator
    Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)
    """
    return 0 if o1 == o2 else 1 if o1 > o2 else -1  # pragma: no mutate


def _to_max_comparator(o1: T, o2: T, comparator: BiFunction[T, T, int]) -> int:
    """
    private function to describe a reverse order comparator
    Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)
    """
    return -comparator(o1, o2)


def _sync_execution(
        values: Iterable[V],
        pipeline: StepPipeline[V, T],
        stop_on_first_completed: bool,
        collector: Collector[T, R]
) -> R:
    """
    private function to describe a sync stream execution
    Note: Outside the Stream class in order to be compatible with multiprocessing
    """
    return _process_values(values, pipeline, stop_on_first_completed, collector)[0]


def _parallel_execution(  # pylint: disable=R0913
        values: Iterable[V],
        pipeline: StepPipeline[V, T],
        parallel_config: ParallelConfiguration,
        ordered_execution: bool,
        stop_on_first_completed: bool,
        collector: Collector[T, R]
) -> R:
    """
    private function to describe a parallel stream execution
    Note: Outside the Stream class in order to be compatible with multiprocessing
    """
    chunksize: int = parallel_config.chunksize
    executor: Executor = parallel_config.executor
    process_values: Final[partial[tuple[R, bool]]] = \
        partial(
            _process_values, pipeline=pipeline, stop_on_first_completed=stop_on_first_completed, collector=collector
        )
    futures: Final[list[Future[tuple[R, bool]]]] = \
        [executor.submit(process_values, chunk) for chunk in get_chunks(values, chunksize)]

    return (_ordered_parallel_execution if ordered_execution else _unordered_parallel_execution)(
        futures=futures,
        collector=collector
    )


def _unordered_parallel_execution(futures: list[Future[tuple[R, bool]]], collector: Collector[T, R]) -> R:
    """
    private function to describe an unordered parallel stream execution
    Note: Outside the Stream class in order to be compatible with multiprocessing
    """
    done: Collection[Future[tuple[R, bool]]]
    not_done: Collection[Future[tuple[R, bool]]] = futures

    try:
        results: R = collector.supplier()
        continue_processing: bool = True

        # 'do {...} while' doesn't exist in python :'(
        while not_done and (continue_processing is True):  # pragma: no mutate
            done, not_done = wait(not_done, return_when=FIRST_COMPLETED)
            for future in done:
                chunk_result: tuple[R, bool] = future.result()
                results = collector.combiner(results, chunk_result[0])
                continue_processing = chunk_result[1]
                if continue_processing is False:
                    break  # pragma: no mutate

        return results
    finally:
        for future in not_done:
            future.cancel()


def _ordered_parallel_execution(futures: list[Future[tuple[R, bool]]], collector: Collector[T, R]) -> R:
    """
    private function to describe an ordered parallel stream execution
    Note: Outside the Stream class in order to be compatible with multiprocessing
    """
    results: R = collector.supplier()
    processed_value: int = 0  # pragma: no mutate
    try:
        for future in futures:
            processed_value += 1  # pragma: no mutate
            chunk_result: tuple[R, bool] = future.result()
            results = collector.combiner(results, chunk_result[0])
            if chunk_result[1] is False:
                break  # pragma: no mutate
    finally:
        for i in range(processed_value, len(futures)):
            futures[i].cancel()

    return results


def _process_values(
        values: Iterable[V],
        pipeline: StepPipeline[V, T],
        stop_on_first_completed: bool,
        collector: Collector[T, R]
) -> tuple[R, bool]:
    """
    private function to describe process stream value set execution
    Note: Outside the Stream class in order to be compatible with multiprocessing
    """
    continue_processing: bool = True
    # Note: Always ordered
    results: R = collector.supplier()
    for result in _sync_generator(values, pipeline):
        results = collector.accumulator(results, result)
        if stop_on_first_completed:
            continue_processing = False  # pragma: no mutate
            break  # pragma: no mutate

    return results, continue_processing


def _sync_generator(values: Iterable[V], pipeline: StepPipeline[V, T]) -> Iterable[T]:
    """
    private function to describe a sync Stream generator
    Note: Outside the Stream class in order to be compatible with multiprocessing
    """
    for value in values:
        result: StepResult[Any] = pipeline.execute(value)
        # Note: go_next TRUE means the value has gone through the whole pipeline and has not been filtered
        if result.go_next:
            yield result.value


def _parallel_generator(
        values: Iterable[V],
        pipeline: StepPipeline[V, T],
        parallel_config: ParallelConfiguration,
        ordered_execution: bool
) -> Iterable[T]:
    """
    private function to describe a parallel Stream generator (ordered or not)
    Note: Outside the Stream class in order to be compatible with multiprocessing
    """
    chunksize: int = parallel_config.chunksize
    executor: Executor = parallel_config.executor
    process_values: Final[partial[tuple[list[T], bool]]] = \
        partial(_process_values, pipeline=pipeline, stop_on_first_completed=False, collector=collectors.to_list())
    futures: Final[list[Future[tuple[list[T], bool]]]] = \
        [executor.submit(process_values, chunk) for chunk in get_chunks(values, chunksize)]
    try:
        futures_iterable: Final[Iterable[Future[tuple[list[T], bool]]]] = \
            (futures if ordered_execution else as_completed(futures))
        for future in futures_iterable:
            for value in future.result()[0]:
                yield value

    except BaseException as e:
        for future in futures:
            future.cancel()
        raise e


##############################
#       PUBLIC CLASSES       #
##############################
@dataclass(frozen=True)
class ParallelConfiguration:
    """
    ParallelConfiguration class that describes Stream parallel configuration when using parallel execution

    Args:
        executor (Executor): The executor to use for parallel (/concurrent) execution
        chunksize (int): If greater than one, the stream values will be chopped into chunks of size chunksize and
            submitted to the process pool. If set to one, the items in the stream will be sent one at a time.

    Raises:
        TypeError: if executor is None
        ValueError: if chunksize is less than 1
    """
    executor: Executor
    chunksize: int = 1

    def __post_init__(self):
        require_non_none(self.executor, "executor must be non None")
        if require_non_none(self.chunksize, "chunksize must be non None") < 1:
            raise ValueError("chunksize must be greater than or equals to 1")


class Stream(Generic[T]):  # pylint: disable=R0904
    __CREATE_KEY: Final[object] = object()

    @classmethod
    def empty(cls) -> Stream[T]:
        """
        Returns an empty sequential Stream

        Returns:
            Stream[T]: An empty sequential Stream
        """
        return cls.of()

    @classmethod
    def of(cls, *values: T) -> Stream[T]:
        """
        Returns a sequential ordered stream whose elements are the specified values

        Args:
            *values: ordered stream elements

        Returns:
            Stream[T]: A sequential ordered stream whose elements are the specified values
        """
        return cls.of_iterable(values)

    @classmethod
    def of_iterable(cls, iterable: Iterable[T]) -> Stream[T]:
        """
        Returns a sequential ordered stream whose elements are values from the given Iterable

        Args:
            iterable: iterable of stream source values

        Returns:
            Stream[T]: A sequential ordered stream whose elements are values from the given Iterable

        Raises:
            TypeError: if iterable is None
        """
        require_non_none(iterable)
        return cls._of(lambda p, o: iterable)

    @classmethod
    def _of(
            cls,
            values_function: BiFunction[Optional[ParallelConfiguration], bool, Iterable[V]],
            pipeline: Optional[StepPipeline[V, R]] = None,
            parallel_config: Optional[JOptional[ParallelConfiguration]] = None,
            ordered_execution: bool = False
    ) -> Stream[R]:
        """
        Private class method in order to simplify the call to Stream private constructor

        Args:
            values_function: The BiFunction which provides the Stream values
            pipeline: The StepPipeline to be executed if presents by the Stream values on terminal operation
            parallel_config: The Stream parallel configuration
            ordered_execution: TRUE if the value must be returned to the encounter order

        Returns:
            Stream[T]: A Stream corresponding to the given parameters
        """
        return Stream(
            values_function=values_function,
            pipeline=require_non_none_else_get(pipeline, _root_pipeline),
            parallel_config=require_non_none_else_get(parallel_config, JOptional.empty),
            ordered_execution=ordered_execution,
            create_key=cls.__CREATE_KEY
        )

    def __init__(  # pylint: disable=R0913
            self,
            values_function: BiFunction[Optional[ParallelConfiguration], bool, Iterable[V]],
            pipeline: StepPipeline[V, T],
            parallel_config: JOptional[ParallelConfiguration],
            ordered_execution: bool,
            create_key: object,
    ):
        """Stream private constructor: Constructs a Stream[T] inspired by java `java.util.stream.Stream<T>`"""
        assert create_key == self.__CREATE_KEY, "Stream private constructor! Please use Stream.of"
        self._values_function: BiFunction[Optional[ParallelConfiguration], bool, Iterable[V]] = \
            require_non_none(values_function)
        self._pipeline: StepPipeline[V, T] = require_non_none(pipeline)
        self._parallel_config: JOptional[ParallelConfiguration] = require_non_none(parallel_config)
        self._ordered_execution: bool = require_non_none(ordered_execution)

    def map(self, mapper: Function[T, R]) -> Stream[R]:
        """
        Returns a stream consisting of the results of applying the given function to the elements of this stream

        Args:
            mapper (Function[T, R]): The function to apply to each element

        Returns:
            Stream[R]: A stream consisting of the results of applying the given function to the elements of this stream

        Raises:
            TypeError: if mapper is None
        """
        require_non_none(mapper)
        return Stream._of(
            values_function=self._values_function,
            # pylint: disable=E1101
            pipeline=self._pipeline.add_handler(cast(Function[T, StepResult[R]], partial(_map_lambda, mapper=mapper))),
            parallel_config=self._parallel_config,
            ordered_execution=self._ordered_execution
        )

    def parallel(self, parallel_config: Optional[ParallelConfiguration]) -> Stream[T]:
        """
        Configures the Stream to use the given parallel configuration and return the current stream

        Note: None parallel configuration is like calling `sequential()` method

        Args:
            parallel_config: The parallel configuration to use

        Returns:
            Stream[T]: The current Stream after set parallel configuration
        """
        self._parallel_config = JOptional.of_noneable(parallel_config)
        return self

    def is_parallel(self) -> bool:
        """
        Returns whether this stream, if a terminal operation were to be executed, would execute in parallel

        Returns:
            bool: True if the Stream uses parallel configuration, otherwise False
        """
        return self._parallel_config.is_present()

    def sequential(self) -> Stream[T]:
        """
        Configures the Stream to use sequential configuration and return the current stream
        (i.e.: Remove the parallel configuration if exists)

        Returns:
            Stream[T]: The current Stream after set sequential configuration
        """
        if self.is_parallel():
            self._parallel_config = JOptional.empty()
        return self

    def filter(self, predicate: Predicate[T]) -> Stream[T]:
        """
        Returns a stream consisting of the elements of this stream that match the given predicate

        Args:
            predicate: The predicate to apply to each element to determine if it should be included

        Returns:
            Stream[T]: A stream consisting of the elements of this stream that match the given predicate

        Raises:
            TypeError: if predicate is None
        """
        return Stream._of(
            values_function=self._values_function,
            # pylint: disable=E1101
            pipeline=self._pipeline.add_handler(
                cast(Function[T, StepResult[T]], partial(_filter_lambda, predicate=require_non_none(predicate)))
            ),
            parallel_config=self._parallel_config,
            ordered_execution=self._ordered_execution
        )

    def collect(self, collector: Collector[T, R]) -> R:
        """
        Performs a reduction operation on the elements of this stream using a Collector

        Args:
            collector: The Collector describing the reduction

        Returns:
            R: The result of the reduction

        Raises:
            TypeError: if collector is None
        """
        return self._execute(collector=require_non_none(collector))

    def collect_from(self, supplier: Supplier[R], accumulator: BiConsumer[R, T], combiner: BiConsumer[R, R]) -> R:
        """
        Performs a reduction operation on the elements of this stream

        Args:
            supplier: A function that creates a new result container. For a parallel execution, this function may be
                called multiple times and must return a fresh value each time
            accumulator: A function that must fold an element into a result container
            combiner: A unction that accepts two partial result containers and merges them, which must be compatible
                with the accumulator function. The combiner function must fold the elements from the second result
                container into the first result container

        Returns:
            R: The result of the reduction

        Raises:
            TypeError: if at least one parameter is None
        """
        return self.collect(collector=collectors.of_biconsumers(supplier, accumulator, combiner))

    def to_list(self) -> list[T]:
        """
        Accumulates the elements of this stream into a list

        Returns:
            list[T]: A list containing the stream elements
        """
        return self.collect(collector=collectors.to_list())

    def to_tuple(self) -> tuple[T, ...]:
        """
        Accumulates the elements of this stream into a tuple

        Returns:
            tuple[T, ...]: a tuple containing the stream elements
        """
        return self.collect(collector=collectors.to_tuple())

    def to_dict(self, key_mapper: Function[T, K], value_mapper: Function[T, V]) -> dict[K, V]:
        """
        Accumulates the elements of this stream into a tuple dict whose keys and values are the result of applying the
        provided mapping functions to the input elements

        Args:
            key_mapper: a mapping function to produce keys
            value_mapper: a mapping function to produce values

        Returns:
            dict[K, V]: a dict containing the stream elements whose keys and values are the result of applying mapping
                functions to the input elements
        """
        return self.collect(collector=collectors.to_dict(key_mapper, value_mapper))

    def all_match(self, predicate: Predicate[T]) -> bool:
        """
        Returns whether all elements of this stream match the provided predicate

        Args:
            predicate: The predicate to apply to elements of this stream

        Returns:
            bool: True if either all elements of the stream match the provided predicate or the stream is empty,
                otherwise False

        Raises:
            TypeError: if predicate is None
        """
        return self.map(predicate).reduce(True, _and_lambda)

    def any_match(self, predicate: Predicate[T]) -> bool:
        """
        Returns whether any elements of this stream match the provided predicate

        Args:
            predicate: The predicate to apply to elements of this stream

        Returns:
            bool: True if any elements of the stream match the provided predicate, otherwise False

        Raises:
            TypeError: if predicate is None
        """
        return self.filter(predicate).find_any().is_present()

    def count(self) -> int:
        """
        Returns the count of elements in this stream

        Returns:
            int: The count of elements in this stream
        """
        return self.collect(collector=collectors.to_counter())

    def for_each(self, consumer: Consumer[T]) -> None:
        """
        Performs an action (/consumer) for each element of this stream

        Args:
            consumer: The Consumer to perform on the elements

        Returns:
            None: nothing

        Raises:
            TypeError: if consumer is None
        """
        self.peek(require_non_none(consumer))
        self._execute()

    def flat_map(self, mapper: Function[T, Stream[R]]) -> Stream[R]:
        """
        Returns a stream consisting of the results of replacing each element of this stream with the contents of a
        mapped stream produced by applying the provided mapping function to each element

        Args:
            mapper: A function to apply to each element which produces a stream of new values

        Returns:
             Stream[R]: The new Stream

        Raises:
            TypeError: if mapper is None
        """
        return self._from_self_config(
            values_function=cast(
                BiFunction[Optional[ParallelConfiguration], bool, Iterable[R]],
                partial(self._flat_map_values_function, mapper=require_non_none(mapper))
            )
        )

    def ordered_execution(self, ordered: bool = True) -> Stream[T]:
        """
        Configures the current Stream to be ordered or not and returns it

        Note: This configuration has no impact in sequential stream

        Args:
            ordered: True if the Stream must be ordered, False for unordered. (Default: True)

        Returns:
            Stream[T]: The current Stream with ordered configuration

        Raises:
            TypeError: if ordered is None
        """
        return Stream._of(
            values_function=self._values_function,
            pipeline=self._pipeline,
            parallel_config=self._parallel_config,
            ordered_execution=ordered
        ) if self._ordered_execution != require_non_none(ordered) else self

    def unordered(self) -> Stream[T]:
        """
        Configures the current Stream to be unordered and returns it

        Note: Is equivalent to call `ordered_execution(False)`
        Note 2: This configuration has no impact in sequential stream

        Returns:
            Stream[T]: The current Stream with unordered configuration
        """
        return self.ordered_execution(False)

    def find_first(self) -> JOptional[T]:
        """
        Returns a JOptional describing the first element of this stream, or an empty JOptional if the stream is empty

        Returns:
            JOptional[T]: A JOptional describing the first element of this stream, or an empty JOptional if the stream
                is empty
        """
        return self.ordered_execution(True).find_any()

    def find_any(self) -> JOptional[T]:
        """
        Returns a JOptional describing some element of the stream, or an empty JOptional if the stream is empty

        Note: if the stream is ordered, find_any and find_first are equivalents

        Returns:
            JOptional[T]: A JOptional describing some element of the stream, or an empty JOptional if the stream is
                empty
        """
        results: list[T] = self._execute(
            stop_on_first_completed=True  # pragma: no mutate
            , collector=collectors.to_list()
        )
        return JOptional.of_noneable(results[0] if results else None)

    def distinct(self) -> Stream[T]:
        """
        Returns a stream consisting of the distinct elements of this stream

        Returns:
            Stream[T]: A stream consisting of the distinct elements of this stream
        """
        return self._from_self_config(values_function=self._distinct_values_function)

    def drop_while(self, predicate: Predicate[T]) -> Stream[T]:
        """
        Returns, if this stream is ordered, a stream consisting of the remaining elements of this stream after dropping
        the longest prefix of elements that match the given predicate. Otherwise, if this stream is unordered, returns a
        stream consisting of the remaining elements of this stream after dropping a subset of elements that match the
        given predicate.

        Args:
            predicate: The predicate to apply to elements to determine the longest prefix of elements

        Returns:
            Stream[T]: The new Stream

        Raises:
            TypeError: if predicate is None
        """
        return self._from_self_config(
            values_function=partial(self._drop_while_values_function, predicate=require_non_none(predicate))
        )

    def limit(self, limit: int) -> Stream[T]:
        """
        Returns a stream consisting of the elements of this stream, truncated to be no longer than maxSize in length

        Args:
            limit: The number of elements the stream should be limited to

        Returns:
            Stream[T]: The truncated Stream

        Raises:
            TypeError: if limit is None
        """
        return self._from_self_config(
            values_function=partial(self._limit_values_function, limit=require_non_none(limit)))

    def max(self, comparator: BiFunction[T, T, int] = _natural_comparator) -> JOptional[T]:
        """
        Returns the maximum element of this stream according to the provided comparator BiFunction

        Args:
            comparator: The comparator BiFunction to compare elements of this stream (Note: Returns a negative int,
                zero, or a positive integer as the first argument is less than, equal to, or greater than the second)
                (default: natural comparator)

        Returns:
            JOptional[T]: A JOptional describing the maximum element of this stream, or an empty JOptional if the stream
                is empty

        Raises:
            TypeError: if comparator is None
        """
        return self.min(partial(_to_max_comparator, comparator=require_non_none(comparator)))

    def min(self, comparator: BiFunction[T, T, int] = _natural_comparator) -> JOptional[T]:
        """
        Returns the minimum element of this stream according to the provided comparator BiFunction

        Args:
            comparator: The comparator BiFunction to compare elements of this stream (Note: Returns a negative int,
                zero, or a positive integer as the first argument is less than, equal to, or greater than the second)
                (default: natural comparator)

        Returns:
            JOptional[T]: A JOptional describing the minimum element of this stream, or an empty JOptional if the stream
                is empty

        Raises:
            TypeError: if comparator is None
        """
        return self.sorted(require_non_none(comparator)).find_first()

    def peek(self, consumer: Consumer[T]) -> Stream[T]:
        """
        Returns a stream consisting of the elements of this stream, additionally performing the provided action
        (/consumer) on each element as elements are consumed from the resulting stream

        Args:
            consumer: The Consumer to perform on the elements as they are consumed from the stream

        Returns:
            Stream[T]: The new Stream

        Raises:
            TypeError: if consumer is None
        """
        return self.map(cast(Function[T, T], partial(_peek_mapper, consumer=require_non_none(consumer))))

    def reduce(self, identity: T, accumulator: BiFunction[T, T, T]) -> T:
        """
        Performs a reduction on the elements of this stream, using the provided identity value and an associative
        accumulation function, and returns the reduced value

        Args:
            identity: The identity value for the accumulating function
            accumulator: The BiFunction for combining two values

        Returns:
            T: The result of the reduction

        Raises:
            TypeError: accumulator is None
        """
        return self.collect(collectors.of(supplier=partial(to_self, obj=identity),
                                          accumulator=accumulator,
                                          combiner=accumulator
                                          )
                            )

    def skip(self, n: int) -> Stream[T]:
        """
        Returns a stream consisting of the remaining elements of this stream after discarding the first n elements of
        the stream

        Note: If this stream contains fewer than n elements then an empty stream will be returned

        Args:
            n: The number of leading elements to skip

        Returns:
            Stream[T]: The new stream

        Raises:
            TypeError: if n is None

        """
        return self._from_self_config(values_function=partial(self._skip_values_function, n=require_non_none(n)))

    def take_while(self, predicate: Predicate[T]) -> Stream[T]:
        """
        Returns, if this stream is ordered, a stream consisting of the longest prefix of elements taken from this stream
        that match the given predicate. Otherwise, if this stream is unordered, returns a stream consisting of a subset
        of elements taken from this stream that match the given predicate

        Args:
            predicate: The predicate to apply to elements to determine the longest prefix of element

        Returns:
            Stream[T]: The new Stream

        Raises:
            TypeError: if predicate is None
        """
        return self._from_self_config(
            values_function=partial(self._take_while_values_function, predicate=require_non_none(predicate))
        )

    def sorted(self, comparator: BiFunction[T, T, int] = _natural_comparator) -> Stream[T]:
        """
        Returns a stream consisting of the elements of this stream, sorted according to the provided comparator

        Args:
            comparator: The comparator BiFunction to compare elements of this stream (Note: Returns a negative int,
                zero, or a positive integer as the first argument is less than, equal to, or greater than the second)
                (default: natural comparator)

        Returns:
            Stream[T]: The new Stream

        Raises:
            TypeError: if comparator is None
        """
        self._ordered_execution = True
        return self._from_self_config(
            values_function=partial(self._sorted_values_function, comparator=require_non_none(comparator))
        )

    def to_generator(self) -> Iterator[T]:
        """
        Returns a generator based on Stream inputs and mapping

        Note: If the Stream is sequential each value is processed when __next__() is called. Otherwise, if the Stream
        uses a parallel configuration, all values are processed at the first __next__() call but each value is returned
        one by one depending on the 'ordered/unordered' configuration

        Note 2: When stream uses parallel with unordered configuration each value is returned when it is available. With
        an ordered configuration the generator wait for each necessary value in order to respect the stream value order

        Returns:
            Iterator[T]: The Stream processed values generator
        """
        # pylint: disable=E1102
        values: Final[Iterable[Any]] = \
            self._values_function(self._parallel_config.or_else(None), self._ordered_execution)
        if not values:
            return

        if self.is_parallel():
            yield from _parallel_generator(
                values=values,
                pipeline=self._pipeline,
                parallel_config=self._parallel_config.get(),
                ordered_execution=self._ordered_execution
            )
        else:
            yield from _sync_generator(values=values, pipeline=self._pipeline)

    def _execute(
            self,
            stop_on_first_completed: bool = False,
            collector: Collector[T, R] = _none_collector()
    ) -> R:
        """
        private method to execute the current Stream
        """
        require_non_none(stop_on_first_completed)
        require_non_none(collector)
        # pylint: disable=E1102
        values: Final[Optional[Iterable[Any]]] = \
            self._values_function(self._parallel_config.or_else(None), self._ordered_execution)

        if not values:
            return collector.supplier()

        if self.is_parallel():
            return _parallel_execution(
                values=values,
                pipeline=self._pipeline,
                parallel_config=self._parallel_config.get(),
                ordered_execution=self._ordered_execution,
                stop_on_first_completed=stop_on_first_completed,
                collector=collector
            )

        return _sync_execution(
            values=values, pipeline=self._pipeline, stop_on_first_completed=stop_on_first_completed, collector=collector
        )

    def _from_self_config(
            self, values_function: BiFunction[Optional[ParallelConfiguration], bool, Iterable[V]]
    ) -> Stream[R]:
        """
        private method that returns a new Stream by copying the current configuration
        Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)
        """
        return Stream._of(
            values_function=values_function,
            parallel_config=self._parallel_config,
            ordered_execution=self._ordered_execution
        )

    def _init_to_values_function(
            self, parallel_config: Optional[ParallelConfiguration], ordered_execution: bool
    ) -> Stream[T]:
        """
        private method that initializes the current stream with the given configuration
        Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)
        """
        return self.ordered_execution(ordered=ordered_execution).parallel(parallel_config)

    def _sorted_values_function(
            self, parallel_config: ParallelConfiguration, ordered_execution: bool, comparator: BiFunction[T, T, int]
    ) -> Iterable[T]:
        """
        private method used by `sorted` public method in replacement of lambda
        Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)
        """
        values: list[T] = self._init_to_values_function(parallel_config, ordered_execution).to_list()
        values.sort(key=cmp_to_key(comparator))
        return values

    def _flat_map_values_function(
            self, parallel_config: Optional[ParallelConfiguration],
            ordered_execution: bool,
            mapper: Function[T, Stream[R]]
    ) -> Iterable[R]:
        """
        private method used by `flat_map` public method in replacement of lambda
        Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)
        """
        list_generator: Final[Iterable[list[R]]] = self \
            ._init_to_values_function(parallel_config, ordered_execution) \
            .map(mapper) \
            .map(_stream_to_list_lambda) \
            .to_generator()
        for values in list_generator:
            for value in values:
                yield value

    def _distinct_values_function(
            self, parallel_config: Optional[ParallelConfiguration], ordered_execution: bool
    ) -> Iterable[T]:
        """
        private method used by `distinct` public method in replacement of lambda
        Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)
        """
        existing_values: set[T] = set()
        for value in self._init_to_values_function(parallel_config, ordered_execution).to_generator():
            if not value in existing_values:
                existing_values.add(value)
                yield value

    def _drop_while_values_function(
            self, parallel_config: ParallelConfiguration, ordered_execution: bool, predicate: Predicate[T]
    ) -> Iterable[T]:
        """
        private method used by `drop_while` public method in replacement of lambda
        Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)
        """
        drop: bool = True
        for value in self._init_to_values_function(parallel_config, ordered_execution).to_generator():
            drop = drop and predicate(value)
            if drop is False:
                yield value

    def _limit_values_function(
            self, parallel_config: ParallelConfiguration, ordered_execution: bool, limit: int
    ) -> Iterable[T]:
        """
        private method used by `limit` public method in replacement of lambda
        Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)
        """
        if limit <= 0:
            return

        counter: int = 0
        for value in self._init_to_values_function(parallel_config, ordered_execution).to_generator():
            yield value
            counter += 1
            if counter >= limit:
                break

    def _skip_values_function(
            self, parallel_config: ParallelConfiguration, ordered_execution: bool, n: int
    ) -> Iterable[T]:
        """
        private method used by `skip` public method in replacement of lambda
        Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)
        """
        counter: int = 0
        for value in self._init_to_values_function(parallel_config, ordered_execution).to_generator():
            if counter >= n:
                yield value
            counter += 1

    def _take_while_values_function(
            self, parallel_config: ParallelConfiguration, ordered_execution: bool, predicate: Predicate[T]
    ) -> Iterable[T]:
        """
        private method used by `take_while` public method in replacement of lambda
        Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)
        """
        for value in self._init_to_values_function(parallel_config, ordered_execution).to_generator():
            if not predicate(value):
                break  # pragma: no mutate
            yield value
