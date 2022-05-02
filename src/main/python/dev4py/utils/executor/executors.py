from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, Executor
from multiprocessing.context import BaseContext
from typing import Optional, Callable, Final

from dev4py.utils.executor import EmptyPoolExecutor, ThreadedProcessPoolExecutor


def select_executor(
        max_process_workers: Optional[int] = 0,
        max_thread_workers: Optional[int] = 0,
        mp_context: Optional[BaseContext] = None,
        process_initializer: Optional[Callable[..., None]] = None,
        process_initargs: tuple = (),
        thread_name_prefix: str = '',
        thread_initializer: Optional[Callable[..., None]] = None,
        thread_initargs: tuple = ()
) -> Executor:
    use_threads: Final[bool] = max_thread_workers != 0
    if max_process_workers == 0:
        return thread_pool_executor(
            max_workers=max_thread_workers,
            thread_name_prefix=thread_name_prefix,
            initializer=thread_initializer,
            initargs=thread_initargs
        ) if use_threads else empty_pool_executor()

    return threaded_process_pool_executor(
        max_process_workers=max_process_workers,
        max_thread_workers_per_process=max_thread_workers,
        mp_context=mp_context,
        process_initializer=process_initializer,
        process_initargs=process_initargs,
        thread_name_prefix=thread_name_prefix,
        thread_initializer=thread_initializer,
        thread_initargs=thread_initargs
    ) if use_threads else process_pool_executor(
        max_workers=max_process_workers,
        mp_context=mp_context,
        initializer=process_initializer,
        initargs=process_initargs
    )


def empty_pool_executor() -> EmptyPoolExecutor:
    return EmptyPoolExecutor()


def thread_pool_executor(
        max_workers: Optional[int] = None,
        thread_name_prefix: str = '',
        initializer: Optional[Callable[..., None]] = None,
        initargs: tuple = ()
) -> ThreadPoolExecutor:
    return ThreadPoolExecutor(
        max_workers=max_workers, thread_name_prefix=thread_name_prefix, initializer=initializer, initargs=initargs)


def process_pool_executor(
        max_workers: Optional[int] = None,
        mp_context: Optional[BaseContext] = None,
        initializer: Optional[Callable[..., None]] = None,
        initargs: tuple = ()
) -> ProcessPoolExecutor:
    return ProcessPoolExecutor(
        max_workers=max_workers, mp_context=mp_context, initializer=initializer, initargs=initargs)


def threaded_process_pool_executor(
        max_process_workers: Optional[int] = None,
        max_thread_workers_per_process: Optional[int] = None,
        mp_context: Optional[BaseContext] = None,
        process_initializer: Optional[Callable[..., None]] = None,
        process_initargs: tuple = (),
        thread_name_prefix: str = '',
        thread_initializer: Optional[Callable[..., None]] = None,
        thread_initargs: tuple = ()
) -> ThreadedProcessPoolExecutor:
    return ThreadedProcessPoolExecutor(
        max_process_workers=max_process_workers,
        max_thread_workers_per_process=max_thread_workers_per_process,
        mp_context=mp_context,
        process_initializer=process_initializer,
        process_initargs=process_initargs,
        thread_name_prefix=thread_name_prefix,
        thread_initializer=thread_initializer,
        thread_initargs=thread_initargs
    )
