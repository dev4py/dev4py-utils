"""Stream module tests"""

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

from concurrent.futures import Executor, ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import FrozenInstanceError
from functools import partial
from multiprocessing import Manager
from sys import maxsize
from typing import Optional, Iterable, Final, Type, Iterator

from pytest import raises, fixture

from dev4py.utils import ParallelConfiguration, Stream, JOptional, lists
from dev4py.utils.collectors import to_list, Collector
from dev4py.utils.objects import non_none, is_none, to_self
from dev4py.utils.pipeline import StepPipeline, StepResult
from dev4py.utils.types import BiFunction, Function, Predicate, Supplier, BiConsumer, Consumer


class _FakeExecutor(Executor):
    """Fake Executor for tests"""
    ...


class TestParallelConfiguration:
    """ParallelConfiguration class tests"""

    class TestConstructor:
        """Constructor tests"""

        class TestNominalCase:
            def test_existing_parameters__should__create_new_parallel_configuration(self) -> None:
                """When all parameters are set, should create a new ParallelConfiguration with given parameters"""
                # GIVEN
                executor: Executor = _FakeExecutor()
                chunksize: int = 2

                # WHEN
                parallel_config: ParallelConfiguration = ParallelConfiguration(
                    executor=executor, chunksize=chunksize
                )

                # THEN
                assert parallel_config.executor == executor
                assert parallel_config.chunksize == chunksize

            def test_no_chunksize__should__create_new_parallel_configuration_with_chunksize_one(self) -> None:
                """When uses default chunksize, should create a new ParallelConfiguration with chunksize set to 1"""
                # GIVEN
                executor: Executor = _FakeExecutor()
                chunksize: int = 1

                # WHEN
                parallel_config: ParallelConfiguration = ParallelConfiguration(executor=executor)

                # THEN
                assert parallel_config.executor == executor
                assert parallel_config.chunksize == chunksize

        class TestErrorCase:
            def test_none_executor__should_raise_type_error(self) -> None:
                """When executor is None, should raise TypeError exception"""
                # GIVEN
                chunksize: int = 1

                # WHEN / THEN
                with raises(TypeError) as error:
                    # noinspection PyTypeChecker
                    ParallelConfiguration(executor=None, chunksize=chunksize)

                assert str(error.value) == "executor must be non None"

            def test_none_chunksize__should_raise_type_error(self) -> None:
                """When chunksize is None, should raise TypeError exception"""
                # GIVEN
                executor: Executor = _FakeExecutor()

                # WHEN / THEN
                with raises(TypeError) as error:
                    # noinspection PyTypeChecker
                    ParallelConfiguration(executor=executor, chunksize=None)

                assert str(error.value) == "chunksize must be non None"

            def test_less_than_one_chunksize__should_raise_value_error(self) -> None:
                """When chunksize is less than one, should raise ValueError exception"""
                # GIVEN
                executor: Executor = _FakeExecutor()

                # WHEN / THEN
                with raises(ValueError) as error:
                    # noinspection PyTypeChecker
                    ParallelConfiguration(executor=executor, chunksize=0)

                assert str(error.value) == "chunksize must be greater than or equals to 1"

    class TestSetters:
        """Setters tests"""

        class TestErrorCase:
            def test_set_new_executor__should__raise_frozen_instance_error(self) -> None:
                """When set a new executor, should raise a FrozenInstanceError exception"""
                # GIVEN
                executor: Executor = _FakeExecutor()
                chunksize: int = 1
                parallel_config: ParallelConfiguration = ParallelConfiguration(
                    executor=executor, chunksize=chunksize
                )

                # WHEN / THEN
                new_executor: Executor = _FakeExecutor()
                with raises(FrozenInstanceError):
                    # noinspection PyDataclass
                    parallel_config.executor = new_executor

            def test_set_new_chunksize__should__raise_frozen_instance_error(self) -> None:
                """When set a new chunksize, should raise a FrozenInstanceError exception"""
                # GIVEN
                executor: Executor = _FakeExecutor()
                chunksize: int = 1
                parallel_config: ParallelConfiguration = ParallelConfiguration(
                    executor=executor, chunksize=chunksize
                )

                # WHEN / THEN
                new_chunksize: int = 10
                with raises(FrozenInstanceError):
                    # noinspection PyDataclass
                    parallel_config.chunksize = new_chunksize


class TestStream:
    """Stream class tests"""
    CONSTRUCTOR_ERROR_MSG: Final[str] = "Stream private constructor! Please use Stream.of"
    TEST_RANGE_MIN_VALUE = 0
    TEST_RANGE_MAX_VALUE = 99
    TEST_VALUES: range = range(TEST_RANGE_MIN_VALUE, TEST_RANGE_MAX_VALUE + 1)
    TEST_STR_VALUES: list[str] = [str(i) for i in TEST_VALUES]

    @staticmethod
    def _predicate_greater_or_eq(i: int, min_value: int) -> bool:
        """test predicate because can't pickle lambda"""
        return i >= min_value

    @staticmethod
    def _predicate_less_than(i: int, value: int) -> bool:
        """test predicate because can't pickle lambda"""
        return i < value

    @fixture(
        scope="module",
        params=[
            None,
            (ProcessPoolExecutor, 1),
            (ThreadPoolExecutor, 1),
            (ProcessPoolExecutor, 3),
            (ThreadPoolExecutor, 3),
        ]
    )
    def parallel_config_fixture(self, request) -> Optional[ParallelConfiguration]:
        """Fixture to manage test ParallelConfiguration"""
        # INIT
        request_param: tuple[Type[Executor], int] = request.param
        parallel_config: Optional[ParallelConfiguration] = None if is_none(request_param) else \
            ParallelConfiguration(
                executor=request_param[0](),
                chunksize=request_param[1]
            )

        # RETURN
        yield parallel_config

        # TEAR DOWN
        if non_none(parallel_config):
            parallel_config.executor.shutdown()

    @fixture
    def test_stream(self, parallel_config_fixture) -> Stream[int]:
        """Fixture to create a new set of test stream"""
        yield Stream.of(*TestStream.TEST_VALUES).parallel(parallel_config_fixture)

    class TestConstructor:
        """Constructor tests"""

        class TestNominalCase:
            def test_valid_create_key__should__create_a_new_stream(self) -> None:
                """When create key is valid, should create a new Stream"""
                # GIVEN
                values_function: BiFunction[Optional[ParallelConfiguration], bool, Iterable[int]] = \
                    lambda pc, order: lists.empty_list()
                pipeline: StepPipeline[int, int] = StepPipeline.of(lambda i: StepResult(value=i))
                parallel_config: JOptional[ParallelConfiguration] = JOptional.empty()
                ordered_execution: bool = False
                # noinspection PyUnresolvedReferences
                create_key: object = Stream._Stream__CREATE_KEY

                # WHEN
                stream: Stream[int] = Stream(
                    values_function=values_function,
                    pipeline=pipeline,
                    parallel_config=parallel_config,
                    ordered_execution=ordered_execution,
                    create_key=create_key
                )

                # THEN
                assert stream._values_function == values_function
                assert stream._pipeline == pipeline
                assert stream._parallel_config == parallel_config
                assert stream._ordered_execution == ordered_execution

        class TestErrorCase:
            def test_none_create_key__should__raise_assertion_error(self) -> None:
                """When create key is none, should raise AssertionError with private constructor message"""
                # GIVEN
                values_function: BiFunction[Optional[ParallelConfiguration], bool, Iterable[int]] = \
                    lambda pc, order: lists.empty_list()
                pipeline: StepPipeline[int, int] = StepPipeline.of(lambda i: StepResult(value=i))
                parallel_config: JOptional[ParallelConfiguration] = JOptional.empty()
                ordered_execution: bool = False

                # WHEN / THEN
                with raises(AssertionError) as error:
                    Stream(
                        values_function=values_function,
                        pipeline=pipeline,
                        parallel_config=parallel_config,
                        ordered_execution=ordered_execution,
                        create_key=None
                    )

                assert str(error.value) == TestStream.CONSTRUCTOR_ERROR_MSG

            def test_invalid_create_key__should__raise_assertion_error(self) -> None:
                """When create key is not valid, should raise AssertionError with private constructor message"""
                # GIVEN
                values_function: BiFunction[Optional[ParallelConfiguration], bool, Iterable[int]] = \
                    lambda pc, order: lists.empty_list()
                pipeline: StepPipeline[int, int] = StepPipeline.of(lambda i: StepResult(value=i))
                parallel_config: JOptional[ParallelConfiguration] = JOptional.empty()
                ordered_execution: bool = False
                create_key: object = object()

                # WHEN / THEN
                with raises(AssertionError) as error:
                    Stream(
                        values_function=values_function,
                        pipeline=pipeline,
                        parallel_config=parallel_config,
                        ordered_execution=ordered_execution,
                        create_key=create_key
                    )

                assert str(error.value) == TestStream.CONSTRUCTOR_ERROR_MSG

            def test_none_values_function__should__raise_type_error(self) -> None:
                """When values_function is None, should raise TypeError exception"""
                # GIVEN
                pipeline: StepPipeline[int, int] = StepPipeline.of(lambda i: StepResult(value=i))
                parallel_config: JOptional[ParallelConfiguration] = JOptional.empty()
                ordered_execution: bool = False
                # noinspection PyUnresolvedReferences
                create_key: object = Stream._Stream__CREATE_KEY

                # WHEN / THEN
                with raises(TypeError):
                    Stream(
                        values_function=None,
                        pipeline=pipeline,
                        parallel_config=parallel_config,
                        ordered_execution=ordered_execution,
                        create_key=create_key
                    )

            def test_none_pipeline__should__raise_type_error(self) -> None:
                """When pipeline is None, should raise TypeError exception"""
                # GIVEN
                values_function: BiFunction[Optional[ParallelConfiguration], bool, Iterable[int]] = \
                    lambda pc, order: lists.empty_list()
                parallel_config: JOptional[ParallelConfiguration] = JOptional.empty()
                ordered_execution: bool = False
                # noinspection PyUnresolvedReferences
                create_key: object = Stream._Stream__CREATE_KEY

                # WHEN / THEN
                with raises(TypeError):
                    # noinspection PyTypeChecker
                    Stream(
                        values_function=values_function,
                        pipeline=None,
                        parallel_config=parallel_config,
                        ordered_execution=ordered_execution,
                        create_key=create_key
                    )

            def test_none_parallel_config__should__raise_type_error(self) -> None:
                """When parallel_config is None, should raise TypeError exception"""
                # GIVEN
                values_function: BiFunction[Optional[ParallelConfiguration], bool, Iterable[int]] = \
                    lambda pc, order: lists.empty_list()
                pipeline: StepPipeline[int, int] = StepPipeline.of(lambda i: StepResult(value=i))
                ordered_execution: bool = False
                # noinspection PyUnresolvedReferences
                create_key: object = Stream._Stream__CREATE_KEY

                # WHEN / THEN
                with raises(TypeError):
                    # noinspection PyTypeChecker
                    Stream(
                        values_function=values_function,
                        pipeline=pipeline,
                        parallel_config=None,
                        ordered_execution=ordered_execution,
                        create_key=create_key
                    )

            def test_none_ordered_execution__should__raise_type_error(self) -> None:
                """When ordered_execution is None, should raise TypeError exception"""
                # GIVEN
                values_function: BiFunction[Optional[ParallelConfiguration], bool, Iterable[int]] = \
                    lambda pc, order: lists.empty_list()
                pipeline: StepPipeline[int, int] = StepPipeline.of(lambda i: StepResult(value=i))
                parallel_config: JOptional[ParallelConfiguration] = JOptional.empty()
                # noinspection PyUnresolvedReferences
                create_key: object = Stream._Stream__CREATE_KEY

                # WHEN / THEN
                with raises(TypeError):
                    # noinspection PyTypeChecker
                    Stream(
                        values_function=values_function,
                        pipeline=pipeline,
                        parallel_config=parallel_config,
                        ordered_execution=None,
                        create_key=create_key
                    )

    class TestEmpty:
        """empty class method tests"""

        class TestNominalCase:
            def test_should__return_an_empty_stream(self) -> None:
                """Should return an empty stream"""
                # GIVEN / WHEN
                stream: Stream[int] = Stream.empty()

                # THEN:
                assert stream.count() == 0

    class TestOf:
        """of class method tests"""

        class TestNominalCase:

            def test_none__should__return_a_stream_of_none(self) -> None:
                """When None value should return a stream of None"""
                # GIVEN / WHEN
                stream: Stream[None] = Stream.of(None)

                # THEN
                assert stream.to_generator().__next__() is None
                assert stream._ordered_execution is False

            def test_existing_parameters__should__return_a_stream_of_parameters(self) -> None:
                """When parameters exists should return a stream of given parameters"""
                # GIVEN / WHEN
                stream: Stream[int] = Stream.of(1, 2, 3, 4)

                # THEN
                assert stream.to_list() == [1, 2, 3, 4]
                assert stream._ordered_execution is False

    class TestOfIterable:
        """of_iterable class method tests"""

        class TestNominalCase:
            def test_iterable_exists__should__return_a_stream_of_iterable_values(self) -> None:
                """When iterable is provided, should return a stream of given iterable values"""
                # GIVEN / WHEN
                stream: Stream[int] = Stream.of_iterable([1, 2, 3, 4])

                # THEN
                assert stream.to_list() == [1, 2, 3, 4]

        class TestErrorCase:
            def test_none_iterable__should__raise_type_error(self) -> None:
                """When iterable is None, should raise TypeError exception"""
                # GIVEN / WHEN / THEN
                with raises(TypeError):
                    # noinspection PyTypeChecker
                    Stream.of_iterable(None)

            def test_not_iterable__should__raise_type_error_on_terminal_operation(self) -> None:
                """When iterable is not iterable, should raise TypeError exception on terminal operation"""
                # GIVEN / WHEN / THEN
                with raises(TypeError):
                    # noinspection PyTypeChecker
                    Stream.of_iterable(1).to_list()

    class TestMap:
        """map method tests"""

        @staticmethod
        def _mapper(i: int) -> str:
            """map mapper test because can't pickle lambda"""
            return str(i)

        class TestNominalCase:
            def test_mapper_exists__should__return_a_stream_with_given_mapper(self, test_stream: Stream[int]) -> None:
                """When mapper exists, should return a stream that uses this mapper on terminal operation"""
                # GIVEN test_stream
                mapper: Function[int, str] = TestStream.TestMap._mapper

                # WHEN
                new_stream: Stream[str] = test_stream.map(mapper)

                # THEN
                assert all(elem in TestStream.TEST_STR_VALUES for elem in new_stream.to_list())

        class TestErrorCase:
            def test_none_mapper_should__raise_type_error(self, test_stream: Stream[int]) -> None:
                """When mapper is None, should raise TypeError exception"""
                # GIVEN test_stream
                # WHEN / THEN
                with raises(TypeError):
                    test_stream.map(None)

    class TestParallel:
        """parallel method tests"""

        class TestNominalCase:
            def test_parallel_config_exists__should__return_a_stream_with_parallel_configuration(self) -> None:
                """When parallel_config is provided, should return a stream with the parallel_config"""
                # GIVEN
                executor: Executor = _FakeExecutor()
                chunksize: int = 3
                parallel_config: ParallelConfiguration = ParallelConfiguration(executor=executor, chunksize=chunksize)

                # WHEN
                new_stream: Stream[int] = Stream.of_iterable(TestStream.TEST_VALUES).parallel(parallel_config)

                # THEN
                assert new_stream.is_parallel()
                assert new_stream._parallel_config.filter(lambda pc: pc == parallel_config).is_present()

            def test_none_parallel_config__should__return_a_sequential_stream(self) -> None:
                # GIVEN / WHEN
                new_stream: Stream[int] = Stream.of_iterable(TestStream.TEST_VALUES).parallel(None)

                # THEN
                assert new_stream.is_parallel() is False

    class TestIsParallel:
        """is_parallel method tests"""

        class TestNominalCase:
            def test_parallel_stream__should__return_true(self) -> None:
                """When stream uses parallel configuration, should return True"""
                # GIVEN
                executor: Executor = _FakeExecutor()
                chunksize: int = 3
                parallel_config: ParallelConfiguration = ParallelConfiguration(executor=executor, chunksize=chunksize)
                stream: Stream[int] = Stream.of_iterable(TestStream.TEST_VALUES).parallel(parallel_config)

                # WHEN
                result: bool = stream.is_parallel()

                # THEN
                assert result is True

            def test_sequential_stream__should__return_false(self) -> None:
                """When stream is sequential, should return False"""

                # GIVEN
                stream: Stream[int] = Stream.of_iterable(TestStream.TEST_VALUES)

                # WHEN
                result: bool = stream.is_parallel()

                # THEN
                assert result is False

    class TestSequential:
        """sequential method tests"""

        class TestNominalCase:

            def test_sequential_stream__should__return_self_and_stay_sequential(self) -> None:
                """When stream is sequential, should return self"""
                # GIVEN
                stream: Stream[int] = Stream.empty().parallel(None)

                # WHEN
                new_stream: Stream[int] = stream.sequential()

                # THEN
                assert new_stream == stream
                assert new_stream.is_parallel() is False

            def test_parallel_stream__should__return_self_as_sequential_stream(self) -> None:
                """When stream is parallel, should return self with sequential configuration"""
                # GIVEN
                stream: Stream[int] = Stream.empty().parallel(ParallelConfiguration(_FakeExecutor()))

                # WHEN
                new_stream: Stream[int] = stream.sequential()

                # THEN
                assert new_stream == stream
                assert new_stream.is_parallel() is False

    class TestFilter:
        """filter method tests"""
        _MIN_VALUE: int = 20

        class TestNominalCase:
            def test_useful_filter__should__remove_values_from_the_stream(self, test_stream: Stream[int]) -> None:
                """
                When some values are concerned by the filter, should return a stream without these values on terminal
                operation
                """
                # GIVEN test_stream
                min_value: int = TestStream.TestFilter._MIN_VALUE
                test_filter: Predicate[int] = partial(TestStream._predicate_greater_or_eq, min_value=min_value)

                # WHEN
                result: list[int] = test_stream.filter(test_filter).to_list()

                # THEN
                assert len(result) == len(TestStream.TEST_VALUES) - min_value
                for i in result:
                    assert test_filter(i) is True
                    assert i in TestStream.TEST_VALUES
                assert all(elem not in result for elem in range(0, min_value))

            def test_useless_filter__should__return_the_stream_with_all_values(self, test_stream: Stream[int]) -> None:
                """
                When no value is concerned by the filter, should return a stream with all values on terminal operation
                """
                # GIVEN test_stream
                min_value: int = -(maxsize - 1)
                test_filter: Predicate[int] = partial(TestStream._predicate_greater_or_eq, min_value=min_value)

                # WHEN
                result: list[int] = test_stream.filter(test_filter).to_list()

                # THEN
                assert len(result) == len(TestStream.TEST_VALUES)
                assert all(elem in result for elem in TestStream.TEST_VALUES)

        class TestErrorCase:
            def test_none_filter__should__raise_type_error(self, test_stream: Stream[int]) -> None:
                """When filter is None, should raise TypeError exception"""
                # Given test_stream
                # WHEN / THEN
                with raises(TypeError):
                    test_stream.filter(None)

    class TestCollect:
        """collect method test"""

        class TestNominalCase:
            def test_collector_exists__should__return_collected_values(self, test_stream: Stream[int]) -> None:
                """When collector exists, should return values as described by collector"""
                # GIVEN test_stream
                collector: Collector[int, list[int]] = to_list()

                # WHEN
                result: list[int] = test_stream.collect(collector)

                # THEN
                assert isinstance(result, list)
                assert len(result) == len(TestStream.TEST_VALUES)
                assert all(elem in result for elem in TestStream.TEST_VALUES)

        class TestErrorCase:
            def test_none_collector__should__raise_type_error(self, test_stream: Stream[int]) -> None:
                """When collector is None, should raise TypeError exception"""
                # GIVEN test_stream
                # WHEN / THEN
                with raises(TypeError):
                    # noinspection PyTypeChecker
                    test_stream.collect(None)

    class TestCollectFrom:
        """collect_from method test"""

        class TestNominalCase:
            def test_existing_parameters__should__return_collected_values(self, test_stream: Stream[int]) -> None:
                """When all parameters are given, should return values as described by these parameters"""
                # GIVEN test_stream
                supplier: Supplier[list[int]] = lists.empty_list
                accumulator: BiConsumer[list[int], int] = lists.append
                combiner: BiConsumer[list[int], list[int]] = lists.extend

                # WHEN
                result: list[int] = test_stream.collect_from(
                    supplier=supplier, accumulator=accumulator, combiner=combiner
                )

                # THEN
                assert isinstance(result, list)
                assert len(result) == len(TestStream.TEST_VALUES)
                assert all(elem in result for elem in TestStream.TEST_VALUES)

        class TestErrorCase:
            def test_none_supplier__should__raise_type_error(self, test_stream: Stream[int]) -> None:
                """When supplier is None, should raise TypeError exception"""
                # GIVEN test_stream
                accumulator: BiConsumer[list[int], int] = lists.append
                combiner: BiConsumer[list[int], list[int]] = lists.extend

                # WHEN / THEN
                with raises(TypeError):
                    # noinspection PyTypeChecker
                    test_stream.collect_from(supplier=None, accumulator=accumulator, combiner=combiner)

            def test_none_accumulator__should__raise_type_error(self, test_stream: Stream[int]) -> None:
                """When accumulator is None, should raise TypeError exception"""
                # GIVEN test_stream
                supplier: Supplier[list[int]] = lists.empty_list
                combiner: BiConsumer[list[int], list[int]] = lists.extend

                # WHEN / THEN
                with raises(TypeError):
                    # noinspection PyTypeChecker
                    test_stream.collect_from(supplier=supplier, accumulator=None, combiner=combiner)

            def test_none_combiner__should__raise_type_error(self, test_stream: Stream[int]) -> None:
                """When combiner is None, should raise TypeError exception"""
                # GIVEN test_stream
                supplier: Supplier[list[int]] = lists.empty_list
                accumulator: BiConsumer[list[int], int] = lists.append

                # WHEN / THEN
                with raises(TypeError):
                    # noinspection PyTypeChecker
                    test_stream.collect_from(supplier=supplier, accumulator=accumulator, combiner=None)

    class TestToList:
        """to_list method tests"""

        class TestNominalCase:
            def test_should__return_stream_values_as_list(self, test_stream: Stream[int]) -> None:
                """Should return stream values as list"""
                # GIVEN test_stream
                # WHEN
                result: list[int] = test_stream.to_list()

                # THEN
                assert isinstance(result, list)
                assert len(result) == len(TestStream.TEST_VALUES)
                assert all(elem in result for elem in TestStream.TEST_VALUES)

    class TestToTuple:
        """to_tuple method tests"""

        class TestNominalCase:
            def test_should__return_stream_values_as_tuple(self, test_stream: Stream[int]) -> None:
                """Should return stream values as tuple"""
                # GIVEN test_stream
                # WHEN
                result: tuple[int, ...] = test_stream.to_tuple()

                # THEN
                assert isinstance(result, tuple)
                assert len(result) == len(TestStream.TEST_VALUES)
                assert all(elem in result for elem in TestStream.TEST_VALUES)

    class TestToDict:
        """to_dict method tests"""

        class TestNominalCase:
            def test_existing_mappers_should__return_stream_values_as_dict(self, test_stream: Stream[int]) -> None:
                """When key/value mappers are provided, should return a dict as described by mappers"""
                # GIVEN test_stream
                key_mapper: Function[int, str] = str
                value_mapper: Function[int, int] = to_self

                # WHEN
                result: dict[str, int] = test_stream.to_dict(key_mapper, value_mapper)

                # THEN
                assert isinstance(result, dict)
                assert len(result) == len(TestStream.TEST_VALUES)
                assert all(elem in result.values() for elem in TestStream.TEST_VALUES)
                assert all(elem in result.keys() for elem in TestStream.TEST_STR_VALUES)

    class TestErrorCase:
        def test_none_key_mapper__should__raise_type_error(self, test_stream: Stream[int]) -> None:
            """When key mapper is None should raise a TypeError exception"""
            # GIVEN test_stream
            value_mapper: Function[int, int] = to_self

            # WHEN / THEN
            with raises(TypeError):
                test_stream.to_dict(None, value_mapper)

        def test_none_value_mapper__should__raise_type_error(self, test_stream: Stream[int]) -> None:
            """When value mapper is None should raise a TypeError exception"""
            # GIVEN test_stream
            key_mapper: Function[int, str] = str

            # WHEN / THEN
            with raises(TypeError):
                test_stream.to_dict(key_mapper, None)

    class TestAllMatch:
        """all_match method tests"""

        class TestNominalCase:
            def test_all_match_given_predicate_should__return_true(self, test_stream: Stream[int]) -> None:
                """When all values match with the given predicate, should return True"""
                # GIVEN test_stream
                predicate: Predicate[int] = non_none

                # WHEN
                result: bool = test_stream.all_match(predicate)

                # THEN
                assert result is True

            def test_at_least_one_value_not_match_given_predicate_should__return_false(
                    self, test_stream: Stream[int]
            ) -> None:
                """When at least one value doesn't match with the given predicate, should return False"""
                # GIVEN test_stream
                predicate: Predicate[int] = partial(TestStream._predicate_greater_or_eq, min_value=10)

                # WHEN
                result: bool = test_stream.all_match(predicate)

                # THEN
                assert result is False

            def test_empty_stream__should__return_true(self) -> None:
                """When stream is empty, should return True"""
                # GIVEN
                stream: Stream[int] = Stream.empty()
                predicate: Predicate[int] = partial(TestStream._predicate_greater_or_eq, min_value=10)

                # WHEN
                result: bool = stream.all_match(predicate)

                # THEN
                assert result is True

        class TestErrorCase:
            def test_none_predicate__should__raise_type_error(self, test_stream: Stream[int]) -> None:
                """When predicate is None should raise a TypeError exception"""
                # GIVEN test_stream
                # WHEN / THEN
                with raises(TypeError):
                    test_stream.all_match(None)

    class TestAnyMatch:
        """any_match method tests"""

        class TestNominalCase:
            def test_all_match_given_predicate_should__return_true(self, test_stream: Stream[int]) -> None:
                """When all values match with the given predicate, should return True"""
                # GIVEN test_stream
                predicate: Predicate[int] = non_none

                # WHEN
                result: bool = test_stream.any_match(predicate)

                # THEN
                assert result is True

            def test_one_value_match_given_predicate_should__return_true(self, test_stream: Stream[int]) -> None:
                """When all values match with the given predicate, should return True"""
                # GIVEN test_stream
                predicate: Predicate[int] = \
                    partial(TestStream._predicate_greater_or_eq, min_value=TestStream.TEST_RANGE_MAX_VALUE)

                # WHEN
                result: bool = test_stream.any_match(predicate)

                # THEN
                assert result is True

            def test_all_not_match_given_predicate_should__return_false(
                    self, test_stream: Stream[int]
            ) -> None:
                """When at least one value doesn't match with the given predicate, should return False"""
                # GIVEN test_stream
                predicate: Predicate[int] = \
                    partial(TestStream._predicate_greater_or_eq, min_value=TestStream.TEST_RANGE_MAX_VALUE + 1)

                # WHEN
                result: bool = test_stream.any_match(predicate)

                # THEN
                assert result is False

            def test_empty_stream__should__return_false(self) -> None:
                """When stream is empty, should return False"""
                # GIVEN
                stream: Stream[int] = Stream.empty()
                predicate: Predicate[int] = partial(TestStream._predicate_greater_or_eq, min_value=10)

                # WHEN
                result: bool = stream.any_match(predicate)

                # THEN
                assert result is False

        class TestErrorCase:
            def test_none_predicate__should__raise_type_error(self, test_stream: Stream[int]) -> None:
                """When predicate is None should raise a TypeError exception"""
                # GIVEN test_stream
                # WHEN / THEN
                with raises(TypeError):
                    test_stream.any_match(None)

    class TestCount:
        """count method tests"""

        class TestNominalCase:
            def test_should__return_the_count_of_stream_elements(self, test_stream: Stream[int]) -> None:
                """Should return the count of elements in this stream"""
                # GIVEN test_stream
                # WHEN
                result: int = test_stream.count()

                # THEN
                assert isinstance(result, int)
                assert result == len(TestStream.TEST_VALUES)

    class TestForEach:
        """for_each method tests"""

        class TestNominalCase:

            def test_consumer_exists_should__call_consumer_for_each_stream_element(
                    self, test_stream: Stream[int]
            ) -> None:
                with Manager() as manager:
                    # GIVEN test_stream
                    result_list: list[int] = manager.list()
                    consumer: Consumer[int] = result_list.append

                    # WHEN
                    test_stream.for_each(consumer)

                    # THEN
                    assert len(result_list) == len(TestStream.TEST_VALUES)
                    assert all(elem in result_list for elem in TestStream.TEST_VALUES)

        class TestErrorCase:
            def test_none_consumer__should__raise_type_error(self, test_stream: Stream[int]) -> None:
                """When consumer is None should raise a TypeError exception"""
                # GIVEN test_stream
                # WHEN / THEN
                with raises(TypeError):
                    test_stream.for_each(None)

    class TestFlatMap:
        """flat_map method tests"""

        @staticmethod
        def _mapper(i: int):
            """flat_map test mapper because can't pickle lambda"""
            # lambda i: Stream.of(i).map(str)
            return Stream.of(i).map(str)

        class TestNominalCase:
            def test_mapper_exists__should__return_stream_with_mapper_each_element_by_mapper_stream_result(
                    self, test_stream: Stream[int]
            ) -> None:
                """
                When mapper exists, should return a stream consisting of the results of replacing each element of this
                stream with the contents of a mapped stream produced by applying the provided mapping function to each
                element
                """
                # GIVEN test_stream
                mapper: Function[int, Stream[str]] = TestStream.TestFlatMap._mapper

                # WHEN
                new_stream: Stream[str] = test_stream.flat_map(mapper)

                # THEN
                result: list[str] = new_stream.to_list()
                assert len(result) == len(TestStream.TEST_STR_VALUES)
                assert all(elem in result for elem in TestStream.TEST_STR_VALUES)

        class TestErrorCase:
            def test_none_mapper__should__raise_type_error(self, test_stream: Stream[int]) -> None:
                """When mapper is None, should raise TypeError exception"""
                # GIVEN test_stream
                # WHEN / THEN
                with raises(TypeError):
                    test_stream.flat_map(None)

    class TestOrderedExecution:
        """ordered_execution method tests"""

        class TestNominalCase:
            def test_ordered_is_true__should__return_mapped_element_in_the_source_order(
                    self, test_stream: Stream[int]
            ) -> None:
                """When ordered is True, should return elements in the source order on terminal operation"""
                # GIVEN test_stream
                ordered_execution: bool = True

                # WHEN
                new_stream: Stream[str] = test_stream.map(str).ordered_execution(ordered_execution)

                # THEN
                result: list[str] = new_stream.to_list()
                assert new_stream._ordered_execution == ordered_execution
                assert result == TestStream.TEST_STR_VALUES

            def test_ordered_is_false__should__return_mapped_source_element_in_random_order(
                    self, test_stream: Stream[int]
            ) -> None:
                """
                When ordered is False, should return all source elements on terminal operation (but not necessary in the
                same order)
                """
                # GIVEN test_stream
                ordered_execution: bool = False

                # WHEN
                new_stream: Stream[str] = test_stream.map(str).ordered_execution(ordered_execution)

                # THEN
                result: list[str] = new_stream.to_list()
                assert new_stream._ordered_execution == ordered_execution
                assert len(result) == len(TestStream.TEST_STR_VALUES)
                assert all(elem in result for elem in TestStream.TEST_STR_VALUES)

        class TestErrorCase:
            def test_none_parameter__should__raise_type_error(self, test_stream: Stream[int]) -> None:
                """When parameter is None, should raise TypeError exception"""
                # GIVEN test_stream
                # WHEN / THEN
                with raises(TypeError):
                    # noinspection PyTypeChecker
                    test_stream.ordered_execution(None)

    class TestUnordered:
        """unordered method tests"""

        class TestNominalCase:
            def test_should__return_mapped_source_element_in_random_order(
                    self, test_stream: Stream[int]
            ) -> None:
                """
                Should return all source elements on terminal operation (but not necessary in the same order)
                """
                # GIVEN test_stream
                # WHEN
                new_stream: Stream[str] = test_stream.map(str).unordered()

                # THEN
                result: list[str] = new_stream.to_list()
                assert new_stream._ordered_execution == False
                assert len(result) == len(TestStream.TEST_STR_VALUES)
                assert all(elem in result for elem in TestStream.TEST_STR_VALUES)

    class TestFindFirst:
        """find_first method tests"""

        class TestNominalCase:

            def test_ordered_stream__should__return_first_encountered_element_in_the_source_order(
                    self, test_stream: Stream[int]
            ) -> None:
                """When stream is ordered, should return the first mapped element in the source order"""
                # GIVEN
                stream: Stream[str] = test_stream.ordered_execution().map(str)

                # WHEN
                result: JOptional[str] = stream.find_first()

                # THEN
                assert result.is_present() is True
                assert result.get() == TestStream.TEST_STR_VALUES[0]

            def test_unordered_stream__should__return_first_encountered_element_in_the_source_order(
                    self, test_stream: Stream[int]
            ) -> None:
                """When stream is ordered, should return the first mapped element in the source order"""
                # GIVEN
                stream: Stream[str] = test_stream.unordered().map(str)

                # WHEN
                result: JOptional[str] = stream.find_first()

                # THEN
                assert result.is_present() is True
                assert result.get() == TestStream.TEST_STR_VALUES[0]

            def test_empty_stream__should__return_empty_joptional(self) -> None:
                """When stream is empty, should return an empty JOptional"""
                # GIVEN
                stream: Stream[str] = Stream.empty().map(str)

                # WHEN
                result: JOptional[str] = stream.find_first()

                # THEN
                assert result.is_present() is False

    class TestFindAny:
        """find_any method tests"""

        class TestNominalCase:

            def test_ordered_stream__should__return_first_encountered_element_in_the_source_order(
                    self, test_stream: Stream[int]
            ) -> None:
                """When stream is ordered, should return the first mapped element in the source order"""
                # GIVEN
                stream: Stream[str] = test_stream.ordered_execution().map(str)

                # WHEN
                result: JOptional[str] = stream.find_any()

                # THEN
                assert result.is_present() is True
                assert result.get() == TestStream.TEST_STR_VALUES[0]

            def test_unordered_stream__should__return_any_mapped_element(
                    self, test_stream: Stream[int]
            ) -> None:
                """When stream is ordered, should return the first mapped element in the source order"""
                # GIVEN
                stream: Stream[str] = test_stream.unordered().map(str)

                # WHEN
                result: JOptional[str] = stream.find_any()

                # THEN
                assert result.is_present() is True
                assert result.get() in TestStream.TEST_STR_VALUES

            def test_empty_stream__should__return_empty_joptional(self) -> None:
                """When stream is empty, should return an empty JOptional"""
                # GIVEN
                stream: Stream[str] = Stream.empty().map(str)

                # WHEN
                result: JOptional[str] = stream.find_any()

                # THEN
                assert result.is_present() is False

    class TestDistinct:
        """distinct method tests"""

        class TestNominalCase:
            def test_empty_stream__should__return_an_empty_stream(self) -> None:
                """When stream is empty, should return an empty stream"""
                # GIVEN
                stream: Stream[int] = Stream.empty()

                # WHEN
                new_stream: Stream[int] = stream.distinct()

                # THEN
                assert new_stream.to_list() == lists.empty_list()

            def test_stream_with_values__should__remove_duplicated_values(
                    self, parallel_config_fixture: ParallelConfiguration
            ) -> None:
                """When values exist, should remove duplicated values"""
                # GIVEN
                values: list[int] = [1, 2, 1, 3, 3, 4, 5, 4]
                stream: Stream[int] = Stream.of_iterable(values).parallel(parallel_config_fixture)

                # WHEN
                new_stream: Stream[int] = stream.distinct()

                # THEN
                expected_values: list[int] = [1, 2, 3, 4, 5]
                result: list[int] = new_stream.to_list()
                assert len(result) == len(expected_values)
                assert all(value in result for value in expected_values)

    class TestDropWhile:
        """drop_while method tests"""

        class TestNominalCase:
            def test_empty_stream__should__return_an_empty_stream(self) -> None:
                """When stream is empty, should return an empty stream"""
                # GIVEN
                stream: Stream[int] = Stream.empty()
                min_value: int = 10
                predicate: Predicate[int] = partial(TestStream._predicate_greater_or_eq, min_value=min_value)

                # WHEN
                new_stream: Stream[int] = stream.drop_while(predicate)

                # THEN
                assert new_stream.to_list() == lists.empty_list()

            def test_ordered_stream_with_matched_predicate__should__return_stream_with_dropped_values(
                    self, test_stream: Stream[int]
            ) -> None:
                """
                When stream is ordered and predicate match at least one value, should return a stream with dropped
                values
                """
                # GIVEN
                stream: Stream[int] = test_stream.ordered_execution()
                min_value: int = 10
                predicate: Predicate[int] = partial(TestStream._predicate_less_than, value=min_value)

                # WHEN
                new_stream: Stream[int] = stream.drop_while(predicate)

                # THEN
                result: list[int] = new_stream.to_list()
                assert len(result) == len(TestStream.TEST_VALUES) - min_value
                assert all(value in result for value in range(min_value, TestStream.TEST_RANGE_MAX_VALUE + 1))

            def test_not_matched_predicate__should__return_stream_with_all_values(
                    self, test_stream: Stream[int]
            ) -> None:
                """When no value match, should return a stream with all values"""
                # GIVEN
                predicate: Predicate[int] = is_none

                # WHEN
                new_stream: Stream[int] = test_stream.drop_while(predicate)

                # THEN
                result: list[int] = new_stream.to_list()
                assert len(result) == len(TestStream.TEST_VALUES)
                assert all(value in result for value in TestStream.TEST_VALUES)

            def test_unordered_stream_with_valid_predicate__should__return_a_stream_with_some_dropped_values(
                    self, test_stream: Stream[int]
            ) -> None:
                """
                When stream is unordered and predicate match at least one value, should return a stream with some
                dropped values
                """
                # GIVEN
                stream: Stream[int] = test_stream.unordered()
                min_value: int = 10
                predicate: Predicate[int] = partial(TestStream._predicate_less_than, value=min_value)

                # WHEN
                new_stream: Stream[int] = stream.drop_while(predicate)

                # THEN
                result: list[int] = new_stream.to_list()
                assert len(result) <= len(TestStream.TEST_VALUES)
                assert all(value in TestStream.TEST_VALUES for value in result)

        class TestErrorCase:
            def test_none_predicate__should__raise_type_error(self, test_stream: Stream[int]) -> None:
                """When predicate is None, should raise TypeError exception"""
                # GIVEN test_stream
                # WHEN / THEN
                with raises(TypeError):
                    # noinspection PyTypeChecker
                    test_stream.drop_while(None)

    class TestLimit:
        """limit method tests"""

        class TestNominalCase:
            def test_empty_stream__should__return_an_empty_stream(self) -> None:
                """When stream is empty, should return an empty stream"""
                # GIVEN
                stream: Stream[int] = Stream.empty()
                limit: int = 10

                # WHEN
                new_stream: Stream[int] = stream.limit(limit)

                # THEN
                assert new_stream.to_list() == lists.empty_list()

            def test_limit_is_zero__should__return_an_empty_stream(self, test_stream: Stream[int]) -> None:
                """When limit is zero, should return an empty stream"""
                # GIVEN test_stream
                limit: int = 0

                # WHEN
                new_stream: Stream[int] = test_stream.limit(limit)

                # THEN
                assert new_stream.to_list() == lists.empty_list()

            def test_negative_limit__should__return_an_empty_stream(self, test_stream: Stream[int]) -> None:
                """When limit is negative, should return an empty stream"""
                # GIVEN test_stream
                limit: int = -1

                # WHEN
                new_stream: Stream[int] = test_stream.limit(limit)

                # THEN
                assert new_stream.to_list() == lists.empty_list()

            def test_less_values_than_limit__should__return_stream_with_all_elements(
                    self, test_stream: Stream[int]
            ) -> None:
                """When stream contains fewer values than the limit should return a stream with all elements"""
                # GIVEN test_stream
                limit: int = maxsize

                # WHEN
                new_stream: Stream[int] = test_stream.limit(limit)

                # THEN
                result: list[int] = new_stream.to_list()
                assert all(value in result for value in TestStream.TEST_VALUES)

            def test_limit_is_one__should__return_a_truncated_stream_of_one_element(
                    self, test_stream: Stream[int]
            ) -> None:
                """When limit is 1 should return a truncated stream of 1 element"""
                # GIVEN test_stream
                limit: int = 1

                # WHEN
                new_stream: Stream[int] = test_stream.limit(limit)

                # THEN
                result: list[int] = new_stream.to_list()
                assert len(result) == limit
                assert result[0] in TestStream.TEST_VALUES

            def test_limit_exists__should__return_a_truncated_stream(
                    self, test_stream: Stream[int]
            ) -> None:
                """When limit exists should return a truncated stream"""
                # GIVEN test_stream
                limit: int = 20

                # WHEN
                new_stream: Stream[int] = test_stream.limit(limit)

                # THEN
                result: list[int] = new_stream.to_list()
                assert len(result) == limit
                assert all(value in TestStream.TEST_VALUES for value in result)

        class TestErrorCase:
            def test_none_limit__should__raise_type_error(self, test_stream: Stream[int]) -> None:
                """When limit is None, should raise TypeError exception"""
                # GIVEN test_stream
                # WHEN / THEN
                with raises(TypeError):
                    # noinspection PyTypeChecker
                    test_stream.limit(None)

    class TestMax:
        """max method tests"""

        class TestNominalCase:
            def test_empty_stream__should__return_an_empty_joptional(self) -> None:
                """When stream is empty, should return an empty joptional"""
                # GIVEN
                stream: Stream[int] = Stream.empty()

                # WHEN
                result: JOptional[int] = stream.max()

                # THEN
                assert result.is_present() is False

            def test_default_comparator__should__return_a_joptional_with_max_natural_value(
                    self, test_stream: Stream[int]
            ) -> None:
                """When default comparator, should return a joptional describing the natural max value"""
                # GIVEN test_stream
                # WHEN
                result: JOptional[int] = test_stream.max()

                # THEN
                assert result.is_present() is True
                assert result.get() == TestStream.TEST_RANGE_MAX_VALUE

            def test_comparator_exists__should__return_a_joptional_with_max_value_as_described_by_comparator(
                    self, test_stream: Stream[int]
            ) -> None:
                """
                When comparator is provided, should return a joptional describing the max value described by the
                comparator
                """
                # GIVEN test_stream
                reverse_comparator: BiFunction[int, int, int] = lambda i1, i2: 0 if i1 == i2 else 1 if i1 < i2 else -1

                # WHEN
                result: JOptional[int] = test_stream.max(reverse_comparator)

                # THEN
                assert result.is_present() is True
                assert result.get() == TestStream.TEST_RANGE_MIN_VALUE

        class TestErrorCase:
            def test_none_comparator__should__raise_type_error(self, test_stream: Stream[int]) -> None:
                """When comparator is None, should raise TypeError exception"""
                # GIVEN test_stream
                # WHEN / THEN
                with raises(TypeError):
                    # noinspection PyTypeChecker
                    test_stream.max(None)

    class TestMin:
        """min method tests"""

        class TestNominalCase:
            def test_empty_stream__should__return_an_empty_joptional(self) -> None:
                """When stream is empty, should return an empty joptional"""
                # GIVEN
                stream: Stream[int] = Stream.empty()

                # WHEN
                result: JOptional[int] = stream.min()

                # THEN
                assert result.is_present() is False

            def test_default_comparator__should__return_a_joptional_with_min_natural_value(
                    self, test_stream: Stream[int]
            ) -> None:
                """When default comparator, should return a joptional describing the natural min value"""
                # GIVEN test_stream
                # WHEN
                result: JOptional[int] = test_stream.min()

                # THEN
                assert result.is_present() is True
                assert result.get() == TestStream.TEST_RANGE_MIN_VALUE

            def test_comparator_exists__should__return_a_joptional_with_min_value_as_described_by_comparator(
                    self, test_stream: Stream[int]
            ) -> None:
                """
                When comparator is provided, should return a joptional describing the min value described by the
                comparator
                """
                # GIVEN test_stream
                reverse_comparator: BiFunction[int, int, int] = lambda i1, i2: 0 if i1 == i2 else 1 if i1 < i2 else -1

                # WHEN
                result: JOptional[int] = test_stream.min(reverse_comparator)

                # THEN
                assert result.is_present() is True
                assert result.get() == TestStream.TEST_RANGE_MAX_VALUE

        class TestErrorCase:
            def test_none_comparator__should__raise_type_error(self, test_stream: Stream[int]) -> None:
                """When comparator is None, should raise TypeError exception"""
                # GIVEN test_stream
                # WHEN / THEN
                with raises(TypeError):
                    # noinspection PyTypeChecker
                    test_stream.min(None)

    class TestPeek:
        """peek method tests"""

        class TestNominalCase:

            def test_consumer_exists_should__call_consumer_for_each_stream_element(
                    self, test_stream: Stream[int]
            ) -> None:
                with Manager() as manager:
                    # GIVEN test_stream
                    result_list: list[int] = manager.list()
                    consumer: Consumer[int] = result_list.append

                    # WHEN
                    test_stream.peek(consumer)
                    test_stream.to_list()

                    # THEN
                    assert len(result_list) == len(TestStream.TEST_VALUES)
                    assert all(elem in result_list for elem in TestStream.TEST_VALUES)

        class TestErrorCase:
            def test_none_consumer__should__raise_type_error(self, test_stream: Stream[int]) -> None:
                """When consumer is None, should raise TypeError exception"""
                # GIVEN test_stream
                # WHEN / THEN
                with raises(TypeError):
                    # noinspection PyTypeChecker
                    test_stream.peek(None)

    class TestReduce:
        """reduce method tests"""

        @staticmethod
        def _reduce_accumulator(i1: int, i2: int) -> int:
            """test reduce accumulator because lambda cannot be pickled"""
            return i1 + i2

        class TestNominalCase:

            def test_empty_stream__should__return_identity(self) -> None:
                """When stream is empty, should return identity value"""
                # GIVEN
                stream: Stream[int] = Stream.empty()
                identity: int = 0
                accumulator: BiFunction[int, int, int] = TestStream.TestReduce._reduce_accumulator

                # WHEN
                result: int = stream.reduce(identity, accumulator)

                # THEN
                assert result == identity

            def test_stream_with_values__should__return_reduction_result(
                    self, test_stream: Stream[int]
            ) -> None:
                """When stream is empty, should return identity value"""
                # GIVEN
                identity: int = 0
                accumulator: BiFunction[int, int, int] = TestStream.TestReduce._reduce_accumulator

                # WHEN
                result: int = test_stream.reduce(identity, accumulator)

                # THEN
                assert result == sum(TestStream.TEST_VALUES)

        class TestErrorCase:
            def test_none_accumulator__should__raise_type_error(self, test_stream: Stream[int]) -> None:
                """When consumer is None, should raise TypeError exception"""
                # GIVEN test_stream
                identity: int = 0

                # WHEN / THEN
                with raises(TypeError):
                    # noinspection PyTypeChecker
                    test_stream.reduce(identity, None)

    class TestSkip:
        """skip method tests"""

        class TestNominalCase:
            def test_empty_stream__should__return_an_empty_stream(self) -> None:
                """When stream is empty, should return an empty stream"""
                # GIVEN
                stream: Stream[int] = Stream.empty()
                skip: int = 10

                # WHEN
                new_stream: Stream[int] = stream.skip(skip)

                # THEN
                assert new_stream.to_list() == lists.empty_list()

            def test_less_values_than_skip__should__return_an_empty_stream(self, test_stream: Stream[int]) -> None:
                """When stream contains fewer values than skip should return an empty"""
                # GIVEN test_stream
                skip: int = maxsize

                # WHEN
                new_stream: Stream[int] = test_stream.skip(skip)

                # THEN
                assert new_stream.to_list() == lists.empty_list()

            def test_skip_is_zero__should__return_stream_with_all_elements(
                    self, test_stream: Stream[int]
            ) -> None:
                """When skip is zero, should return a stream with all elements"""
                # GIVEN test_stream
                skip: int = 0

                # WHEN
                new_stream: Stream[int] = test_stream.skip(skip)

                # THEN
                result: list[int] = new_stream.to_list()
                assert all(value in result for value in TestStream.TEST_VALUES)

            def test_negative_skip__should__return_an_empty_stream(self, test_stream: Stream[int]) -> None:
                """When skip is negative, should return a stream with all elements"""
                # GIVEN test_stream
                skip: int = -1

                # WHEN
                new_stream: Stream[int] = test_stream.skip(skip)

                # THEN
                result: list[int] = new_stream.to_list()
                assert all(value in result for value in TestStream.TEST_VALUES)

            def test_skip_exists__should__return_a_truncated_stream(
                    self, test_stream: Stream[int]
            ) -> None:
                """When skip exists should return a truncated stream"""
                # GIVEN test_stream
                skip: int = 20

                # WHEN
                new_stream: Stream[int] = test_stream.skip(skip)

                # THEN
                result: list[int] = new_stream.to_list()
                assert len(result) == len(TestStream.TEST_VALUES) - skip
                assert all(value in TestStream.TEST_VALUES for value in result)

        class TestErrorCase:
            def test_none_parameter__should__raise_type_error(self, test_stream: Stream[int]) -> None:
                """When parameter is None, should raise TypeError exception"""
                # GIVEN test_stream
                # WHEN / THEN
                with raises(TypeError):
                    # noinspection PyTypeChecker
                    test_stream.skip(None)

    class TestTakeWhile:
        """take_while method tests"""

        class TestNominalCase:
            def test_empty_stream__should__return_an_empty_stream(self) -> None:
                """When stream is empty, should return an empty stream"""
                # GIVEN
                stream: Stream[int] = Stream.empty()
                min_value: int = 10
                predicate: Predicate[int] = partial(TestStream._predicate_less_than, value=min_value)

                # WHEN
                new_stream: Stream[int] = stream.take_while(predicate)

                # THEN
                assert new_stream.to_list() == lists.empty_list()

            def test_ordered_stream_with_matched_predicate__should__return_stream_with_taken_values(
                    self, test_stream: Stream[int]
            ) -> None:
                """
                When stream is ordered and predicate match at least one value, should return a stream with taken
                values
                """
                # GIVEN
                stream: Stream[int] = test_stream.ordered_execution()
                min_value: int = 10
                predicate: Predicate[int] = partial(TestStream._predicate_less_than, value=min_value)

                # WHEN
                new_stream: Stream[int] = stream.take_while(predicate)

                # THEN
                result: list[int] = new_stream.to_list()
                assert len(result) == min_value
                assert all(value in result for value in range(0, min_value))

            def test_not_matched_predicate__should__return_stream_with_all_values(
                    self, test_stream: Stream[int]
            ) -> None:
                """When no value match, should return an empty stream"""
                # GIVEN
                predicate: Predicate[int] = is_none

                # WHEN
                new_stream: Stream[int] = test_stream.take_while(predicate)

                # THEN
                assert new_stream.to_list() == lists.empty_list()

            def test_unordered_stream_with_valid_predicate__should__return_a_stream_with_some_taken_values(
                    self, test_stream: Stream[int]
            ) -> None:
                """
                When stream is unordered and predicate match at least one value, should return a stream with some
                taken values (the stream may be empty)
                """
                # GIVEN
                stream: Stream[int] = test_stream.unordered()
                min_value: int = 50
                predicate: Predicate[int] = partial(TestStream._predicate_less_than, value=min_value)

                # WHEN
                new_stream: Stream[int] = stream.take_while(predicate)

                # THEN
                result: list[int] = new_stream.to_list()
                assert len(result) <= min_value
                assert all(value in TestStream.TEST_VALUES for value in result)

        class TestErrorCase:
            def test_none_predicate__should__raise_type_error(self, test_stream: Stream[int]) -> None:
                """When predicate is None, should raise TypeError exception"""
                # GIVEN test_stream
                # WHEN / THEN
                with raises(TypeError):
                    # noinspection PyTypeChecker
                    test_stream.take_while(None)

    class TestSorted:
        """sorted method tests"""

        class TestNominalCase:
            def test_empty_stream__should__return_an_empty_ordered_stream(self) -> None:
                """When stream is empty, should return an empty stream with ordered configuration"""
                # GIVEN
                stream: Stream[int] = Stream.empty()

                # WHEN
                new_stream: Stream[int] = stream.sorted()

                # THEN
                assert new_stream.to_list() == lists.empty_list()
                assert new_stream._ordered_execution is True

            def test_default_comparator__should__return_an_ordered_natural_order_sorted_stream(
                    self, parallel_config_fixture: ParallelConfiguration
            ) -> None:
                """When uses default comparator, should return an ordered stream with natural ordered values"""
                # GIVEN
                values: list[int] = [2, 5, 1, 3, 7, 120, 7, 10]
                stream: Stream[int] = Stream.of_iterable(values).parallel(parallel_config_fixture)

                # WHEN
                new_stream: Stream[int] = stream.sorted()

                # THEN
                expected_result: list[int] = sorted(values)
                result: list[int] = new_stream.to_list()
                assert new_stream._ordered_execution is True
                assert result == expected_result

            def test_comparator_exists__should__return_an_ordered_stream_based_on_comparator(
                    self, parallel_config_fixture: ParallelConfiguration
            ) -> None:
                """
                When comparator is provided, should return an ordered stream with ordered values based on given
                comparator
                """
                # GIVEN
                values: list[int] = [2, 5, 1, 3, 7, 120, 7, 10]
                stream: Stream[int] = Stream.of_iterable(values).parallel(parallel_config_fixture)
                reverse_comparator: BiFunction[int, int, int] = lambda i1, i2: 0 if i1 == i2 else 1 if i1 < i2 else -1

                # WHEN
                new_stream: Stream[int] = stream.sorted(reverse_comparator)

                # THEN
                expected_result: list[int] = sorted(values, reverse=True)
                result: list[int] = new_stream.to_list()
                assert new_stream._ordered_execution is True
                assert result == expected_result

        class TestErrorCase:
            def test_none_comparator__should__raise_type_error(self, test_stream: Stream[int]) -> None:
                """When comparator is None, should raise TypeError exception"""
                # GIVEN test_stream
                # WHEN / THEN
                with raises(TypeError):
                    # noinspection PyTypeChecker
                    test_stream.sorted(None)

    class TestToGenerator:
        """to_generator method tests"""

        class TestNominalCase:

            def test_empty_stream__should__generate_nothing(self) -> None:
                """When stream is empty, should generate nothing"""
                # GIVEN
                stream: Stream[int] = Stream.empty()

                # WHEN
                generator: Iterator[int] = stream.to_generator()

                # THEN
                with raises(StopIteration):
                    generator.__next__()

            def test_ordered_stream__should__generate_mapped_values_in_source_order(
                    self, test_stream: Stream[int]
            ) -> None:
                """When stream is ordered, should return mapped values in source order"""
                # GIVEN test_stream
                stream: Stream[str] = test_stream.ordered_execution().map(str)

                # WHEN
                generator: Iterator[str] = stream.to_generator()

                # THEN
                for value in TestStream.TEST_STR_VALUES:
                    assert generator.__next__() == value
                with raises(StopIteration):
                    generator.__next__()

            def test_unordered_stream__should__generate_mapped_values_in_random_order(
                    self, test_stream: Stream[int]
            ) -> None:
                # GIVEN test_stream
                stream: Stream[str] = test_stream.unordered().map(str)

                # WHEN
                generator: Iterator[str] = stream.to_generator()

                # THEN
                counter: int = 0
                for value in generator:
                    counter += 1
                    assert value in TestStream.TEST_STR_VALUES
                assert counter == len(TestStream.TEST_STR_VALUES)
