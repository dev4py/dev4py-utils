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

from itertools import islice
from typing import Iterator, Iterable

from dev4py.utils.objects import require_non_none
from dev4py.utils.types import V


def get_chunks(values: Iterable[V], chunksize: int) -> Iterator[list[V]]:
    """
    Returns a generator of chunk where values will be chopped into chunks of size chunksize

    Args:
        values: The values to chunk
        chunksize: The chunk size

    Returns:
        Iterator[list[V]]: The chunk iterator

    Raises:
        TypeError: if values or chunksize is None
        ValueError: if chunksize is negative
    """
    require_non_none(chunksize)
    it = iter(require_non_none(values))
    while True:
        chunk = list(islice(it, chunksize))
        if not chunk:
            return
        yield chunk
