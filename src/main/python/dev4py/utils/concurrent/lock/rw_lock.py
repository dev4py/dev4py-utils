"""The `RWLock` module contains the implementation of a simple Readers-Writer lock class"""

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

from multiprocessing.managers import SyncManager
from threading import Lock as threading_Lock
from typing import Final, Optional, cast

from dev4py.utils.concurrent.protocols import Value, Lock
from dev4py.utils.concurrent.threading import ThreadingValue
from dev4py.utils.objects import is_none
from dev4py.utils.types import Supplier


class _ReadLock(Lock):
    """A private _ReadLock designed for the RWLock class"""

    def __init__(
            self,
            nb_readers: Value[int],
            readers_lock: Lock,
            write_lock: Lock,
            write_lock_shared_access_lock: Lock
    ):
        self._nb_readers: Value[int] = nb_readers
        self._readers_lock: Final[Lock] = readers_lock
        self._write_lock: Final[Lock] = write_lock
        self._write_lock_shared_access_lock: Final[Lock] = write_lock_shared_access_lock

    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        acquire: bool = True
        with self._write_lock_shared_access_lock:
            with self._readers_lock:
                if self._has_readers() is False:
                    # pylint: disable=R1732
                    acquire = self._write_lock.acquire(blocking=blocking, timeout=timeout)

                if acquire is True:
                    self._increase_nb_readers()

        return acquire

    def release(self) -> None:
        with self._readers_lock:
            if self._has_readers() is False:
                raise RuntimeError("release unlocked ReadLock from RWLock")
            self._decrease_nb_readers()
            if self._has_readers() is False:
                self._write_lock.release()

    __enter__ = acquire

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def _has_readers(self) -> bool:
        return self._nb_readers.value > 0

    def _increase_nb_readers(self) -> None:
        self._nb_readers.value += 1

    def _decrease_nb_readers(self) -> None:
        self._nb_readers.value -= 1


class _WriteLock(Lock):
    """A private _WriteLock designed for the RWLock class"""

    def __init__(self, write_lock: Lock, write_lock_shared_access_lock: Lock):
        self._write_lock: Final[Lock] = write_lock
        self._write_lock_shared_access_lock: Final[Lock] = write_lock_shared_access_lock

    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        with self._write_lock_shared_access_lock:
            return self._write_lock.acquire(blocking=blocking, timeout=timeout)

    def release(self) -> None:
        self._write_lock.release()

    __enter__ = acquire

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


class RWLock:
    """
    RWLock class described a threading or multiprocessing lock that allows concurrent access for read-only
    operations, write operations require exclusive access
    """

    def __init__(
            self,
            manager: Optional[SyncManager] = None
    ):
        """
        Create a new RWLock instance

        By default, it can be used for threading case (i.e.: not for multiprocessing)
        Note: A manager can be provided as parameter in order to manage multiprocessing case

        Args:
            manager (optional): the manager to use in manage multiprocessing case (default: None)
        """
        lock_supplier: Supplier[Lock]
        nb_readers_value: Value[int]
        if is_none(manager):
            lock_supplier = threading_Lock
            nb_readers_value = ThreadingValue(0)
        else:
            lock_supplier = cast(SyncManager, manager).Lock
            nb_readers_value = cast(SyncManager, manager).Value(int, 0)

        write_lock_shared_access_lock: Final[Lock] = lock_supplier()
        write_lock: Final[Lock] = lock_supplier()
        self._write_lock: Final[Lock] = _WriteLock(
            write_lock=write_lock,
            write_lock_shared_access_lock=write_lock_shared_access_lock
        )
        self._read_lock: Final[Lock] = _ReadLock(
            nb_readers=nb_readers_value,
            readers_lock=lock_supplier(),
            write_lock=write_lock,
            write_lock_shared_access_lock=write_lock_shared_access_lock
        )

    def write_lock(self) -> Lock:
        """
        Returns the lock used for writing

        Note: If no threads are reading or writing, only one thread can acquire the write lock

        Returns:
            write_lock: the write_Lock
        """
        return self._write_lock

    def read_lock(self) -> Lock:
        """
        Returns the lock used for reading

        Note: If no thread acquired the write lock or requested for it, multiple threads can acquire the read lock

        Returns:
            read_lock: the read_lock
        """
        return self._read_lock
