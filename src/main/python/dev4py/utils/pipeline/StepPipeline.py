"""The `StepPipeline` class is used in order to create a Pipeline where each step can stop the execution"""

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

from dataclasses import dataclass
from typing import Generic, Final, Any, Optional, Union

from dev4py.utils.JOptional import JOptional
from dev4py.utils.objects import require_non_none, require_non_none_else
from dev4py.utils.types import Function, T, N, IN, OUT


@dataclass
class StepResult(Generic[T]):
    """
    Represents a Step result

    Args:
        value: the result value of T type
        go_next: True if the next step must be executed, otherwise False
    """
    value: T
    go_next: bool = True


class _Step(Generic[IN, OUT]):

    def __init__(self, handler: Function[IN, StepResult[OUT]]):
        """_Step constructor"""
        self._handler: Final[Function[IN, StepResult[OUT]]] = require_non_none(handler)
        self._next: JOptional[_Step[OUT, Any]] = JOptional.empty()

    def add_next(self, next_handler: Function[OUT, StepResult[N]]) -> _Step[OUT, N]:
        """
        Adds a next step and returns it

        Args:
            next_handler: the next step handler

        Returns:
            _Step[OUT, N]: The new created step

        """
        next_step: _Step[OUT, N] = _Step(handler=require_non_none(next_handler))
        self._next = JOptional.of(next_step)
        return next_step

    def execute(self, value: IN) -> StepResult[Union[OUT, Any]]:
        """
        Executes the current step and if `go_next` is True call the next step if it exists. Returns the last executed
        step.

        Note: It means if the returned StepResult `go_next` field is TRUE all steps were executed. Otherwise, one step
        has stopped the execution.

        Args:
            value: The value of IN type

        Returns:
            StepResult[Union[OUT, Any]]: The last executed StepResult. Can be an intermediate step if `go_next` is False
        """
        step_result: Final[StepResult[OUT]] = self._handler(value)
        return self._next.get().execute(step_result.value) \
            if step_result.go_next and self._next.is_present() else step_result


class StepPipeline(Generic[IN, OUT]):
    __CREATE_KEY: Final[object] = object()

    @classmethod
    def of(cls, handler: Function[IN, StepResult[OUT]]) -> StepPipeline[IN, OUT]:
        """
        Returns a StepPipeline[IN, OUT] initialized with the given handler

        Note: the handler returned value is a `StepResult`. The function result value must be put in `value` field. To
        stop the current pipeline at this step `go_next` field must be set to False.

        Args:
            handler: the first step handler

        Returns:
            StepPipeline[IN, OUT]: The new pipeline StepPipeline which consumes an IN value and last step consumes an
            OUT value

        """
        return cls._of(step=_Step(handler))

    @classmethod
    def _of(cls, step: _Step[Any, OUT], head: Optional[_Step[IN, Any]] = None) -> StepPipeline[IN, OUT]:
        """
        !!! PRIVATE _OF CLASS METHOD !!!

        Returns a StepPipeline[IN, OUT] by using the given last step and the given head step

        Args:
            step: the last step
            head: the head step

        Returns:
            StepPipeline[IN, OUT]: The new pipeline StepPipeline which consumes an IN value and last step consumes an
            OUT value
        """
        return StepPipeline(cls.__CREATE_KEY, step=step, head=head)

    def __init__(self, create_key: object, step: _Step[Any, OUT], head: Optional[_Step[IN, Any]] = None):
        """
        StepPipeline private constructor: Constructs a Pipeline which consumes an IN value and last step consumes a OUT
        value
        """
        assert create_key == self.__CREATE_KEY, "StepPipeline private constructor! Please use StepPipeline.of"
        require_non_none(step)
        self._head: _Step[IN, Any] = require_non_none_else(head, step)
        self._last: _Step[Any, OUT] = step

    def add_handler(self, next_handler: Function[OUT, StepResult[N]]) -> StepPipeline[IN, N]:
        """
        Adds a new step to the pipeline by using the given handler and returns the new Pipeline

        Note: the handler returned value is a `StepResult`. The function result value must be put in `value` field. To
        stop the current pipeline at this step `go_next` field must be set to False.

        Args:
            next_handler: the new step handler

        Returns:
            StepPipeline[IN, N]: The new pipeline StepPipeline which consumes an IN value and last step consumes an N
                value

        """
        return StepPipeline._of(step=self._last.add_next(next_handler), head=self._head)

    def execute(self, value: IN) -> StepResult[Union[OUT, Any]]:
        """
        Executes the current pipeline and returns the last executed Step

        Note: The last executed step can be an intermediate one if `go_next` is false. If `go_next` is True it means
        that the pipeline was totally executed for the given value.

        Args:
            value: The value of IN type

        Returns:
            StepResult[Union[OUT, Any]]: The last executed StepResult. Can be an intermediate step if `go_next` is False

        """
        return self._head.execute(value)
