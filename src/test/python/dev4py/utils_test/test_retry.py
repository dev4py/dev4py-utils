"""retry module tests"""

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
from dataclasses import FrozenInstanceError
from time import time
from typing import Awaitable
from unittest.mock import patch, MagicMock

from pytest import raises

from dev4py.utils import retry
from dev4py.utils.retry import RetryConfiguration
from dev4py.utils.types import Function


##############################
#     PUBLIC MODULE PART     #
##############################
class TestRetryConfiguration:
    """RetryConfiguration class tests"""

    class TestConstructor:
        """Constructor tests"""

        class TestNominalCase:
            def test_existing_parameters__should__create_new_retry_configuration(self) -> None:
                """When all parameters are set, should create a new RetryConfiguration with given parameters"""
                # GIVEN
                exponent: int = 7
                delay: float = 0.5
                max_tries: int = 10

                # WHEN
                retry_config: RetryConfiguration = RetryConfiguration(
                    exponent=exponent, delay=delay, max_tries=max_tries
                )

                # THEN
                assert retry_config.exponent == exponent
                assert retry_config.delay == delay
                assert retry_config.max_tries == max_tries

            def test_min_valued_parameters__should__create_new_retry_configuration(self) -> None:
                """
                When all parameters are set to their min value, should create a new RetryConfiguration with given
                parameters
                """
                # GIVEN
                exponent: int = 0
                delay: float = 0
                max_tries: int = 1

                # WHEN
                retry_config: RetryConfiguration = RetryConfiguration(
                    exponent=exponent, delay=delay, max_tries=max_tries
                )

                # THEN
                assert retry_config.exponent == exponent
                assert retry_config.delay == delay
                assert retry_config.max_tries == max_tries

            def test_no_parameters__should__create_new_default_retry_configuration(self) -> None:
                """When no parameters are set, should create a new RetryConfiguration with default parameters"""
                # GIVEN / WHEN
                retry_config: RetryConfiguration = RetryConfiguration()

                # THEN
                assert retry_config.exponent == 2
                assert retry_config.delay == 0.1
                assert retry_config.max_tries == 3

        class TestErrorCase:
            def test_none_exponent__should_raise_type_error(self) -> None:
                """When exponent is None, should raise TypeError exception"""
                # GIVEN
                delay: float = 0.5
                max_tries: int = 10

                # WHEN / THEN
                with raises(TypeError) as error:
                    # noinspection PyTypeChecker
                    RetryConfiguration(exponent=None, delay=delay, max_tries=max_tries)

                assert str(error.value) == "exponent must be non None"

            def test_none_delay__should_raise_type_error(self) -> None:
                """When delay is None, should raise TypeError exception"""
                # GIVEN
                exponent: int = 7
                max_tries: int = 10

                # WHEN / THEN
                with raises(TypeError) as error:
                    # noinspection PyTypeChecker
                    RetryConfiguration(exponent=exponent, delay=None, max_tries=max_tries)

                assert str(error.value) == "delay must be non None"

            def test_none_max_tries__should_raise_type_error(self) -> None:
                """When max_tries is None, should raise TypeError exception"""
                # GIVEN
                exponent: int = 7
                delay: float = 0.5

                # WHEN / THEN
                with raises(TypeError) as error:
                    # noinspection PyTypeChecker
                    RetryConfiguration(exponent=exponent, delay=delay, max_tries=None)

                assert str(error.value) == "max_tries must be non None"

            def test_less_than_zero_exponent__should_raise_value_error(self) -> None:
                """When exponent is less than zero, should raise ValueError exception"""
                # GIVEN
                exponent: int = -1
                delay: float = 0.5
                max_tries: int = 3

                # WHEN / THEN
                with raises(ValueError) as error:
                    RetryConfiguration(exponent=exponent, delay=delay, max_tries=max_tries)

                assert str(error.value) == "exponent must be greater than or equals to 0"

            def test_less_than_zero_delay__should_raise_value_error(self) -> None:
                """When delay is less than zero, should raise ValueError exception"""
                # GIVEN
                exponent: int = 1
                delay: float = -0.5
                max_tries: int = 3

                # WHEN / THEN
                with raises(ValueError) as error:
                    RetryConfiguration(exponent=exponent, delay=delay, max_tries=max_tries)

                assert str(error.value) == "delay must be greater than or equals to 0"

            def test_less_than_one_max_tries__should_raise_value_error(self) -> None:
                """When max_tries is less than one, should raise ValueError exception"""
                # GIVEN
                exponent: int = 7
                delay: float = 0.5
                max_tries: int = 0

                # WHEN / THEN
                with raises(ValueError) as error:
                    RetryConfiguration(exponent=exponent, delay=delay, max_tries=max_tries)

                assert str(error.value) == "max_tries must be greater than or equals to 1"

    class TestSetters:
        """Setters tests"""

        class TestErrorCase:
            def test_set_new_exponent__should__raise_frozen_instance_error(self) -> None:
                """When set a new exponent, should raise a FrozenInstanceError exception"""
                # GIVEN
                exponent: int = 7
                delay: float = 0.5
                max_tries: int = 10
                retry_config: RetryConfiguration = RetryConfiguration(
                    exponent=exponent, delay=delay, max_tries=max_tries
                )

                # WHEN / THEN
                new_exponent: int = 8
                with raises(FrozenInstanceError):
                    # noinspection PyDataclass
                    retry_config.exponents = new_exponent

            def test_set_new_delay__should__raise_frozen_instance_error(self) -> None:
                """When set a new delay, should raise a FrozenInstanceError exception"""
                # GIVEN
                exponent: int = 7
                delay: float = 0.5
                max_tries: int = 10
                retry_config: RetryConfiguration = RetryConfiguration(
                    exponent=exponent, delay=delay, max_tries=max_tries
                )

                # WHEN / THEN
                new_delay: float = 2.1
                with raises(FrozenInstanceError):
                    # noinspection PyDataclass
                    retry_config.delay = new_delay

            def test_set_new_max_tries__should__raise_frozen_instance_error(self) -> None:
                """When set a new max_tries, should raise a FrozenInstanceError exception"""
                # GIVEN
                exponent: int = 7
                delay: float = 0.5
                max_tries: int = 10
                retry_config: RetryConfiguration = RetryConfiguration(
                    exponent=exponent, delay=delay, max_tries=max_tries
                )

                # WHEN / THEN
                new_max_tries: int = 5
                with raises(FrozenInstanceError):
                    # noinspection PyDataclass
                    retry_config.max_tries = new_max_tries

    class TestGetWaitingInterval:
        """get_waiting_interval method tests"""

        class TestNominalCase:
            def test_valid_retry_number__should__return_exponential_backoff_result(self) -> None:
                """When retry_number is valid, should return the exponential backoff depending on it"""
                # GIVEN
                exponent: int = 3
                delay: float = 0.5
                max_tries: int = 10
                retry_config: RetryConfiguration = RetryConfiguration(
                    exponent=exponent, delay=delay, max_tries=max_tries
                )
                retry_number: int = 5

                # WHEN
                backoff: float = retry_config.get_waiting_interval(retry_number=retry_number)

                # THEN
                assert backoff == delay * (exponent ** retry_number)

            def test_retry_number_equals_to_max_tries__should__return_exponential_backoff_result(self) -> None:
                """When retry_number is equals to max tries, should return the exponential backoff depending on it"""
                # GIVEN
                exponent: int = 3
                delay: float = 0.5
                max_tries: int = 10
                retry_config: RetryConfiguration = RetryConfiguration(
                    exponent=exponent, delay=delay, max_tries=max_tries
                )

                # WHEN
                backoff: float = retry_config.get_waiting_interval(retry_number=max_tries)

                # THEN
                assert backoff == delay * (exponent ** max_tries)

        class TestErrorCase:
            def test_none_retry_number__should__raise_type_error(self) -> None:
                """When retry_number is None, should raise a TypeError exception"""
                # GIVEN
                exponent: int = 7
                delay: float = 0.5
                max_tries: int = 10
                retry_config: RetryConfiguration = RetryConfiguration(
                    exponent=exponent, delay=delay, max_tries=max_tries
                )

                # WHEN / THEN
                with raises(TypeError):
                    # noinspection PyTypeChecker
                    retry_config.get_waiting_interval(None)

            def test_zero_retry_number__should__raise_value_error(self) -> None:
                """When retry_number is zero, should raise a ValueError exception"""
                # GIVEN
                exponent: int = 7
                delay: float = 0.5
                max_tries: int = 10
                retry_config: RetryConfiguration = RetryConfiguration(
                    exponent=exponent, delay=delay, max_tries=max_tries
                )

                # WHEN / THEN
                with raises(ValueError) as error:
                    # noinspection PyTypeChecker
                    retry_config.get_waiting_interval(0)

                assert str(error.value) == "retry_number must be greater than 0"

            def test_negative_retry_number__should__raise_value_error(self) -> None:
                """When retry_number is negative, should raise a ValueError exception"""
                # GIVEN
                exponent: int = 7
                delay: float = 0.5
                max_tries: int = 10
                retry_config: RetryConfiguration = RetryConfiguration(
                    exponent=exponent, delay=delay, max_tries=max_tries
                )

                # WHEN / THEN
                with raises(ValueError) as error:
                    # noinspection PyTypeChecker
                    retry_config.get_waiting_interval(-1)

                assert str(error.value) == "retry_number must be greater than 0"

            def test_retry_number_greater_than_max_tries__should__raise_value_error(self) -> None:
                """When retry_number is greater than max_tries, should raise a ValueError exception"""
                # GIVEN
                exponent: int = 7
                delay: float = 0.5
                max_tries: int = 10
                retry_config: RetryConfiguration = RetryConfiguration(
                    exponent=exponent, delay=delay, max_tries=max_tries
                )

                # WHEN / THEN
                with raises(ValueError) as error:
                    # noinspection PyTypeChecker
                    retry_config.get_waiting_interval(max_tries + 1)

                assert str(error.value) == "retry_number greater than configured max_tries"


class TestToRetryable:
    """to_retryable function tests"""
    _EXPONENT: int = 2
    _DELAY: float = 0.01
    _MAX_TRIES: int = 3
    _RETRY_CONFIG: RetryConfiguration = RetryConfiguration(exponent=_EXPONENT, delay=_DELAY, max_tries=_MAX_TRIES)
    _SEMI_FAILURE_CALL: int = 0

    @staticmethod
    def _successful_function(i: int) -> int:
        print(i)
        return i * i

    @staticmethod
    def _failure_function(i: int) -> int:
        print(i)
        raise ValueError(i)

    @staticmethod
    def _semi_failure_function(i: int) -> int:
        TestToRetryable._SEMI_FAILURE_CALL = (TestToRetryable._SEMI_FAILURE_CALL + 1) % 2
        return TestToRetryable._failure_function(i) \
            if TestToRetryable._SEMI_FAILURE_CALL == 1 \
            else TestToRetryable._successful_function(i)

    class TestNominalCase:

        @patch('builtins.print')
        def test_callable_in_success__should__return_retryable_callable_with_success_value(
                self, counter_mock: MagicMock
        ) -> None:
            """When the given callable always succeed, should return a retryable one and execution should succeed"""
            # GIVEN TestToRetryable.RETRY_CONFIG
            test_callable: Function[int, int] = TestToRetryable._successful_function

            # WHEN
            retryable_callable: Function[int, int] = retry.to_retryable(test_callable)

            # THEN
            param: int = 2
            assert retryable_callable(param) == (param * param)
            counter_mock.assert_called_once_with(param)
            assert counter_mock.call_count == 1

        @patch('builtins.print')
        def test_failure_callable_with_default_on_failure__should__return_retryable_and_raise_error_after_retry(
                self, counter_mock: MagicMock
        ) -> None:
            """When the given callable always failed, should return a retryable which raises an error on execution"""
            # GIVEN TestToRetryable.RETRY_CONFIG
            test_callable: Function[int, int] = TestToRetryable._failure_function

            # WHEN
            retryable_callable: Function[int, int] = \
                retry.to_retryable(test_callable, retry_config=TestToRetryable._RETRY_CONFIG)

            # THEN
            param: int = 2
            expected_min_duration: float = sum(
                [
                    TestToRetryable._RETRY_CONFIG.get_waiting_interval(n_retry)
                    for n_retry in range(1, TestToRetryable._MAX_TRIES)
                ]
            )
            exec_duration: float = time()
            with raises(ValueError) as error:
                retryable_callable(param)
            exec_duration = time() - exec_duration
            assert exec_duration >= expected_min_duration
            counter_mock.assert_called_with(param)
            assert counter_mock.call_count == TestToRetryable._MAX_TRIES
            assert str(error.value) == str(param)

        @patch('builtins.print')
        def test_failure_callable_with_on_failure__should__return_retryable_and_call_on_failure_parameter(
                self, counter_mock: MagicMock
        ) -> None:
            """
            When the given callable always failed and on_failure is provided, should return a retryable which calls the
            given on_failure function
            """
            # GIVEN TestToRetryable.RETRY_CONFIG
            test_callable: Function[int, int] = TestToRetryable._failure_function
            default_value: int = 7
            on_failure: Function[BaseException, int] = lambda _: default_value

            # WHEN
            retryable_callable: Function[int, int] = \
                retry.to_retryable(test_callable, retry_config=TestToRetryable._RETRY_CONFIG, on_failure=on_failure)

            # THEN
            param: int = 2
            expected_min_duration: float = sum(
                [
                    TestToRetryable._RETRY_CONFIG.get_waiting_interval(n_retry)
                    for n_retry in range(1, TestToRetryable._MAX_TRIES)
                ]
            )
            exec_duration: float = time()
            assert retryable_callable(param) == default_value
            exec_duration = time() - exec_duration
            counter_mock.assert_called_with(param)
            assert counter_mock.call_count == TestToRetryable._MAX_TRIES
            assert exec_duration >= expected_min_duration

        @patch('builtins.print')
        def test_semi_failure_callable__should__raise_callable_error_after_retry(
                self, counter_mock: MagicMock
        ) -> None:
            """
            When the given callable failed once, should return a retryable and execution should succeed after one retry
            """
            # GIVEN TestToRetryable.RETRY_CONFIG
            TestToRetryable._SEMI_FAILURE_CALL = 0
            test_callable: Function[int, int] = TestToRetryable._semi_failure_function

            # WHEN
            retryable_callable: Function[int, int] = \
                retry.to_retryable(test_callable, retry_config=TestToRetryable._RETRY_CONFIG)

            # THEN
            param: int = 2
            expected_min_duration: float = TestToRetryable._RETRY_CONFIG.get_waiting_interval(1)
            exec_duration: float = time()
            assert retryable_callable(param) == (param * param)
            exec_duration = time() - exec_duration
            assert exec_duration >= expected_min_duration
            counter_mock.assert_called_with(param)
            assert counter_mock.call_count == 2

        class TestErrorCase:
            def test_none_sync_callable__should__raise_type_error(self) -> None:
                """When sync_callable is None, should raise a TypeError exception"""
                # GIVEN / WHEN / THEN
                with raises(TypeError):
                    # noinspection PyTypeChecker
                    retry.to_retryable(sync_callable=None)

            def test_none_retry_config__should__raise_type_error(self) -> None:
                """When retry_config is None, should raise a TypeError exception"""
                # GIVEN
                test_callable: Function[int, int] = TestToRetryable._semi_failure_function

                # WHEN / THEN
                with raises(TypeError):
                    # noinspection PyTypeChecker
                    retry.to_retryable(sync_callable=test_callable, retry_config=None)

            def test_none_on_failure__should__raise_type_error(self) -> None:
                """When on_failure is None, should raise a TypeError exception"""
                # GIVEN
                test_callable: Function[int, int] = TestToRetryable._semi_failure_function

                # WHEN / THEN
                with raises(TypeError):
                    # noinspection PyTypeChecker
                    retry.to_retryable(sync_callable=test_callable, on_failure=None)


class TestToAsyncRetryable:
    """to_async_retryable function tests"""
    _EXPONENT: int = 2
    _DELAY: float = 0.01
    _MAX_TRIES: int = 3
    _RETRY_CONFIG: RetryConfiguration = RetryConfiguration(exponent=_EXPONENT, delay=_DELAY, max_tries=_MAX_TRIES)
    _SEMI_FAILURE_CALL: int = 0

    @staticmethod
    async def _successful_function(i: int) -> int:
        print(i)
        return i * i

    @staticmethod
    async def _failure_function(i: int) -> int:
        print(i)
        raise ValueError(i)

    @staticmethod
    async def _semi_failure_function(i: int) -> int:
        TestToAsyncRetryable._SEMI_FAILURE_CALL = (TestToAsyncRetryable._SEMI_FAILURE_CALL + 1) % 2
        return await TestToAsyncRetryable._failure_function(i) \
            if TestToAsyncRetryable._SEMI_FAILURE_CALL == 1 \
            else await TestToAsyncRetryable._successful_function(i)

    class TestNominalCase:

        @patch('builtins.print')
        async def test_callable_in_success__should__return_retryable_callable_with_success_value(
                self, counter_mock: MagicMock
        ) -> None:
            """When the given callable always succeed, should return a retryable one and execution should succeed"""
            # GIVEN TestToAsyncRetryable.RETRY_CONFIG
            test_callable: Function[int, Awaitable[int]] = TestToAsyncRetryable._successful_function

            # WHEN
            retryable_callable: Function[int, Awaitable[int]] = retry.to_async_retryable(test_callable)

            # THEN
            param: int = 2
            assert await retryable_callable(param) == (param * param)
            counter_mock.assert_called_once_with(param)
            assert counter_mock.call_count == 1

        @patch('builtins.print')
        async def test_failure_callable_with_default_on_failure__should__return_retryable_and_raise_error_after_retry(
                self, counter_mock: MagicMock
        ) -> None:
            """When the given callable always failed, should return a retryable which raises an error on execution"""
            # GIVEN TestToAsyncRetryable.RETRY_CONFIG
            test_callable: Function[int, Awaitable[int]] = TestToAsyncRetryable._failure_function

            # WHEN
            retryable_callable: Function[int, Awaitable[int]] = \
                retry.to_async_retryable(test_callable, retry_config=TestToAsyncRetryable._RETRY_CONFIG)

            # THEN
            param: int = 2
            expected_min_duration: float = sum(
                [
                    TestToAsyncRetryable._RETRY_CONFIG.get_waiting_interval(n_retry)
                    for n_retry in range(1, TestToAsyncRetryable._MAX_TRIES)
                ]
            )
            exec_duration: float = time()
            with raises(ValueError) as error:
                await retryable_callable(param)
            exec_duration = time() - exec_duration
            assert exec_duration >= expected_min_duration
            counter_mock.assert_called_with(param)
            assert counter_mock.call_count == TestToAsyncRetryable._MAX_TRIES
            assert str(error.value) == str(param)

        @patch('builtins.print')
        async def test_failure_callable_with_on_failure__should__return_retryable_and_call_on_failure_parameter(
                self, counter_mock: MagicMock
        ) -> None:
            """
            When the given callable always failed and on_failure is provided, should return a retryable which calls the
            given on_failure function
            """
            # GIVEN TestToAsyncRetryable.RETRY_CONFIG
            test_callable: Function[int, Awaitable[int]] = TestToAsyncRetryable._failure_function
            default_value: int = 7
            on_failure: Function[BaseException, int] = lambda _: default_value

            # WHEN
            retryable_callable: Function[int, Awaitable[int]] = \
                retry.to_async_retryable(test_callable, retry_config=TestToAsyncRetryable._RETRY_CONFIG,
                                         on_failure=on_failure)

            # THEN
            param: int = 2
            expected_min_duration: float = sum(
                [
                    TestToAsyncRetryable._RETRY_CONFIG.get_waiting_interval(n_retry)
                    for n_retry in range(1, TestToAsyncRetryable._MAX_TRIES)
                ]
            )
            exec_duration: float = time()
            assert await retryable_callable(param) == default_value
            exec_duration = time() - exec_duration
            counter_mock.assert_called_with(param)
            assert counter_mock.call_count == TestToAsyncRetryable._MAX_TRIES
            assert exec_duration >= expected_min_duration

        @patch('builtins.print')
        async def test_semi_failure_callable__should__raise_callable_error_after_retry(
                self, counter_mock: MagicMock
        ) -> None:
            """
            When the given callable failed once, should return a retryable and execution should succeed after one retry
            """
            # GIVEN TestToAsyncRetryable.RETRY_CONFIG
            TestToAsyncRetryable._SEMI_FAILURE_CALL = 0
            test_callable: Function[int, Awaitable[int]] = TestToAsyncRetryable._semi_failure_function

            # WHEN
            retryable_callable: Function[int, Awaitable[int]] = \
                retry.to_async_retryable(test_callable, retry_config=TestToAsyncRetryable._RETRY_CONFIG)

            # THEN
            param: int = 2
            expected_min_duration: float = TestToAsyncRetryable._RETRY_CONFIG.get_waiting_interval(1)
            exec_duration: float = time()
            assert await retryable_callable(param) == (param * param)
            exec_duration = time() - exec_duration
            assert exec_duration >= expected_min_duration
            counter_mock.assert_called_with(param)
            assert counter_mock.call_count == 2

        class TestErrorCase:
            def test_none_async_callable__should__raise_type_error(self) -> None:
                """When async_callable is None, should raise a TypeError exception"""
                # GIVEN / WHEN / THEN
                with raises(TypeError):
                    # noinspection PyTypeChecker
                    retry.to_async_retryable(async_callable=None)

            def test_none_retry_config__should__raise_type_error(self) -> None:
                """When retry_config is None, should raise a TypeError exception"""
                # GIVEN
                test_callable: Function[int, Awaitable[int]] = TestToAsyncRetryable._semi_failure_function

                # WHEN / THEN
                with raises(TypeError):
                    # noinspection PyTypeChecker
                    retry.to_async_retryable(async_callable=test_callable, retry_config=None)

            def test_none_on_failure__should__raise_type_error(self) -> None:
                """When on_failure is None, should raise a TypeError exception"""
                # GIVEN
                test_callable: Function[int, Awaitable[int]] = TestToAsyncRetryable._semi_failure_function

                # WHEN / THEN
                with raises(TypeError):
                    # noinspection PyTypeChecker
                    retry.to_async_retryable(async_callable=test_callable, on_failure=None)
