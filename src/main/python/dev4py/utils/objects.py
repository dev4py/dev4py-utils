"""
The `objects` module provides a set of utility functions to simplify objects/variables operations or checks
"""

from typing import Any, Optional, cast

from dev4py.utils.types import Supplier, T


def is_none(obj: Any) -> bool:
    """
    Checks if the given object is None

    Args:
        obj: The object to check

    Returns:
        object: True if obj is None, False otherwise
    """
    return obj is None


def non_none(obj: Any) -> bool:
    """
    Checks if the given object is not None

    Args:
        obj: The object to check

    Returns:
        object: True if obj is NOT None, False otherwise
    """
    return obj is not None


def require_non_none(obj: Optional[T], message: str = "None object error") -> T:
    """
    Checks if the given object is not None or raises an error

    Args:
        obj: The object to check
        message: The error message is case of obj is None

    Returns:
        object: obj if obj is not None

    Raises:
        TypeError: Raises a TypeError if obj is None
    """
    if is_none(obj):
        raise TypeError(message)
    return cast(T, obj)


def require_non_none_else(obj: Optional[T], default: T) -> T:
    """
    Checks if the given object is not None and returns it or returns the default one

    Args:
        obj: The object to check and return
        default: The default object to return if obj is None

    Returns:
        object: obj if not None, default_obj otherwise

    Raises:
        TypeError: Raises a TypeError if obj and default_obj are None
    """
    return cast(T, obj) if non_none(obj) else require_non_none(default)


def require_non_none_else_get(obj: Optional[T], supplier: Supplier[T]) -> T:
    """
    Checks if the given object is not None and returns it or returns the object from the given supplier

    Args:
        obj: The object to check and return
        supplier: The supplier to call if obj is None

    Returns:
        object: obj if not None, the supplier call result otherwise

    Raises:
        TypeError: Raises a TypeError if obj and supplier or supplied object are None
    """
    return cast(T, obj) if non_none(obj) else require_non_none(require_non_none(supplier, "Supplier cannot be None")())


def to_string(obj: Any, default_str: Optional[str] = None) -> str:
    """
    Returns the result of calling str function for the given object if not null or default_str otherwise

    Args:
        obj: The object to stringify
        default_str: The str value to return if obj is None

    Returns:
        str: A str representing obj, default_str otherwise
    """
    return str(obj if non_none(obj) else default_str)
