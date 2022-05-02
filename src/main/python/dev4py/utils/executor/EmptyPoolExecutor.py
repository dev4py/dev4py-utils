from __future__ import annotations

from concurrent.futures import Executor, Future
from typing import Callable

from dev4py.utils.types import T, P


class EmptyPoolExecutor(Executor):

    def __init__(self):
        ...

    def submit(self, fn: Callable[P, T], /, *args: P.args, **kwargs: P.kwargs) -> Future[T]:
        future: Future[T] = Future()
        try:
            future.set_running_or_notify_cancel()
            future.set_result(fn(*args, **kwargs))
        except BaseException as e:
            future.set_exception(e)
        return future
