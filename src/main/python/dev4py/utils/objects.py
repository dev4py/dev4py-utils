"""
The `objects` module provides a set of utility functions to simplify objects/variables operations or checks
"""

from typing import Any, Optional, cast

from dev4py.utils.types import Supplier, T


def is_none(obj: Any) -> bool:
    """
    Checks if the given object is None

    @param obj: the object to check
    @return: True if obj is None, False otherwise
    """
    return obj is None


def non_none(obj: Any) -> bool:
    """
    Checks if the given object is not None

    @param obj: the object to check
    @return: True if obj is not None, False otherwise
    """
    return obj is not None


def require_non_none(obj: Optional[T], message: str = "None object error") -> T:
    """
    Checks if the given object is not None or raises an error

    @param obj: The object to check
    @param message: The error message is case of obj is None
    @return: obj if obj is not None
    @raise TypeError: Raises a TypeError if obj is None
    """
    if is_none(obj):
        raise TypeError(message)
    return cast(T, obj)


def require_non_none_else(obj: Optional[T], default_obj: T) -> T:
    """
    Checks if the given object is not None and returns it or returns the default one

    @param obj: The object to check and return
    @param default_obj: The default object to return if obj is None
    @return: obj if not None, default_obj otherwise
    @raise TypeError: Raises a TypeError if obj and default_obj are None
    """
    return cast(T, obj) if non_none(obj) else require_non_none(default_obj)


def require_non_none_else_get(obj: Optional[T], supplier: Supplier[T]) -> T:
    """
    Checks if the given object is not None and returns it or returns the object from the given supplier

    @param obj: The object to check and return
    @param supplier: The supplier to call if obj is None
    @return: obj if not None, the supplier call result otherwise
    @raise TypeError: Raises a TypeError if obj and supplier or supplied object are None
    """
    return cast(T, obj) if non_none(obj) else require_non_none(require_non_none(supplier, "Supplier cannot be None")())


def to_string(obj: Any, default_str: Optional[str] = None) -> str:
    """
    Returns the result of calling str function for the given object if not null or default_str otherwise

    @param obj: The object
    @param default_str: The str value to return if obj is None
    @return: A str representing obj, default_str otherwise
    """
    return str(obj if non_none(obj) else default_str)
