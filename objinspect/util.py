import typing as T
from types import FunctionType
from enum import EnumMeta

import typing_extensions


def type_to_str(t: T.Any) -> str:
    """
    Convert a Python type to its string representation (without the module name).

    Args:
        t (Any): A Python type.

    Returns:
        str: The string representation of the Python type.

    Example:
        >>> type_to_str(datetime.datetime)
        'datetime'
        >>> type_to_str(int)
        'int'
    """
    type_str = repr(t)
    if "<class '" in type_str:
        type_str = type_str.split("'")[1]
    return type_str.split(".")[-1]


def get_enum_choices(e) -> tuple[str, ...]:
    """
    Get the options of a Python Enum.

    Args:
        e (enum.Enum): A Python Enum.

    Returns:
        tuple: A tuple of the names of the Enum options.

    Example:
        >>> import enum
        >>> class Color(enum.Enum):
        ...     RED = 1
        ...     GREEN = 2
        ...     BLUE = 3
        >>> get_enum_choices(Color)
        ('RED', 'GREEN', 'BLUE')
    """
    return tuple(e.__members__.keys())


def get_literal_choices(literal_t) -> tuple[str, ...]:
    """
    Get the options of a Python Literal.
    """
    return T.get_args(literal_t)


def call_method(obj: object, name: str, args: tuple = (), kwargs: dict = {}) -> T.Any:
    """
    Call a method with the given name on the given object.

    Args:
        obj (object): The object to call the method on.
        name (str): The name of the method to call.
        args (tuple, optional): The positional arguments to pass to the method. Defaults to ().
        kwargs (dict, optional): The keyword arguments to pass to the method. Defaults to {}.

    Returns:
        object: The result of calling the method.

    Examples:
    >>> import math
    >>> call_method(math, "pow", args=(2, 2))
    4.0
    """
    return getattr(obj, name)(*args, **kwargs)


def get_uninherited_methods(cls) -> list[str]:
    """
    Get the methods of a class that are not inherited from its parent classes.
    """
    return [
        name
        for name, method in cls.__dict__.items()
        if isinstance(method, (FunctionType, classmethod, staticmethod))
    ]


def is_enum(t: T.Any) -> bool:
    return isinstance(t, EnumMeta)


def is_literal(t: T.Any) -> bool:
    return t is typing_extensions.Literal or (
        hasattr(t, "__origin__") and t.__origin__ is typing_extensions.Literal
    )


__all__ = [
    "type_to_str",
    "get_enum_choices",
    "get_literal_choices",
    "call_method",
    "get_uninherited_methods",
    "is_enum",
    "is_literal",
]
