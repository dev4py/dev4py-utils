"""The `JOptional` class provides a java like Optional class"""
from __future__ import annotations

from typing import Generic, Optional, Final, Any, cast

from dev4py.utils import objects
from dev4py.utils.types import T, Supplier, Function, R, Consumer, Runnable, Predicate


class JOptional(Generic[T]):
    """A class inspired from the java.util.Optional class"""

    __EMPTY: JOptional[Any]
    __CREATE_KEY: Final[object] = object()
    __NO_VALUE_ERROR_MSG: Final[str] = "No value present"

    @classmethod
    def of(cls, value: T) -> JOptional[T]:
        """
        Returns a JOptional describing the given non-None value

        Args:
            value: The value to describe, which must be non-None

        Returns:
            JOptional[T]: A JOptional of value T type with the value present

        Raises:
            TypeError: Raises a TypeError if value is None
        """
        return JOptional(objects.require_non_none(value, cls.__NO_VALUE_ERROR_MSG), cls.__CREATE_KEY)

    @classmethod
    def of_noneable(cls, value: Optional[T]) -> JOptional[T]:
        """
        Returns a JOptional describing the given value, if non-None, otherwise returns an empty JOptional

        Args:
            value: The possibly-None value to describe

        Returns:
            JOptional[T]: A JOptional of value T type with the value present if the specified value is non-None,
            otherwise an empty Optional
        """
        return cls.empty() if objects.is_none(value) else cls.of(cast(T, value))

    @classmethod
    def empty(cls) -> JOptional[T]:
        """Return an empty instance of JOptional"""
        return cls.__EMPTY

    def __init__(self, value: Optional[T], create_key: object):
        """JOptional private constructor: Constructs an instance with the described value"""
        assert create_key == self.__CREATE_KEY, \
            "JOptional private constructor! Please use JOptional.of or JOptional.of_noneable"
        self._value: Optional[T] = value

    def is_present(self) -> bool:
        """
        If a value is present, returns true, otherwise false

        Returns:
            bool: true if a value is present, otherwise false
        """
        return objects.non_none(self._value)

    def is_empty(self) -> bool:
        """
        If a value is not present, returns true, otherwise false.

        Returns:
            bool: true if a value is not present, otherwise false
        """
        return objects.is_none(self._value)

    def get(self) -> T:
        """
        If a value is present, returns the value, otherwise raises a ValueError

        Returns:
            value: The non-None value described by this JOptional

        Raises:
            ValueError: Raises a ValueError no value is present
        """
        return self.or_else_raise()

    def or_else(self, other: Optional[T]) -> Optional[T]:
        """
        If a value is present, returns the value, otherwise returns other
        Args:
            other: The value to be returned, if no value is present. May be None.

        Returns:
            value: The value, if present, otherwise other
        """
        return self.or_else_get(lambda: other)

    def or_else_get(self, supplier: Supplier[Optional[T]]) -> Optional[T]:
        """
        If a value is present, returns the value, otherwise returns the result produced by the supplying function

        Args:
            supplier: The supplying function that produces a value to be returned

        Returns:
            value: The value, if present, otherwise the result produced by the supplying function

        Raises:
            TypeError: if no value is present and the supplying function is None
        """
        return self._value if self.is_present() else supplier()

    def or_else_raise(
            self, supplier: Supplier[Exception] = lambda: cast(Exception, ValueError(JOptional.__NO_VALUE_ERROR_MSG))
    ) -> T:
        """
        If a value is present, returns the value, otherwise raises an exception produced by the exception supplying
        function

        Args:
            supplier: The supplying function that produces an exception to be raised (default: ValueError)

        Returns:
            value: The value, if present

        Raises:
            Exception: If no value is present
            TypeError: if no value is present and the exception supplying function is None
        """
        if self.is_empty():
            raise supplier()
        return cast(T, self._value)

    def or_get(self, supplier: Supplier[JOptional[T]]) -> JOptional[T]:
        """
        This is the `or` equivalent in java Optional (Reminder: `or` is a python keyword)

        If a value is present, returns a JOptional describing the value, otherwise returns a JOptional produced by the
        supplying function

        Args:
            supplier: The supplying function that produces a JOptional to be returned

        Returns:
            JOptional[T]: Returns a JOptional describing the value of this JOptional, if a value is present, otherwise
            a JOptional produced by the supplying function

        Raises:
            TypeError: if the supplying function is None or value is not present and produces a None result
        """
        objects.require_non_none(supplier)
        return self if self.is_present() else objects.require_non_none(supplier())

    def map(self, mapper: Function[T, R]) -> JOptional[R]:
        """
        If a value is present, returns a JOptional describing (as if by of_noneable) the result of applying the given
        mapping function to the value, otherwise returns an empty JOptional

        If the mapping function returns a None result then this method returns an empty JOptional.

        Args:
            mapper: The mapping function to apply to a value, if present

        Returns:
            JOptional[R]: A JOptional describing the result of applying a mapping function to the value of this
            JOptional, if a value is present, otherwise an empty JOptional

        Raises:
            TypeError: If the mapping function is None
        """
        return self.flat_map(lambda v: JOptional.of_noneable(objects.require_non_none(mapper)(v)))

    def flat_map(self, mapper: Function[T, JOptional[R]]) -> JOptional[R]:
        """
        If a value is present, returns the result of applying the given JOptional-bearing mapping function to the value,
        otherwise returns an empty JOptional

        This method is similar to map(Function), but the mapping function is one whose result is already a JOptional,
        and if invoked, flatMap does not wrap it within an additional JOptional

        Args:
            mapper: The mapping function to apply to a value, if present

        Returns:
            JOptional[R]: The result of applying a JOptional-bearing mapping function to the value of this JOptional,
            if a value is present, otherwise an empty JOptional

        Raises:
            TypeError: if the mapping function is None or returns a None result
        """
        objects.require_non_none(mapper)
        return JOptional.empty() if self.is_empty() else objects.require_non_none(mapper(cast(T, self._value)))

    def if_present(self, consumer: Consumer[T]) -> None:
        """
        If a value is present, performs the given consumer with the value, otherwise does nothing

        Args:
            consumer: The consumer to be performed, if a value is present

        Returns:
            Nothing

        Raises:
            TypeError: if the consumer is None and the value is present
        """
        # pylint: disable=W0106
        self.is_present() and consumer(cast(T, self._value))

    def if_empty(self, empty_action: Runnable) -> None:
        """
        If a value is not present, performs the given runnable, otherwise does nothing

        Args:
            empty_action: The runnable to be performed, if a value is not present

        Returns:
            Nothing

        Raises:
            TypeError: if the runnable is None and the value is not present
        """
        # pylint: disable=W0106
        self.is_empty() and empty_action()

    def if_present_or_else(self, consumer: Consumer[T], empty_action: Runnable) -> None:
        """
        If a value is present, performs the given consumer with the value, otherwise performs the given empty_action

        Args:
            consumer: The consumer to be performed, if a value is present
            empty_action: The runnable to be performed, if a value is not

        Returns:
            Nothing

        Raises:
            TypeError: if the consumer is None and the value is present or if the runnable is None and the value is not
            present
        """
        # pylint: disable=W0106
        consumer(cast(T, self._value)) if self.is_present() else empty_action()

    def filter(self, predicate: Predicate[T]) -> JOptional[T]:
        """
        If a value is present, and the value matches the given predicate, returns a JOptional describing the value,
        otherwise returns an empty JOptional

        Args:
            predicate: The predicate to apply to a value, if present

        Returns:
            JOptional[T]: A JOptional describing the value of this JOptional, if a value is present and the value
            matches the given predicate, otherwise an empty JOptional

        Raises:
            TypeError: if the predicate is None
        """
        return self if self.is_empty() or predicate(cast(T, self._value)) else JOptional.empty()

    def peek(self, consumer: Consumer[T]) -> JOptional[T]:
        """
        If a value is present, performs the given consumer with the value, otherwise does nothing and returns the
        current JOptional

        Args:
            consumer: The consumer to be performed, if a value is present

        Returns:
             JOptional[T]: The current JOptional (self)

        Raises:
            TypeError: if the consumer is None and the value is present
        """
        self.if_present(consumer)
        return self


# INIT STATIC VARIABLES
# noinspection PyProtectedMember
# noinspection PyUnresolvedReferences
# pylint: disable=W0212
JOptional._JOptional__EMPTY = JOptional(None, JOptional._JOptional__CREATE_KEY)  # type: ignore
