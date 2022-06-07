"""The `SimplePipeline` class is used in order to create a Pipeline with one operation per step"""

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

from functools import partial
from typing import Generic, Final, cast

from dev4py.utils.objects import require_non_none
from dev4py.utils.types import OUT, IN, Function, R


class SimplePipeline(Generic[IN, OUT]):
    """A `SimplePipeline` with input of IN type and output of OUT type"""

    __CREATE_KEY: Final[object] = object()

    @classmethod
    def of(cls, handler: Function[IN, OUT]) -> SimplePipeline[IN, OUT]:
        """
        Returns a SimplePipeline[IN, OUT] initialized with the given handler

        Args:
            handler: The first pipeline handler

        Returns:
            SimplePipeline[IN, OUT]: The pipeline with the given handler as first operation

        """
        return SimplePipeline(handler, cls.__CREATE_KEY)

    def __init__(self, handler: Function[IN, OUT], create_key: object):
        """SimplePipeline private constructor: Constructs a Pipeline which processes IN to OUT value"""
        assert create_key == self.__CREATE_KEY, "SimplePipeline private constructor! Please use SimplePipeline.of"
        self._handler: Function[IN, OUT] = require_non_none(handler)

    def _add_handler_lambda(self, value: IN, handler: Function[OUT, R]) -> R:
        """
        private method to describe add_handler method new handler
        Note: lambda are not used in order to be compatible with multiprocessing (lambda are not serializable)
        """
        # lambda value: handler(self._handler(value))
        return handler(self._handler(value))

    def add_handler(self, handler: Function[OUT, R]) -> SimplePipeline[IN, R]:
        """
        Adds an operation/operation/step to the pipeline

        Args:
            handler: The handler to add

        Returns:
            SimplePipeline[IN, R]: The new pipeline where input is still of IN type but output is now of R type

        """
        require_non_none(handler)
        return SimplePipeline.of(cast(Function[IN, R], partial(self._add_handler_lambda, handler=handler)))

    def execute(self, value: IN) -> OUT:
        """
        Executes the current pipeline on the given value of IN type

        Args:
            value: The value of IN type

        Returns:
            OUT: the pipeline output of OUT type
        """
        return self._handler(value)
