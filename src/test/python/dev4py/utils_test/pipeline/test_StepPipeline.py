"""StepPipeline module tests"""

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

from typing import Final, Optional

from pytest import raises

from dev4py.utils.objects import non_none
# noinspection PyProtectedMember
from dev4py.utils.pipeline.StepPipeline import StepResult, StepPipeline, _Step
from dev4py.utils.types import Function


class TestStepPipeline:
    """StepPipeline class tests"""
    CONSTRUCTOR_ERROR_MSG: Final[str] = "StepPipeline private constructor! Please use StepPipeline.of"
    INIT_HANDLER: Function[int, StepResult[str]] = lambda v: StepResult(str(v))

    class TestConstructor:
        """Constructor tests"""

        class TestNominalCase:

            def test_none_create_key__should__raise_assertion_error(self):
                """When create key is none, should raise AssertionError with private constructor message"""
                # GIVEN / WHEN / THEN
                with raises(AssertionError) as error:
                    StepPipeline(None, _Step(TestStepPipeline.INIT_HANDLER))

                assert str(error.value) == TestStepPipeline.CONSTRUCTOR_ERROR_MSG

            def test_invalid_create_key__should__raise_assertion_error(self):
                """When create key is invalid, should raise AssertionError with private constructor message"""
                # GIVEN / WHEN / THEN
                with raises(AssertionError) as error:
                    StepPipeline(object(), _Step(TestStepPipeline.INIT_HANDLER))

                assert str(error.value) == TestStepPipeline.CONSTRUCTOR_ERROR_MSG

            def test_valid_create_key__should__create_a_new_simple_pipeline(self):
                """When create key is valid, should create a new pipeline"""
                # GIVEN
                value: int = 1

                # WHEN
                # noinspection PyUnresolvedReferences
                pipeline: StepPipeline[int, str] = \
                    StepPipeline(StepPipeline._StepPipeline__CREATE_KEY, _Step(TestStepPipeline.INIT_HANDLER))

                # THEN
                result: StepResult[str] = pipeline.execute(value)
                assert non_none(result)
                assert result.go_next
                assert '1' == result.value

            class TestErrorCase:
                def test_none_handler__should__raise_type_error(self) -> None:
                    """When no step is provided, should raise a TypeError exception"""
                    # GIVEN / WHEN / THEN
                    with raises(TypeError):
                        # noinspection PyTypeChecker
                        # noinspection PyUnresolvedReferences
                        StepPipeline(StepPipeline._StepPipeline__CREATE_KEY, None)

    class TestOf:
        """of class method tests"""

        class TestNominalCase:
            def test_handler_exists__should__return_pipeline_with_handler(self) -> None:
                """When a handler is provided, should return a pipeline initialized with given handler"""
                # GIVEN
                value: int = 1

                # WHEN
                pipeline: StepPipeline[int, str] = StepPipeline.of(TestStepPipeline.INIT_HANDLER)

                # THEN
                result: StepResult[str] = pipeline.execute(value)
                assert non_none(result)
                assert result.go_next
                assert '1' == result.value

        class TestErrorCase:
            def test_none_handler__should__raise_type_error(self) -> None:
                """When no handler is provided, should raise a TypeError exception"""
                # GIVEN / WHEN / THEN
                with raises(TypeError):
                    StepPipeline.of(None)

    class TestAddHandler:
        """add_handler method tests"""

        class TestNominalCase:
            def test_handler_exists__should__return_pipeline_with_added_handler(self) -> None:
                """
                When a handler is provided, should return a new pipeline with given handler(/operation) added
                """
                # GIVEN
                value: int = 1
                pipeline: StepPipeline[int, str] = StepPipeline.of(TestStepPipeline.INIT_HANDLER)
                handler: Function[str, str] = lambda s: StepResult(s + "_new_handler_suffix")

                # WHEN
                new_pipeline: StepPipeline[int, str] = pipeline.add_handler(handler)

                # WHEN
                result: StepResult[str] = new_pipeline.execute(value)
                assert non_none(result)
                assert result.go_next
                assert '1_new_handler_suffix' == result.value

        class TestErrorCase:
            def test_none_handler__should__raise_type_error(self) -> None:
                """When no handler is provided, should raise a TypeError exception"""
                # GIVEN
                pipeline: StepPipeline[int, str] = StepPipeline.of(TestStepPipeline.INIT_HANDLER)

                # WHEN / THEN
                with raises(TypeError):
                    pipeline.add_handler(None)

    class TestExecute:
        """execute method tests"""

        class TestNominalCase:
            def test_none_value__should__return_execution_result(self) -> None:
                """When a value is None, should return the execution result"""
                # GIVEN
                pipeline: StepPipeline[Optional[int], str] = StepPipeline.of(TestStepPipeline.INIT_HANDLER)

                # WHEN
                result: StepResult[str] = pipeline.execute(None)

                # THEN
                assert result.go_next
                assert 'None' == result.value

            def test_value_exists__should__return_execution_result(self) -> None:
                """When a value is provided, should return the execution result"""
                # GIVEN
                value: int = 1
                pipeline: StepPipeline[Optional[int], str] = StepPipeline.of(TestStepPipeline.INIT_HANDLER)

                # WHEN
                result: StepResult[str] = pipeline.execute(value)

                # THEN
                assert result.go_next
                assert '1' == result.value

            def test_value_exists_with_multi_steps__should__return_execution_result(self) -> None:
                """When a value is provided with multi steps, should return the execution result"""
                # GIVEN
                value: int = 1
                pipeline: StepPipeline[Optional[int], str] = StepPipeline.of(TestStepPipeline.INIT_HANDLER) \
                    .add_handler(lambda s: StepResult(s + '_handler1')) \
                    .add_handler(lambda s: StepResult(s + '_handler2'))

                # WHEN
                result: StepResult[str] = pipeline.execute(value)

                # THEN
                assert result.go_next
                assert '1_handler1_handler2' == result.value

            def test_value_exists_with_partial_multi_steps__should__return_execution_result(self) -> None:
                """
                When a value is provided with multi steps but one of them stop the execution, should return the partial
                execution result
                """
                # GIVEN
                value: int = 1
                pipeline: StepPipeline[Optional[int], str] = StepPipeline.of(TestStepPipeline.INIT_HANDLER) \
                    .add_handler(lambda s: StepResult(s + '_handler1', go_next=False)) \
                    .add_handler(lambda s: StepResult(s + '_handler2'))

                # WHEN
                result: StepResult[str] = pipeline.execute(value)

                # THEN
                assert result.go_next is False
                assert '1_handler1' == result.value
