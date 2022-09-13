"""The `KeyLock` class is used in order to lock threads or processes depending on a key"""

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

from dataclasses import dataclass
from functools import partial
from multiprocessing.managers import SyncManager
# noinspection PyProtectedMember
from multiprocessing.process import current_process, parent_process, BaseProcess, AuthenticationString  # type: ignore
from threading import RLock as threading_RLock
from typing import TypeVar, Hashable, Final, Optional, cast, Generic, Any

from dev4py.utils.concurrent.protocols import Lock, Value
from dev4py.utils.concurrent.threading import ThreadingValue
from dev4py.utils.objects import require_non_none, is_none
from dev4py.utils.types import Supplier, Function

##############################
#         CONSTANTS          #
##############################
K = TypeVar('K', bound=Hashable)
_DEFAULT_NB_USAGE: int = 1


##############################
#  PRIVATE MODULE FUNCTIONS  #
##############################

def _supply_and_check_lock(lock_supplier: Supplier[Lock]) -> Lock:
    lock: Lock = lock_supplier()
    if not isinstance(lock, Lock):
        raise TypeError("Supplier[Lock] error: lock_supplier must supply lock respecting Lock protocol structure")
    return lock


def _build_lock_supplier(
        lock_factory: Optional[Function[Optional[SyncManager], Lock]],
        default: Supplier[Lock],
        manager: Optional[_ShareableManager] = None
) -> Supplier[Lock]:
    if is_none(lock_factory):
        return default

    if not callable(lock_factory):
        raise TypeError("lock_factory must be Callable")

    return partial(_supply_and_check_lock, partial(lock_factory, manager))


def _to_int_value(manager: _ShareableManager, i: int):
    return manager.Value(int, i)


##############################
#      PRIVATE CLASSES       #
##############################
@dataclass
class _LockEntry:
    """_LockEntry class: a KeyLock dict entry"""
    lock: Lock
    nb_usage_value: Value[int]

    def increment_nb_usage(self) -> None:
        self.nb_usage_value.value += 1

    def decrement_nb_usage(self) -> None:
        self.nb_usage_value.value -= 1

    def is_used_only_once(self) -> bool:
        return self.nb_usage_value.value == _DEFAULT_NB_USAGE


class _KeyLockDict(Generic[K]):
    """
    _KeyLockDict class is used in order to manage key & lock mapping

    Notes:
        * loads method is used in order to get (or create if not exists) a new lock based on a key
        * release method is used in order to remove a lock from the _KeyLockDict depending on a key when the lock is no
            longer used
    """

    def __init__(
            self,
            key_lock_dict: dict[K, _LockEntry],
            dict_lock: Lock,
            lock_supplier: Supplier[Lock],
            int_value_function: Function[int, Value[int]]
    ):
        self._key_lock_dict: Final[dict[K, _LockEntry]] = key_lock_dict
        self._dict_lock: Final[Lock] = dict_lock
        self._lock_supplier: Final[Supplier[Lock]] = lock_supplier
        self._int_value_function: Function[int, Value[int]] = int_value_function

    def load(self, key: K) -> Lock:
        with self._dict_lock:
            lock_entry: Optional[_LockEntry] = self._key_lock_dict.get(key)
            if is_none(lock_entry):
                lock_entry = _LockEntry(
                    lock=self._lock_supplier(), nb_usage_value=self._int_value_function(_DEFAULT_NB_USAGE)
                )
                self._key_lock_dict[key] = lock_entry
            else:
                cast(_LockEntry, lock_entry).increment_nb_usage()
            return cast(_LockEntry, lock_entry).lock

    def release(self, key: K) -> Lock:
        with self._dict_lock:
            lock_entry: Optional[_LockEntry] = self._key_lock_dict.get(key)
            if is_none(lock_entry):
                raise RuntimeError("release unlocked KeyLock")

            lock_entry = cast(_LockEntry, lock_entry)
            if lock_entry.is_used_only_once():
                self._key_lock_dict.pop(key)
            else:
                lock_entry.decrement_nb_usage()
            return lock_entry.lock


class _ShareableManager(SyncManager):
    """
    _ShareableManager class implements a multiprocessing.Manager that can be shared between process & subprocesses
    """
    _AUTH_KEY: Final[str] = '_authkey'
    _SOURCE_PROCESS_IDENT_KEY: Final[str] = '_source_process_ident'

    # noinspection PyProtectedMember
    def __init__(self, manager: SyncManager):
        super().__init__(
            address=manager.address,
            authkey=manager._authkey,  # type: ignore
            serializer=manager._serializer,  # type: ignore
            ctx=manager._ctx  # type: ignore
        )
        # pylint: disable=E1101
        self.connect()

    def __getstate__(self) -> dict[str, Any]:
        state = self.__dict__.copy()
        if state[_ShareableManager._AUTH_KEY] == current_process().authkey:
            del state[_ShareableManager._AUTH_KEY]
        else:
            state[_ShareableManager._SOURCE_PROCESS_IDENT_KEY] = current_process().ident
            state[_ShareableManager._AUTH_KEY] = bytes(state[_ShareableManager._AUTH_KEY])
        return state

    def __setstate__(self, state: dict[str, Any]):
        if _ShareableManager._AUTH_KEY in state:
            parent_proc: Final[Optional[BaseProcess]] = parent_process()
            if parent_proc is None or state.pop(_ShareableManager._SOURCE_PROCESS_IDENT_KEY, None) != parent_proc.ident:
                raise RuntimeError(
                    "For security reasons, ShareableManager MUST ONLY BE SHARED LOCALLY BETWEEN PARENT AND SUBPROCESSES"
                )
            state[_ShareableManager._AUTH_KEY] = AuthenticationString(state[_ShareableManager._AUTH_KEY])
        else:
            state[_ShareableManager._AUTH_KEY] = current_process().authkey
        self.__dict__.update(state)


class _KeyLock(Lock, Generic[K]):
    """A thread or process lock by key"""

    def __init__(self, key: K, key_lock_manager: KeyLockManager):
        """
        Create a new KeyLock managed by the given KeyLockManager

        Args:
            key: The key
            key_lock_manager: The KeyLockManager
        """
        self._key: Final[K] = key
        self._key_lock_manager: Final[KeyLockManager] = key_lock_manager

    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        """
        Acquire a lock by using the current key, blocking or non-blocking.

        Args:
            blocking: Set to True, if another thread owns the lock, block until the lock is unlocked.
                Set to False, do not block (i.e.: returns false immediately, otherwise, do the same thing as when
                called with True) (default: True)
            timeout: When set to a positive value, block for at most the number of seconds specified by timeout and
                as long as the lock cannot be acquired (default: -1)

        Returns:
            bool: Return true if the lock has been acquired, false if the timeout has elapsed
        """
        return self._key_lock_manager.acquire(key=self._key, blocking=blocking, timeout=timeout)

    def release(self) -> None:
        """
        Release a lock by using the current key
        """
        self._key_lock_manager.release(key=self._key)

    __enter__ = acquire

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


##############################
#       PUBLIC CLASSES       #
##############################
class KeyLockManager(Generic[K]):
    """A threads or processes KeyLockManager which allows to create locks depending on a key"""

    def __init__(
            self,
            manager: Optional[SyncManager] = None,
            lock_factory: Optional[Function[Optional[SyncManager], Lock]] = None
    ):
        """
        !!!WARNING!!!: IN MULTIPROCESSING CONTEXT DUE TO PERFORMANCE ISSUES USE IT WITH PRECAUTION

        Create a new KeyLockManager which allows to create locks for threads or processes depending on a key

        In Multiprocessing context, a manager MUST be provided. If manager is None, it means the KeyLockManager is used
        in a threading context

        The locks type is defined by the lock_factory. If lock_factory is None, RLock are used (from the manager if
        manager is not None, otherwise threading.RLock are used)

        Note: the configured manager is used as parameter of the lock_factory (i.e.: If None (in threading context)
        the parameter is set to None)

        To use Lock (instead of RLock), you can use: `lambda m: m.lock()` if manager is set otherwise
        `lambda _: threading.lock()`

        Args:
            manager: An optional SyncManager which must be provided in Multiprocessing context. In threading context
                it must set to None (Default: None)
            lock_factory: A function used in order to create each lock. The configured manager is used as parameter. If
                None RLock are used (i.e.: manager.lock if managed is not None otherwise threading.lock)
        """
        self._key_lock_dict: _KeyLockDict[K]
        if is_none(manager):
            self._key_lock_dict = _KeyLockDict(
                key_lock_dict={},
                dict_lock=threading_RLock(),
                lock_supplier=_build_lock_supplier(lock_factory=lock_factory, default=threading_RLock),
                int_value_function=ThreadingValue[int]
            )
        else:
            shareable_manager: Final[_ShareableManager] = _ShareableManager(manager=cast(SyncManager, manager))
            self._key_lock_dict = _KeyLockDict(
                key_lock_dict=cast(dict[K, _LockEntry], shareable_manager.dict()),
                dict_lock=shareable_manager.RLock(),
                lock_supplier=_build_lock_supplier(
                    lock_factory=lock_factory, default=shareable_manager.RLock, manager=shareable_manager
                ),
                int_value_function=partial(_to_int_value, shareable_manager)
            )

    def lock(self, key: K) -> Lock:
        """
        Returns the Lock associated with the given key and created by using the lock_supplier from the constructor

        Args:
            key: The key

        Returns:
            Lock: The Lock associated with the given key and created by using the lock_supplier from the constructor
        """
        return _KeyLock(key=key, key_lock_manager=self)

    def acquire(self, key: K, blocking: bool = True, timeout: float = -1) -> bool:
        """
        Acquire a lock by using the current key, blocking or non-blocking.

        Args:
            key: The key
            blocking: Set to True, if another thread owns the lock, block until the lock is unlocked.
                Set to False, do not block (i.e.: returns false immediately, otherwise, do the same thing as when called
                with True) (default: True)
            timeout: When set to a positive value, block for at most the number of seconds specified by timeout and
                as long as the lock cannot be acquired (default: -1)

        Returns:
            bool: Return true if the lock has been acquired, false if the timeout has elapsed
        """
        require_non_none(key, "KeyLockManager error: key cannot be None")
        acquire: Final[bool] = self._key_lock_dict.load(key=key).acquire(blocking=blocking, timeout=timeout)
        if acquire is False:
            self._key_lock_dict.release(key=key)
        return acquire

    def release(self, key: K) -> None:
        """
        Release a lock by using the current key
        """
        require_non_none(key, "KeyLockManager error: key cannot be None")
        self._key_lock_dict.release(key=key).release()
