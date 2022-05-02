from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor, ProcessPoolExecutor
from multiprocessing import Manager
from multiprocessing.context import BaseContext
from multiprocessing.managers import ValueProxy
from queue import Queue
from threading import Thread, Lock, Semaphore
from typing import Optional, Callable, Generic, Union, Final, cast
from uuid import UUID, uuid4

from dev4py.utils.objects import non_none, require_non_none
from dev4py.utils.types import P, T


##############################
#      GLOBAL VARIABLES      #
#    (process local vars)    #
##############################
# Note:
#   - All global variables are process local but shared by threads
#   - Using UUID as executor identifier to avoid conflict in multi executor in Multithread (not multiprocess) context
#   - Python's built-in structures are thread-safe for single operations
class _ProcessVariables:
    def __init__(self):
        self.thread_pools: dict[UUID, ThreadPoolExecutor] = {}
        self.queue: Optional[Queue] = None
        self.semaphore: Optional[Semaphore] = None
        self.queue_lock: Lock = Lock()

    def get_queue(self) -> Queue:
        return require_non_none(self.queue)

    def get_semaphore(self) -> Semaphore:
        return require_non_none(self.semaphore)


_PROCESS_VARS = _ProcessVariables()


##############################
#        PUBLIC CLASS        #
##############################
class ThreadedProcessPoolExecutor(ProcessPoolExecutor):
    def __init__(
            self,
            max_process_workers: Optional[int] = None,
            max_thread_workers_per_process: Optional[int] = None,
            mp_context: Optional[BaseContext] = None,
            process_initializer: Optional[Callable[..., None]] = None,
            process_initargs: tuple = (),
            thread_name_prefix: str = '',
            thread_initializer: Optional[Callable[..., None]] = None,
            thread_initargs: tuple = ()
    ):
        self._id: Final[UUID] = uuid4()
        self._task_id: int = 0
        self._task_in_progress: dict[int, Future] = {}
        self._manager: Final[Manager] = Manager()
        self._results_queues: list[Queue] = []
        self._results_threads: list[Thread] = []
        queue_idx = self._manager.Value('i', -1)
        for _ in range(0, max_process_workers):
            queue: Queue = self._manager.Queue()  # Queue[Optional[tuple[int, _ThreadResult]]]
            thread: Thread = Thread(target=self._fill_results_job, args=(queue,))
            self._results_queues.append(queue)
            self._results_threads.append(thread)
            thread.start()

        super().__init__(
            max_workers=max_process_workers,
            mp_context=mp_context,
            initializer=_process_initializer,
            initargs=(
                self._id,
                self._manager.Lock(),
                queue_idx,
                self._results_queues,
                max_thread_workers_per_process,
                process_initializer,
                process_initargs,
                thread_name_prefix,
                thread_initializer,
                thread_initargs
            )
        )

    def shutdown(self, wait=True, *, cancel_futures=False) -> None:
        try:
            # Sends signal to stop
            for queue in self._results_queues:
                queue.put(None)
            for thread in self._results_threads:
                thread.join(timeout=2)
        finally:
            try:
                if self._task_in_progress:
                    if cancel_futures:
                        for future in self._task_in_progress.values():
                            future.cancel()
                    raise RuntimeError("Shutdown ThreadedProcessPoolExecutor while tasks still run")
            finally:
                try:
                    super().shutdown(wait=wait, cancel_futures=cancel_futures)
                finally:
                    self._manager.shutdown()
        # TODO: shutdown threadpool

    def submit(self, fn: Callable[P, T], /, *args: P.args, **kwargs: P.kwargs) -> Future[T]:
        future: Future[T] = Future()
        self._task_id = self._task_id + 1 % 2147483647  # C INT_MAX: avoid infinite incrementation
        future.set_running_or_notify_cancel()
        self._task_in_progress[self._task_id] = future
        super().submit(_process_with_threads_submit, self._id, self._task_id, fn, *args, **kwargs)
        return future

    def _fill_results_job(self, queue: Queue) -> None:
        go_next: bool = True
        while go_next:
            result: Union[Optional[tuple[int, _ThreadResult[T]]]] = queue.get()
            go_next = non_none(result)
            if go_next:
                _copy_future_state(result[1], self._task_in_progress.pop(result[0]))
            queue.task_done()


##############################
#   PRIVATE MODULE CLASSES   #
##############################
class _ThreadResult(Generic[T]):
    """
    This private class is useful to avoid "TypeError: cannot pickle '_thread.RLock' object" when returning Future from
    process pool to the main process
    """

    def __init__(self):
        self._done: bool = False
        self._cancelled: bool = False
        self._result: Optional[T] = None
        self._exception: Optional[BaseException] = None
        self._done_callbacks: list[Callable[[_ThreadResult[T]], None]] = []

    def set_result(self, result: T) -> None:
        self._result: Optional[T] = result
        self._done = True
        self._invoke_callbacks()

    def result(self) -> Optional[T]:
        return self._result

    def cancelled(self):
        return self._cancelled

    def cancel(self):
        self._cancelled = True
        self._invoke_callbacks()

    def set_running_or_notify_cancel(self):
        return not self._cancelled

    def set_exception(self, exception: BaseException) -> None:
        self._exception = exception
        self._done = True
        self._invoke_callbacks()

    def exception(self):
        return self._exception

    def running(self) -> bool:
        return not (self._done or self._cancelled)

    def add_done_callback(self, fn: Callable[[_ThreadResult[T]], None]):
        if self._done or self._cancelled:
            fn(self)
        else:
            self._done_callbacks.append(fn)

    def _invoke_callbacks(self):
        for callback in self._done_callbacks:
            callback(self)


##############################
#  PRIVATE MODULE FUNCTIONS  #
##############################
def _process_initializer(
        executor_id: UUID,
        process_lock: Lock,
        pool_queue_idx: ValueProxy[int],
        pool_queues: list[Queue],
        max_thread_workers: Optional[int],
        processes_initializer: Optional[Callable[..., None]],
        processes_initargs: tuple,
        thread_name_prefix: str,
        thread_initializer: Optional[Callable[..., None]],
        thread_initargs: tuple
) -> None:
    with process_lock:
        pool_queue_idx.set(pool_queue_idx.get() + 1)
        _PROCESS_VARS.queue = pool_queues[pool_queue_idx.get()]
    _PROCESS_VARS.thread_pools[executor_id] = \
        ThreadPoolExecutor(
            max_workers=max_thread_workers,
            thread_name_prefix=thread_name_prefix,
            initializer=thread_initializer,
            initargs=thread_initargs
        )
    _PROCESS_VARS.semaphore = Semaphore(max_thread_workers - 1)
    if non_none(processes_initializer):
        cast(Callable[..., None], processes_initializer)(*processes_initargs)


def _copy_future_state(source: Union[Future[T], _ThreadResult[T]], destination: Union[Future[T], _ThreadResult[T]]):
    if source.cancelled():
        destination.cancel()
    if not destination.running() and not destination.set_running_or_notify_cancel():
        return
    exception = source.exception()
    if exception is not None:
        destination.set_exception(exception)
    else:
        result = source.result()
        destination.set_result(result)


def _to_thread_result(future: Future[T]) -> _ThreadResult[T]:
    thread_result: Final[_ThreadResult[T]] = _ThreadResult()
    _copy_future_state(future, thread_result)
    return thread_result


def _process_with_threads_submit(
        executor_id: UUID, task_id: int, fn: Callable[P, T], /, *args: P.args, **kwargs: P.kwargs
) -> None:
    future: Future[T] = require_non_none(_PROCESS_VARS.thread_pools.get(executor_id)).submit(fn, *args, **kwargs)
    # Note: we have to use a Queue to send result in order to not lock the current process while waiting result
    future.add_done_callback(lambda f: _thread_done_callback(task_id, f))
    _PROCESS_VARS.get_semaphore().acquire()


def _thread_done_callback(task_id: int, future: Future[T]) -> None:
    with _PROCESS_VARS.queue_lock:
        _PROCESS_VARS.get_queue().put((task_id, _to_thread_result(future)))
    _PROCESS_VARS.get_semaphore().release()
