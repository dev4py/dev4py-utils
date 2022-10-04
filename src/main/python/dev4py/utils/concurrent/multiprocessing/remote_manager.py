"""
This module contains a multiprocessing remote Manager implementation in order to simplify the objects sharing between
processes
"""

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

from contextlib import contextmanager
# noinspection PyProtectedMember
from multiprocessing.context import BaseContext
from multiprocessing.managers import SyncManager
# noinspection PyProtectedMember
from multiprocessing.process import current_process, BaseProcess, AuthenticationString  # type: ignore
from typing import Optional, Callable, TypeVar, Hashable, Any, Iterable, TypeAlias, cast, Iterator

from dev4py.utils import JOptional
from dev4py.utils.objects import non_none, is_none

##############################
#         CONSTANTS          #
##############################
K = TypeVar('K', bound=Hashable)
_REMOTE_DICT_TYPE: TypeAlias = dict[Hashable, Any]
_REMOTE_MANAGER_DICT: Optional[_REMOTE_DICT_TYPE] = None


##############################
#  PRIVATE MODULE FUNCTIONS  #
##############################
def _get_remote_manager_dict_singleton() -> _REMOTE_DICT_TYPE:
    # pylint: disable=W0603
    global _REMOTE_MANAGER_DICT
    if is_none(_REMOTE_MANAGER_DICT):
        _REMOTE_MANAGER_DICT = {}
    return cast(_REMOTE_DICT_TYPE, _REMOTE_MANAGER_DICT)


def _put(key: K, value: Any) -> None:
    _get_remote_manager_dict_singleton()[key] = value


def _get(key: K) -> Optional[Any]:
    return _get_remote_manager_dict_singleton().get(key)


##############################
#       PUBLIC CLASSES       #
##############################
class RemoteManager(SyncManager):
    """
    RemoteManager class: a `SyncManager` implementation in order to simplify the objects sharing between processes

    Notes:
        In addition to SyncManager methods, it provides:
        * A `put` method in order to add instantiated object and associated it with a key
        * A `get` method in order to get the object associated to a key

        Since manipulated objects type are not predictable, AutoProxy is used in order to "proxify" them
    """

    def __init__(
            self,
            address: Optional[tuple[str, int]] = None,
            authkey: Optional[bytes] = None,
            serializer: str = 'pickle',
            ctx: Optional[BaseContext] = None
    ):
        """
        RemoteManager constructor

        Args:
            address (tuple[str, int]): A tuple['Host', Port] (example ('127.0.0.1', 5000)) representing the manager
                address (optional, default: None)
            authkey: The authentication key (optional, default: None)
            serializer: The serializer (default: pickle)
            ctx: The BaseContext (optional, default: None)
        """
        super().__init__(address=address, authkey=authkey, serializer=serializer, ctx=ctx)
        self._required_process_authkey: Optional[AuthenticationString] = \
            AuthenticationString(authkey) if non_none(authkey) else None
        self._process_authkey: Optional[AuthenticationString] = None
        self._port: int = \
            cast(int, JOptional.of_noneable(address).filter(lambda a: len(a) == 2).map(lambda a: a[-1]).or_else(0))

    def start(self, initializer: Optional[Callable[..., Any]] = None, initargs: Iterable[Any] = ()) -> None:
        """
        Spawn a server process for this manager object

        Args:
            initializer: If initializer is not None then the subprocess will call initializer(*initargs) when it starts
            initargs: The initializer arguments

        Notes:
            Prefer use `with` statement instead of calling start/shutdown directly

        Examples:
            ```python
            // Prefer use "with" statement instead of calling start/shutdown directly
            with RemoteManager() as manager:
                ...
            ```
        """
        self._configure_authkey()
        # pylint: disable=R1732
        super().start(initializer=initializer, initargs=initargs)

    def shutdown(self) -> None:
        """
        Shutdown the manager process.

        Notes:
            * Only available after start() was called
            * Prefer use `with` statement instead of calling start/shutdown directly

        Examples:
            ```python
            // Prefer use "with" statement instead of calling start/shutdown directly
            with RemoteManager() as manager:
                ...
            ```
        """
        self._reset_authkey()
        super().shutdown()

    def connect(self) -> None:
        """
        Connect manager object to the server process

        Notes:
            * This method is used by remote client manager
            * Please prefer use `with` statement with the `client` method

        Examples:
            ```python
            // Please Prefer use "with" statement with the `client` method
            with RemoteManager(address=('HOST', PORT), authkey=b'secret_key').client() as client_manager:
                ...
            ```
        """
        self._configure_authkey()
        # pylint: disable=E1101
        super().connect()

    def disconnect(self) -> None:
        """
        Disconnect manager object from the server process

        Notes:
            * This method is used by remote client manager
            * Please prefer use `with` statement with the `client` method

        Examples:
            ```python
            // Please Prefer use "with" statement with the `client` method
            with RemoteManager(address=('HOST', PORT), authkey=b'secret_key').client() as client_manager:
                ...
            ```
        """
        self._reset_authkey()

    @contextmanager
    def client(self) -> Iterator[RemoteManager]:
        """
        A method to use with the `with` statement for remote client manager

        Examples:
            ```python
            with RemoteManager(address=('HOST', PORT), authkey=b'secret_key').client() as client_manager:
                ...
            ```

        Returns:
             Iterator[RemoteManager]: The RemoteManager client instance
        """
        try:
            self.connect()
            yield self
        finally:
            self.disconnect()

    def put(self, key: K, value: Any) -> None:
        """
        Associates the specified value with the specified key in the current RemoteManager

        Args:
            key: The key with which the specified value is to be associated
            value: The value to be associated with the specified key
        """
        # pylint: disable=E1101
        # noinspection PyUnresolvedReferences
        return self._put(self._build_instance_key(key), value)  # type: ignore

    def get(self, key: K) -> Optional[Any]:
        """
        Returns the value from the current RemoteManager with the given key if presents, otherwise returns None

        Args:
            key: The searched key

        Returns:
            Optional[Any]: The value from the current RemoteManager with the given key if presents, otherwise returns
                None
        """
        # pylint: disable=E1101
        # noinspection PyUnresolvedReferences
        return self._get(self._build_instance_key(key))  # type: ignore

    def _configure_authkey(self) -> None:
        """
        If an authkey is specified, we have to use it as current process authkey in order to avoid known python manager
        errors
        """
        if non_none(self._required_process_authkey):
            process: BaseProcess = current_process()
            self._process_authkey = process.authkey
            process.authkey = cast(AuthenticationString, self._required_process_authkey)

    def _reset_authkey(self) -> None:
        """
        If an authkey is specified, we have to reset the current process authkey when the current manager is closed in
        order to reset the initial process context
        """
        if non_none(self._process_authkey):
            current_process().authkey = cast(AuthenticationString, self._process_authkey)

    def _build_instance_key(self, key: K) -> tuple[int, K]:
        """
        Since the _REMOTE_MANAGER_DICT is a global singleton we have to build specific RemoteManager instance key in
        order to avoid potential key conflicts if several RemoteManagers are used on the same host. TO do that, each
        object key is completed by the current RemoteManager port

        Args:
            key: The key to use

        Returns:
            tuple[int, K]: A key without conflict between RemoteManager instances (tuple[port, key])
        """
        return self._port, key


# pylint: disable=E1101
RemoteManager.register('_put', callable=_put)
# pylint: disable=E1101
RemoteManager.register('_get', callable=_get)
