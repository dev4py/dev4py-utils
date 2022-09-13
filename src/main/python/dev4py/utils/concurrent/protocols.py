"""This module contains protocols used in concurrent environment"""

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


from abc import abstractmethod
from types import TracebackType
from typing import runtime_checkable, Protocol, Optional, Type

from dev4py.utils.types import T


@runtime_checkable
class Lock(Protocol):
    """Protocol describing Locks"""

    @abstractmethod
    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        """
        Acquire a lock, blocking or non-blocking.

        Args:
            blocking: Set to True, if another thread owns the lock, block until the lock is unlocked. Set to
                False, do not block (i.e.: returns false immediately, otherwise, do the same thing as when called with
                True) (default: True)
            timeout: When set to a positive value, block for at most the number of seconds specified by timeout and as
                long as the lock cannot be acquired (default: -1)

        Returns:
            bool: Return true if the lock has been acquired, false if the timeout has elapsed
        """

    @abstractmethod
    def release(self) -> None:
        """
        Release a lock
        """

    @abstractmethod
    def __enter__(self) -> bool: ...

    @abstractmethod
    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType]
    ) -> Optional[bool]: ...


@runtime_checkable
class Value(Protocol[T]):
    """Protocol describing a wrapper for a generic 'value' field"""
    value: T

    @abstractmethod
    def get(self) -> T:
        """
        The value field getter

        Returns:
            T: The value
        """

    @abstractmethod
    def set(self, value: T) -> None:
        """
        The value field setter

        Args:
            value: new value The value
        """
