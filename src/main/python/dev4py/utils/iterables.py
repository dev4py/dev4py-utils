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
