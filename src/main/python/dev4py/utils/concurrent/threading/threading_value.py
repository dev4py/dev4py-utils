"""The ThreadingValue class implements the Value protocol for threads"""

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

from dev4py.utils.concurrent.protocols import Value
from dev4py.utils.types import T


@dataclass
class ThreadingValue(Value[T]):
    """
    ThreadingValue class: an equivalent implementation of the multiprocessing.Value for Threading context

    This can be useful when your development has to manage multiprocessing and threading

    Args:
        value (T): the wrapped value
    """
    value: T

    def get(self) -> T:
        """
        The value field getter

        Returns:
            T: The value
        """
        return self.value

    def set(self, value: T) -> None:
        """
        The value field setter

        Args:
            value: new value The value
        """
        self.value = value
