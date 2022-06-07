"""iterable module tests"""

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

from typing import Iterable, Iterator

from pytest import raises

from dev4py.utils import iterables


class TestGetChunks:
    """get_chunks function test"""

    class TestNominalCase:

        def test_exiting_parameters__should__return_a_chunk_generator(self) -> None:
            """When iterable and size are given, should return a chunk generator"""
            # GIVEN
            iterable: Iterable[int] = [1, 2, 3, 4, 5, 6, 7]
            chunk_size: int = 3

            # WHEN
            chunk_gen: Iterator[list[int]] = iterables.get_chunks(iterable, chunk_size)

            # THEN
            assert chunk_gen.__next__() == [1, 2, 3]
            assert chunk_gen.__next__() == [4, 5, 6]
            assert chunk_gen.__next__() == [7]
            with raises(StopIteration):
                chunk_gen.__next__()

    class TestErrorCase:
        def test_none_iterable__should__raise_type_error(self) -> None:
            """When the iterable is None, should raise TypeError exception"""
            # GIVEN
            chunk_size: int = 3

            # WHEN / THEN
            with raises(TypeError):
                # noinspection PyTypeChecker
                iterables.get_chunks(None, chunk_size).__next__()

        def test_none_chunk_size__should__raise_type_error(self) -> None:
            """When the chunk_size is None, should raise TypeError exception"""
            # GIVEN
            iterable: Iterable[int] = []

            # WHEN / THEN
            with raises(TypeError):
                # noinspection PyTypeChecker
                iterables.get_chunks(iterable, None).__next__()

        def test_negative_chunk_size__should__raise_value_error(self) -> None:
            """When the chunk_size is negative, should raise ValueError exception"""
            # GIVEN
            iterable: Iterable[int] = []
            chunk_size: int = -1

            # WHEN / THEN
            with raises(ValueError):
                # noinspection PyTypeChecker
                iterables.get_chunks(iterable, chunk_size).__next__()
