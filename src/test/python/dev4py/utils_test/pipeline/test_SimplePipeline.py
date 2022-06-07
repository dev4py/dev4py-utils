"""SimplePipeline module tests"""

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

from dev4py.utils.pipeline.SimplePipeline import SimplePipeline
from dev4py.utils.types import Function


class TestSimplePipeline:
    """SimplePipeline class tests"""
    CONSTRUCTOR_ERROR_MSG: Final[str] = "SimplePipeline private constructor! Please use SimplePipeline.of"
    INIT_HANDLER: Function[int, str] = lambda v: str(v)

    class TestConstructor:
        """Constructor tests"""

        class TestNominalCase:

            def test_none_create_key__should__raise_assertion_error(self):
                """When create key is none, should raise AssertionError with private constructor message"""
                # GIVEN / WHEN / THEN
                with raises(AssertionError) as error:
                    SimplePipeline(TestSimplePipeline.INIT_HANDLER, None)

                assert str(error.value) == TestSimplePipeline.CONSTRUCTOR_ERROR_MSG

            def test_invalid_create_key__should__raise_assertion_error(self):
                """When create key is invalid, should raise AssertionError with private constructor message"""
                # GIVEN / WHEN / THEN
                with raises(AssertionError) as error:
                    SimplePipeline(TestSimplePipeline.INIT_HANDLER, object())

                assert str(error.value) == TestSimplePipeline.CONSTRUCTOR_ERROR_MSG

            def test_valid_create_key__should__create_a_new_simple_pipeline(self):
                """When create key is valid, should create a new pipeline"""
                # GIVEN
                value: int = 1

                # WHEN
                # noinspection PyUnresolvedReferences
                pipeline: SimplePipeline[int, str] = SimplePipeline(TestSimplePipeline.INIT_HANDLER,
                                                                    SimplePipeline._SimplePipeline__CREATE_KEY)

                # THEN
                assert '1' == pipeline.execute(value)

            class TestErrorCase:
                def test_none_handler__should__raise_type_error(self) -> None:
                    """When no handler is provided, should raise a TypeError exception"""
                    # GIVEN / WHEN / THEN
                    with raises(TypeError):
                        # noinspection PyUnresolvedReferences
                        SimplePipeline(None, SimplePipeline._SimplePipeline__CREATE_KEY)

    class TestOf:
        """of class method tests"""

        class TestNominalCase:
            def test_handler_exists__should__return_pipeline_with_handler(self) -> None:
                """When a handler is provided, should return a SimplePipeline initialized with given handler"""
                # GIVEN
                value: int = 1

                # WHEN
                pipeline: SimplePipeline[int, str] = SimplePipeline.of(TestSimplePipeline.INIT_HANDLER)

                # THEN
                assert '1' == pipeline.execute(value)

        class TestErrorCase:
            def test_none_handler__should__raise_type_error(self) -> None:
                """When no handler is provided, should raise a TypeError exception"""
                # GIVEN / WHEN / THEN
                with raises(TypeError):
                    SimplePipeline.of(None)

    class TestAddHandler:
        """add_handler method tests"""

        class TestNominalCase:
            def test_handler_exists__should__return_pipeline_with_added_handler(self) -> None:
                """
                When a handler is provided, should return a new SimplePipeline with given handler(/operation) added
                """
                # GIVEN
                value: int = 1
                pipeline: SimplePipeline[int, str] = SimplePipeline.of(TestSimplePipeline.INIT_HANDLER)
                handler: Function[str, str] = lambda s: s + "_new_handler_suffix"

                # WHEN
                new_pipeline: SimplePipeline[int, str] = pipeline.add_handler(handler)

                # THEN
                assert '1_new_handler_suffix' == new_pipeline.execute(value)

        class TestErrorCase:
            def test_none_handler__should__raise_type_error(self) -> None:
                """When no handler is provided, should raise a TypeError exception"""
                # GIVEN
                pipeline: SimplePipeline[int, str] = SimplePipeline.of(TestSimplePipeline.INIT_HANDLER)

                # WHEN / THEN
                with raises(TypeError):
                    pipeline.add_handler(None)

    class TestExecute:
        """execute method tests"""

        class TestNominalCase:
            def test_none_value__should__return_execution_result(self) -> None:
                """When a value is None, should return the execution result"""
                # GIVEN
                pipeline: SimplePipeline[Optional[int], str] = SimplePipeline.of(TestSimplePipeline.INIT_HANDLER)

                # WHEN
                result: str = pipeline.execute(None)

                # THEN
                assert 'None' == result

            def test_value_exists__should__return_execution_result(self) -> None:
                """When a value is provided, should return the execution result"""
                # GIVEN
                value: int = 1
                pipeline: SimplePipeline[int, str] = SimplePipeline.of(TestSimplePipeline.INIT_HANDLER)

                # WHEN
                result: str = pipeline.execute(value)

                # THEN
                assert '1' == result
